"""Leakage audit.

Before a blind benchmark may run, this checks that the discovery engine cannot
have seen the reference answers:

  * no answer signature appears in discovery-facing source;
  * no strategy hint from 0.1 appears in discovery-facing source;
  * blind problem inputs use only the minimal schema and contain no answer;
  * no discovery module imports the answer/evaluation/problem-specific modules;
  * every kernel rule the blind engine may accept is a general rule.

Legacy problem-specific rules still present in the shared 0.1 kernel are
listed explicitly as gated: the blind controller's allowlist and tactic set
make them unreachable.
"""
from __future__ import annotations

import ast
import os
import re
from dataclasses import dataclass, field
from typing import List

from . import answers
from .problem import ALLOWED_KEYS, BlindProblem, BlindProblemError

PKG = os.path.dirname(os.path.abspath(__file__))
AXIOM = os.path.dirname(PKG)

EVALUATION_ONLY = {"answers.py", "library.py", "evaluation.py", "leakage.py"}

# General 0.1 modules that the blind engine reuses.
GENERAL_MODULES = [
    "kernel/expressions.py", "kernel/propositions.py", "kernel/inference.py",
    "kernel/predicates.py", "kernel/proof_objects.py", "kernel/types.py",
    "reasoning/backward.py", "reasoning/forward.py", "reasoning/search.py",
    "reasoning/unification.py", "reasoning/rewriting.py",
    "invention/lemmas.py", "invention/invariants.py", "invention/definitions.py",
    "invention/expressions.py", "invention/generalization.py",
    "memory/theorem_store.py", "memory/knowledge_graph.py", "memory/search_history.py",
    "verification/proof_export.py", "verification/lean_bridge.py",
    "discovery/evaluation.py", "discovery/counterexamples.py",
    "ideas/space.py", "ideas/engine.py", "ideas/run.py",
    "swarm/common.py", "swarm/worker.py", "swarm/merge.py", "swarm/plan.py",
]

# Legacy modules that still contain target-specific mathematics. They are
# reported, not silently ignored; the blind engine gates them by allowlist.
# New modules that must also be free of reference-answer signatures.  They are
# not part of the blind engine, but the audit still scans them so a future
# import cannot silently leak a known answer.
NEW_MODULES = [
    "sunit/hunt.py", "sunit/check.py", "sunit/lean_export.py",
    "llm/config.py", "llm/client.py", "llm/schema.py", "llm/ideas.py",
    "llm/usage.py", "swarm/sunit.py", "swarm/schedule.py",
    "abc_proof/__init__.py", "abc_proof/check.py",
    "abc_prover/__init__.py", "abc_prover/routes.py",
    "abc_prover/proposals.py", "abc_prover/lean.py",
    "abc_prover/ledger.py", "abc_prover/prompt.py",
    "abc_prover/loop.py",
]

GATED_MODULES = {
    "kernel/inference.py": "contains the 0.1 collatz_descent rule; not in BLIND_ALLOWED_RULES",
    "reasoning/backward.py": "has an unused collatz_descent_auto placeholder in 0.1 DIRECT_RULES; "
                             "blind tactics use their own rule list",
    "invention/constructions.py": "contains handcrafted residue-class families; never imported by blind engine",
    "discovery/strategies.py": "contains special problem strategies; never imported by blind engine",
    "problems/library.py": "contains 0.1 problem modules with withheld answers; never imported by blind engine",
}

FORBIDDEN_IMPORTS = {
    "axiom.blind.answers", "blind.answers", "answers",
    "axiom.blind.library", "blind.library", "library",
    "axiom.blind.evaluation", "blind.evaluation", "evaluation",
    "axiom.problems.library", "problems.library", "library",
    "axiom.invention.constructions", "invention.constructions", "constructions",
    "axiom.discovery.strategies", "discovery.strategies", "strategies",
}


@dataclass
class AuditReport:
    ok: bool
    findings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def render(self) -> str:
        lines = ["AXIOM 0.2 leakage audit", "=" * 24,
                 "result: " + ("PASS" if self.ok else "FAIL")]
        if self.findings:
            lines.append("findings:")
            for f in self.findings:
                lines.append("  - " + f)
        else:
            lines.append("findings: none (0 target-specific leaks in discovery-facing code)")
        if self.notes:
            lines.append("notes:")
            for n in self.notes:
                lines.append("  - " + n)
        return "\n".join(lines)


def _norm(text: str) -> str:
    return re.sub(r"\s+", "", text.lower())


def _read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def audit_leakage() -> AuditReport:
    report = AuditReport(ok=True)
    blind_files = [os.path.join(PKG, f) for f in sorted(os.listdir(PKG))
                   if f.endswith(".py") and f not in EVALUATION_ONLY]
    general_files = [os.path.join(AXIOM, rel) for rel in GENERAL_MODULES
                     if os.path.exists(os.path.join(AXIOM, rel))]
    new_files = [os.path.join(AXIOM, rel) for rel in NEW_MODULES
                 if os.path.exists(os.path.join(AXIOM, rel))]
    discovery_files = blind_files + general_files + new_files

    signatures = [(key, val["signature"]) for key, val in answers.CASES.items()
                  if val.get("signature")]

    for path in discovery_files:
        src = _norm(_read(path))
        rel = os.path.relpath(path, AXIOM).replace(os.sep, "/")
        for key, sig in signatures:
            if _norm(sig) in src:
                report.findings.append(f"{rel}: contains answer signature of {key}: {sig!r}")
        if rel not in GATED_MODULES:
            for token in answers.STRATEGY_HINTS:
                if _norm(token) in src:
                    report.findings.append(f"{rel}: contains 0.1 strategy hint {token!r}")

    # Import isolation.
    for path in blind_files:
        tree = ast.parse(_read(path))
        for node in ast.walk(tree):
            mods = []
            if isinstance(node, ast.Import):
                mods = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                mods = [node.module]
            for mod in mods:
                if mod in FORBIDDEN_IMPORTS:
                    report.findings.append(
                        f"{os.path.relpath(path, AXIOM)} imports isolated module {mod}")

    # Blind problem inputs: schema and answer absence for discover-mode cases.
    from .library import CASES
    for key, data in CASES.items():
        name = data.get("name", key)
        unknown = set(data) - ALLOWED_KEYS
        if unknown:
            report.findings.append(f"library[{name}]: extra keys {sorted(unknown)}")
        try:
            BlindProblem.from_dict(data)
        except BlindProblemError as exc:
            report.findings.append(f"library[{name}]: {exc}")
        if data.get("target") == "discover":
            raw = _norm(repr(data))
            sig = answers.CASES.get(key, {}).get("signature")
            if sig and _norm(sig) in raw:
                report.findings.append(f"library[{name}]: discover input contains answer {sig!r}")

    # Rule allowlist must contain no legacy problem-specific rule.
    from .tactics import BLIND_ALLOWED_RULES
    for bad in ("collatz_descent", "es_family", "special"):
        if bad in BLIND_ALLOWED_RULES:
            report.findings.append(f"BLIND_ALLOWED_RULES contains problem-specific rule {bad!r}")

    for rel, why in GATED_MODULES.items():
        report.notes.append(f"gated 0.1 module {rel}: {why}")
    report.notes.append(
        "all accepted proofs are re-checked by the kernel and filtered through BLIND_ALLOWED_RULES")
    report.notes.append("reference answers live only in blind/answers.py, imported by evaluation")
    report.ok = not report.findings
    return report


if __name__ == "__main__":
    print(audit_leakage().render())
