"""Prompts for the abc proof-attempt loop.

The model is a Lean proof engineer, not an oracle.  It receives the route
graph, previously checked lemmas, and recent Lean errors.  It is told,
explicitly, that abc is open and that no response can close it.
"""
from __future__ import annotations

import json
from typing import Dict, List

from . import MAX_LEAN_CHARS
from .routes import route_brief, route_names

SYSTEM = (
    "You are a Lean 4 proof engineer. You write small, self-contained lemmas "
    "that compile with Mathlib. You never claim to prove the abc conjecture. "
    "Return JSON only, with no markdown and no commentary."
)

#: True, checkable starter targets.  Statements only; the model must supply
#: the proof, and the loop checks it like any other proposal.
SUGGESTED = (
    {
        "name": "rad_one_prime",
        "statement": "theorem rad_one_prime : Abc.rad 1 = 1",
        "route": "definitions",
    },
    {
        "name": "rad_dvd",
        "statement": "theorem rad_dvd (n : \u2115) : Abc.rad n \u2223 n",
        "route": "definitions",
    },
    {
        "name": "rad_le",
        "statement": ("theorem rad_le (n : \u2115) (h : 0 < n) : "
                      "Abc.rad n \u2264 n"),
        "route": "definitions",
    },
    {
        "name": "rad_pos",
        "statement": ("theorem rad_pos (n : \u2115) (h : 0 < n) : "
                      "0 < Abc.rad n"),
        "route": "definitions",
    },
)


def build_prompt(routes: Dict[str, object], checked: List[dict],
                 failures: List[dict], max_proposals: int,
                 statement_source: str = "") -> List[dict]:
    payload = {
        "target": "Abc.Statement (the abc conjecture; OPEN and unproved)",
        "target_source": statement_source,
        "routes": route_brief(routes),
        "suggested_lemmas": list(SUGGESTED),
        "known_facts": [
            "`Abc.rad n` is defined as `n.primeFactors.prod id`; there are no "
            "`Nat.rad_*` lemmas.",
            "`Nat.prod_primeFactors_dvd (n) : \u220f p \u2208 n.primeFactors, p \u2223 n`.",
            "`Nat.prime_of_mem_primeFactors (hp : p \u2208 n.primeFactors) : p.Prime`.",
            "`Finset.prod_pos` proves a product of positive factors is positive.",
        ],
        "already_checked": [
            {
                "name": a.get("name", ""),
                "signature": a.get("signature", ""),
                "route": a.get("route", ""),
            }
            for a in checked[-12:]
        ],
        "recent_failures": [
            {
                "name": a.get("name", ""),
                "route": a.get("route", ""),
                "error": str(a.get("reason", ""))[:400],
            }
            for a in failures[-6:]
        ],
        "limits": {
            "max_proposals": max(1, int(max_proposals)),
            "max_lean_chars": MAX_LEAN_CHARS,
        },
    }
    user = (
        "Here is the current proof-attempt state as JSON:\n"
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + "\n\nReturn JSON exactly in this shape:\n"
        '{"proposals": [{"name": "rad_pos", "lean": '
        '"theorem rad_pos (n : \u2115) (h : 0 < n) : 0 < Abc.rad n := by ...", '
        '"route": "definitions", "rationale": "short reason"}]}\n\n'
        "Rules:\n"
        "- Each `lean` value must be one complete `theorem <name> ... := by ...` "
        "or `lemma <name> ... := by ...` declaration.\n"
        "- No imports, namespace, section, end, set_option, sorry, admit, axiom, "
        "constant, unsafe, native_decide, #eval, or metaprogramming.\n"
        "- Use only Abc.Statement definitions and Mathlib.\n"
        "- Prefer small lemmas you can complete. If a proof is uncertain, "
        "propose a smaller true lemma.\n"
        "- Do not claim abc is solved. Do not state `Abc.Statement` as proved.\n"
        "- Do not invent `Nat.rad_*` lemmas. Use the facts listed above.\n"
        "- When using a suggested lemma, keep its statement and hypotheses "
        "exactly as given.\n"
        f"- Return at most {max(1, int(max_proposals))} proposals.\n"
        "- `route` must be one of: " + ", ".join(route_names(routes)) + "."
    )
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user},
    ]
