"""The trusted inference kernel.

Every rule here is a small, separately checkable soundness argument.
The kernel never searches: it only checks a given Proof tree. Anything
that is not accepted here stays CONJECTURED, however promising.

Trusted base (be honest about it):
  * this file
  * SymPy polynomial arithmetic (expand, Poly coefficients, together)
  * exact evaluators of named predicates in kernel/predicates.py
Lean export (verification/) is how this trust gets removed.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Callable, Dict, Tuple

import sympy as sp

from .expressions import (Expr, Var, Const, Add, Mul, Sub, Pow, Sum, SeqTerm,
                          sym)
from .propositions import (Prop, Eq, Le, Lt, Divides, And, ForAll, Exists,
                           BoundedForAll, Pred, strip_forall)
from .proof_objects import Proof
from . import predicates  # noqa: F401  (registers trusted predicates)

Result = Tuple[bool, str]
RULES: Dict[str, Callable[["Kernel", Proof], Result]] = {}

FINITE_CHECK_LIMIT = 2_000_000


def rule(name):
    def deco(fn):
        RULES[name] = fn
        return fn
    return deco


class Kernel:
    def __init__(self, assumptions=()):
        self.assumptions = {a.key() for a in assumptions}

    def check(self, proof: Proof) -> Result:
        for p in proof.premises:
            ok, msg = self.check(p)
            if not ok:
                return False, f"premise failed: {msg}"
        fn = RULES.get(proof.rule)
        if fn is None:
            return False, f"unknown rule {proof.rule}"
        try:
            proof.conclusion.typecheck()
            return fn(self, proof)
        except Exception as exc:  # any error means rejection
            return False, f"{proof.rule}: {type(exc).__name__}: {exc}"


# ------------------------------------------------------------ helpers

def _closed(e: Expr) -> bool:
    return e.is_closed_form()


def _closed_exp(e: Expr) -> bool:
    """Closed form that may also contain c^t with constant base c."""
    if isinstance(e, Pow) and isinstance(e.base, Const):
        return _closed_exp(e.exp)
    if isinstance(e, (Sum, SeqTerm)):
        return False
    return all(_closed_exp(c) for c in e.children())


def _poly(e, *vars_):
    """SymPy Poly over QQ in the given symbols, or None if not polynomial."""
    s = sp.expand(e)
    gens = [sym(v) if isinstance(v, str) else v for v in vars_]
    if not s.is_polynomial(*gens):
        return None
    if s.free_symbols - set(gens):
        return None
    return sp.Poly(s, *gens, domain="QQ")


def _int_coeffs(p: sp.Poly) -> bool:
    return all(sp.Rational(c).q == 1 for c in p.coeffs())


def _nonneg_after_shift(diff, var: str, lower: int, strict: bool) -> bool:
    """Sufficient test that diff(n) >= 0 (or > 0) for all integers n >= lower:
    substitute n = m + lower and require every coefficient >= 0."""
    m = sp.Symbol("m_shift", integer=True)
    shifted = sp.expand(sp.sympify(diff).subs(sym(var), m + lower))
    p = _poly(shifted, m)
    if p is None:
        return False
    coeffs = p.all_coeffs()
    if any(c < 0 for c in coeffs):
        return False
    if strict and coeffs[-1] <= 0:
        return False
    return True


def class_instance(body: Prop, var: Var, modulus: int, residue: int) -> Prop:
    """body with var replaced by modulus*k + residue (shared with tactics)."""
    k = Var("k", var.typ)
    return body.subst({var.name: Add(Mul(Const(modulus), k), Const(residue))})


def collatz_parity_descent(k: int, r: int, lower: int, max_steps: int = 400):
    """Symbolically iterate n -> n/2 or 3n+1 on n = 2^k j + r while parity is
    determined. Returns (True, steps) if the value provably drops below n."""
    a, b = 2 ** k, r
    for step in range(1, max_steps + 1):
        if a % 2 == 1:
            return False, step
        if b % 2 == 0:
            a, b = a // 2, b // 2
        else:
            a, b = 3 * a, 3 * b + 1
        if a < 2 ** k and (2 ** k - a) * lower + (r - b) > 0:
            return True, step
    return False, max_steps


# ------------------------------------------------------------ rules

@rule("given")
def _given(k: Kernel, p: Proof) -> Result:
    if p.conclusion.key() in k.assumptions:
        return True, "assumption"
    return False, "not an assumption"


@rule("algebraic_identity")
def _alg(k: Kernel, p: Proof) -> Result:
    _, body = strip_forall(p.conclusion)
    if not isinstance(body, Eq) or not (_closed(body.lhs) and _closed(body.rhs)):
        return False, "needs an equation between closed-form terms"
    diff = sp.together(body.lhs.to_sympy() - body.rhs.to_sympy())
    num, _ = sp.fraction(diff)
    if sp.expand(num) == 0:
        return True, "identity holds wherever denominators are nonzero"
    return False, "not an identity"


@rule("residue_divisibility")
def _res(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    if len(binders) != 1 or not isinstance(body, Divides) or not isinstance(body.d, Const):
        return False, "shape: forall n: d | f(n)"
    var = binders[0][0].name
    d = body.d.value
    if d.denominator != 1 or d <= 0 or d > 100_000:
        return False, "d must be a positive integer"
    d = int(d)
    if not _closed(body.e):
        return False, "f must be closed form"
    poly = _poly(body.e.to_sympy(), var)
    if poly is None or not _int_coeffs(poly):
        return False, "f must be a polynomial with integer coefficients"
    for r in range(d):
        if int(poly.eval(r)) % d != 0:
            return False, f"fails at residue {r} mod {d}"
    return True, f"f(n) = f(n mod {d}) mod {d}, all residues checked"


@rule("sum_induction")
def _sumind(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    if len(binders) != 1 or not isinstance(body, Eq) or not isinstance(body.lhs, Sum):
        return False, "shape: forall n >= L: Sum[i=a..n](g(i)) = F(n)"
    n, L = binders[0]
    s, F = body.lhs, body.rhs
    if s.hi != n or not isinstance(s.lo, Const) or not _closed_exp(s.body) or not _closed_exp(F):
        return False, "upper limit must be the bound variable; body and F closed form"
    if s.body.free_vars() - {s.index.name} or F.free_vars() - {n.name}:
        return False, "unexpected free variables"
    base = s.evaluate({n.name: Fraction(L)}) == F.evaluate({n.name: Fraction(L)})
    if not base:
        return False, "base case fails"
    N = n.to_sympy()
    step = (F.to_sympy().subs(N, N + 1) - F.to_sympy()
            - s.body.to_sympy().subs(s.index.to_sympy(), N + 1))
    num, _ = sp.fraction(sp.together(sp.expand(step, power_exp=True)))
    if sp.expand(num, power_exp=True) != 0:
        return False, "inductive step fails"
    return True, "base case and F(n+1) - F(n) = g(n+1)"


@rule("shift_nonneg")
def _shift(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    if len(binders) != 1 or not isinstance(body, (Le, Lt)):
        return False, "shape: forall n >= L: g <= f"
    n, L = binders[0]
    if not (_closed(body.lhs) and _closed(body.rhs)):
        return False, "closed forms required"
    diff = body.rhs.to_sympy() - body.lhs.to_sympy()
    if _poly(diff, n.name) is None:
        return False, "difference must be a polynomial in n"
    if _nonneg_after_shift(diff, n.name, L, isinstance(body, Lt)):
        return True, f"f - g has nonnegative coefficients after n = m + {L}"
    return False, "shift test inconclusive"


@rule("exp_induction")
def _expind(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    if len(binders) != 1 or not isinstance(body, (Le, Lt)):
        return False, "shape: forall n >= L: p(n) <= a^n"
    n, L = binders[0]
    rhs = body.rhs
    if not (isinstance(rhs, Pow) and isinstance(rhs.base, Const) and rhs.exp == n):
        return False, "right side must be a^n"
    a = rhs.base.value
    if a.denominator != 1 or a <= 0:
        return False, "a must be a positive integer"
    if not _closed(body.lhs) or body.lhs.free_vars() - {n.name}:
        return False, "p must be closed form in n"
    pn = body.lhs.to_sympy()
    if _poly(pn, n.name) is None:
        return False, "p must be a polynomial"
    base_l = body.lhs.evaluate({n.name: Fraction(L)})
    base_r = Fraction(int(a) ** L)
    if not (base_l < base_r if isinstance(body, Lt) else base_l <= base_r):
        return False, "base case fails"
    N = n.to_sympy()
    q = sp.expand(int(a) * pn - pn.subs(N, N + 1))
    if not _nonneg_after_shift(q, n.name, L, strict=False):
        return False, "step a*p(n) >= p(n+1) not established"
    return True, "a^(n+1) = a*a^n >= a*p(n) >= p(n+1)"


@rule("range_split")
def _rsplit(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    if not isinstance(c, ForAll) or len(p.premises) != 2:
        return False, "needs a finite part and a tail part"
    fin, tail = p.premises[0].conclusion, p.premises[1].conclusion
    if not (isinstance(fin, BoundedForAll) and isinstance(tail, ForAll)):
        return False, "premise shapes"
    M = tail.lower
    want_fin = BoundedForAll(c.var, c.lower, M - 1, c.body)
    want_tail = ForAll(c.var, c.body, M)
    if fin.key() == want_fin.key() and tail.key() == want_tail.key():
        return True, "finite range plus tail"
    return False, "premises do not match"


@rule("finite_check")
def _finite(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    if not isinstance(c, BoundedForAll):
        return False, "needs a bounded statement"
    if c.hi - c.lo > FINITE_CHECK_LIMIT:
        return False, "range too large for direct checking"
    if c.evaluate({}):
        return True, f"checked all {max(0, c.hi - c.lo + 1)} cases"
    return False, "a case fails"


@rule("instantiate")
def _inst(k: Kernel, p: Proof) -> Result:
    prem = p.premises[0].conclusion
    v = p.data["value"]
    if not isinstance(prem, ForAll) or v < prem.lower:
        return False, "bad instantiation"
    if prem.instance(v).key() == p.conclusion.key():
        return True, "instance"
    return False, "conclusion is not the instance"


@rule("and_intro")
def _andi(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    if not isinstance(c, And) or len(c.parts) != len(p.premises):
        return False, "shape"
    if all(a.key() == b.conclusion.key() for a, b in zip(c.parts, p.premises)):
        return True, "conjunction"
    return False, "premises do not match parts"


@rule("forall_and")
def _fand(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    if not (isinstance(c, ForAll) and isinstance(c.body, And)):
        return False, "shape"
    want = [ForAll(c.var, part, c.lower).key() for part in c.body.parts]
    got = [q.conclusion.key() for q in p.premises]
    return (True, "pointwise conjunction") if want == got else (False, "mismatch")


@rule("divisibility_combine")
def _dcomb(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    _, body = strip_forall(c)
    if not isinstance(c, ForAll) or not isinstance(body, Divides) or len(p.premises) != 2:
        return False, "shape"
    a, b = p.premises[0].conclusion, p.premises[1].conclusion
    da, db = a.body.d.value, b.body.d.value
    if math.gcd(int(da), int(db)) != 1 or Fraction(da * db) != body.d.value:
        return False, "factors must be coprime with product d"
    wa = ForAll(c.var, Divides(Const(da), body.e), c.lower).key()
    wb = ForAll(c.var, Divides(Const(db), body.e), c.lower).key()
    if a.key() == wa and b.key() == wb:
        return True, "coprime divisors multiply"
    return False, "premises do not match"


@rule("forall_exists_witness")
def _fexw(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    if not (isinstance(c, ForAll) and isinstance(c.body, Exists)) or len(p.premises) != 2:
        return False, "shape: forall k: exists x: B"
    ex = c.body
    w: Expr = p.data["witness"]
    if not _closed(w) or w.free_vars() - {c.var.name}:
        return False, "witness must be closed form in the bound variable"
    poly = _poly(w.to_sympy(), c.var.name)
    if poly is None or not _int_coeffs(poly):
        return False, "witness must be an integer-coefficient polynomial"
    want_body = ForAll(c.var, ex.body.subst({ex.var.name: w}), c.lower).key()
    want_low = ForAll(c.var, Le(Const(ex.lower), w), c.lower).key()
    if p.premises[0].conclusion.key() == want_body and p.premises[1].conclusion.key() == want_low:
        return True, "explicit integer witness"
    return False, "premises do not match witness"


@rule("residue_split")
def _rsplit_mod(k: Kernel, p: Proof) -> Result:
    c = p.conclusion
    m = int(p.data["modulus"])
    if not isinstance(c, ForAll) or len(p.premises) != m:
        return False, "need one premise per residue class"
    for r, prem in enumerate(p.premises):
        q = prem.conclusion
        if not isinstance(q, ForAll):
            return False, "class premise must be universal"
        if q.key() != ForAll(Var("k", c.var.typ), class_instance(c.body, c.var, m, r), q.lower).key():
            return False, f"class {r} premise mismatch"
        first = c.lower + ((r - c.lower) % m)
        if m * q.lower + r > first:
            return False, f"class {r} lower bound leaves a gap"
    return True, "every residue class covered"


@rule("sequence_closed_form")
def _seqcf(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    if len(binders) != 1 or binders[0][1] != 0 or not isinstance(body, Eq):
        return False, "shape: forall n >= 0: a(n) = g(n)"
    n = binders[0][0]
    if not (isinstance(body.lhs, SeqTerm) and body.lhs.index == n and _closed_exp(body.rhs)):
        return False, "shape"
    seq, g = body.lhs.seq, body.rhs
    if g.evaluate({n.name: Fraction(0)}) != seq.init:
        return False, "base case fails"
    N = n.to_sympy()
    gs = g.to_sympy()
    step = seq.rule.to_sympy().subs({sym("x"): gs, sym("n"): N}, simultaneous=True) - gs.subs(N, N + 1)
    num, _ = sp.fraction(sp.together(sp.expand(step, power_exp=True)))
    if sp.expand(num, power_exp=True) != 0:
        return False, "recurrence step fails"
    return True, "g(0) = a(0) and g satisfies the recurrence"


@rule("recurrence_invariant")
def _recinv(k: Kernel, p: Proof) -> Result:
    seq, I = p.data["seq"], p.data["I"]
    n = Var("n")
    c0 = I.evaluate({"x": Fraction(seq.init), "n": Fraction(0)})
    want = ForAll(n, Eq(I.subst({"x": SeqTerm(seq, n)}), Const(c0)), 0)
    if p.conclusion.key() != want.key():
        return False, "conclusion does not match invariant"
    X, N = sym("x"), sym("n")
    Is = I.to_sympy()
    step = Is.subs({X: seq.rule.to_sympy(), N: N + 1}, simultaneous=True) - Is
    num, _ = sp.fraction(sp.together(step))
    if sp.expand(num) != 0:
        return False, "I is not invariant"
    return True, "I(F(x,n), n+1) = I(x,n)"


@rule("recurrence_mod_invariant")
def _recmod(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    if len(binders) != 1 or not isinstance(body, Divides) or not isinstance(body.e, Sub):
        return False, "shape: forall n: m | a(n) - c"
    m, term, c = body.d, body.e.a, body.e.b
    if not (isinstance(m, Const) and isinstance(term, SeqTerm) and isinstance(c, Const)):
        return False, "shape"
    seq = term.seq
    mi, ci = int(m.value), int(c.value)
    if (seq.init - ci) % mi != 0:
        return False, "base case fails"
    t = sp.Symbol("t_mod", integer=True)
    F = seq.rule.to_sympy().subs(sym("x"), ci + mi * t)
    poly = _poly(sp.expand(F - ci), t, sym("n"))
    if poly is None or not _int_coeffs(poly):
        return False, "rule must be an integer polynomial"
    if all(int(cf) % mi == 0 for cf in poly.coeffs()):
        return True, f"a(n) = {ci} mod {mi} is preserved by the rule"
    return False, "not preserved"


@rule("collatz_descent")
def _collatz(k: Kernel, p: Proof) -> Result:
    binders, body = strip_forall(p.conclusion)
    kk, r = int(p.data["k"]), int(p.data["r"])
    if len(binders) != 1 or not isinstance(body, Pred) or body.name != "collatz_descends":
        return False, "shape"
    j, L = binders[0]
    want = Add(Mul(Const(2 ** kk), j), Const(r))
    if body.args[0] != want or L < 1:
        return False, "argument must be 2^k*j + r with j >= 1"
    ok, steps = collatz_parity_descent(kk, r, L)
    return (True, f"parity determined for {steps} steps, value drops") if ok else (False, "no descent")


@rule("residue_cover")
def _rcover(k: Kernel, p: Proof) -> Result:
    """Reduction theorem over residue classes.

    Conclusion: goal itself (no open classes) or Implies(And(open), goal),
    where goal = forall n >= L: P(n) and each open item is
    forall k >= k_r: P(M k + r).
    Premises: class proofs forall k >= k_i: P(M_i k + r_i) with M_i | M.
    Sound: every n >= L has n = r' mod M; either r' is open (hypothesis)
    or some premise class contains n with k = (n - r_i)/M_i >= k_i.
    """
    from .propositions import Implies
    M = int(p.data["modulus"])
    open_res = [int(r) for r in p.data.get("open", [])]
    c = p.conclusion
    goal = c.b if isinstance(c, Implies) else c
    if not isinstance(goal, ForAll) or M < 1:
        return False, "shape"
    L = goal.lower
    kvar = Var("k", goal.var.typ)

    def class_stmt(mod, r):
        first = L + ((r - L) % mod)
        return ForAll(kvar, class_instance(goal.body, goal.var, mod, r), (first - r) // mod)

    want_open = [class_stmt(M, r).key() for r in open_res]
    if open_res:
        if not isinstance(c, Implies):
            return False, "open classes need an implication"
        hyps = c.a.parts if isinstance(c.a, And) else (c.a,)
        if [h.key() for h in hyps] != want_open:
            return False, "hypotheses do not match open classes"
    elif isinstance(c, Implies):
        return False, "no open classes: conclusion must be the goal"
    prem = []
    classes = p.data.get("classes", [])
    if len(classes) != len(p.premises):
        return False, "one (modulus, residue) entry per premise required"
    for q, (mi, ri) in zip(p.premises, classes):
        mi, ri = int(mi), int(ri)
        if M % mi:
            return False, "premise modulus must divide M"
        if q.conclusion.key() != ForAll(kvar, class_instance(goal.body, goal.var, mi, ri),
                                        q.conclusion.lower).key():
            return False, f"premise for class {ri} mod {mi} has the wrong statement"
        prem.append((mi, ri, q.conclusion.lower))
    opens = set(open_res)
    for r in range(M):
        if r in opens:
            continue
        first = L + ((r - L) % M)
        if not any(r % mi == ri % mi and first >= mi * ki + ri for mi, ri, ki in prem):
            return False, f"class {r} mod {M} is neither covered nor listed as open"
    return True, f"all classes mod {M} covered except {len(open_res)} listed"


PRIME_VAR = "q_prime"


def prime_hypothesis(goal: ForAll, M: int, open_res):
    """forall q >= 2: (is_prime(q) and q = r mod M for some open r) -> P(q)."""
    from .propositions import Implies, Or, Pred
    from .expressions import Sub
    q = Var(PRIME_VAR, goal.var.typ)
    cls = Or(tuple(Divides(Const(M), Sub(q, Const(r))) for r in open_res))
    return ForAll(q, Implies(And((Pred("is_prime", (q,)), cls)),
                             goal.body.subst({goal.var.name: q})), 2)


def scaling_homogeneous(goal: ForAll) -> Tuple[bool, str]:
    """True if forall n: exists v..: E = 0 is invariant under (n, v) -> (t n, t v)."""
    p = goal.body
    names = []
    while isinstance(p, Exists):
        if p.lower < 0:
            return False, "witness lower bounds must be >= 0"
        names.append(p.var.name)
        p = p.body
    if not isinstance(p, Eq) or not (_closed(p.lhs) and _closed(p.rhs)):
        return False, "body must be an exists-chain over an equation"
    gens = [sym(goal.var.name)] + [sym(v) for v in names]
    E = sp.together(p.lhs.to_sympy() - p.rhs.to_sympy())
    if E.free_symbols - set(gens):
        return False, "unexpected free symbols"
    num, den = sp.fraction(E)
    for part in (num, den):
        part = sp.expand(part)
        if part.is_number:
            continue
        if not sp.Poly(part, *gens).is_homogeneous:
            return False, "equation is not homogeneous in (n, witnesses)"
    return True, "homogeneous"


@rule("prime_reduction")
def _prime_red(k: Kernel, p: Proof) -> Result:
    """Target follows from its truth on primes in the open classes.

    Needs: target forall n >= 2: exists v >= l (l >= 0): E(n, v) = 0 with E
    homogeneous, so a solution for a prime factor q of n scales by n/q to a
    solution for n. Every residue class mod M that can contain a prime is
    either covered by a premise (from its first element >= 2) or open.
    """
    from .propositions import Implies
    M = int(p.data["modulus"])
    open_res = [int(r) for r in p.data.get("open", [])]
    c = p.conclusion
    goal = c.b if isinstance(c, Implies) else c
    if not isinstance(goal, ForAll) or goal.lower != 2:
        return False, "target must be forall n >= 2"
    ok, why = scaling_homogeneous(goal)
    if not ok:
        return False, why
    if open_res:
        if not isinstance(c, Implies) or c.a.key() != prime_hypothesis(goal, M, open_res).key():
            return False, "hypothesis must be the prime statement for the open classes"
    elif isinstance(c, Implies):
        return False, "no open classes: conclusion must be the target"
    kvar = Var("k", goal.var.typ)
    classes = p.data.get("classes", [])
    if len(classes) != len(p.premises):
        return False, "one class label per premise"
    prem = []
    for q, (mi, ri) in zip(p.premises, classes):
        mi, ri = int(mi), int(ri)
        if M % mi or q.conclusion.key() != ForAll(
                kvar, class_instance(goal.body, goal.var, mi, ri), q.conclusion.lower).key():
            return False, f"bad premise for class {ri} mod {mi}"
        prem.append((mi, ri, q.conclusion.lower))
    opens = set(open_res)
    from .predicates import is_prime
    for r in range(M):
        if r in opens:
            continue
        if not (math.gcd(r, M) == 1 or (is_prime(r) and M % r == 0)):
            continue  # this class contains no prime
        first = 2 + ((r - 2) % M)
        if not any(r % mi == ri % mi and first >= mi * ki + ri for mi, ri, ki in prem):
            return False, f"prime-bearing class {r} mod {M} not covered"
    return True, f"reduced to primes in {len(open_res)} classes mod {M} by scaling symmetry"
