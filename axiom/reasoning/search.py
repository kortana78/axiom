"""Proof search: iterative-deepening AND-OR search over tactics, plus a
fair scheduler that shares compute between competing strategies.

Fairness rule (Theorem F of the design): heuristics decide ORDER, never
EXCLUSION. Every strategy receives a nonzero share in every round and
budgets grow each round, so nothing provable inside the rule system is
ruled out forever.
"""
from __future__ import annotations

import time
from typing import Callable, Dict, List, Optional

from ..kernel.proof_objects import Proof
from ..kernel.propositions import Prop
from .backward import Alternative, DEFAULT_TACTICS, TacticContext


class BudgetExhausted(Exception):
    pass


class ProofSearch:
    def __init__(self, ctx: TacticContext, tactics=None, max_steps: int = 2000):
        self.ctx = ctx
        self.tactics = tactics or DEFAULT_TACTICS
        self.max_steps = max_steps
        self.steps = 0
        self._failed: Dict[str, int] = {}

    def prove(self, goal: Prop, max_depth: int = 4) -> Optional[Proof]:
        self.steps = 0
        try:
            for depth in range(1, max_depth + 1):
                p = self._prove(goal, depth)
                if p is not None:
                    return p
        except BudgetExhausted:
            pass
        return None

    def _tick(self):
        self.steps += 1
        if self.steps > self.max_steps:
            raise BudgetExhausted()

    def _prove(self, goal: Prop, depth: int) -> Optional[Proof]:
        key = goal.key()
        if key in self.ctx.known:
            return self.ctx.known[key]
        if self._failed.get(key, 0) >= depth:
            return None
        for tac in self.tactics:
            self._tick()
            for alt in tac(goal, self.ctx):
                if isinstance(alt, Proof):
                    self.ctx.known[key] = alt
                    return alt
                if depth <= 1:
                    continue
                subproofs: List[Proof] = []
                for sg in alt.subgoals:
                    sp_ = self._prove(sg, depth - 1)
                    if sp_ is None:
                        break
                    subproofs.append(sp_)
                else:
                    proof = alt.build(subproofs)
                    ok, msg = self.ctx.kernel.check(proof)
                    if ok:
                        self.ctx.known[key] = proof
                        return proof
                    self.ctx.fail(goal, alt.name, "assembled proof rejected: " + msg)
        self._failed[key] = max(self._failed.get(key, 0), depth)
        return None


class FairScheduler:
    """Round-robin over strategy generators with weighted, growing slices.

    Each strategy is a generator that yields after a unit of work. A
    strategy that finishes (StopIteration) is retired. The scheduler
    stops when all are retired or the wall-clock budget runs out.
    """

    def __init__(self, time_budget: float):
        self.time_budget = time_budget
        self.entries: List[dict] = []

    def add(self, name: str, gen, weight: float = 1.0):
        self.entries.append({"name": name, "gen": gen, "weight": max(weight, 0.05),
                             "units": 0, "done": False})

    def run(self, on_round: Callable[[int], bool] | None = None):
        start = time.time()
        rnd = 0
        while any(not e["done"] for e in self.entries):
            rnd += 1
            for e in self.entries:
                if e["done"]:
                    continue
                slice_units = max(1, int(e["weight"] * rnd))
                for _ in range(slice_units):
                    if time.time() - start > self.time_budget:
                        return "time_budget_exhausted"
                    try:
                        next(e["gen"])
                        e["units"] += 1
                    except StopIteration:
                        e["done"] = True
                        break
            if on_round and on_round(rnd):
                return "stopped_by_controller"
        return "all_strategies_finished"
