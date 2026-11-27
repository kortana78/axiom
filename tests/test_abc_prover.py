"""Tests for the bounded abc proof-attempt loop.

The fake checker tests the loop's bookkeeping.  The optional real-Lean test
uses a deliberately trivial fake statement; it tests the harness, not abc.
"""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.abc_prover import (  # noqa: E402
    CHECKED,
    LEDGER_PATH,
    NO_PROOF,
    REJECTED,
    ROUTES_PATH,
    STATUS_PATH,
)
from axiom.abc_prover.lean import LeanHarness  # noqa: E402
from axiom.abc_prover.ledger import (  # noqa: E402
    build_status,
    load_ledger,
    stats,
)
from axiom.abc_prover.loop import run  # noqa: E402
from axiom.abc_prover.prompt import build_prompt  # noqa: E402
from axiom.abc_prover.proposals import (  # noqa: E402
    parse_proposals,
    sanitize,
    signature,
)
from axiom.abc_prover.routes import (  # noqa: E402
    load_routes,
    open_gaps,
    route_names,
)
from axiom.abc_proof.check import sha256_file  # noqa: E402
from axiom.llm.client import LLMResponse  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROUTES = os.path.join(ROOT, ROUTES_PATH)

GOOD_LEAN = "theorem one_pos : (0 : Nat) < 1 := by norm_num"
TARGET_LEAN = (
    "theorem abc_proved : Abc.Statement := by\n"
    "  exact Classical.choice (show Nonempty Abc.Statement from \u27e8by assumption\u27e9)"
)


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, messages, **_kwargs):
        self.calls.append(messages)
        text = self.responses.pop(0) if self.responses else '{"proposals": []}'
        return LLMResponse(text=text, model="fake", attempts=1)


def _proposal(name="one_pos", lean=GOOD_LEAN, route="definitions"):
    return {"name": name, "lean": lean, "route": route, "rationale": "test"}


def _response(*proposals):
    return json.dumps({"proposals": list(proposals)})


def _checker(calls=None, result=None):
    def check(code, name):
        if calls is not None:
            calls.append((code, name))
        if result is not None:
            return dict(result)
        return {
            "ok": True, "status": CHECKED, "reason": "fake acceptance",
            "axioms": [], "output": "", "seconds": 0.1,
        }
    return check


def _run(tmp_path, responses, checker=None, rounds=1, max_proposals=2,
         max_requests=1):
    return run(
        rounds=rounds,
        max_proposals=max_proposals,
        time_budget=30,
        ledger_path=str(tmp_path / "ledger.json"),
        status_path=str(tmp_path / "status.json"),
        routes_path=ROUTES,
        target_path=str(tmp_path / "target.lean"),
        usage_path=str(tmp_path / "usage.json"),
        client=FakeClient(responses),
        checker=checker or _checker(),
        max_requests=max_requests,
    )


def test_routes_are_honest():
    routes = load_routes(ROUTES)
    assert "abc_statement" in route_names(routes)
    nodes = routes["nodes"]
    assert nodes["abc_statement"]["status"] == "open"
    assert nodes["iut"]["status"] == "disputed"
    assert nodes["mason_stothers"]["status"] == "known"
    assert "abc_statement" in open_gaps(routes)


def test_prompt_mentions_open_target_and_routes():
    routes = load_routes(ROUTES)
    messages = build_prompt(routes, [], [], 2)
    assert messages[0]["role"] == "system"
    user = messages[1]["content"]
    assert "OPEN and unproved" in user
    assert "abc_statement" in user
    assert "already_checked" in user
    assert "No imports" in user


def test_valid_proposal_parses():
    proposals, bad = parse_proposals(
        _response(_proposal()), ["definitions"], 2)
    assert not bad
    assert len(proposals) == 1
    assert proposals[0]["name"] == "one_pos"
    assert proposals[0]["target_like"] is False
    assert proposals[0]["id"].startswith("sha256:")


