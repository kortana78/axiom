"""Candidate evaluation: which conjectures deserve proof effort first.

Scores only change ORDER. Low-scoring candidates are delayed, never dropped.
"""
from __future__ import annotations

from ..invention.lemmas import Conjecture


def score(c: Conjecture, goal_key: str | None = None) -> float:
    simplicity = 1.0 / (1 + c.prop.size())
    evidence = min(c.evidence, 200) / 200
    relevance = 0.0
    if goal_key and c.prop.key() == goal_key:
        relevance = 1.0
    return 2.0 * relevance + evidence + 10 * simplicity


def rank(cands, goal_key=None):
    return sorted(cands, key=lambda c: -score(c, goal_key))
