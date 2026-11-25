"""Invented definitions: new named objects built from existing ones.

A Definition is never a claim. It is a new concept that the rest of the
system can reason about. Each records why it was introduced.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from ..kernel.expressions import Expr, Sequence, Var, Const, Add, Sub, SeqTerm


@dataclass
class Definition:
    name: str
    kind: str              # "sequence", "term", "predicate-pattern", "representation"
    body: object
    reason: str
    parent: Optional[str] = None
    meta: dict = field(default_factory=dict)

    def __str__(self):
        return f"{self.name} := {self.body}   ({self.kind}; {self.reason})"


def difference_sequence(seq: Sequence) -> Definition:
    """b(n) = a(n+1) - a(n). For a(n+1) = F(a(n), n) this is F(x,n) - x."""
    body = Sub(seq.rule, Var("x"))
    return Definition(f"Delta_{seq.name}", "term", body,
                      "first difference often exposes hidden polynomial structure",
                      parent=seq.name)


def shifted_sequence(seq: Sequence, c: int) -> Sequence:
    """c(n) = a(n) + c as a new recursively defined sequence."""
    rule = Add(seq.rule.subst({"x": Sub(Var("x"), Const(c))}), Const(c))
    return Sequence(f"{seq.name}_plus_{c}", seq.init + c, rule)
