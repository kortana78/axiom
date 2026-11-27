"""Persistent ledger and honest status for the abc proof-attempt loop."""
from __future__ import annotations

import json
import os
import time
from typing import Dict, List

from . import CHECKED, LEDGER_PATH, NO_PROOF, REJECTED, STATUS_PATH
from .routes import open_gaps

COMMENT = ("Lean-checked auxiliary lemmas only. CHECKED is not a proof of "
           "Abc.Statement. The abc alarm remains the only judge.")


def utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def load_ledger(path: str = LEDGER_PATH) -> Dict[str, object]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("comment", COMMENT)
    data.setdefault("updated_utc", "")
    data.setdefault("attempts", [])
    if not isinstance(data["attempts"], list):
        data["attempts"] = []
    data.setdefault("stats", {})
    return data


def save_json(path: str, data: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


def write_target_attempt(path: str, attempt: Dict[str, object]) -> None:
    """Save a checked target-like lemma for human review, never promotion."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "-- Lean-checked target-like lemma proposed by axiom.abc_prover.\n"
            "-- This is NOT lean/Abc/Proof.lean and has NOT been promoted.\n"
            "-- Review it; the abc alarm must verify any proof independently.\n"
            "\n"
            + str(attempt.get("lean", "")).rstrip() + "\n")


def append_attempt(ledger: Dict[str, object], attempt: Dict[str, object],
                   keep: int = 200) -> None:
    attempts = [a for a in (ledger.get("attempts") or [])
                if isinstance(a, dict)]
    attempts.append(attempt)
    ledger["attempts"] = attempts[-max(1, int(keep)):]


def stats(ledger: Dict[str, object]) -> Dict[str, object]:
    attempts = [a for a in (ledger.get("attempts") or [])
                if isinstance(a, dict)]
    routes: Dict[str, Dict[str, int]] = {}
    for a in attempts:
        route = str(a.get("route", "other"))
        bucket = routes.setdefault(route, {"checked": 0, "rejected": 0})
        if a.get("status") == CHECKED:
            bucket["checked"] += 1
        elif a.get("status") == REJECTED:
            bucket["rejected"] += 1
    return {
        "total": len(attempts),
        "checked": sum(1 for a in attempts if a.get("status") == CHECKED),
        "rejected": sum(1 for a in attempts if a.get("status") == REJECTED),
        "target_attempts": sum(
            1 for a in attempts
            if a.get("target_like") and a.get("status") == CHECKED),
        "routes": routes,
    }


def build_status(ledger: Dict[str, object],
                 routes: Dict[str, object]) -> Dict[str, object]:
    st = stats(ledger)
    return {
        "abc": "OPEN",
        "verdict": NO_PROOF,
        "checked_lemmas": st["checked"],
        "rejected_lemmas": st["rejected"],
        "target_attempts": st["target_attempts"],
        "routes": st["routes"],
        "open_gaps": open_gaps(routes),
        "updated_utc": utc_now(),
        "note": COMMENT,
    }


def save_ledger(ledger: Dict[str, object],
                path: str = LEDGER_PATH) -> Dict[str, object]:
    ledger["comment"] = COMMENT
    ledger["updated_utc"] = utc_now()
    ledger["stats"] = stats(ledger)
    save_json(path, ledger)
    return ledger


def save_status(status: Dict[str, object],
                path: str = STATUS_PATH) -> None:
    save_json(path, status)
