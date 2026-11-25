"""Auxiliary constructions: explicit objects that make a proof possible.

* Erdos-Straus: polynomial families x(k), y(k), z(k) solving
  4/n = 1/x + 1/y + 1/z on a whole residue class n = M k + r.
* Collatz: residue classes mod 2^k on which the trajectory provably
  drops below its start (parity-vector descent).
Each construction is returned as a Proof for the kernel to check.
"""
from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Tuple

import sympy as sp

from ..kernel.expressions import Add, Const, Div, Expr, Mul, Var, from_sympy, sym
from ..kernel.inference import class_instance, collatz_parity_descent
from ..kernel.proof_objects import Proof
from ..kernel.propositions import Eq, Exists, ForAll, Le, Pred

# ------------------------------------------------------------ Erdos-Straus

X, Y, Z, N = Var("x"), Var("y"), Var("z"), Var("n")
ES_BODY = Exists(X, Exists(Y, Exists(Z, Eq(Div(Const(4), N),
                                            Add(Add(Div(Const(1), X), Div(Const(1), Y)), Div(Const(1), Z))), 1), 1), 1)
ES_STATEMENT = ForAll(N, ES_BODY, 2)


def _int_poly(e, k):
    e = sp.expand(e)
    if not e.is_polynomial(k):
        return None
    p = sp.Poly(e, k)
    if all(sp.Rational(c).q == 1 for c in p.coeffs()):
        return p
    return None


def _positive_from(p: sp.Poly, lower: int) -> bool:
    k = p.gens[0]
    m = sp.Symbol("m_pos")
    q = sp.Poly(sp.expand(p.as_expr().subs(k, m + lower)), m)
    cs = q.all_coeffs()
    return all(c >= 0 for c in cs) and cs[-1] >= 1


def es_family(M: int, r: int, t_max: int = 120, s_max: int = 80) -> Optional[Tuple[sp.Expr, sp.Expr, sp.Expr, int]]:
    """Search integer-polynomial x, y, z in k for n = M k + r."""
    if M % 4:
        return None
    k = sym("k")
    lower = 0 if r >= 2 else 1
    n = M * k + r
    samples = [lower + i for i in range(4)]
    nv = [M * s + r for s in samples]
    for t in range(1, t_max + 1):
        if (r + t) % 4:
            continue
        x = (n + t) / 4
        D = sp.expand(n * x)
        Dv = [v * (v + t) // 4 for v in nv]
        cands = []
        for a in range(1, t // 2 + 1):
            b = t - a
            if all(d % a == 0 and d % b == 0 for d in Dv):
                cands.append((D / a, D / b))
        for s in range(1, s_max + 1):
            if all((d + s) % t == 0 and (d * (d + s)) % (t * s) == 0 for d in Dv):
                cands.append(((D + s) / t, D * (D + s) / (t * s)))
        for y, z in cands:
            px, py, pz = _int_poly(x, k), _int_poly(y, k), _int_poly(z, k)
            if not (px and py and pz):
                continue
            if all(_positive_from(p, lower) for p in (px, py, pz)):
                return sp.expand(x), sp.expand(y), sp.expand(z), lower
    return None


def es_class_statement(M: int, r: int, lower: int):
    k = Var("k")
    return ForAll(k, class_instance(ES_BODY, N, M, r), lower)


def es_class_proof(M: int, r: int, fam) -> Proof:
    """Assemble the kernel proof for one residue class from a family."""
    x, y, z, lower = fam
    k = Var("k")
    wx, wy, wz = from_sympy(x), from_sympy(y), from_sympy(z)
    goal = es_class_statement(M, r, lower)
    ex_x = goal.body
    body_y = ex_x.body.subst({"x": wx})          # Exists y ...
    body_z = body_y.body.subst({"y": wy})        # Exists z ...
    final = body_z.body.subst({"z": wz})         # Eq(...)
    eq_proof = Proof("algebraic_identity", ForAll(k, final, lower))
    low = lambda w: Proof("shift_nonneg", ForAll(k, Le(Const(1), w), lower))
    pz = Proof("forall_exists_witness", ForAll(k, body_z, lower), [eq_proof, low(wz)], {"witness": wz})
    py = Proof("forall_exists_witness", ForAll(k, body_y, lower), [pz, low(wy)], {"witness": wy})
    px = Proof("forall_exists_witness", goal, [py, low(wx)], {"witness": wx})
    return px


# ------------------------------------------------------------ Collatz

def collatz_class_statement(k: int, r: int):
    j = Var("j")
    return ForAll(j, Pred("collatz_descends", (Add(Mul(Const(2 ** k), j), Const(r)),)), 1)


def collatz_open_classes(max_k: int):
    """Refine residue classes mod 2^k; return (proofs, open residues at max_k)."""
    proofs = []
    open_res = [1]  # even numbers descend immediately; handled at k=1 below
    proofs.append(Proof("collatz_descent", collatz_class_statement(1, 0), [], {"k": 1, "r": 0}))
    for k in range(2, max_k + 1):
        nxt = []
        for r0 in open_res:
            for r in (r0, r0 + 2 ** (k - 1)):
                ok, _ = collatz_parity_descent(k, r, 1)
                if ok:
                    proofs.append(Proof("collatz_descent", collatz_class_statement(k, r), [], {"k": k, "r": r}))
                else:
                    nxt.append(r)
        open_res = nxt
    return proofs, open_res
