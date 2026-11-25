"""Persistent research memory for a blind investigation.

Every run leaves a complete, inspectable record. The engine never stores a
solution it was given: only statements it derived, conjectured, refuted or
attempted, each with the epistemic status assigned by the trusted verifier.
"""
from __future__ import annotations

import json
import os
from typing import Dict

from ..kernel.proof_objects import Status


class ResearchMemory:
    FILES = ("original_statement.json", "definitions.json", "conjectures.json",
             "invented_lemmas.json", "counterexamples.json", "proof_attempts.json",
             "failed_strategies.json", "discoveries.json", "final_proof.lean",
             "research_report.md")

    def __init__(self, root: str, name: str):
        self.dir = os.path.join(root, name)
        self.db_path = os.path.join(self.dir, "axiom.db")

    def _dump(self, name: str, data):
        with open(os.path.join(self.dir, name), "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)

    def write_all(self, ctl, summary: dict, lean_info: Dict):
        os.makedirs(self.dir, exist_ok=True)
        store = ctl.store

        self._dump("original_statement.json", ctl.problem.to_dict())
        self._dump("definitions.json", {
            "given": {
                "sequences": [str(s) for s in ctl.problem.given_sequences],
                "terms": [str(e) for e in ctl.problem.given_terms],
                "assumptions": [str(a) for a in ctl.problem.given_assumptions],
            },
            "invented": [{"name": d.name, "kind": d.kind, "body": str(d.body),
                          "reason": d.reason, "parent": d.parent}
                         for d in ctl.definitions],
            "structure_found_by_analysis": ctl.structure.report(),
        })

        conjecture_rows, lemma_rows, refuted_rows = [], [], []
        for key, prop in store.props.items():
            status = store.status(prop)
            row = {"statement": key, "status": status.value if status else None,
                   "origin": ctl.origins.get(key, ""), "note": ""}
            for sk, st, origin, rule, note in store.rows(ctl.problem.name):
                if sk == key:
                    row.update({"rule": rule, "note": note, "origin": origin})
                    break
            conjecture_rows.append(row)
            if status in (Status.DERIVED, Status.VERIFIED) and key in store.proofs:
                lemma_rows.append({"statement": key, "rule": store.proofs[key].rule,
                                   "status": status.value, "origin": row["origin"]})
            elif status == Status.REFUTED:
                refuted_rows.append(row)
        self._dump("conjectures.json", conjecture_rows)
        self._dump("invented_lemmas.json", lemma_rows)
        self._dump("counterexamples.json", refuted_rows)

        self._dump("proof_attempts.json", ctl.attempts)
        failures = [{"goal": g, "tactic": t, "reason": r}
                    for g, t, r in store.failures(ctl.problem.name, limit=500)]
        self._dump("failed_strategies.json", {
            "kernel_rejections": failures,
            "mutations_applied": ctl.applied_mutations,
            "failed_proof_routes": [a for a in ctl.attempts if not a["success"]],
        })

        established = [{"statement": key, "rule": p.rule,
                        "status": store.status(p.conclusion).value,
                        "origin": ctl.origins.get(key, "")}
                       for key, p in store.proofs.items()]
        self._dump("discoveries.json", {
            "problem": ctl.problem.name,
            "goal": summary["goal"],
            "goal_status": summary["goal_status"],
            "stop_reason": summary["stop_reason"],
            "elapsed_s": summary["elapsed_s"],
            "established": established,
            "invented_and_proved": summary["invented_and_proved"],
            "findings": summary["findings"],
            "bounded_upto": summary["bounded_upto"],
            "counts": summary["counts"],
        })

        with open(os.path.join(self.dir, "final_proof.lean"), "w", encoding="utf-8") as fh:
            fh.write(lean_info["lean_source"])

        self._write_report(ctl, summary, lean_info, lemma_rows, refuted_rows)

    def _write_report(self, ctl, summary, lean_info, lemmas, refuted):
        L = ["# AXIOM 0.2 research record: " + ctl.problem.name, ""]
        L.append("## Original statement (as given, nothing withheld from the record)")
        L.append("```json")
        L.append(json.dumps(ctl.problem.to_dict(), indent=2))
        L.append("```")
        L.append("")
        L.append(f"- domain: {ctl.problem.domain}")
        L.append(f"- target mode: {ctl.problem.target}")
        L.append(f"- target: `{summary['goal']}`" if summary["goal"] else "- target: discover")
        L.append(f"- target status after run: **{summary['goal_status']}**")
        L.append(f"- time: {summary['elapsed_s']} s ({summary['stop_reason']})")
        L.append(f"- statement counts: {summary['counts']}")
        L.append("")

        L.append("## Structure discovered from the statement (not supplied)")
        for k, v in summary["structure"].items():
            L.append(f"- {k}: {v}")
        L.append("")

        if lemmas:
            L.append("## Established results (kernel checked)")
            for r in lemmas:
                L.append(f"- `{r['statement']}` — rule `{r['rule']}`, origin: {r['origin']}")
            L.append("")
        if ctl.definitions:
            L.append("## Invented definitions")
            for d in ctl.definitions:
                L.append(f"- {d}")
            L.append("")
        if summary["findings"]:
            L.append("## Findings")
            for k, v in summary["findings"].items():
                L.append(f"- {k}: {v}")
            L.append("")
        if refuted:
            L.append("## Refuted candidates (with counterexamples)")
            for r in refuted:
                L.append(f"- `{r['statement']}` — {r['note']}")
            L.append("")
        if ctl.applied_mutations:
            L.append("## Strategy mutations applied")
            for m in ctl.applied_mutations:
                L.append(f"- Q{m['question']} `{m['name']}` (round {m['at_round']}): {m['rationale']}")
            L.append("")
        goal_key = ctl.goal_key()
        if goal_key and goal_key in ctl.store.proofs:
            L.append("## Proof of the target")
            L.append("```")
            L.append(ctl.store.proofs[goal_key].render())
            L.append("```")
            L.append("")
        L.append("## Proof attempts")
        L.append(f"- total attempts: {len(ctl.attempts)}; successful: "
                 f"{sum(1 for a in ctl.attempts if a['success'])}")
        for a in ctl.attempts[:30]:
            L.append(f"- {a['route']} budget {a['budget']}: "
                     f"{'accepted' if a['success'] else 'no proof'} | `{a['goal'][:110]}`")
        L.append("")
        L.append("## Lean")
        L.append(f"- exported theorems: {lean_info['exported']}; "
                 f"not yet translatable: {lean_info['skipped']}")
        L.append(f"- {lean_info['lean_note']}")
        L.append("")
        L.append("## Search history (first events)")
        L.append("```")
        L.append(ctl.history.render(limit=60))
        L.append("```")

        with open(os.path.join(self.dir, "research_report.md"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(L))
