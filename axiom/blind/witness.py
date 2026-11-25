"""Blind witness construction over residue classes.

Applies to any target of the shape

    forall n >= L: exists v1 >= l1: ... exists vk >= lk: LHS = RHS

with LHS, RHS rational in n and the v's. Nothing here knows which problem it
is working on. The method:

  1. Moduli come from the statement itself: the integer coefficients of the
     cleared equation give a base b, and the schedule is lcm(b, 1..j).
  2. For each residue class n = M k + r, search integer polynomial witnesses
     from a small generic grammar: (atom + c) / d, where the atoms are built
     from n and the witnesses already chosen (n, n^2, v_j, n v_j, v_i v_j).
  3. The last variable is solved exactly from the equation when it can be;
     otherwise it is searched like the others.
  4. Cheap numeric filtering at several k, then exact symbolic checks, then a
     kernel proof (forall_exists_witness chain + algebraic_identity).
  5. Classes that fail are lifted to the next modulus and tried again with a
     larger grammar. After every pass the kernel certifies a reduction
     theorem with residue_cover: the target follows from the open classes.
     If no class is open, that is a complete proof of the target.
"""
from __future__ import annotations

import math
import time
from dataclasses import dataclass
from functools import reduce
from typing import Dict, List, Optional, Tuple

import sympy as sp

from ..kernel.expressions import Const, Var, from_sympy, sym
from ..kernel.inference import class_instance
from ..kernel.proof_objects import Proof
from ..kernel.propositions import And, Eq, Exists, ForAll, Implies, Le, Prop


@dataclass
class Shape:
    n: Var
    lower: int
    vars: List[Tuple[str, int]]
    body: Prop
    eq: Eq


def detect(goal: Prop) -> Optional[Shape]:
    if not isinstance(goal, ForAll):
        return None
    vars_, p = [], goal.body
    while isinstance(p, Exists):
        vars_.append((p.var.name, p.lower))
        p = p.body
    if not vars_ or not isinstance(p, Eq):
        return None
    if not (p.lhs.is_closed_form() and p.rhs.is_closed_form()):
        return None
    return Shape(goal.var, goal.lower, vars_, goal.body, p)


def _lcm(a, b):
    return a * b // math.gcd(a, b)


