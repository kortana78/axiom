"""Tests for the Lean-only abc proof alarm.

The real abc statement is never proved here.  The optional integration test
uses a deliberately trivial fake ``Abc.Statement`` to exercise the full
Lean harness; that is a test of the alarm, not a claim about abc.
"""
import json
import os
import re
import shutil
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.abc_proof import (  # noqa: E402
    ALLOWED_AXIOMS,
    FROZEN_PATH,
    LEAN_ACCEPTED,
    OPEN,
    PROOF_PATH,
    REJECTED,
    STATEMENT_PATH,
)
from axiom.abc_proof.check import (  # noqa: E402
    check,
    gate_status,
    parse_axioms,
    read_frozen,
    sha256_file,
    source_report,
    strip_lean_comments_and_strings,
)
from axiom.swarm.dashboard import (  # noqa: E402
    ABC_LEAN_ACCEPTED,
    ABC_OPEN,
    ABC_REJECTED,
    abc_banner,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text)
    return path


def _fake_runner(ok=True, axioms=None, reason="Lean accepted the proof",
                 output="'Abc.abc_proved' depends on axioms: []"):
    calls = []

    def runner(statement_path, proof_path, mathlib, timeout):
        calls.append((statement_path, proof_path, mathlib, timeout))
        return {
            "ok": ok,
            "reason": reason,
            "axioms": list(axioms or []),
            "output": output,
            "commands": ["fake lean"],
            "lean_version": "fake-lean",
            "mathlib_version": "fake-mathlib",
            "lean_toolchain": "fake-toolchain",
            "seconds": 0.1,
        }

    return runner, calls


def _valid_proof(path):
    return _write(path, (
        "import Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : Abc.Statement := by\n"
        "  exact Classical.choice (show Nonempty Abc.Statement from ⟨by assumption⟩)\n"
    ))


def test_frozen_hash_matches_statement():
    assert sha256_file(os.path.join(ROOT, STATEMENT_PATH)) == read_frozen(
        os.path.join(ROOT, FROZEN_PATH))


def test_hash_is_newline_insensitive(tmp_path):
    lf = tmp_path / "lf.txt"
    crlf = tmp_path / "crlf.txt"
    lf.write_bytes(b"a\nb\n")
    crlf.write_bytes(b"a\r\nb\r\n")
    assert sha256_file(str(lf)) == sha256_file(str(crlf))


def test_missing_proof_is_open(tmp_path):
    status = check(
        os.path.join(ROOT, STATEMENT_PATH),
        str(tmp_path / "Proof.lean"),
        os.path.join(ROOT, FROZEN_PATH),
        mathlib=None,
    )
    assert status["verdict"] == OPEN
    assert status["proof_present"] is False
    assert status["statement_hash_ok"] is True


def test_changed_statement_fails_hash(tmp_path):
    changed = tmp_path / "Statement.lean"
    shutil.copyfile(os.path.join(ROOT, STATEMENT_PATH), changed)
    with open(changed, "a", encoding="utf-8") as fh:
        fh.write("\n-- a weakened statement would go here\n")
    status = check(
        str(changed),
        str(tmp_path / "Proof.lean"),
        os.path.join(ROOT, FROZEN_PATH),
    )
    assert status["verdict"] == REJECTED
    assert status["statement_hash_ok"] is False
    assert "frozen" in status["reason"].lower()


def test_sorry_proof_rejected_before_lean(tmp_path):
    proof = _write(tmp_path / "Proof.lean", (
        "import Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : Abc.Statement := by\n"
        "  sorry\n"
    ))
    runner, calls = _fake_runner()
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "sorry" in status["reason"]
    assert calls == []


def test_axiom_declaration_rejected(tmp_path):
    proof = _write(tmp_path / "Proof.lean", (
        "import Abc.Statement\n"
        "\n"
        "axiom bad : Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : Abc.Statement := bad\n"
    ))
    runner, calls = _fake_runner()
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "axiom" in status["reason"]
    assert calls == []


