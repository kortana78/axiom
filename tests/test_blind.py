"""AXIOM 0.2 blind-discovery tests.

Run with: python -m pytest -q  (or python tests/test_blind.py)
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.blind.controller import BlindController
from axiom.blind.evaluation import score_case
from axiom.blind.leakage import audit_leakage
from axiom.blind.library import CASES
from axiom.blind.memory import ResearchMemory
from axiom.blind.problem import (BlindProblem, BlindProblemError, parse_definition,
                                 parse_prop)
from axiom.kernel.proof_objects import Proof
from axiom.kernel.propositions import ForAll, Pred
from axiom.kernel.expressions import Var
from axiom.blind.tactics import BLIND_ALLOWED_RULES


def _run(key, time=8.0, root=None):
    root = root or tempfile.mkdtemp(prefix="axiom_blind_test_")
    problem = BlindProblem.from_dict(CASES[key])
    ctl = BlindController(problem, time_budget=time, research_dir=root)
    s = ctl.run()
    ctl.write_record()
    return ctl, s


def test_blind_schema_rejects_solution_hints():
    data = dict(CASES["hidden_div_42"])
    data["known_solution"] = "42 | n^7 - n"
    try:
        BlindProblem.from_dict(data)
    except BlindProblemError as exc:
        assert "extra keys" in str(exc)
    else:
        raise AssertionError("blind interface accepted a solution hint")


def test_parser_understands_the_statement_language():
    p = parse_prop("forall n >= 0: 30 | n^5 - n")
    assert isinstance(p, ForAll)
    assert str(p).startswith("forall n >= 0")
    kind, obj = parse_definition("a(0) = 0; a(n+1) = a(n) + 2*n + 1")
    assert kind == "sequence" and obj.init == 0


def test_leakage_audit_passes():
    report = audit_leakage()
    assert report.ok, report.render()


def test_problem_specific_rule_is_rejected():
    assert "collatz_descent" not in BLIND_ALLOWED_RULES
    ctl, _ = _run("hidden_div_30", time=3.0)
    goal = ForAll(Var("n"), Pred("is_odd", (Var("n"),)))
    assert not ctl.accept(Proof("collatz_descent", goal, [], {"k": 1, "r": 0}),
                          "illegal rule")


def test_hidden_theorem_is_proved_without_its_proof():
    ctl, s = _run("hidden_div_42")
    assert s["goal_status"] in ("derived", "verified")


def test_research_level_content_is_invented():
    ctl, s = _run("research_sum_squares")
    r = score_case("research", "research_sum_squares", s, ctl)
    assert r.passed, r.detail


def test_strategy_mutation_runs_when_stalled():
    ctl, s = _run("research_rec_squares", time=12.0)
    assert ctl.applied_mutations
    assert any(m["question"] in range(1, 7) for m in ctl.applied_mutations)


def test_persistent_research_record_has_every_file():
    root = tempfile.mkdtemp(prefix="axiom_blind_files_")
    ctl, _ = _run("hidden_div_30", time=5.0, root=root)
    for name in ResearchMemory.FILES:
        assert os.path.exists(os.path.join(ctl.memory.dir, name)), name


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
