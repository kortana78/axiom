"""First-order matching of expression patterns with metavariables."""
from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Dict, Optional

from ..kernel.expressions import Expr, Var, Const


@dataclass(frozen=True)
class Meta(Expr):
    """Pattern variable ?name, matches any subterm."""
    name: str
    def subst(self, m): return m.get("?" + self.name, self)
    def free_vars(self): return set()
    def __str__(self): return "?" + self.name


def match(pattern: Expr, term: Expr, sub: Optional[Dict[str, Expr]] = None):
    """Return a substitution {?x: term} making pattern equal term, or None."""
    sub = dict(sub or {})
    if isinstance(pattern, Meta):
        key = "?" + pattern.name
        if key in sub:
            return sub if sub[key] == term else None
        sub[key] = term
        return sub
    if type(pattern) is not type(term):
        return None
    if isinstance(pattern, (Var, Const)):
        return sub if pattern == term else None
    for f in fields(pattern):
        a, b = getattr(pattern, f.name), getattr(term, f.name)
        if isinstance(a, Expr):
            sub = match(a, b, sub)
            if sub is None:
                return None
        elif a != b:
            return None
    return sub


def instantiate(pattern: Expr, sub: Dict[str, Expr]) -> Expr:
    return _inst(pattern, sub)


def _inst(e: Expr, sub):
    if isinstance(e, Meta):
        return sub["?" + e.name]
    if isinstance(e, (Var, Const)):
        return e
    kwargs = {}
    for f in fields(e):
        v = getattr(e, f.name)
        kwargs[f.name] = _inst(v, sub) if isinstance(v, Expr) else v
    return type(e)(**kwargs)
