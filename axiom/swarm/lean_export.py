"""Lean 4 (Mathlib) export of class witness families.

Each family becomes a theorem about the denominator-cleared equation over
the integers, with k = m + kl for a natural number m:

    theorem cls_M_r (m : Nat) : exists v1 .. vk : Int,
        lower bounds /\\ NUM(n, v) = 0

The identity is closed by `ring`, the lower bounds by `nlinarith` with
nonnegative powers of m. The reduction step (residue_cover / prime_reduction)
is NOT formalized in Lean yet; only the class lemmas are. A family counts
as VERIFIED only after Lean accepts its theorem.
"""
from __future__ import annotations

import os

import sympy as sp

from ..kernel.expressions import sym

MAX_THEOREMS = 400


def _lean(e) -> str:
    """Integer polynomial in symbols -> Lean term over Int."""
    s = sp.sstr(sp.expand(e)).replace("**", "^")
    return s


def theorem(st, c, idx) -> str:
    eng = st.engine
    M, r, kl = c["M"], c["r"], c["kl"]
    k = sp.Symbol("k", integer=True)
    m = sp.Symbol("mz", integer=True)   # printed as (m:ℤ)
    polys = [sp.sympify(p, locals={"k": k}) for p in c["polys"]]
    polys_m = [sp.expand(p.subs(k, m + kl)) for p in polys]
    n_m = sp.expand(M * (m + kl) + r)
    subs = {eng.N: n_m}
    names = [v for v, _ in eng.s.vars]
    for v, p in zip(eng.V, polys_m):
        subs[v] = p
    lows = [lo for _, lo in eng.s.vars]
    vs = " ".join(names)
    nm = eng.s.n.name
    num = sp.expand(eng.num)
    # statement uses the variables; witnesses supplied by refine
    num_stmt = _lean(num.subs(eng.N, sym("__n__"))).replace("__n__", f"({_lean(n_m)})")
    bounds = " ∧ ".join(f"{lo} ≤ {v}" for v, lo in zip(names, lows))
    hint = ", ".join(f"pow_nonneg hm {d}" for d in range(2, 9))
    wit = ", ".join(f"({_lean(p)})" for p in polys_m)
    goals = len(names) + 1
    cast = lambda t: t.replace("mz", "(m:ℤ)")
    num_stmt, wit = cast(num_stmt), cast(wit)
    return (
        f"/-- class n = {M}k + {r}, k = m + {kl}. Witnesses: {c['polys']} -/\n"
        f"theorem cls_{M}_{r} (m : ℕ) : ∃ {vs} : ℤ, {bounds} ∧ {num_stmt} = 0 := by\n"
        f"  have hm : (0:ℤ) ≤ (m:ℤ) := by positivity\n"
        f"  refine ⟨{wit}, {', '.join(['?_'] * goals)}⟩\n"
        + "".join(f"  · nlinarith [hm, {hint}]\n" for _ in names)
        + "  · ring\n"
    )


def write(st, valid, out_dir, pid):
    os.makedirs(out_dir, exist_ok=True)
    lines = ["import Mathlib", "",
             f"/-! AXIOM swarm export for `{pid}`.",
             f"    Statement: {st.entry['statement']}",
             "    Class lemmas only (denominator-cleared form). The reduction step is not",
             "    formalized in Lean yet. -/", "",
             "set_option maxHeartbeats 400000", ""]
    for i, c in enumerate(valid[:MAX_THEOREMS]):
        lines.append(theorem(st, c, i))
    src = "\n".join(lines)
    with open(os.path.join(out_dir, f"{pid}.lean"), "w", encoding="utf-8") as fh:
        fh.write(src)
    return src
