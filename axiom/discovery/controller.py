"""Discovery controller.

Holds the mathematical state S = (Gamma, D, G, C, P, F, R):
  Gamma  established results          -> store.proofs / ctx.known
  D      definitions and objects       -> self.definitions
  G      current goals                 -> self.goals
  C      candidate conjectures         -> self.conjectures
  P      partial proofs and failures   -> ctx.failures, store failures
  F      frontier                      -> unfinished strategies in the scheduler
  R      resources and history         -> self.history, time budget
and runs competing strategies under a fair scheduler.
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
from ..problems.base import Problem
from ..reasoning.backward import TacticContext
from ..reasoning.search import FairScheduler
from ..verification import lean_bridge, proof_export
from . import strategies as S
from .counterexamples import find_counterexample


class Controller:
    def __init__(self, problem: Problem, time_budget: float = 60.0, db_path: str = ":memory:",
                 explore: bool = False):
        self.explore = explore
        self.problem = problem
        self.time_budget = time_budget
        self.kernel = Kernel()
        self.store = TheoremStore(db_path, self.kernel)
        self.ctx = TacticContext(self.kernel, known={}, residue_moduli=(2, 3, 4))
        self.graph = KnowledgeGraph()
        self.history = SearchHistory()
        self.definitions: List[Definition] = []
        self.conjectures: Dict[str, Conjecture] = {}
        self.goals: List[Prop] = [problem.goal] if problem.goal is not None else []
        self.findings: dict = {}
        self.bounded_upto: Optional[int] = None
        self.goal_refuted = False
        self.origins: Dict[str, str] = {}
        self._last_change = time.time()
        if problem.goal is not None:
            self.store.conjecture(problem.goal, problem.name, "problem statement")

    # ---------------------------------------------------------- state ops
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
        ce = find_counterexample(c.prop, small=30, randoms=10, big=10 ** 3)
        if ce:
            self.store.refute(c.prop, self.problem.name, str(ce))
            self.history.log("invention", "candidate refuted", str(c.prop), "refuted")
            return
        if not prove_now:
            c.meta["proved"] = True  # keep it out of the prover queue
        self.conjectures[key] = c
        self.store.conjecture(c.prop, self.problem.name, c.origin, c.note)
        self.graph.add_node(key, "conjecture", origin=c.origin)
        self.history.log("invention", c.origin, str(c.prop), "conjectured")
        self._last_change = time.time()

    def define(self, d: Definition):
        self.definitions.append(d)
        self.graph.add_node(d.name, "definition", reason=d.reason)
        self.history.log("invention", "new definition", str(d), "defined")

    def accept(self, proof: Proof, origin: str) -> bool:
        key = proof.conclusion.key()
        if key in self.store.proofs:
            return True
        if self.store.add_proof(proof, self.problem.name, origin):
            self.ctx.known[key] = proof
            self.graph.add_proof(proof)
            self.origins[key] = origin
            if key in self.conjectures:
                self.conjectures[key].meta["proved"] = True
            self.history.log("kernel", "accepted", f"{proof.rule}: {proof.conclusion}"[:160], "derived")
            self._last_change = time.time()
            return True
        self.history.log("kernel", "rejected", str(proof.conclusion)[:160], "rejected")
        return False

    # ---------------------------------------------------------- run
    def run(self) -> dict:
        sch = FairScheduler(self.time_budget)
        sch.add("counterexample_hunt", S.counterexample_hunt(self), 1.0)
        sch.add("invent_from_data", S.invent_from_data(self), 1.0)
        sch.add("invent_invariants", S.invent_invariants(self), 1.0)
        sch.add("prove_conjectures", S.prove_conjectures(self), 1.5)
        sch.add("forward_reasoning", S.forward_reasoning(self), 0.5)
        sch.add("direct_proof", S.direct_proof(self), 1.0)
        sch.add("bounded_verification", S.bounded_verification(self), 0.5)
        for name in self.problem.special:
            sch.add(name, S.SPECIAL[name](self), 1.0)
        t0 = time.time()
        stop = sch.run(on_round=lambda r: (not self.explore) and (self.goal_proved() or self.goal_refuted))
        self.elapsed = time.time() - t0
        self.stop_reason = stop
        if self.problem.goal is not None and not self.goal_proved() and not self.goal_refuted:
            note = "search ended without proof or counterexample; this is NOT a refutation"
            if self.bounded_upto:
                note += f"; verified for all cases up to {self.bounded_upto}"
            self.store.undecided(self.problem.goal, self.problem.name, note)
        return self.summary()

    # ---------------------------------------------------------- reporting
    def summary(self) -> dict:
        rows = self.store.rows(self.problem.name)
        by = {}
        for key, status, origin, rule, note in rows:
            by.setdefault(status, []).append({"statement": key, "origin": origin, "rule": rule, "note": note})
        goal_status = self.store.status(self.problem.goal).value if self.problem.goal is not None else None
        invented = [k for k, c in self.conjectures.items() if c.meta.get("proved") and k in self.store.proofs]
        return {
            "problem": self.problem.name,
            "title": self.problem.title,
            "known_status": self.problem.known_status,
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
            "graph": self.graph.summary(),
        }

    def write_record(self, out_dir: str, try_lean: bool = False) -> str:
        os.makedirs(out_dir, exist_ok=True)
        s = self.summary()
        base = os.path.join(out_dir, self.problem.name)
        with open(base + ".json", "w", encoding="utf-8") as fh:
            json.dump(s, fh, indent=2, default=str)

        proofs = [p for p in self.store.proofs.values()
                  if not isinstance(p.conclusion, BoundedForAll)]
        lean_src, exported, skipped = proof_export.export_file(proofs, f"problem: {self.problem.name}")
        with open(base + ".lean", "w", encoding="utf-8") as fh:
            fh.write(lean_src)
        lean_note = "Lean not run."
        if try_lean and exported:
            res = lean_bridge.check_file(lean_src)
            lean_note = res.output[:2000] if res.available else res.output
            if res.ok:
                for p in exported:
                    self.store.mark_verified(p.conclusion, self.problem.name, "Lean accepted export")
                lean_note = f"Lean accepted all {len(exported)} exported theorems."

        L = []
        L.append(f"# AXIOM research record: {self.problem.title}")
        L.append("")
        L.append(f"- problem id: {self.problem.name}")
        L.append(f"- mathematical status before run: {self.problem.known_status}")
        if self.problem.goal is not None:
            L.append(f"- target: `{self.problem.goal}`")
            L.append(f"- target status after run: **{s['goal_status']}**")
        L.append(f"- time used: {s['elapsed_s']} s ({s['stop_reason']})")
        L.append(f"- statement counts: {s['counts']}")
        if self.problem.withheld:
            L.append(f"- withheld from the system (for rediscovery scoring): {self.problem.withheld}")
        if self.problem.notes:
            L.append(f"- notes: {self.problem.notes}")
        L.append("")
        if self.findings:
            L.append("## Findings")
            for k, v in self.findings.items():
                if isinstance(v, list) and len(v) > 40:
                    v = f"{len(v)} items: {v[:40]} ..."
                L.append(f"- {k}: {v}")
            L.append("")
        L.append("## Established results (kernel checked)")
        shown = 0
        for key, p in self.store.proofs.items():
            if shown >= 40:
                L.append(f"- ... {len(self.store.proofs) - shown} more (see JSON)")
                break
            L.append(f"- `{key}`")
            L.append(f"  - rule: {p.rule}; origin: {self.origins.get(key, '')}")
            shown += 1
        L.append("")
        for status in (Status.CONJECTURED, Status.UNDECIDED, Status.REFUTED):
            items = s["statements"].get(status.value, [])
            if not items:
                continue
            L.append(f"## {status.value}")
            for it in items[:40]:
                L.append(f"- `{it['statement']}` ({it['origin']}) {it['note'] or ''}")
            L.append("")
        if self.definitions:
            L.append("## Invented definitions")
            for d in self.definitions:
                L.append(f"- {d}")
            L.append("")
        goal_key = self.goal_key()
        if goal_key and goal_key in self.store.proofs:
            L.append("## Proof of the target")
            L.append("```")
            L.append(self.store.proofs[goal_key].render())
            L.append("```")
            L.append("")
        fails = self.store.failures(self.problem.name, limit=25)
        if fails:
            L.append("## Recorded failures (kept on purpose)")
            for g, t, r in fails:
                L.append(f"- {t}: {r} | goal `{g[:120]}`")
            L.append("")
        L.append("## Lean")
        L.append(f"- exported theorems: {len(exported)}; not yet translatable: {len(skipped)}")
        L.append(f"- {lean_note}")
        L.append("")
        L.append("## Search history (first events)")
        L.append("```")
        L.append(self.history.render(limit=60))
        L.append("```")
        with open(base + ".md", "w", encoding="utf-8") as fh:
            fh.write("\n".join(L))
        return base + ".md"
