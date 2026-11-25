"""Generalisation and strengthening.

Replace a constant by a parameter, scan which parameter values make the
statement hold, and look for a pattern in that set. Instances can often
be proved; the general statement may stay CONJECTURED, and that is
recorded honestly.
"""
from __future__ import annotations

from fractions import Fraction
from typing import Callable, List

from ..kernel.expressions import Const, Expr, Pow, Sub, Var
from ..kernel.propositions import PREDICATES, Divides, ForAll, Implies, Pred
from .lemmas import Conjecture


def parameter_scan(make_prop: Callable[[int], object], params, test_values) -> List[int]:
    """Return the parameters p for which make_prop(p) holds on all test values.
    make_prop(p) must return ForAll(n, body)."""
    good = []
    for p in params:
        prop = make_prop(p)
        if all(prop.instance(v).evaluate({}) for v in test_values if v >= prop.lower):
            good.append(p)
    return good


def pattern_of_set(values: List[int], params) -> List[str]:
    """Names of library predicates that exactly match values within params."""
    out = []
    s = set(values)
    for name in ("is_prime", "is_odd", "is_power_of_two", "is_square"):
        fn = PREDICATES[name]
        if all((p in s) == fn(p) for p in params):
            out.append(name)
    return out


def fermat_style_generalisation(max_p: int = 30) -> List[Conjecture]:
    """Discover for which p the statement p | n^p - n holds for all n."""
    n, p = Var("n"), Var("p")
    make = lambda q: ForAll(n, Divides(Const(q), Sub(Pow(n, Const(q)), n)), 0)
    params = list(range(2, max_p + 1))
    good = parameter_scan(make, params, range(0, 60))
    out = []
    for pat in pattern_of_set(good, params):
        prop = ForAll(p, ForAll(n, Implies(Pred(pat, (p,)), Divides(p, Sub(Pow(n, p), n))), 0), 2)
        out.append(Conjecture(prop, "parameter scan", len(params) * 60,
                              note=f"holds exactly for p in {good}", meta={"instances": good}))
    return out
