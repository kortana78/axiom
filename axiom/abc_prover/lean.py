"""Compile one proposed lemma against the frozen statement with Lean.

The harness is deliberately strict: the statement is re-hashed, the proposal is
wrapped in a fixed namespace, and only the standard axioms are accepted.  It
never writes ``lean/Abc/Proof.lean``.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import time
from typing import Dict, List, Optional

from ..abc_proof import ALLOWED_AXIOMS, FROZEN_PATH
from ..abc_proof.check import (
    _version_info,
    _which_lake,
    parse_axioms,
    read_frozen,
    sha256_file,
)
from . import CHECKED, REJECTED


class LeanUnavailable(RuntimeError):
    pass


def wrap_attempt(code: str, name: str) -> str:
    """Place a proposal in a fixed namespace and print its axioms."""
    return (
        "import Abc.Statement\n"
        "import Mathlib\n"
        "\n"
        "set_option maxHeartbeats 400000\n"
        "\n"
        "namespace AbcProver\n"
        "\n"
        f"{code.rstrip()}\n"
        "\n"
        f"#print axioms AbcProver.{name}\n"
        "\n"
        "end AbcProver\n"
    )


def _run_utf8(cmd: List[str], cwd: str, env: Dict[str, str],
              timeout: float) -> Dict[str, object]:
    """Run a command with UTF-8 capture; Lean output is not cp1252."""
    started = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           timeout=timeout)
        return {
            "returncode": p.returncode,
            "output": (p.stdout or "") + (p.stderr or ""),
            "seconds": round(time.time() - started, 1),
            "command": " ".join(cmd),
        }
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout or ""
        err = exc.stderr or ""
        if isinstance(out, bytes):
            out = out.decode("utf-8", "replace")
        if isinstance(err, bytes):
            err = err.decode("utf-8", "replace")
        return {
            "returncode": -1,
            "output": out + err + "\nTIMEOUT\n",
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


def error_lines(output: str) -> List[str]:
    out: List[str] = []
    for line in output.splitlines():
        s = line.strip()
        if s.startswith("error:") or ": error:" in s:
            out.append(s)
    return out[:5]


class LeanHarness:
    """A reusable Lean workspace for a batch of proposals."""

    def __init__(self, statement_path: str, mathlib: Optional[str],
                 frozen_path: str = FROZEN_PATH, timeout: float = 180.0):
        self.statement_path = statement_path
        self.mathlib = mathlib
        self.frozen_path = frozen_path
        self.timeout = timeout
        self.tmp: Optional[str] = None
        self.env: Optional[Dict[str, str]] = None
        self.lake: Optional[str] = None
        self.versions: Dict[str, str] = {
            "lean_version": "not run",
            "mathlib_version": "not run",
            "lean_toolchain": "not run",
        }
        self.commands: List[str] = []

    def __enter__(self) -> "LeanHarness":
        if not self.mathlib or not os.path.isdir(self.mathlib):
            raise LeanUnavailable("Mathlib checkout not found")
        self.lake = _which_lake()
        if not self.lake:
            raise LeanUnavailable("lake executable not found (install elan)")
        try:
            frozen = read_frozen(self.frozen_path)
        except (OSError, ValueError) as exc:
            raise LeanUnavailable(f"cannot read frozen statement hash: {exc}")
        actual = sha256_file(self.statement_path)
        if actual != frozen:
            raise LeanUnavailable(
                "Statement.lean does not match the frozen SHA-256; refusing to "
                "check lemmas against a changed target")

        self.versions = _version_info(self.mathlib, self.lake)
        self.tmp = tempfile.mkdtemp(prefix="axiom_abc_prover_")
        abc_dir = os.path.join(self.tmp, "Abc")
        os.makedirs(abc_dir, exist_ok=True)
        stmt = os.path.join(abc_dir, "Statement.lean")
        shutil.copyfile(self.statement_path, stmt)
        if sha256_file(stmt) != frozen:
            raise LeanUnavailable("Statement.lean changed during the copy")

        env = os.environ.copy()
        old_path = env.get("LEAN_PATH", "")
        env["LEAN_PATH"] = self.tmp + (os.pathsep + old_path if old_path else "")
        self.env = env

        res = self._compile(stmt, os.path.join(abc_dir, "Statement.olean"))
        if int(res["returncode"]) != 0:
            raise LeanUnavailable(
                "the frozen Statement.lean did not compile:\n"
                + str(res.get("output", ""))[-2000:])
        return self

    def __exit__(self, *_exc) -> None:
        if self.tmp:
            shutil.rmtree(self.tmp, ignore_errors=True)
            self.tmp = None

    def _compile(self, src: str, olean: Optional[str] = None) -> Dict[str, object]:
        assert self.tmp and self.env and self.lake
        cmd = [self.lake, "env", "lean", f"--root={self.tmp}"]
        if olean:
            cmd += ["-o", olean]
        cmd.append(src)
        res = _run_utf8(cmd, self.mathlib or ".", self.env, self.timeout)
        self.commands.append(str(res["command"]))
        return res

    def check(self, code: str, name: str) -> Dict[str, object]:
        """Return ``CHECKED`` only if Lean accepts the lemma and its axioms."""
        started = time.time()
        if not self.tmp or not self.env:
            return {
                "ok": False, "status": REJECTED,
                "reason": "Lean harness is not open",
                "axioms": [], "output": "", "commands": [],
                **self.versions, "seconds": 0.0,
            }
        src = os.path.join(self.tmp, "Abc", "Attempt.lean")
        with open(src, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(wrap_attempt(code, name))
        res = self._compile(src)
        output = str(res.get("output", ""))
        base = {
            "axioms": [],
            "output": output,
            "commands": list(self.commands),
            **self.versions,
            "seconds": round(time.time() - started, 1),
        }
        if int(res.get("returncode", 1)) != 0:
            errors = error_lines(output)
            reason = "Lean rejected the lemma"
            if errors:
                reason += ": " + errors[0]
            return {"ok": False, "status": REJECTED, "reason": reason, **base}

        axioms = parse_axioms(output)
        if axioms is None:
            return {
                "ok": False, "status": REJECTED,
                "reason": f"could not read `#print axioms AbcProver.{name}`",
                **base,
            }
        extra = sorted(set(axioms) - ALLOWED_AXIOMS)
        if extra:
            return {
                "ok": False, "status": REJECTED,
                "reason": "lemma depends on non-allowed axioms: "
                          + ", ".join(extra),
                "axioms": axioms,
                **{k: v for k, v in base.items() if k != "axioms"},
            }
        return {
            "ok": True, "status": CHECKED,
            "reason": "Lean accepted the lemma with only allowed axioms",
            "axioms": axioms,
            **{k: v for k, v in base.items() if k != "axioms"},
        }