def test_constant_declaration_rejected(tmp_path):
    proof = _write(tmp_path / "Proof.lean", (
        "import Abc.Statement\n"
        "\n"
        "constant bad : Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : Abc.Statement := bad\n"
    ))
    runner, calls = _fake_runner()
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "constant" in status["reason"]
    assert calls == []


def test_trivial_theorem_about_different_statement_rejected(tmp_path):
    proof = _write(tmp_path / "Proof.lean", (
        "import Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : True := trivial\n"
    ))
    runner, calls = _fake_runner()
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "Abc.Statement" in status["reason"]
    assert calls == []


def test_missing_import_rejected(tmp_path):
    proof = _write(tmp_path / "Proof.lean", (
        "theorem Abc.abc_proved : Abc.Statement := by\n"
        "  assumption\n"
    ))
    runner, calls = _fake_runner()
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "import Abc.Statement" in status["reason"]
    assert calls == []


def test_extra_axiom_from_lean_rejected(tmp_path):
    proof = _valid_proof(tmp_path / "Proof.lean")
    runner, _ = _fake_runner(
        axioms=["propext", "Classical.choice", "Quot.sound", "Lean.ofReduceBool"])
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "Lean.ofReduceBool" in status["reason"]


def test_allowed_axioms_accepted(tmp_path):
    proof = _valid_proof(tmp_path / "Proof.lean")
    runner, calls = _fake_runner(
        axioms=["propext", "Classical.choice", "Quot.sound"])
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == LEAN_ACCEPTED
    assert status["axioms"] == ["propext", "Classical.choice", "Quot.sound"]
    assert len(calls) == 1
    assert set(status["axioms"]) <= ALLOWED_AXIOMS


def test_lean_error_rejected(tmp_path):
    proof = _valid_proof(tmp_path / "Proof.lean")
    runner, _ = _fake_runner(ok=False, reason="Lean rejected Proof.lean",
                             output="error: unknown identifier")
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), lean_runner=runner)
    assert status["verdict"] == REJECTED
    assert "Lean rejected" in status["reason"]


def test_proof_present_without_mathlib_is_rejected(tmp_path):
    proof = _valid_proof(tmp_path / "Proof.lean")
    status = check(os.path.join(ROOT, STATEMENT_PATH), proof,
                   os.path.join(ROOT, FROZEN_PATH), mathlib=None)
    assert status["verdict"] == REJECTED
    assert "Mathlib" in status["reason"]


def test_parse_axioms():
    assert parse_axioms(
        "'Abc.abc_proved' depends on axioms: [propext, Classical.choice, Quot.sound]"
    ) == ["propext", "Classical.choice", "Quot.sound"]
    assert parse_axioms(
        "'Abc.abc_proved' depends on axioms: [propext,\n  Classical.choice, Quot.sound]"
    ) == ["propext", "Classical.choice", "Quot.sound"]
    assert parse_axioms("'Abc.abc_proved' does not depend on any axioms") == []
    assert parse_axioms("'Abc.abc_proved' depends on axioms: [Lean.ofReduceBool]") == [
        "Lean.ofReduceBool"]
    assert parse_axioms("no axiom line here") is None


def test_source_scanner_ignores_comments_and_strings():
    src = (
        "-- this comment mentions sorry and admit\n"
        "/- a nested /- block -/ with axiom bad -/\n"
        'def msg : String := "sorry admit axiom"\n'
        "import Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : Abc.Statement := by\n"
        "  trivial\n"
    )
    report = source_report(src)
    assert report["ok"] is True, report
    assert "sorry" not in strip_lean_comments_and_strings(src)
    assert "admit" not in strip_lean_comments_and_strings(src)


def test_gate_status(tmp_path, capsys):
    def write(verdict):
        path = tmp_path / f"{verdict}.json"
        path.write_text(json.dumps({"verdict": verdict, "reason": "test"}),
                        encoding="utf-8")
        return str(path)

    assert gate_status(write(OPEN)) == 0
    assert gate_status(write(LEAN_ACCEPTED)) == 0
    assert gate_status(write(REJECTED)) == 1
    assert gate_status(str(tmp_path / "missing.json")) == 1
    capsys.readouterr()


