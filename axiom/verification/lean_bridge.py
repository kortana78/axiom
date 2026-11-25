"""Run exported proofs through the Lean 4 kernel when it is available.

Set AXIOM_LEAN_PROJECT to a Lake project that depends on Mathlib.
Without it, results stay DERIVED (Axiom kernel) and are never reported
as VERIFIED.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class LeanResult:
    available: bool
    ok: bool
    output: str


def lean_available() -> bool:
    return bool(os.environ.get("AXIOM_LEAN_PROJECT")) and shutil.which("lake") is not None


def check_file(lean_source: str, filename: str = "AxiomExport.lean", timeout: int = 900) -> LeanResult:
    if not lean_available():
        return LeanResult(False, False, "Lean not configured (set AXIOM_LEAN_PROJECT and install lake)")
    proj = os.environ["AXIOM_LEAN_PROJECT"]
    path = os.path.join(proj, filename)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(lean_source)
    try:
        r = subprocess.run(["lake", "env", "lean", path], cwd=proj, capture_output=True,
                           text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return LeanResult(True, False, "Lean timed out")
    out = r.stdout + r.stderr
    ok = r.returncode == 0 and "sorry" not in lean_source and "error" not in out.lower()
    return LeanResult(True, ok, out)
