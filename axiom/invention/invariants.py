"""Invariant synthesis for recursively defined sequences.

Polynomial invariants are found by linear algebra, not guessing: write
I(x, n) = sum c_ij x^i n^j, impose I(F(x,n), n+1) = I(x,n) as a
polynomial identity, and solve for the c_ij.
"""
from __future__ import annotations

from fractions import Fraction
from typing import List

import sympy as sp

from ..kernel.expressions import Const, Expr, SeqTerm, Sequence, Sub, Var, from_sympy, sym
from ..kernel.proof_objects import Proof
from ..kernel.propositions import Divides, Eq, ForAll
from .expressions import monomials
from .lemmas import Conjecture


def polynomial_invariants(seq: Sequence, max_degree: int = 3) -> List[Expr]:
    X, N = sym("x"), sym("n")
    mons = [m for m in monomials(["x", "n"], max_degree) if m.has(X)]
    mons += [m for m in monomials(["n"], max_degree)]
    cs = sp.symbols(f"c0:{len(mons)}")
    I = sum(c * m for c, m in zip(cs, mons))
    F = seq.rule.to_sympy()
    step = sp.expand(I.subs({X: F, N: N + 1}, simultaneous=True) - I)
    if not step.is_polynomial(X, N):
        return []
    eqs = sp.Poly(step, X, N).coeffs()
    sol = sp.linsolve(eqs, cs)
    out = []
    for s in sol:
        free = sorted(set().union(*[e.free_symbols for e in s]) & set(cs), key=str)
        for f in free:
            sub = {g: (1 if g == f else 0) for g in free}
            Ii = sp.expand(sum(si.subs(sub) * m for si, m in zip(s, mons)))
            if Ii != 0 and Ii.has(X):
                out.append(from_sympy(Ii))
    return out


def invariant_proofs(seq: Sequence, max_degree: int = 3) -> List[Proof]:
    n = Var("n")
    out = []
    for I in polynomial_invariants(seq, max_degree):
        c0 = I.evaluate({"x": Fraction(seq.init), "n": Fraction(0)})
        concl = ForAll(n, Eq(I.subst({"x": SeqTerm(seq, n)}), Const(c0)), 0)
        out.append(Proof("recurrence_invariant", concl, [], {"seq": seq, "I": I}))
    return out


def modular_invariants(seq: Sequence, max_modulus: int = 12, samples: int = 120) -> List[Conjecture]:
    poly = sp.Poly(sp.expand(seq.rule.to_sympy()), sym("x"), sym("n"))
    if any(sp.Rational(c).q != 1 for c in poly.coeffs()):
        return []
    n = Var("n")
    out = []
    for m in range(2, max_modulus + 1):
        res = set(seq.values_mod(m, samples))
        if len(res) == 1:
            c = res.pop()
            out.append(Conjecture(ForAll(n, Divides(Const(m), Sub(SeqTerm(seq, n), Const(c))), 0),
                                  "modular pattern", samples))
    return out
