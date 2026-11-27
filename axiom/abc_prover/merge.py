"""Merge per-worker abc proof-attempt ledgers into the public ledger.

Workers write only to ``results/abc_prover/workers/<id>/ledger.json``.  The
supervisor (and each worker after a run) merges those files into
``results/abc_prover/ledger.json`` under a cross-process lock.  Duplicate
proposal ids are collapsed, with a Lean-checked copy preferred over a rejected
one.

This module never writes ``lean/Abc/Proof.lean`` and never writes the alarm
status.  A target-like checked lemma is copied only to
``results/abc_prover/target_attempt.lean`` for human review.
"""
from __future__ import annotations

import glob
import os
from typing import Dict, List

from . import (
    CHECKED,
    LEDGER_PATH,
    REJECTED,
    ROUTES_PATH,
    STATUS_PATH,
    TARGET_ATTEMPT_PATH,
    WORKERS_DIR,
)
from .ledger import (
    build_status,
    load_ledger,
    save_ledger,
    save_status,
    utc_now,
    write_target_attempt,
)
from .lock import FileLock
from .routes import load_routes


def worker_ledgers(workers_dir: str = WORKERS_DIR) -> List[str]:
    return sorted(glob.glob(os.path.join(workers_dir, "*", "ledger.json")))


def _key(attempt: dict) -> str:
    value = attempt.get("id") or attempt.get("signature") or ""
    return str(value)


def collect_attempts(paths: List[str]) -> List[dict]:
    """Read ledgers, collapse duplicate ids, and sort by check time."""
    by_id: Dict[str, dict] = {}
    for path in paths:
        if not path or not os.path.exists(path):
            continue
        ledger = load_ledger(path)
        for attempt in ledger.get("attempts") or []:
            if not isinstance(attempt, dict):
                continue
            key = _key(attempt)
            if not key:
                continue
            previous = by_id.get(key)
            if previous is None:
                by_id[key] = attempt
                continue
            previous_checked = previous.get("status") == CHECKED
            current_checked = attempt.get("status") == CHECKED
            if current_checked and not previous_checked:
                by_id[key] = attempt
            elif current_checked == previous_checked:
                if str(attempt.get("checked_at", "")) >= str(
                        previous.get("checked_at", "")):
                    by_id[key] = attempt
    return sorted(by_id.values(),
                  key=lambda a: (str(a.get("checked_at", "")), _key(a)))


def merge_all(ledger_path: str = LEDGER_PATH,
              status_path: str = STATUS_PATH,
              routes_path: str = ROUTES_PATH,
              target_path: str = TARGET_ATTEMPT_PATH,
              workers_dir: str = WORKERS_DIR,
              keep: int = 500) -> Dict[str, object]:
    """Merge the public ledger plus every worker ledger; return the status."""
    paths = [ledger_path] + worker_ledgers(workers_dir)
    with FileLock(ledger_path + ".lock"):
        attempts = collect_attempts(paths)[-max(1, int(keep)):]
        ledger = {
            "comment": (
                "Lean-checked auxiliary lemmas only. CHECKED is not a proof of "
                "Abc.Statement. The abc alarm remains the only judge."),
            "updated_utc": utc_now(),
            "attempts": attempts,
        }
        save_ledger(ledger, ledger_path)
        status = build_status(ledger, load_routes(routes_path))
        save_status(status, status_path)

        target = None
        for attempt in attempts:
            if (attempt.get("status") == CHECKED
                    and attempt.get("target_like")):
                target = attempt
        if target is not None:
            write_target_attempt(target_path, target)
        return status


def counts(ledger_path: str = LEDGER_PATH) -> Dict[str, int]:
    ledger = load_ledger(ledger_path)
    attempts = [a for a in (ledger.get("attempts") or [])
                if isinstance(a, dict)]
    return {
        "checked": sum(1 for a in attempts if a.get("status") == CHECKED),
        "rejected": sum(1 for a in attempts if a.get("status") == REJECTED),
        "total": len(attempts),
    }
