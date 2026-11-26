"""The Lean-only abc proof alarm.

Run with a Mathlib checkout when ``lean/Abc/Proof.lean`` exists::

    python -m axiom.abc_proof.check --mathlib /path/to/mathlib4

Without ``--mathlib`` the checker still freezes the statement, detects a
missing proof, and rejects source-level problems.  It never accepts a proof
without actually running Lean.

Verdicts
--------
``OPEN``
    No proof file, or no frozen-statement mismatch.  The conjecture is open.
``REJECTED``
    The statement hash changed, the proof source contains ``sorry``/``admit``/
    an axiom, Lean rejected the proof, the target theorem is not exactly
    ``Abc.abc_proved : Abc.Statement``, or the axiom list contains anything
    outside ``propext``, ``Classical.choice``, ``Quot.sound``.
``LEAN_ACCEPTED``
    Lean compiled the proof against the frozen statement and ``#print axioms``
    listed only the allowed axioms.  Human review is still required.

Only :func:`check` can produce ``LEAN_ACCEPTED``.  There is deliberately no
CLI flag or environment variable that sets a verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple

from . import (
    ALLOWED_AXIOMS,
    FROZEN_PATH,
    LEAN_ACCEPTED,
    OPEN,
    PROOF_PATH,
    REJECTED,
    STATEMENT_PATH,
    STATUS_PATH,
)

LeanRunner = Callable[[str, str, Optional[str], float], Dict[str, object]]


# ---------------------------------------------------------------------------
# hashing and frozen statement
# ---------------------------------------------------------------------------

def normalize_newlines(data: bytes) -> bytes:
    """Hash text identically on LF and CRLF checkouts."""
    return data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def sha256_file(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(normalize_newlines(fh.read())).hexdigest()


def read_frozen(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        text = fh.read().strip()
    if not text:
        raise ValueError("frozen hash file is empty")
    token = text.split()[0].lower()
    if not re.fullmatch(r"[0-9a-f]{64}", token):
        raise ValueError("frozen hash must be 64 hexadecimal characters")
    return token


# ---------------------------------------------------------------------------
# source checks
# ---------------------------------------------------------------------------

def strip_lean_comments_and_strings(src: str) -> str:
    """Remove comments and string literals so keywords in prose do not count.

    Lean block comments nest.  Line comments and ordinary strings are handled;
    interpolation inside ``s!"..."`` is skipped with the rest of the string,
    which is conservative for this check (it can only hide code, never create a
    false ``sorry``).
    """
    out: List[str] = []
    i, n, block = 0, len(src), 0
    while i < n:
        if block:
            if src.startswith("/-", i):
                block += 1
                i += 2
            elif src.startswith("-/", i):
                block -= 1
                i += 2
            else:
                i += 1
            continue
        if src.startswith("--", i):
            j = src.find("\n", i)
            if j < 0:
                break
            out.append("\n")
            i = j + 1
            continue
        if src.startswith("/-", i):
            block = 1
            i += 2
            continue
        if src[i] == '"':
            i += 1
            while i < n:
                if src[i] == "\\":
                    i += 2
                elif src[i] == '"':
                    i += 1
                    break
                else:
                    i += 1
            out.append('""')
            continue
        out.append(src[i])
        i += 1
    return "".join(out)


_TARGET_RE = re.compile(
    r"(?m)^\s*(?:@\[[^\]]*\]\s*)*"
    r"theorem\s+(?:Abc\.)?abc_proved\s*:\s*(?:Abc\.)?Statement\s*:="
)
_IMPORT_RE = re.compile(r"(?m)^\s*import\s+Abc\.Statement\s*$")
_AXIOM_RE = re.compile(
    r"(?m)^\s*(?:@\[[^\]]*\]\s*)*"
    r"(?:(?:private|protected|unsafe)\s+)*"
    r"(?:axiom|constant)\s+([A-Za-z0-9_'.]+)"
)


def source_report(src: str) -> Dict[str, object]:
    clean = strip_lean_comments_and_strings(src)
    reasons: List[str] = []
    if re.search(r"\bsorry\b", clean):
        reasons.append("proof source contains `sorry`")
    if re.search(r"\badmit\b", clean):
        reasons.append("proof source contains `admit`")
    axioms = sorted(set(_AXIOM_RE.findall(clean)))
    if axioms:
        reasons.append("proof source declares an axiom/constant: " + ", ".join(axioms))
    imports_statement = bool(_IMPORT_RE.search(clean))
    if not imports_statement:
        reasons.append("proof source must `import Abc.Statement`")
    target_found = bool(_TARGET_RE.search(clean))
    if not target_found:
        reasons.append(
            "proof source must contain `theorem Abc.abc_proved : Abc.Statement := ...`"
        )
    return {
        "ok": not reasons,
        "reasons": reasons,
        "imports_statement": imports_statement,
        "target_found": target_found,
        "axiom_declarations": axioms,
    }


# ---------------------------------------------------------------------------
# Lean execution
# ---------------------------------------------------------------------------

def _which_lake() -> Optional[str]:
    for cand in (
        shutil.which("lake"),
        os.path.expanduser("~/.elan/bin/lake"),
        os.path.expanduser("~/.elan/bin/lake.exe"),
    ):
        if cand and os.path.isfile(cand):
            return cand
    return None


def _run(cmd: List[str], cwd: str, env: Dict[str, str],
         timeout: float) -> Dict[str, object]:
    started = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True,
                           text=True, timeout=timeout)
        return {
            "returncode": p.returncode,
            "output": (p.stdout or "") + (p.stderr or ""),
            "seconds": round(time.time() - started, 1),
            "command": " ".join(cmd),
        }
    except subprocess.TimeoutExpired as exc:
        out = (exc.stdout or "") + (exc.stderr or "")
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        return {
            "returncode": -1,
            "output": out + "\nTIMEOUT\n",
            "seconds": round(time.time() - started, 1),
            "command": " ".join(cmd),
        }
    except OSError as exc:
        return {
            "returncode": -2,
            "output": f"failed to run Lean: {exc}\n",
            "seconds": round(time.time() - started, 1),
            "command": " ".join(cmd),
        }


def _version_info(mathlib: Optional[str], lake: Optional[str]) -> Dict[str, str]:
    out = {"lean_version": "not run", "mathlib_version": "not run",
           "lean_toolchain": "not run"}
    if not mathlib:
        return out
    if lake:
        env = os.environ.copy()
        p = _run([lake, "env", "lean", "--version"], mathlib, env, 120)
        text = str(p.get("output", "")).strip().splitlines()
        if text and int(p.get("returncode", 1)) == 0:
            out["lean_version"] = text[0].strip()
    try:
        p = subprocess.run(["git", "-C", mathlib, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        if p.returncode == 0 and p.stdout.strip():
            out["mathlib_version"] = p.stdout.strip()
    except OSError:
        pass
    toolchain = os.path.join(mathlib, "lean-toolchain")
    try:
        with open(toolchain, encoding="utf-8") as fh:
            out["lean_toolchain"] = fh.read().strip() or "unknown"
    except OSError:
        pass
    return out


def run_lean_check(statement_path: str, proof_path: str,
                   mathlib: Optional[str], timeout: float = 3600.0,
                   frozen_hash: Optional[str] = None,
                   proof_hash: Optional[str] = None) -> Dict[str, object]:
    """Compile the proof against the frozen statement and read its axioms."""
    started = time.time()
    if not mathlib or not os.path.isdir(mathlib):
        return {"ok": False, "reason": "Mathlib checkout not found",
                "axioms": [], "output": "", "commands": [],
                "lean_version": "not run", "mathlib_version": "not run",
                "lean_toolchain": "not run", "seconds": 0.0}
    lake = _which_lake()
    if not lake:
        return {"ok": False, "reason": "lake executable not found (install elan)",
                "axioms": [], "output": "", "commands": [],
                "lean_version": "not run", "mathlib_version": "not run",
                "lean_toolchain": "not run", "seconds": 0.0}

    versions = _version_info(mathlib, lake)
    commands: List[str] = []
    outputs: List[str] = []

    with tempfile.TemporaryDirectory(prefix="axiom_abc_proof_") as tmp:
        abc_dir = os.path.join(tmp, "Abc")
        os.makedirs(abc_dir, exist_ok=True)
        stmt_copy = os.path.join(abc_dir, "Statement.lean")
        proof_copy = os.path.join(abc_dir, "Proof.lean")
        check_copy = os.path.join(abc_dir, "Check.lean")
        shutil.copyfile(statement_path, stmt_copy)
        shutil.copyfile(proof_path, proof_copy)

        # Re-hash the copies so a file changed between the source check and the
        # copy cannot be checked under the frozen hash.
        if frozen_hash is not None and sha256_file(stmt_copy) != frozen_hash:
            return {"ok": False,
                    "reason": "Statement.lean changed during the check",
                    "axioms": [], "output": "", "commands": commands,
                    **versions, "seconds": round(time.time() - started, 1)}
        if proof_hash is not None and sha256_file(proof_copy) != proof_hash:
            return {"ok": False,
                    "reason": "Proof.lean changed during the check",
                    "axioms": [], "output": "", "commands": commands,
                    **versions, "seconds": round(time.time() - started, 1)}

        with open(check_copy, "w", encoding="utf-8") as fh:
            fh.write(
                "import Abc.Statement\n"
                "import Abc.Proof\n"
                "\n"
                "#check (Abc.abc_proved : Abc.Statement)\n"
                "#print axioms Abc.abc_proved\n"
            )

        env = os.environ.copy()
        old_path = env.get("LEAN_PATH", "")
        env["LEAN_PATH"] = tmp + (os.pathsep + old_path if old_path else "")

        def compile_file(src: str, olean: Optional[str]) -> Dict[str, object]:
            cmd = [lake, "env", "lean", f"--root={tmp}"]
            if olean:
                cmd += ["-o", olean]
            cmd.append(src)
            res = _run(cmd, mathlib, env, timeout)
            commands.append(str(res["command"]))
            outputs.append(
                f"$ {res['command']}\n{res['output']}"
                f"[exit {res['returncode']}]\n"
            )
            return res

        stmt = compile_file(stmt_copy, os.path.join(abc_dir, "Statement.olean"))
        if int(stmt["returncode"]) != 0:
            return {"ok": False,
                    "reason": "the frozen Statement.lean did not compile",
                    "axioms": [], "output": "\n".join(outputs),
                    "commands": commands, **versions,
                    "seconds": round(time.time() - started, 1)}

        proof = compile_file(proof_copy, os.path.join(abc_dir, "Proof.olean"))
        if int(proof["returncode"]) != 0:
            return {"ok": False, "reason": "Lean rejected Proof.lean",
                    "axioms": [], "output": "\n".join(outputs),
                    "commands": commands, **versions,
                    "seconds": round(time.time() - started, 1)}

        check = compile_file(check_copy, None)
        output = "\n".join(outputs)
        if int(check["returncode"]) != 0:
            return {"ok": False,
                    "reason": ("Lean could not verify "
                               "`Abc.abc_proved : Abc.Statement`"),
                    "axioms": [], "output": output, "commands": commands,
                    **versions, "seconds": round(time.time() - started, 1)}

        axioms = parse_axioms(str(check["output"]))
        if axioms is None:
            return {"ok": False,
                    "reason": "could not read `#print axioms Abc.abc_proved`",
                    "axioms": [], "output": output, "commands": commands,
                    **versions, "seconds": round(time.time() - started, 1)}
        extra = sorted(set(axioms) - ALLOWED_AXIOMS)
        if extra:
            return {"ok": False,
                    "reason": "proof depends on non-allowed axioms: "
                              + ", ".join(extra),
                    "axioms": axioms, "output": output, "commands": commands,
                    **versions, "seconds": round(time.time() - started, 1)}
        return {"ok": True,
                "reason": "Lean accepted the proof with only allowed axioms",
                "axioms": axioms, "output": output, "commands": commands,
                **versions, "seconds": round(time.time() - started, 1)}


def parse_axioms(output: str) -> Optional[List[str]]:
    """Parse ``#print axioms`` output.

    Accepted forms include::

        'Abc.abc_proved' depends on axioms: [propext, Classical.choice, Quot.sound]
        'Abc.abc_proved' does not depend on any axioms

    Returns ``None`` if neither form is present.
    """
    matches = re.findall(r"depends on axioms:\s*\[([^\]]*)\]", output, re.S)
    if matches:
        names: List[str] = []
        for body in matches:
            names.extend(x.strip() for x in body.split(",") if x.strip())
        return names
    if re.search(r"does not depend on any axioms", output):
        return []
    return None


# ---------------------------------------------------------------------------
# verdict
# ---------------------------------------------------------------------------

def git_head(repo: str = ".") -> str:
    try:
        p = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"],
                           capture_output=True, text=True, timeout=30)
        if p.returncode == 0 and p.stdout.strip():
            return p.stdout.strip()
    except OSError:
        pass
    return "unknown"


def utc_now() -> str:
    return (datetime.now(timezone.utc).replace(microsecond=0)
            .isoformat().replace("+00:00", "Z"))


def _base_status(statement_path: str, proof_path: str) -> Dict[str, object]:
    return {
        "verdict": OPEN,
        "reason": "",
        "axioms": [],
        "allowed_axioms": sorted(ALLOWED_AXIOMS),
        "statement_path": statement_path,
        "statement_sha256": None,
        "frozen_sha256": None,
        "statement_hash_ok": False,
        "proof_path": proof_path,
        "proof_present": False,
        "proof_sha256": None,
        "lean_version": "not run",
        "mathlib_version": "not run",
        "lean_toolchain": "not run",
        "commit": git_head(),
        "ci_ref": os.environ.get("GITHUB_REF", ""),
        "ci_sha": os.environ.get("GITHUB_SHA", ""),
        "checked_at": utc_now(),
        "lean_output": "",
        "commands": [],
        "seconds": 0.0,
    }


def check(statement_path: str = STATEMENT_PATH,
          proof_path: str = PROOF_PATH,
          frozen_path: str = FROZEN_PATH,
          mathlib: Optional[str] = None,
          timeout: float = 3600.0,
          lean_runner: Optional[LeanRunner] = None) -> Dict[str, object]:
    """Compute the alarm status.  This is the only writer of the verdict."""
    status = _base_status(statement_path, proof_path)

    try:
        actual = sha256_file(statement_path)
        status["statement_sha256"] = actual
    except OSError as exc:
        status.update(verdict=REJECTED,
                      reason=f"cannot read Statement.lean: {exc}")
        return status

    try:
        frozen = read_frozen(frozen_path)
        status["frozen_sha256"] = frozen
    except (OSError, ValueError) as exc:
        status.update(verdict=REJECTED,
                      reason=f"cannot read frozen statement hash: {exc}")
        return status

    hash_ok = hmac.compare_digest(actual, frozen)
    status["statement_hash_ok"] = hash_ok
    if not hash_ok:
        status.update(
            verdict=REJECTED,
            reason=("Statement.lean does not match the frozen SHA-256; "
                    "refusing to check any proof"),
        )
        return status

    proof_exists = os.path.exists(proof_path)
    status["proof_present"] = proof_exists
    if not proof_exists:
        status.update(verdict=OPEN,
                      reason="lean/Abc/Proof.lean is absent; abc remains OPEN")
        return status
    if not os.path.isfile(proof_path):
        status.update(verdict=REJECTED,
                      reason="lean/Abc/Proof.lean is not a regular file")
        return status

    try:
        proof_hash = sha256_file(proof_path)
        status["proof_sha256"] = proof_hash
        with open(proof_path, encoding="utf-8") as fh:
            src = fh.read()
    except (OSError, UnicodeDecodeError) as exc:
        status.update(verdict=REJECTED,
                      reason=f"cannot read Proof.lean as UTF-8: {exc}")
        return status

    report = source_report(src)
    status["proof_source"] = report
    if not report["ok"]:
        status.update(verdict=REJECTED,
                      reason="; ".join(report["reasons"]))
        return status

    if lean_runner is None:
        result = run_lean_check(statement_path, proof_path, mathlib, timeout,
                                frozen_hash=frozen, proof_hash=proof_hash)
    else:
        result = lean_runner(statement_path, proof_path, mathlib, timeout)

    status["lean_output"] = str(result.get("output", "") or "")
    status["commands"] = list(result.get("commands", []) or [])
    status["axioms"] = list(result.get("axioms", []) or [])
    status["lean_version"] = str(result.get("lean_version", "unknown"))
    status["mathlib_version"] = str(result.get("mathlib_version", "unknown"))
    status["lean_toolchain"] = str(result.get("lean_toolchain", "unknown"))
    status["seconds"] = float(result.get("seconds", 0.0) or 0.0)

    if not result.get("ok"):
        status.update(verdict=REJECTED,
                      reason=str(result.get("reason", "Lean rejected the proof")))
        return status

    extra = sorted(set(status["axioms"]) - ALLOWED_AXIOMS)
    if extra:
        status.update(
            verdict=REJECTED,
            reason="proof depends on non-allowed axioms: " + ", ".join(extra),
        )
        return status

    status.update(
        verdict=LEAN_ACCEPTED,
        reason=("Lean accepted Abc.abc_proved : Abc.Statement with only the "
                "allowed axioms; human review is still required"),
    )
    return status


def write_status(path: str, status: Dict[str, object]) -> None:
    """Write the status atomically.  This is the alarm's only output path."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(status, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def read_status(path: str) -> Dict[str, object]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("status must be a JSON object")
    return data


