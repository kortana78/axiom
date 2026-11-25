"""Run Lean on exported class lemmas and record which theorems Lean accepted.

    python -m axiom.swarm.lean_check --mathlib /path/to/mathlib4

Run from a Mathlib checkout (`lake exe cache get` done). A family is marked
Lean-verified only if its theorem has no error and the file has no `sorry`.
"""
from __future__ import annotations

import argparse
import glob
import os
import re
import subprocess
import time

from .common import save_json


def check_file(path, mathlib, timeout=5400):
    src = open(path, encoding="utf-8").read()
    names = [(i + 1, m.group(1)) for i, line in enumerate(src.splitlines())
             for m in [re.match(r"theorem (\S+)", line)] if m]
    t0 = time.time()
    try:
        r = subprocess.run(["lake", "env", "lean", os.path.abspath(path)], cwd=mathlib,
                           capture_output=True, text=True, timeout=timeout)
        out, code = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, code = "timeout", -1
    bad_lines = [int(m.group(1)) for m in re.finditer(r":(\d+):\d+: error", out)]
    failed = set()
    for ln in bad_lines:
        owner = None
        for start, name in names:
            if start <= ln:
                owner = name
        failed.add(owner or "<file>")
    ok = [n for _, n in names if n not in failed]
    return {"file": path, "theorems": len(names), "accepted": len(ok) if code != -1 else 0,
            "failed": sorted(x for x in failed if x), "returncode": code,
            "sorry_present": "sorry" in src, "seconds": round(time.time() - t0, 1),
            "log_tail": out[-3000:],
            "summary": (f"Lean accepted {len(ok)}/{len(names)} class lemmas" if code != -1 else "Lean timed out")}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mathlib", required=True)
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    for path in sorted(glob.glob(os.path.join(a.results, "*", "lean", "*.lean"))):
        res = check_file(path, a.mathlib)
        pid = path.split(os.sep)[-3]
        save_json(os.path.join(a.results, pid, "lean_status.json"), res)
        print(f"[lean {pid}] {res['summary']}; failed: {res['failed'][:10]}")


if __name__ == "__main__":
    main()
