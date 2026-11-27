"""Validate and normalize LLM proof proposals before Lean sees them.

The model returns JSON objects with a name, a complete Lean declaration, a
route tag, and a rationale.  This module rejects anything that could smuggle in
an axiom, a ``sorry``, a different import, or metaprogramming.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Dict, List, Tuple

from ..abc_proof.check import strip_lean_comments_and_strings
from ..llm.client import LLMError, parse_json_text
from . import MAX_LEAN_CHARS

NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_']*$")

#: Tokens that are never allowed in a proposal.  The source is stripped of
#: comments and strings first, so prose may mention them safely.
_BANNED = (
    ("sorryAx", r"\bsorryAx\b"),
    ("sorry", r"\bsorry\b"),
    ("admit", r"\badmit\b"),
    ("axiom", r"\baxiom\b"),
    ("constant", r"\bconstant\b"),
    ("unsafe", r"\bunsafe\b"),
    ("partial", r"\bpartial\b"),
    ("opaque", r"\bopaque\b"),
    ("extern", r"\bextern\b"),
    ("implemented_by", r"\bimplemented_by\b"),
    ("native_decide", r"\bnative_decide\b"),
    ("import", r"\bimport\b"),
    ("namespace", r"\bnamespace\b"),
    ("section", r"\bsection\b"),
    ("end", r"\bend\b"),
    ("set_option", r"\bset_option\b"),
    ("#eval", r"#eval\b"),
    ("#exit", r"#exit\b"),
    ("run_cmd", r"\brun_cmd\b"),
    ("elab", r"\belab\b"),
    ("macro", r"\bmacro\b"),
    ("syntax", r"\bsyntax\b"),
    ("notation", r"\bnotation\b"),
    ("private", r"\bprivate\b"),
    ("protected", r"\bprotected\b"),
)

_DECL_RE = re.compile(r"(?m)^\s*(?:theorem|lemma)\s+([A-Za-z_][A-Za-z0-9_']*)\b")
_TARGET_TYPE_RE = re.compile(r"(?ms)^\s*(?:theorem|lemma)\s+\w+\b(.*?):=")


def sanitize(lean: str, name: str) -> Dict[str, object]:
    """Return ``ok`` plus human-readable reasons for a rejection."""
    reasons: List[str] = []
    if not NAME_RE.match(name or ""):
        reasons.append("name must be a simple Lean identifier")
    if len(lean) > MAX_LEAN_CHARS:
        reasons.append(f"lemma exceeds {MAX_LEAN_CHARS} characters")
    clean = strip_lean_comments_and_strings(lean)
    for label, pattern in _BANNED:
        if re.search(pattern, clean):
            reasons.append(f"lemma contains forbidden token `{label}`")
    decl = re.compile(rf"(?m)^\s*(?:theorem|lemma)\s+{re.escape(name)}\b")
    if not decl.search(clean):
        reasons.append(f"lemma must declare `theorem {name}` or `lemma {name}`")
    return {"ok": not reasons, "reasons": reasons, "clean": clean}


def is_target_like(clean: str) -> bool:
    """True when the declared type mentions ``Abc.Statement``."""
    m = _TARGET_TYPE_RE.search(clean)
    if not m:
        return False
    return bool(re.search(r"\b(?:Abc\.)?Statement\b", m.group(1)))


def proposal_id(lean: str) -> str:
    return "sha256:" + hashlib.sha256(lean.strip().encode("utf-8")).hexdigest()[:16]


def signature(lean: str, limit: int = 400) -> str:
    m = re.search(r"(?ms)^\s*(?:theorem|lemma)\s+.*?:=", lean)
    text = m.group(0)[:-2] if m else lean
    return " ".join(text.split())[:limit]


def parse_proposals(text: str, allowed_routes: List[str],
                    max_proposals: int) -> Tuple[List[dict], List[str]]:
    """Parse a model response into at most ``max_proposals`` safe proposals."""
    try:
        payload = parse_json_text(text)
    except LLMError as exc:
        return [], [str(exc)]
    if isinstance(payload, dict):
        items = payload.get("proposals", payload.get("lemmas", []))
    elif isinstance(payload, list):
        items = payload
    else:
        items = []
    if not isinstance(items, list):
        return [], ["`proposals` must be a list"]

    allowed = set(allowed_routes)
    out: List[dict] = []
    bad: List[str] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict):
            bad.append(f"proposal {i}: not a JSON object")
            continue
        name = str(item.get("name", "")).strip()
        lean = str(item.get("lean", "")).strip()
        route = str(item.get("route", "definitions")).strip()
        rationale = str(item.get("rationale", "")).strip()
        report = sanitize(lean, name)
        if not report["ok"]:
            bad.append(f"{name or i}: " + "; ".join(report["reasons"]))
            continue
        if route not in allowed:
            bad.append(f"{name}: unknown route {route!r}")
            continue
        if len(out) >= max(1, int(max_proposals)):
            bad.append(f"{name}: over the per-round proposal limit")
            continue
        out.append({
            "name": name,
            "lean": lean,
            "route": route,
            "rationale": rationale[:500],
            "target_like": is_target_like(str(report["clean"])),
            "id": proposal_id(lean),
        })
    return out, bad


def proposal_json(proposals: List[dict]) -> str:
    return json.dumps({"proposals": proposals}, indent=2, ensure_ascii=False)
