"""Search history: every action with its justification, including failures.

Failed approaches are kept on purpose: they show which statements are
too strong, which assumptions are missing, and where new ideas are needed.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List


@dataclass
class Event:
    t: float
    strategy: str
    action: str
    detail: str
    outcome: str


@dataclass
class SearchHistory:
    events: List[Event] = field(default_factory=list)
    start: float = field(default_factory=time.time)

    def log(self, strategy: str, action: str, detail: str, outcome: str):
        self.events.append(Event(time.time() - self.start, strategy, action, detail, outcome))

    def by_outcome(self, outcome: str) -> List[Event]:
        return [e for e in self.events if e.outcome == outcome]

    def render(self, limit: int = 200) -> str:
        lines = []
        for e in self.events[:limit]:
            lines.append(f"{e.t:7.2f}s  {e.strategy:<22} {e.action:<26} {e.outcome:<12} {e.detail}")
        if len(self.events) > limit:
            lines.append(f"... {len(self.events) - limit} more events")
        return "\n".join(lines)
