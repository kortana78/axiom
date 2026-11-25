"""Lemma and conjecture invention from data.

Pattern: compute examples cheaply, fit a structured candidate, test it
on fresh examples, and only then hand it to proof search. Everything
returned here is CONJECTURED until the kernel says otherwise.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Callable, List, Optional

import sympy as sp

from ..kernel.expressions import (Const, Expr, Pow, SeqTerm, Sequence, Sum, Var,
                                  from_sympy, sym)
from ..kernel.propositions import (Divides, Eq, ForAll, Implies, Le, Pred, Prop,
                                   PREDICATES)


@dataclass
class Conjecture:
    prop: Prop
    origin: str
    evidence: int
    note: str = ""
    meta: dict = field(default_factory=dict)

    def __str__(self):
        return f"{self.prop}   [from {self.origin}, {self.evidence} checks]"


def _fit_polynomial(points, var: str, max_degree: int) -> Optional[sp.Expr]:
    x = sym(var)
    for deg in range(max_degree + 1):
        if len(points) < deg + 3:
            break
        base = points[: deg + 1]
        poly = sp.interpolate([(a, sp.Rational(b.numerator, b.denominator)) for a, b in base], x)
        if all(sp.Rational(b.numerator, b.denominator) == poly.subs(x, a) for a, b in points):
            return sp.expand(poly)
    return None


def _fit_exponential(points, var: str) -> Optional[sp.Expr]:
    """v(n) = A*b^n + C for an integer base b in 2..9."""
    x = sym(var)
    vals = [v for _, v in points]
    n0 = points[0][0]
    for b in range(2, 10):
        consts = {vals[i + 1] - b * vals[i] for i in range(len(vals) - 1)}
        if len(consts) == 1:
            k = consts.pop()
            C = k / (1 - b)
            A = (vals[0] - C) / Fraction(b) ** n0
            e = sp.Rational(A.numerator, A.denominator) * sp.Integer(b) ** x + sp.Rational(C.numerator, C.denominator)
            return e
    return None


def closed_form_for_sum(s: Sum, n: Var, lower: int, samples: int = 14, max_degree: int = 10) -> List[Conjecture]:
    pts = [(v, s.evaluate({n.name: Fraction(v)})) for v in range(lower, lower + samples)]
    out = []
    for fitter, tag in ((lambda p: _fit_polynomial(p, n.name, max_degree), "polynomial fit"),
                        (lambda p: _fit_exponential(p, n.name), "exponential fit")):
        e = fitter(pts)
        if e is not None:
            out.append(Conjecture(ForAll(n, Eq(s, from_sympy(e)), lower), tag, samples))
    return out


def closed_form_for_sequence(seq: Sequence, samples: int = 16) -> List[Conjecture]:
    try:
        vals = seq.values(samples)
    except OverflowError:
        return []
    if max(abs(v.numerator) for v in vals).bit_length() > 4000:
        return []  # grows too fast for a polynomial or simple exponential
    pts = list(enumerate(vals))
    n = Var("n")
    out = []
    for fitter, tag in ((lambda p: _fit_polynomial(p, "n", 8), "polynomial fit"),
                        (lambda p: _fit_exponential(p, "n"), "exponential fit")):
        e = fitter(pts)
        if e is not None:
            out.append(Conjecture(ForAll(n, Eq(SeqTerm(seq, n), from_sympy(e)), 0), tag, samples))
    return out


def divisibility_conjectures(f: Expr, n: Var, lower: int = 0, samples: int = 60) -> List[Conjecture]:
    """gcd of all sampled values: conjecture that it always divides f."""
    g = 0
    for v in range(lower, lower + samples):
        val = f.evaluate({n.name: Fraction(v)})
        if val.denominator != 1:
            return []
        g = math.gcd(g, int(val))
    out = []
    if g > 1:
        out.append(Conjecture(ForAll(n, Divides(Const(g), f), lower), "gcd of values", samples,
                              note="strongest constant divisor consistent with data"))
        for p, a in sp.factorint(g).items():
            if p ** a != g:
                out.append(Conjecture(ForAll(n, Divides(Const(p ** a), f), lower),
                                      "prime power part of gcd", samples))
    return out


def inequality_threshold(lhs: Expr, rhs: Expr, n: Var, horizon: int = 400, max_start: int = 40) -> List[Conjecture]:
    """Smallest L with lhs <= rhs on [L, horizon]."""
    ok = [lhs.evaluate({n.name: Fraction(v)}) <= rhs.evaluate({n.name: Fraction(v)})
          for v in range(0, horizon + 1)]
    for L in range(0, max_start + 1):
        if all(ok[L:]):
            return [Conjecture(ForAll(n, Le(lhs, rhs), L), "threshold scan", horizon - L + 1)]
    return []


def _generated_patterns():
    """A generic pattern grammar, not a list of known answers:
    c * square for c = 1..6, unions of two such families, primes, powers of
    two, odd numbers, and single residue classes mod 2..6."""
    import math as _m
    names = []

    def sq(v):
        return v >= 0 and _m.isqrt(v) ** 2 == v

    def reg(name, fn):
        PREDICATES.setdefault(name, fn)
        names.append(name)

    for c in range(1, 7):
        reg(f"sq_times_{c}", lambda v, c=c: v % c == 0 and sq(v // c))
    for a in range(1, 7):
        for b in range(a + 1, 7):
            reg(f"sq_times_{a}_or_{b}",
                lambda v, a=a, b=b: (v % a == 0 and sq(v // a)) or (v % b == 0 and sq(v // b)))
    for m in range(2, 7):
        for r in range(m):
            reg(f"res_{r}_mod_{m}", lambda v, r=r, m=m: v % m == r)
    names += ["is_prime", "is_power_of_two", "is_odd"]
    return names


PATTERN_LIBRARY = _generated_patterns()


def characterise_predicate(pred_name: str, N: int = 3000) -> List[Conjecture]:
    """Mine an implication pred(n) -> pattern(n) from data, n in [1, N]."""
    fn = PREDICATES[pred_name]
    hits = [v for v in range(1, N + 1) if fn(v)]
    out = []
    n = Var("n")
    found = []
    for pat in PATTERN_LIBRARY:
        pf = PREDICATES[pat]
        if hits and all(pf(v) for v in hits):
            # keep only the most specific patterns: skip one implied by a found one
            if any(all(PREDICATES[q](v) <= pf(v) for v in range(1, min(N, 600) + 1)) for q in found):
                continue
            found.append(pat)
            exact = all(fn(v) == pf(v) for v in range(1, N + 1))
            out.append(Conjecture(ForAll(n, Implies(Pred(pred_name, (n,)), Pred(pat, (n,))), 1),
                                  "pattern miner", N,
                                  note="exact characterisation on sample" if exact else "one-way implication on sample"))
    return out
