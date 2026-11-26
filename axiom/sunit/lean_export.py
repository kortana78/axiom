"""Lean 4 export of an S-unit certificate.

Only the solution list is exported: for each triple we state ``a + b = c``,
coprimality, and explicit factorisations of ``a``, ``b`` and ``c`` into primes
that are members of ``S``.  The statements are closed by kernel ``decide``
(no ``native_decide``).

Completeness is *not* formalized here.  It is the computer-assisted,
independently re-checked part of the certificate.  The exported file must
never be described as a Lean proof of completeness or of the abc conjecture.
"""
from __future__ import annotations

import os
from typing import Dict


def _factor(n: int) -> Dict[int, int]:
    out: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def _smooth_expr(n: int) -> str:
    """A decidable conjunction asserting ``n`` is a product of primes in S."""
    if n == 1:
        return "(1 : ℕ) = 1"
    f = _factor(n)
    prod = " * ".join(f"{p} ^ {e}" for p, e in sorted(f.items()))
    parts = [f"({n} : ℕ) = {prod}"]
    parts += [f"({p} : ℕ) ∈ S" for p in sorted(f)]
    return " ∧ ".join(parts)


def theorem(i: int, t) -> str:
    a, b, c = (int(x) for x in t)
    return (
        f"theorem sol_{i} :\n"
        f"    ({a} : ℕ) + {b} = {c} ∧ Nat.Coprime {a} {b} ∧\n"
        f"    {_smooth_expr(a)} ∧\n"
        f"    {_smooth_expr(b)} ∧\n"
        f"    {_smooth_expr(c)} := by\n"
        f"  decide\n"
    )


def write(cert: dict, out_dir: str, pid: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    S = [int(p) for p in cert["S"]]
    sols = [tuple(int(x) for x in t) for t in cert["solutions"]]
    lines = [
        "import Mathlib",
        "",
        f"/-! AXIOM S-unit certificate for `{pid}`.",
        "",
        f"    S = {S}",
        f"    solutions = {len(sols)}",
        "",
        "    The solution list, the sum, coprimality and the explicit",
        "    factorisations into primes of S are checked by Lean's kernel",
        "    (`decide`).  Completeness of the list is computer-assisted and",
        "    independently re-checked by `axiom.sunit.check`; it is NOT",
        "    formalized in Lean.  This file says nothing about the abc",
        "    conjecture. -/",
        "",
        "set_option maxHeartbeats 400000",
        "",
        "namespace AxiomSunit",
        "",
        f"def S : Finset ℕ := ({{{', '.join(str(p) for p in S)}}} : Finset ℕ)",
        "",
        "def solutions : List (ℕ × ℕ × ℕ) :=",
        "  [" + ", ".join(f"({a}, {b}, {c})" for a, b, c in sols) + "]",
        "",
        f"theorem solution_count : solutions.length = {len(sols)} := by",
        "  decide",
        "",
    ]
    for i, t in enumerate(sols):
        lines.append(theorem(i, t))
    lines.append("#print axioms solution_count")
    if sols:
        lines.append("#print axioms sol_0")
    lines += ["", "end AxiomSunit", ""]
    src = "\n".join(lines)
    path = os.path.join(out_dir, f"{pid}.lean")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(src)
    return src