def test_sorry_is_rejected_before_lean():
    proposals, bad = parse_proposals(
        _response(_proposal(lean="theorem bad : False := by\n  sorry")),
        ["definitions"], 2)
    assert proposals == []
    assert any("sorry" in b for b in bad)


def test_axiom_and_constant_are_rejected():
    for lean in (
        "axiom bad : False\ntheorem one_pos : (0 : Nat) < 1 := by norm_num",
        "constant bad : False\ntheorem one_pos : (0 : Nat) < 1 := by norm_num",
    ):
        proposals, bad = parse_proposals(
            _response(_proposal(lean=lean)), ["definitions"], 2)
        assert proposals == []
        assert any("axiom" in b or "constant" in b for b in bad)


def test_imports_namespaces_and_set_option_are_rejected():
    for lean in (
        "import Mathlib\ntheorem one_pos : (0 : Nat) < 1 := by norm_num",
        "namespace Foo\ntheorem one_pos : (0 : Nat) < 1 := by norm_num\nend Foo",
        "set_option maxHeartbeats 1\ntheorem one_pos : (0 : Nat) < 1 := by norm_num",
        "theorem one_pos : (0 : Nat) < 1 := by native_decide",
    ):
        proposals, bad = parse_proposals(
            _response(_proposal(lean=lean)), ["definitions"], 2)
        assert proposals == [], lean
        assert bad, lean


def test_wrong_name_is_rejected():
    proposals, bad = parse_proposals(
        _response(_proposal(name="other")), ["definitions"], 2)
    assert proposals == []
    assert any("must declare" in b for b in bad)


def test_signature_extraction():
    assert signature(GOOD_LEAN).startswith("theorem one_pos")
    assert signature(GOOD_LEAN).endswith("< 1")


def test_checked_lemma_is_recorded_and_abc_stays_open(tmp_path):
    report = _run(tmp_path, [_response(_proposal())])
    assert report["abc"] == "OPEN"
    assert report["verdict"] == NO_PROOF
    assert report["checked"] == 1
    ledger = load_ledger(str(tmp_path / "ledger.json"))
    assert stats(ledger)["checked"] == 1
    status = json.load(open(tmp_path / "status.json", encoding="utf-8"))
    assert status["abc"] == "OPEN"
    assert status["verdict"] == NO_PROOF
    assert status["checked_lemmas"] == 1
    assert "not a proof" in status["note"]


def test_rejected_lemma_is_recorded(tmp_path):
    result = {
        "ok": False, "status": REJECTED,
        "reason": "lemma depends on non-allowed axioms: Lean.ofReduceBool",
        "axioms": ["Lean.ofReduceBool"], "output": "error", "seconds": 0.1,
    }
    report = _run(tmp_path, [_response(_proposal())],
                  checker=_checker(result=result))
    assert report["checked"] == 0
    ledger = load_ledger(str(tmp_path / "ledger.json"))
    attempts = ledger["attempts"]
    assert attempts[-1]["status"] == REJECTED
    assert "Lean.ofReduceBool" in attempts[-1]["reason"]


def test_target_like_is_saved_but_not_promoted(tmp_path):
    before = os.path.exists(os.path.join(ROOT, "lean", "Abc", "Proof.lean"))
    report = _run(tmp_path, [_response(_proposal("abc_proved", TARGET_LEAN))])
    assert report["target_attempts"] == 1
    target = tmp_path / "target.lean"
    assert target.exists()
    assert "NOT lean/Abc/Proof.lean" in target.read_text(encoding="utf-8")
    assert os.path.exists(os.path.join(ROOT, "lean", "Abc", "Proof.lean")) == before
    ledger = load_ledger(str(tmp_path / "ledger.json"))
    assert ledger["attempts"][-1]["target_like"] is True


def test_duplicate_is_not_rechecked(tmp_path):
    calls = []
    response = _response(_proposal())
    report = _run(tmp_path, [response, response],
                  checker=_checker(calls=calls), rounds=2, max_requests=2)
    assert len(calls) == 1
    assert report["skipped_duplicates"] == 1


