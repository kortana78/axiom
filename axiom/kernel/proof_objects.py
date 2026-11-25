"""Proof objects and epistemic statuses.

A Proof is an explicit tree: a rule, a conclusion, premise proofs and
rule data. Only the kernel decides whether a Proof is valid.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List

from .propositions import Prop


class Status(Enum):
    """These statuses are never interchangeable."""
    KNOWN = "known"                      # given axiom or assumption
    CONJECTURED = "conjectured"          # heuristic proposal, unproved
    REFUTED = "refuted"                  # a checked counterexample exists
    DERIVED = "derived"                  # proof accepted by the Axiom kernel
    VERIFIED = "verified"                # proof also accepted by Lean
    UNDECIDED = "undecided_within_budget"  # search ran out; NOT a refutation


@dataclass
class Proof:
    rule: str
    conclusion: Prop
    premises: List["Proof"] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)

    def size(self) -> int:
        return 1 + sum(p.size() for p in self.premises)

    def rules_used(self) -> set:
        out = {self.rule}
        for p in self.premises:
            out |= p.rules_used()
        return out

    def render(self, indent: int = 0) -> str:
        pad = "  " * indent
        extra = ""
        if self.data:
            shown = {k: str(v) for k, v in self.data.items() if k not in ("seq",)}
            if shown:
                extra = "  " + str(shown)
        lines = [f"{pad}[{self.rule}] {self.conclusion}{extra}"]
        for p in self.premises:
            lines.append(p.render(indent + 1))
        return "\n".join(lines)

    def to_dict(self) -> dict:
        return {
            "rule": self.rule,
            "conclusion": str(self.conclusion),
            "data": {k: str(v) for k, v in self.data.items()},
            "premises": [p.to_dict() for p in self.premises],
        }
