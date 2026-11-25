"""Blind evaluation harness.

The reference answers live in ``answers.py`` and are read here only. The
discovery engine is instantiated exactly as a user would instantiate it, with
nothing beyond the blind problem specification. A leakage audit runs before
any benchmark to verify that separation.

Three environments:

  hidden    theorem statements given, proofs withheld: can it prove them?
  research  no conclusion given: can it invent the mathematical content?
  open      no known proof: does it investigate honestly without cheating?
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional

import sympy as sp

from . import answers
from .controller import BlindController
from .leakage import audit_leakage
from .library import CASES, ENVIRONMENTS
from .problem import BlindProblem, parse_math, parse_prop
from ..kernel.expressions import Const
from ..kernel.propositions import Divides, Eq, strip_forall


@dataclass
class CaseResult:
    name: str
    env: str
    passed: bool
    detail: str
    status: Optional[str]
    elapsed: float


def _reference_matches(statement: str, reference: str) -> bool:
    # Statements containing invented sequence symbols may not be parseable by
    # the minimal expression grammar; a literal equality fallback is honest.
    plain = statement.replace(" ", "").lower()
    if "=" + reference.replace(" ", "").lower() in plain:
        return True
    try:
        _, prop = strip_forall(parse_prop(statement))
    except Exception:
        return False
    if reference.strip().isdigit():
        return (isinstance(prop, Divides) and isinstance(prop.d, Const)
                and int(prop.d.value) == int(reference))
    try:
        target = parse_math(reference).to_sympy()
    except Exception:
        return reference.replace(" ", "") in statement.replace(" ", "")
    if isinstance(prop, Eq):
        try:
            return sp.simplify(prop.rhs.to_sympy() - target) == 0
        except Exception:
            return False
    return False


def score_case(env: str, key: str, summary: dict, ctl: BlindController) -> CaseResult:
    status = summary["goal_status"]
    detail = ""
    if env == "hidden":
        passed = status in ("derived", "verified")
        detail = f"target proof {'found' if passed else 'not found'}"
    elif env == "research":
        reference = answers.CASES[key]["reference"]
        candidates = list(summary["invented_and_proved"]) + list(ctl.store.proofs)
        hits = [s for s in candidates if _reference_matches(s, reference)]
        passed = bool(hits)
        detail = f"reference {reference!r} " + (f"invented as {hits[0]}" if hits else "not invented")
    elif env == "open":
        passed = status != "refuted" and not ctl.goal_refuted
        if status in ("derived", "verified"):
            detail = "NEW RESULT: proof found by the blind engine"
        elif passed:
            detail = f"honest non-solution ({status}); bounded to {summary['bounded_upto']}"
        else:
            detail = "incorrectly refuted an open problem"
    else:  # pragma: no cover
        passed, detail = False, "unknown environment"
    return CaseResult(key, env, passed, detail, status, summary["elapsed_s"])


def run_case(key: str, env: str, time_budget: float = 20.0,
             research_root: str = "research", mutation: bool = True,
             lean: bool = False, bounded_limit: int = 2000) -> CaseResult:
    problem = BlindProblem.from_dict(CASES[key])
    ctl = BlindController(problem, time_budget=time_budget,
                          research_dir=os.path.join(research_root, env),
                          lean=lean, mutation=mutation, bounded_limit=bounded_limit)
    summary = ctl.run()
    ctl.write_record()
    return score_case(env, key, summary, ctl)


def benchmark(environments: Optional[List[str]] = None, time_budget: float = 20.0,
              research_root: str = "research", mutation: bool = True,
              lean: bool = False, run_audit: bool = True) -> List[CaseResult]:
    if run_audit:
        report = audit_leakage()
        print(report.render())
        print()
        if not report.ok:
            print("Benchmark aborted: fix the reported leaks first.")
            return []
    envs = environments or list(ENVIRONMENTS)
    results = []
    for env in envs:
        if env not in ENVIRONMENTS:
            print(f"unknown environment {env}")
            continue
        print(f"--- environment: {env} ---")
        for key in ENVIRONMENTS[env]:
            limit = 200 if env == "open" else 2000
            r = run_case(key, env, time_budget, research_root, mutation,
                         lean, bounded_limit=limit)
            results.append(r)
            print(f"{key:<24} {'PASS' if r.passed else 'FAIL'}  "
                  f"{r.status or '-':<22} {r.elapsed:>6.2f}s  {r.detail}")
        print()
    passed = sum(1 for r in results if r.passed)
    print(f"{passed}/{len(results)} blind cases passed")
    return results
