"""Lean export of ABC record arithmetic.

Only two facts are formalized per record: a + b = c and Nat.Coprime a b.
The radical and quality are exact integer computations performed by the
Python merger; they are not formalized here. Nothing in this file proves
the abc conjecture.
"""
from __future__ import annotations

import os

MAX_RECORDS = 100


def theorem(rec: dict, idx: int) -> str:
    a, b, c = int(rec["a"]), int(rec["b"]), int(rec["c"])
    q = float(rec.get("q", 0.0))
    rad = int(rec.get("rad", 0))
    return (
        f"/-- a={a}, b={b}, c={c}, rad(abc)={rad}, q={q:.6f}. -/\n"
        f"theorem rec_{idx:03d}_add : {a} + {b} = {c} := by norm_num\n"
        f"theorem rec_{idx:03d}_coprime : Nat.Coprime {a} {b} := by decide\n"
    )


def write(records: list, out_dir: str, pid: str, statement: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    lines = [
        "import Mathlib",
        "",
        f"/-! AXIOM ABC record export for `{pid}`.",
        f"    Statement: {statement}",
        "",
        "    Each theorem checks a+b=c and coprimality for one recorded triple.",
        "    The radical and quality are exact integer computations by the Python",
        "    merger (prime factorizations are included in records.json). They are",
        "    not formalized here, and this file does not prove the abc conjecture. -/",
        "",
    ]
    for i, rec in enumerate(records[:MAX_RECORDS]):
        lines.append(theorem(rec, i))
    src = "\n".join(lines)
    with open(os.path.join(out_dir, f"{pid}.lean"), "w", encoding="utf-8") as fh:
        fh.write(src)
    return src
