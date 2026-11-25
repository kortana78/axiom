"""The blind autonomous discovery loop.

    receive -> analyse -> invent -> explore -> test -> prove -> verify
                 ^                                              |
                 +-------- analyse failure, mutate strategies <-+

The controller holds exactly the same state as 0.1,
S = (Gamma, D, G, C, P, F, R), but none of its inputs can carry a solution.
When the frontier stalls it invokes Strategy Mutation instead of only raising
the search budget.
"""
from __future__ import annotations

import json
import os
import time
from typing import Dict, List, Optional

from ..invention.definitions import Definition
from ..invention.lemmas import Conjecture
from ..kernel.inference import Kernel
from ..kernel.proof_objects import Proof, Status
from ..kernel.propositions import BoundedForAll, Prop
from ..memory.knowledge_graph import KnowledgeGraph
from ..memory.search_history import SearchHistory
from ..memory.theorem_store import TheoremStore
from ..reasoning.backward import TacticContext
from ..reasoning.search import FairScheduler
from ..verification import lean_bridge, proof_export
from . import counterexamples as CE
from . import strategies as S
from .analysis import analyze
from .memory import ResearchMemory
from .mutation import StrategyMutation
from .problem import BlindProblem
from .tactics import BLIND_ALLOWED_RULES, BLIND_TACTICS
from . import witness as W


