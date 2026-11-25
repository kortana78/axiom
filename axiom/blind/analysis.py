"""Blind structural analysis.

The engine reads the statement and the given definitions and works out for
itself which mathematical objects exist: bound variables, terms, sums,
recurrences, inequalities, predicates and constants. Nothing here knows what
the answer is or which objects will turn out to be useful. Everything that is
found is handed to the same general invention machinery.

Moduli and shift offsets are *discovered* from constants in the statement and
from sampled values of the terms. They are not chosen by the problem author.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from fractions import Fraction
from typing import List, Optional, Tuple

import sympy as sp

from ..kernel.expressions import (Const, Expr, SeqTerm, Sequence, Sum, Var)
from ..kernel.propositions import (And, BoundedForAll, Divides, Eq, Exists,
                                   ForAll, Implies, Le, Lt, Not, Or, Pred, Prop)
from .problem import BlindProblem


@dataclass
class Structure:
    goal: Optional[Prop]
    binders: List[Tuple[Var, int]] = field(default_factory=list)
    main_var: Optional[Var] = None
    lower: int = 0
    terms: List[Tuple[Expr, Var, int]] = field(default_factory=list)
    sums: List[Tuple[Sum, Var, int]] = field(default_factory=list)
    inequalities: List[Tuple[Expr, Expr, Var]] = field(default_factory=list)
    sequences: List[Sequence] = field(default_factory=list)
    predicates: List[str] = field(default_factory=list)
    constants: List[int] = field(default_factory=list)
    moduli: List[int] = field(default_factory=list)
    offsets: List[int] = field(default_factory=list)

    def report(self) -> dict:
        return {
            "bound_variables": [f"{v.name} >= {lo}" for v, lo in self.binders],
            "terms_to_study": [str(e) for e, _, _ in self.terms],
            "sums_to_study": [str(s) for s, _, _ in self.sums],
            "sequences_to_study": [str(s) for s in self.sequences],
            "inequalities_to_study": [f"{a} <= {b}" for a, b, _ in self.inequalities],
            "predicates": sorted(set(self.predicates)),
            "constants": sorted(set(self.constants)),
            "discovered_moduli": self.moduli,
            "discovered_offsets": self.offsets,
        }


def _add_unique(seq: list, item):
    if item not in seq:
        seq.append(item)


def _walk_prop(p: Prop, st: Structure, var: Optional[Var], lower: int):
    if isinstance(p, ForAll):
        st.binders.append((p.var, p.lower))
        _walk_prop(p.body, st, p.var, p.lower)
    elif isinstance(p, (Exists, BoundedForAll)):
        _walk_prop(p.body, st, p.var, lower)
    elif isinstance(p, (And, Or)):
        for part in p.parts:
            _walk_prop(part, st, var, lower)
    elif isinstance(p, (Not, Implies)):
        for part in (p.parts if isinstance(p, And) else
                     ((p.a, p.b) if isinstance(p, Implies) else (p.p,))):
            _walk_prop(part, st, var, lower)
    elif isinstance(p, Divides):
        if isinstance(p.d, Const) and p.d.value.denominator == 1 and p.d.value > 0:
            _add_unique(st.constants, int(p.d.value))
        _walk_expr(p.e, st, var, lower)
    elif isinstance(p, Eq):
        if isinstance(p.lhs, Sum):
            _walk_expr(p.lhs, st, var, lower)
        else:
            _walk_expr(p.lhs, st, var, lower)
    elif isinstance(p, (Le, Lt)):
        _add_unique(st.inequalities, (p.lhs, p.rhs, var))
        _walk_expr(p.lhs, st, var, lower)
        _walk_expr(p.rhs, st, var, lower)
    elif isinstance(p, Pred):
        _add_unique(st.predicates, p.name)
        for a in p.args:
            _walk_expr(a, st, var, lower)


def _walk_expr(e: Expr, st: Structure, var: Optional[Var], lower: int):
    if isinstance(e, Sum):
        v = e.hi if isinstance(e.hi, Var) else var
        if isinstance(v, Var):
            lo = int(e.lo.value) if isinstance(e.lo, Const) else lower
            _add_unique(st.sums, (e, v, lo))
        _walk_expr(e.body, st, var, lower)
    elif isinstance(e, SeqTerm):
        _add_unique(st.sequences, e.seq)
    elif isinstance(e, Const):
        return
    else:
        free = e.free_vars()
        if free and var is not None and var.name in free:
            _add_unique(st.terms, (e, var, lower))


def _discover_from_data(st: Structure):
    """Sample terms; derive candidate moduli and shift offsets from the data."""
    factors: List[int] = []
    for d in st.constants:
        factors.extend(_prime_powers(d))
    offsets: List[int] = []
    for e, v, lo in list(st.terms):
        g, stabilized = 0, None
        for i in range(lo, lo + 41):
            try:
                val = e.evaluate({v.name: Fraction(i)})
            except Exception:
                break
            if val.denominator != 1:
                break
            new = math.gcd(g, int(val))
            if new != g:
                g, stabilized = new, i - lo
        if g > 1:
            factors.extend(_prime_powers(g))
        if stabilized is not None:
            offsets.append(stabilized)
    for f in factors:
        if f <= 64:
            _add_unique(st.moduli, f)
    for o in sorted(set(offsets)):
        if 0 <= o <= 40:
            _add_unique(st.offsets, o)


def _prime_powers(n: int) -> List[int]:
    out = []
    for p, a in sp.factorint(n).items():
        for k in range(1, a + 1):
            if p ** k <= 64:
                _add_unique(out, p ** k)
    return out


def analyze(problem: BlindProblem) -> Structure:
    st = Structure(goal=problem.goal)
    if problem.goal is not None:
        _walk_prop(problem.goal, st, None, 0)
    st.main_var = st.binders[0][0] if st.binders else None
    st.lower = st.binders[0][1] if st.binders else 0

    for seq in problem.given_sequences:
        _add_unique(st.sequences, seq)
    if not st.binders:
        for e in list(problem.study) + list(problem.given_terms):
            free = e.free_vars()
            if free:
                st.main_var = Var(sorted(free)[0])
                st.lower = 0
                break
    for e in list(problem.study) + list(problem.given_terms):
        _walk_expr(e, st, st.main_var, st.lower)

    _discover_from_data(st)
    return st