class Engine:
    def __init__(self, shape: Shape):
        self.s = shape
        self.N = sym(shape.n.name)
        self.V = [sym(v) for v, _ in shape.vars]
        expr = sp.together(shape.eq.lhs.to_sympy() - shape.eq.rhs.to_sympy())
        num, _ = sp.fraction(expr)
        self.num = sp.expand(num)
        args = [self.N] + self.V
        self.num_f = sp.lambdify(args, self.num, modules="math")
        # exact solution for the last variable, if rational
        self.last_solver = None
        try:
            sols = sp.solve(self.num, self.V[-1])
        except Exception:
            sols = []
        for sol in sols:
            if sol.free_symbols <= set([self.N] + self.V[:-1]) and sol.is_rational_function(*args[:-1]):
                A, B = sp.fraction(sp.together(sol))
                A, B = sp.expand(A), sp.expand(B)
                den = reduce(_lcm, [sp.Rational(c).q for c in
                                    sp.Poly(A, *args[:-1]).coeffs() + sp.Poly(B, *args[:-1]).coeffs()], 1)
                A, B = sp.expand(A * den), sp.expand(B * den)
                self.last_solver = (A, B, sp.lambdify(args[:-1], A, modules="math"),
                                    sp.lambdify(args[:-1], B, modules="math"))
                break
        coeffs = [abs(int(c)) for c in sp.Poly(self.num, *args).coeffs() if sp.Rational(c).q == 1]
        base = reduce(_lcm, [c for c in coeffs if c > 1], 1)
        self.base = base

    # ---------------------------------------------------------------- moduli
    def moduli(self, limit: int = 20000) -> List[int]:
        out, cur = [], self.base
        for j in range(1, 30):
            cur = _lcm(cur, j)
            if cur > limit:
                break
            if not out or cur != out[-1]:
                out.append(cur)
        return out

    # --------------------------------------------------------------- grammar
    def _atoms(self, i: int, nv, wv):
        """Atom values at the samples for variable i: list of (sym_expr, values)."""
        N = self.N
        atoms = [(N, nv), (N * N, [a * a for a in nv])]
        for j in range(i):
            atoms.append((self.V[j], wv[j]))
            atoms.append((N * self.V[j], [a * b for a, b in zip(nv, wv[j])]))
        for j in range(i):
            for l in range(j, i):
                atoms.append((self.V[j] * self.V[l], [a * b for a, b in zip(wv[j], wv[l])]))
        return atoms

    def _candidates(self, i, nv, wv, T, D, lo):
        out = []
        for rank, (a_sym, a_val) in enumerate(self._atoms(i, nv, wv)):
            for d in range(1, D + 1):
                res = {v % d for v in a_val}
                if len(res) != 1:
                    continue
                base_c = (-res.pop()) % d
                c0 = base_c - d  # small negative offsets only (c0 >= -d)
                while c0 <= T:
                    vals = [(v + c0) // d for v in a_val]
                    if min(vals) >= lo:
                        out.append((rank * 3 + d + 2 * abs(c0) + (1 if c0 < 0 else 0), (a_sym + c0) / d, vals))
                    c0 += d
        out.sort(key=lambda t: t[0])
        return out

    # ------------------------------------------------------------ one class
    def search_class(self, M: int, r: int, T: int, D: int, deadline: float):
        L = self.s.lower
        kl = max(0, -(-(L - r) // M))
        ks = [kl + j for j in (0, 1, 2, 3, 5, 8)]
        nv = [M * k + r for k in ks]
        k_sym = sp.Symbol("k", integer=True)
        nsub = M * k_sym + r
        nvars = len(self.V)
        free_last = self.last_solver is not None
        searched = nvars - 1 if free_last else nvars
        lows = [lo for _, lo in self.s.vars]
        steps = [0]

        def finish(wsyms):
            # exact symbolic check of all witnesses as polynomials in k
            polys = []
            subs = {self.N: nsub}
            for idx, w in enumerate(wsyms):
                e = sp.expand(sp.cancel(sp.together(w.subs(subs))))
                if not e.is_polynomial(k_sym):
                    return None
                pk = sp.Poly(e, k_sym)
                if any(sp.Rational(c).q != 1 for c in pk.coeffs()):
                    return None
                polys.append(e)
                subs[self.V[idx]] = e
            return polys

        exhausted = [True]

        def rec(i, wv, wsyms, budget):
            steps[0] += 1
            if steps[0] % 2000 == 0 and time.time() > deadline:
                raise TimeoutError
            if i == searched:
                if free_last:
                    A, B, Af, Bf = self.last_solver
                    for s_idx in range(len(nv)):
                        args = [nv[s_idx]] + [w[s_idx] for w in wv]
                        b = Bf(*args)
                        if b == 0:
                            return None
                        a = Af(*args)
                        if a % b or a // b < lows[-1]:
                            return None
                    ws = wsyms + [A / B]
                else:
                    for s_idx in range(len(nv)):
                        args = [nv[s_idx]] + [w[s_idx] for w in wv]
                        if self.num_f(*args) != 0:
                            return None
                    ws = wsyms
                return finish(ws)
            for cost, w_sym, vals in self._candidates(i, nv, wv, T, D, lows[i]):
                if cost > budget:
                    exhausted[0] = False      # something was skipped: deepen later
                    break
                got = rec(i + 1, wv + [vals], wsyms + [w_sym], budget - cost)
                if got is not None:
                    return got
            return None

        # iterative deepening on the total cost of all unknowns together, so a
        # cheap y is never starved by an expensive search below an early x
        polys, budget = None, 24
        try:
            while True:
                exhausted[0] = True
                polys = rec(0, [], [], budget)
                if polys is not None or exhausted[0]:
                    break
                budget *= 2
        except TimeoutError:
            return None, kl, "timeout"
        if polys is None:
            return None, kl, "exhausted"
        # positivity from kl, checked by shift; kernel re-checks anyway
        return polys, kl, "found"

    # ----------------------------------------------------------- proof
    def class_statement(self, M, r, kl):
        return ForAll(Var("k", self.s.n.typ), class_instance(self.s.body, self.s.n, M, r), kl)

    def class_proof(self, M, r, kl, polys) -> Proof:
        k = Var("k", self.s.n.typ)
        ws = [from_sympy(p) for p in polys]
        goal = self.class_statement(M, r, kl)
        bodies = [goal.body]
        for (vname, _), w in zip(self.s.vars, ws):
            bodies.append(bodies[-1].body.subst({vname: w}))
        proof = Proof("algebraic_identity", ForAll(k, bodies[-1], kl))
        for idx in range(len(ws) - 1, -1, -1):
            low = Proof("shift_nonneg", ForAll(k, Le(Const(self.s.vars[idx][1]), ws[idx]), kl))
            proof = Proof("forall_exists_witness", ForAll(k, bodies[idx], kl), [proof, low],
                          {"witness": ws[idx]})
        return proof

    def reduction_proof(self, goal: ForAll, M: int, covered, open_res) -> Proof:
        k = Var("k", goal.var.typ)
        L = goal.lower
        hyps = []
        for r in open_res:
            first = L + ((r - L) % M)
            hyps.append(ForAll(k, class_instance(goal.body, goal.var, M, r), (first - r) // M))
        concl = goal if not hyps else Implies(hyps[0] if len(hyps) == 1 else And(tuple(hyps)), goal)
        if len(hyps) == 1:
            # residue_cover expects And for any number of hypotheses; keep a 1-tuple
            concl = Implies(And(tuple(hyps)), goal)
        return Proof("residue_cover", concl, [c[3] for c in covered],
                     {"modulus": M, "open": list(open_res),
                      "classes": [(c[0], c[1]) for c in covered]})


    def prime_reduction_proof(self, goal, M, covered, open_res) -> Proof:
        from ..kernel.inference import prime_hypothesis
        concl = goal if not open_res else Implies(prime_hypothesis(goal, M, open_res), goal)
        return Proof("prime_reduction", concl, [c[3] for c in covered],
                     {"modulus": M, "open": list(open_res),
                      "classes": [(c[0], c[1]) for c in covered]})


# --------------------------------------------------------------- obstructions

def diagnose(open_res: List[int], M: int) -> List[str]:
    """Generic properties shared by all open residues (and rare overall)."""
    if not open_res:
        return []
    out = []
    squares = {(x * x) % M for x in range(M)}
    if all(r in squares for r in open_res):
        out.append(f"every open residue is a square mod {M} ({len(squares)} of {M} residues are squares)")
    primes = [p for p in sp.factorint(M)]
    qr_all = [r for r in range(M) if all(r % p in {(x * x) % p for x in range(p)} for p in primes)]
    if all(r in qr_all for r in open_res) and len(qr_all) < M:
        out.append(f"every open residue is a square modulo each prime factor of {M}")
    best = None
    for m in sorted(d for d in sp.divisors(M) if d > 1):
        if len({r % m for r in open_res}) == 1:
            best = m
    if best:
        out.append(f"strongest shared congruence: every open residue is {open_res[0] % best} mod {best}")
    return out


# ------------------------------------------------------------------ strategy

def witness_construction(ctl):
    goal = ctl.problem.goal
    shape = detect(goal) if goal is not None else None
    if shape is None:
        return
    eng = Engine(shape)
    mods = eng.moduli()
    ctl.findings["witness_moduli_schedule"] = mods
    ctl.history.log("witness", "start", f"base {eng.base}, moduli {mods}", "planned")
    covered = []            # (M, r, kl, proof)
    prev_M, open_res = None, None
    T, D = 24, 12
    level = 0
    while True:
        if level < len(mods):
            M = mods[level]
            if prev_M is None:
                open_res = list(range(M))
            else:
                open_res = [r + prev_M * t for r in open_res for t in range(M // prev_M)]
        else:
            M = prev_M          # final modulus: keep enlarging the grammar
        still_open = []
        for r in open_res:
            deadline = time.time() + 2.0 + level
            polys, kl, why = eng.search_class(M, r, T, D, deadline)
            if polys is not None:
                proof = eng.class_proof(M, r, kl, polys)
                if ctl.accept(proof, f"witness construction: class {r} mod {M}"):
                    covered.append((M, r, kl, proof))
                    ctl.findings.setdefault("witness_examples", {})
                    if len(ctl.findings["witness_examples"]) < 6:
                        ctl.findings["witness_examples"][f"n = {M}k + {r}"] = [str(p) for p in polys]
                    yield
                    continue
            still_open.append(r)
            yield
        open_res = still_open
        # kernel-certified reduction after every pass
        red = eng.reduction_proof(goal, M, covered, open_res)
        if ctl.accept(red, f"reduction: target follows from {len(open_res)} open classes mod {M}"):
            ctl.findings["reduction"] = {
                "modulus": M, "open_classes": len(open_res), "of": M,
                "open_sample": open_res[:30],
                "statement": "target holds for all n >= %d if it holds on the open classes" % shape.lower}
        # symmetry: if the equation is scale invariant, only primes matter
        prime_open = [r for r in open_res if math.gcd(r, M) == 1 or (sp.isprime(r) and M % r == 0)]
        pr = eng.prime_reduction_proof(goal, M, covered, prime_open)
        if ctl.accept(pr, f"prime reduction mod {M} via scaling symmetry"):
            ctl.findings["prime_reduction"] = {
                "modulus": M, "open_prime_classes": prime_open[:40], "count": len(prime_open),
                "statement": "target holds for all n >= 2 if it holds for every prime in these classes"}
            if not prime_open:
                ctl.accept(pr, "complete proof via prime reduction")
        ctl.findings["obstruction_diagnosis"] = diagnose(open_res, M)
        ctl.history.log("witness", "pass", f"mod {M}: {len(open_res)} open, grammar T={T} D={D}",
                        "complete" if not open_res else "partial")
        if not open_res:
            return
        prev_M = M
        level += 1
        T, D = int(T * 1.6), int(D * 1.6)
        if T > 2000:
            return
        yield
