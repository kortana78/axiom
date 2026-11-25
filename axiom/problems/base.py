"""Problem format.

A problem gives a target statement (or none, for pure discovery) and the
mathematical objects involved. Useful lemmas are deliberately NOT given:
the point is to see whether Axiom invents them.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from ..kernel.propositions import Prop


@dataclass
class Problem:
    name: str
    title: str
    goal: Optional[Prop]
    known_status: str                       # "theorem" or "open"
    stage: int                              # 1 rediscover, 2 invent, 4 open
    sums: list = field(default_factory=list)          # (Sum, n, lower)
    terms: list = field(default_factory=list)         # (expr, n, lower)
    inequalities: list = field(default_factory=list)  # (lhs, rhs, n)
    sequences: list = field(default_factory=list)     # Sequence
    predicates: list = field(default_factory=list)    # names for the pattern miner
    special: List[str] = field(default_factory=list)  # extra strategies
    bounded_limit: int = 2000
    bounded_goal: Optional[Prop] = None   # decidable equivalent used for finite checks
    params: dict = field(default_factory=dict)
    withheld: List[str] = field(default_factory=list)
    notes: str = ""