class BlindController:
    def __init__(self, problem: BlindProblem, time_budget: float = 60.0,
                 research_dir: str = "research", db_path: Optional[str] = None,
                 lean: bool = False, mutation: bool = True,
                 bounded_limit: int = 2000, explore: bool = False):
        self.problem = problem
        self.time_budget = time_budget
        self.bounded_limit = bounded_limit
        self.explore = explore
        self.use_mutation = mutation
        self.lean = lean
        self.structure = analyze(problem)
        self.kernel = Kernel(assumptions=[p for p in problem.given_assumptions])
        self.memory = ResearchMemory(research_dir, problem.name)
        os.makedirs(self.memory.dir, exist_ok=True)
        self.store = TheoremStore(db_path or self.memory.db_path, self.kernel)
        self.ctx = TacticContext(self.kernel, known={},
                                 residue_moduli=tuple(self.structure.moduli))
        self.graph = KnowledgeGraph()
        self.history = SearchHistory()
        self.definitions: List[Definition] = []
        self.conjectures: Dict[str, Conjecture] = {}
        self.findings: dict = {}
        self.attempts: List[dict] = []
        self.bounded_upto: Optional[int] = None
        self.goal_refuted = False
        self.origins: Dict[str, str] = {}
        self.progress = 0
        self._last_change = time.time()
        self.elapsed = 0.0
        self.stop_reason = "not_started"
        self._run_start = time.time()
        self.mutator = StrategyMutation(self)
        self.applied_mutations: List[dict] = []
        self._restore_memory()
        if problem.goal is not None:
            self.store.conjecture(problem.goal, problem.name, "problem statement")
        for a in problem.given_assumptions:
            proof = Proof("given", a)
            if self.kernel.check(proof)[0]:
                self.ctx.known[a.key()] = proof

    # ------------------------------------------------------------- state ops
    def _restore_memory(self):
        """Re-read the research record from an earlier run and re-verify it.

        Nothing is trusted from disk: stored conclusions are re-checked by the
        same kernel before they become facts in this run.
        """
        path = os.path.join(self.memory.dir, "discoveries.json")
        if not os.path.exists(path):
            return
        try:
            with open(path, encoding="utf-8") as fh:
                old = json.load(fh)
        except Exception:
            return
        from .problem import parse_prop
        restored = 0
        for item in old.get("established", []):
            try:
                prop = parse_prop(item["statement"])
                proof = Proof(item["rule"], prop)
                ok, _ = self.kernel.check(proof)
                if ok and set(proof.rules_used()) <= BLIND_ALLOWED_RULES:
                    self.ctx.known[prop.key()] = proof
                    self.store.add_proof(proof, self.problem.name, "restored from research memory")
                    self.origins[prop.key()] = "restored from research memory"
                    restored += 1
            except Exception:
                continue
        if restored:
            self.findings["restored_from_memory"] = restored
            self.progress += restored

    def goal_key(self):
        return self.problem.goal.key() if self.problem.goal is not None else None

    def goal_proved(self) -> bool:
        k = self.goal_key()
        return k is not None and k in self.store.proofs

    def discovery_quiet(self) -> bool:
        return time.time() - self._last_change > 2.0

    def propose(self, c: Conjecture, prove_now: bool = True):
        key = c.prop.key()
        if key in self.conjectures or key in self.store.proofs:
            return
        try:
            c.prop.typecheck()
        except Exception as exc:
            self.history.log("invention", "reject ill-typed", str(c.prop), str(exc))
            return
        ce = CE.find_counterexample(c.prop, small=30, randoms=10, big=10 ** 3)
        if ce is not None:
            self.refute(c.prop, str(ce))
            self.history.log("invention", "candidate refuted", str(c.prop), "refuted")
            return
        if not prove_now:
            c.meta["proved"] = True
        self.conjectures[key] = c
        self.store.conjecture(c.prop, self.problem.name, c.origin, c.note)
        self.graph.add_node(key, "conjecture", origin=c.origin)
        self.history.log("invention", c.origin, str(c.prop), "conjectured")
        self._last_change = time.time()
        self.progress += 1

    def define(self, d: Definition):
        for old in self.definitions:
            if old.name == d.name:
                return
        self.definitions.append(d)
        self.graph.add_node(d.name, "definition", reason=d.reason)
        self.history.log("invention", "new definition", str(d), "defined")
        self._last_change = time.time()
        self.progress += 1

    def refute(self, prop: Prop, counterexample: str):
        self.store.refute(prop, self.problem.name, counterexample)
        self.history.log("test", "counterexample", f"{prop} at {counterexample}", "refuted")
        self._last_change = time.time()
        self.progress += 1
        if self.goal_key() == prop.key():
            self.goal_refuted = True

    def accept(self, proof: Proof, origin: str) -> bool:
        key = proof.conclusion.key()
        if key in self.store.proofs:
            return True
        used = proof.rules_used()
        if not used <= BLIND_ALLOWED_RULES:
            self.history.log("verifier", "reject non-general rule",
                             f"{sorted(used - BLIND_ALLOWED_RULES)} in {proof.conclusion}", "rejected")
            return False
        if self.store.add_proof(proof, self.problem.name, origin):
            self.ctx.known[key] = proof
            self.graph.add_proof(proof)
            self.origins[key] = origin
            if key in self.conjectures:
                self.conjectures[key].meta["proved"] = True
            self.history.log("kernel", "accepted", f"{proof.rule}: {proof.conclusion}"[:160], "derived")
            self._last_change = time.time()
            self.progress += 1
            return True
        self.history.log("kernel", "rejected", str(proof.conclusion)[:160], "rejected")
        return False

    def log_attempt(self, goal: Prop, route: str, budget: int, proof: Optional[Proof]):
        self.attempts.append({
            "goal": str(goal), "route": route, "budget": budget,
            "success": proof is not None,
            "kernel_note": str(proof.data.get("kernel", "")) if proof else "",
            "at_s": round(time.time() - (self._run_start or time.time()), 3),
        })

    # ----------------------------------------------------------------- run
    def _strategies(self):
        return [
            ("counterexample_hunt", S.counterexample_hunt(self), 1.0),
            ("invent_from_objects", S.invent_from_objects(self), 1.0),
            ("invent_invariants", S.invent_invariants(self), 1.0),
            ("prove_conjectures", S.prove_conjectures(self), 1.5),
            ("direct_proof", S.direct_proof(self), 1.0),
            ("bounded_verification", S.bounded_verification(self), 0.5),
            ("forward_reasoning", S.forward_reasoning(self), 0.5),
            ("residue_exploration", S.residue_exploration(self), 0.5),
            ("witness_construction", W.witness_construction(self), 1.5),
        ]

    def run(self) -> dict:
        self._run_start = time.time()
        sch = FairScheduler(self.time_budget)
        for name, gen, weight in self._strategies():
            sch.add(name, gen, weight)
        last_progress, stall = self.progress, 0

        def on_round(round_no):
            nonlocal last_progress, stall
            if (self.goal_proved() or self.goal_refuted) and not self.explore:
                return True
            if self.progress == last_progress:
                stall += 1
            else:
                last_progress, stall = self.progress, 0
            if self.use_mutation and stall >= 3 and len(self.applied_mutations) < 12:
                mutations = self.mutator.mutate()
                for m in mutations:
                    sch.add(m.name, m.generator(self), 0.7)
                    self.applied_mutations.append({
                        "question": m.question, "name": m.name,
                        "rationale": m.rationale, "at_round": round_no})
                    self.history.log("mutation", f"Q{m.question} {m.name}",
                                     m.rationale, "new_strategy")
                stall = 0
            return False

        self.stop_reason = sch.run(on_round=on_round)
        self.elapsed = time.time() - self._run_start
        if (self.problem.goal is not None and not self.goal_proved()
                and not self.goal_refuted):
            note = "search ended without proof or counterexample; this is NOT a refutation"
            if self.bounded_upto:
                note += f"; verified for all cases up to {self.bounded_upto}"
            self.store.undecided(self.problem.goal, self.problem.name, note)
        return self.summary()

    # ----------------------------------------------------------- reporting
    def summary(self) -> dict:
        rows = self.store.rows(self.problem.name)
        by = {}
        for key, status, origin, rule, note in rows:
            by.setdefault(status, []).append(
                {"statement": key, "origin": origin, "rule": rule, "note": note})
        goal_status = (self.store.status(self.problem.goal).value
                       if self.problem.goal is not None else None)
        invented = [k for k, c in self.conjectures.items()
                    if c.meta.get("proved") and k in self.store.proofs]
        return {
            "problem": self.problem.name,
            "domain": self.problem.domain,
            "target": self.problem.target,
            "formal_statement": self.problem.formal_statement,
            "goal": str(self.problem.goal) if self.problem.goal is not None else None,
            "goal_status": goal_status,
            "stop_reason": self.stop_reason,
            "elapsed_s": round(self.elapsed, 2),
            "counts": {k: len(v) for k, v in by.items()},
            "statements": by,
            "invented_and_proved": invented,
            "definitions": [str(d) for d in self.definitions],
            "findings": self.findings,
            "bounded_upto": self.bounded_upto,
            "structure": self.structure.report(),
            "mutations": self.applied_mutations,
            "proof_attempts": len(self.attempts),
            "graph": self.graph.summary(),
        }

    def write_record(self, try_lean: Optional[bool] = None) -> str:
        lean = self.lean if try_lean is None else try_lean
        proofs = [p for p in self.store.proofs.values()
                  if not isinstance(p.conclusion, BoundedForAll)]
        lean_src, exported, skipped = proof_export.export_file(
            proofs, f"blind problem: {self.problem.name}")
        lean_note = "Lean not run."
        if lean and exported:
            res = lean_bridge.check_file(lean_src)
            lean_note = res.output[:2000] if res.available else res.output
            if res.ok:
                for p in exported:
                    self.store.mark_verified(p.conclusion, self.problem.name, "Lean accepted export")
                lean_note = f"Lean accepted all {len(exported)} exported theorems."
        s = self.summary()
        self.memory.write_all(self, s, {
            "lean_source": lean_src,
            "exported": len(exported),
            "skipped": len(skipped),
            "lean_note": lean_note,
        })
        return os.path.join(self.memory.dir, "research_report.md")