def gate_status(path: str) -> int:
    """Exit 1 unless the status is OPEN or LEAN_ACCEPTED."""
    try:
        status = read_status(path)
    except (OSError, ValueError) as exc:
        print(f"[abc-proof] REJECTED: cannot read status: {exc}")
        return 1
    verdict = status.get("verdict")
    if verdict == REJECTED:
        print(f"[abc-proof] REJECTED: {status.get('reason', '')}")
        return 1
    if verdict not in (OPEN, LEAN_ACCEPTED):
        print(f"[abc-proof] REJECTED: unknown verdict {verdict!r}")
        return 1
    print(f"[abc-proof] {verdict}: {status.get('reason', '')}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Lean-only abc proof alarm")
    ap.add_argument("--statement", default=STATEMENT_PATH)
    ap.add_argument("--proof", default=PROOF_PATH)
    ap.add_argument("--frozen", default=FROZEN_PATH)
    ap.add_argument("--status", default=STATUS_PATH)
    ap.add_argument("--mathlib", default=None)
    ap.add_argument("--timeout", type=float, default=3600.0)
    ap.add_argument("--no-fail", action="store_true",
                    help="write the status but exit 0 even on REJECTED")
    ap.add_argument("--gate", default=None,
                    help="read this status file and exit 1 on REJECTED")
    a = ap.parse_args(argv)
    if a.gate:
        return gate_status(a.gate)

    status = check(a.statement, a.proof, a.frozen, a.mathlib, a.timeout)
    write_status(a.status, status)
    print(f"[abc-proof] {status['verdict']}: {status['reason']}")
    if status["verdict"] == LEAN_ACCEPTED:
        print("[abc-proof] HUMAN REVIEW REQUIRED before any announcement.")
    if status["verdict"] == REJECTED and not a.no_fail:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