def test_request_budget_stops_the_loop(tmp_path):
    client = FakeClient([_response(_proposal())])
    calls = []
    run(
        rounds=3, max_proposals=1, time_budget=30,
        ledger_path=str(tmp_path / "ledger.json"),
        status_path=str(tmp_path / "status.json"),
        routes_path=ROUTES,
        target_path=str(tmp_path / "target.lean"),
        usage_path=str(tmp_path / "usage.json"),
        client=client, checker=_checker(calls=calls), max_requests=1,
    )
    assert len(client.calls) == 1
    assert len(calls) == 1


def test_build_status_is_always_no_proof(tmp_path):
    ledger = load_ledger(str(tmp_path / "missing.json"))
    status = build_status(ledger, load_routes(ROUTES))
    assert status["abc"] == "OPEN"
    assert status["verdict"] == NO_PROOF
    assert status["checked_lemmas"] == 0


def test_no_prover_module_writes_lean_accepted():
    import re

    quoted = re.compile(r"""["']LEAN_ACCEPTED["']""")
    assigned = re.compile(r"verdict\s*=\s*LEAN_ACCEPTED\b")
    dicted = re.compile(r"""["']verdict["']\s*:\s*LEAN_ACCEPTED\b""")
    prover_dir = os.path.join(ROOT, "axiom", "abc_prover")
    for name in sorted(os.listdir(prover_dir)):
        if not name.endswith(".py"):
            continue
        src = open(os.path.join(prover_dir, name), encoding="utf-8").read()
        assert not quoted.search(src), name
        assert not assigned.search(src), name
        assert not dicted.search(src), name
        assert "PROOF_PATH" not in src, name
        assert "write_status" not in src, name


def test_dashboard_shows_prover_section(tmp_path):
    from axiom.swarm import dashboard

    root = tmp_path / "results"
    (root / "abc_proof").mkdir(parents=True)
    (root / "abc_prover").mkdir(parents=True)
    (root / "abc_proof" / "status.json").write_text(json.dumps({
        "verdict": "OPEN", "reason": "no proof",
    }), encoding="utf-8")
    (root / "abc_prover" / "ledger.json").write_text(json.dumps({
        "attempts": [{
            "name": "one_pos", "route": "definitions", "status": CHECKED,
            "axioms": [], "checked_at": "2026-01-01T00:00:00Z",
        }],
    }), encoding="utf-8")
    queue = tmp_path / "queue.json"
    queue.write_text('{"problems": []}', encoding="utf-8")
    dashboard.build(str(queue), str(root))
    html = (root / "index.html").read_text(encoding="utf-8")
    md = (root / "SUMMARY.md").read_text(encoding="utf-8")
    for text in (html, md):
        assert "abc conjecture: OPEN. No result here proves it." in text
        assert "ABC proof attempts" in text
        assert "checked lemmas: 1" in text
        assert "not a proof" in text


@pytest.mark.skipif(not os.environ.get("AXIOM_MATHLIB"),
                    reason="set AXIOM_MATHLIB to a Mathlib checkout for the real Lean path")
def test_real_lean_harness_accepts_and_rejects(tmp_path):
    mathlib = os.environ["AXIOM_MATHLIB"]
    stmt = tmp_path / "Statement.lean"
    stmt.write_text(
        "namespace Abc\n\nabbrev Statement : Prop := True\n\nend Abc\n",
        encoding="utf-8")
    frozen = tmp_path / "frozen.sha256"
    frozen.write_text(sha256_file(str(stmt)) + "  Statement.lean\n",
                      encoding="utf-8")
    with LeanHarness(str(stmt), mathlib, frozen_path=str(frozen),
                     timeout=900) as harness:
        good = harness.check(
            "theorem trivial_true : True := by trivial", "trivial_true")
        assert good["status"] == CHECKED, good
        assert good["axioms"] == []
        bad = harness.check("theorem bad : False := by sorry", "bad")
        assert bad["status"] == REJECTED, bad
        assert "sorryAx" in bad["axioms"] or "non-allowed" in bad["reason"]