def test_dashboard_banner_is_from_status_only():
    assert abc_banner(None) == ABC_OPEN
    assert abc_banner({}) == ABC_OPEN
    assert abc_banner({"verdict": OPEN}) == ABC_OPEN
    assert abc_banner({"verdict": REJECTED}) == ABC_REJECTED
    assert abc_banner({"verdict": "nonsense"}) == ABC_OPEN
    assert abc_banner({"verdict": LEAN_ACCEPTED, "axioms": []}) == \
        ABC_LEAN_ACCEPTED.format(axioms="none")
    assert abc_banner({
        "verdict": LEAN_ACCEPTED,
        "axioms": ["propext", "Quot.sound"],
    }) == ABC_LEAN_ACCEPTED.format(axioms="propext, Quot.sound")


def test_only_checker_writes_lean_accepted():
    """No production module other than the checker may write the verdict."""
    quoted = re.compile(r"""["']LEAN_ACCEPTED["']""")
    assigned = re.compile(r"verdict\s*=\s*LEAN_ACCEPTED\b")
    dicted = re.compile(r"""["']verdict["']\s*:\s*LEAN_ACCEPTED\b""")

    roots = [os.path.join(ROOT, "axiom"), os.path.join(ROOT, "deploy"),
             os.path.join(ROOT, ".github")]
    files = []
    for base in roots:
        for dirpath, _dirnames, names in os.walk(base):
            for name in names:
                if name.endswith((".py", ".yml", ".yaml", ".sh")):
                    files.append(os.path.join(dirpath, name))

    quoted_hits, writer_hits, status_writers = [], [], []
    for path in files:
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        text = open(path, encoding="utf-8").read()
        if quoted.search(text):
            quoted_hits.append(rel)
        if assigned.search(text) or dicted.search(text):
            writer_hits.append(rel)
        if "write_status" in text:
            status_writers.append(rel)

    assert quoted_hits == ["axiom/abc_proof/__init__.py"], quoted_hits
    assert writer_hits == ["axiom/abc_proof/check.py"], writer_hits
    assert status_writers == ["axiom/abc_proof/check.py"], status_writers

    check_src = open(os.path.join(ROOT, "axiom", "abc_proof", "check.py"),
                     encoding="utf-8").read()
    assert "--verdict" not in check_src


def test_committed_status_matches_open_state():
    if os.path.exists(os.path.join(ROOT, PROOF_PATH)):
        pytest.skip("Proof.lean exists; the alarm status is no longer OPEN")
    with open(os.path.join(ROOT, "results", "abc_proof", "status.json"),
              encoding="utf-8") as fh:
        status = json.load(fh)
    assert status["verdict"] == OPEN
    assert status["statement_hash_ok"] is True
    assert status["proof_present"] is False


@pytest.mark.skipif(not os.environ.get("AXIOM_MATHLIB"),
                    reason="set AXIOM_MATHLIB to a Mathlib checkout for the real Lean path")
def test_real_lean_acceptance_path_with_fake_statement(tmp_path):
    """Exercise the real lake/Lean harness; the statement is fake on purpose."""
    mathlib = os.environ["AXIOM_MATHLIB"]
    abc = tmp_path / "Abc"
    abc.mkdir()
    stmt = _write(str(abc / "Statement.lean"), (
        "namespace Abc\n"
        "\n"
        "abbrev Statement : Prop := True\n"
        "\n"
        "end Abc\n"
    ))
    proof = _write(str(abc / "Proof.lean"), (
        "import Abc.Statement\n"
        "\n"
        "theorem Abc.abc_proved : Abc.Statement := trivial\n"
    ))
    frozen = _write(str(tmp_path / "frozen.sha256"),
                    sha256_file(stmt) + "  Abc/Statement.lean\n")
    status = check(stmt, proof, frozen, mathlib=mathlib, timeout=600)
    assert status["verdict"] == LEAN_ACCEPTED, status
    assert status["axioms"] == []
    assert status["lean_version"].startswith("Lean")
