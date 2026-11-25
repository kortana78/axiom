"""Rewriting: normal forms and pattern rewrite rules.

Rewrites produce candidate reformulations. They never establish truth:
any rewritten goal still has to be proved by the kernel.
"""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import List

import sympy as sp

from ..kernel.expressions import Expr, Var, Const, from_sympy
from .unification import match, _inst


@dataclass(frozen=True)
class RewriteRule:
    name: str
    lhs: Expr
    rhs: Expr


def normalize(e: Expr) -> Expr:
    """Expanded polynomial normal form for closed-form terms."""
    if not e.is_closed_form():
        return e
    return from_sympy(sp.expand(e.to_sympy()))


def factor_form(e: Expr) -> Expr:
    if not e.is_closed_form():
        return e
    return from_sympy(sp.factor(e.to_sympy()))


def rewrite_once(e: Expr, rules: List[RewriteRule]) -> List[Expr]:
    """All terms reachable by one rule application anywhere in e."""
    out = []
    for r in rules:
        s = match(r.lhs, e)
        if s is not None:
            out.append(_inst(r.rhs, s))
    if isinstance(e, (Var, Const)):
        return out
    for f in fields(e):
        child = getattr(e, f.name)
        if isinstance(child, Expr):
            for new in rewrite_once(child, rules):
                kwargs = {g.name: getattr(e, g.name) for g in fields(e)}
                kwargs[f.name] = new
                out.append(type(e)(**kwargs))
    return out
