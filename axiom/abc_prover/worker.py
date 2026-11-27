"""One persistent abc proof-attempt worker.

A worker owns one Lean harness and one local ledger.  It asks the shared
provider pool for a request, runs one bounded LLM -> Lean round, merges its
attempts into the fleet ledger, and writes a heartbeat.  It loops until
SIGTERM/SIGINT (or ``--rounds`` is reached).

Run it under :mod:`axiom.abc_prover.supervisor`; running one by hand is fine
for debugging.  It never writes ``lean/Abc/Proof.lean`` or the alarm status.
"""
from __future__ import annotations

import argparse
import os
import random
import re
import signal
import socket
import threading
import time
import traceback
from typing import Dict, Optional

from ..abc_proof import STATEMENT_PATH
from ..llm.config import load_providers
from . import (
    LEDGER_PATH,
    NO_PROOF,
    QUOTA_DIR,
    ROUTES_PATH,
    STATUS_PATH,
    TARGET_ATTEMPT_PATH,
    USAGE_PATH,
    WORKERS_DIR,
)
from .lean import LeanHarness, LeanUnavailable
from .ledger import save_json, utc_now
from .loop import run as run_loop
from .merge import merge_all
from .pool import ProviderPool, QuotaStore, SharedUsage

_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def safe_id(worker_id: str) -> str:
    return _SAFE.sub("_", worker_id or "worker")[:64] or "worker"


def worker_paths(worker_id: str, workers_dir: str = WORKERS_DIR) -> Dict[str, str]:
    directory = os.path.join(workers_dir, safe_id(worker_id))
    return {
        "dir": directory,
        "ledger": os.path.join(directory, "ledger.json"),
        "status": os.path.join(directory, "status.json"),
        "target": os.path.join(directory, "target_attempt.lean"),
        "heartbeat": os.path.join(directory, "heartbeat.json"),
        "log": os.path.join(directory, "worker.log"),
    }


def heartbeat(worker_id: str, pool: Optional[ProviderPool],
              report: Optional[dict], status: Optional[dict],
              started_utc: str, iterations: int,
              error: str = "", path: Optional[str] = None) -> dict:
    paths = worker_paths(worker_id)
    providers = []
    if pool is not None:
        try:
            providers = pool.public()
        except Exception as exc:  # accounting must not kill the worker
            providers = [{"error": str(exc)[:200]}]
    data = {
        "worker": safe_id(worker_id),
        "pid": os.getpid(),
        "host": socket.gethostname(),
        "started_utc": started_utc,
        "updated_utc": utc_now(),
        "iterations": int(iterations),
        "abc": "OPEN",
        "verdict": NO_PROOF,
        "checked_lemmas": int((status or {}).get("checked_lemmas", 0) or 0),
        "rejected_lemmas": int((status or {}).get("rejected_lemmas", 0) or 0),
        "target_attempts": int((status or {}).get("target_attempts", 0) or 0),
        "providers": providers,
        "last_report": {
            key: (report or {}).get(key)
            for key in ("enabled", "requests", "new_attempts", "checked",
                        "rejected", "skipped_duplicates", "elapsed_s")
        },
        "error": str(error)[:1000],
        "note": ("A checked lemma is not a proof of Abc.Statement. "
                 "The abc alarm remains the only judge."),
    }
    save_json(path or paths["heartbeat"], data)
    return data


def run_once(worker_id: str, pool: ProviderPool, checker,
             *, rounds: int = 1, max_proposals: int = 2,
             max_requests: int = 1, time_budget: float = 900.0,
             transport=None, ledger_path: Optional[str] = None,
             status_path: Optional[str] = None,
             target_path: Optional[str] = None,
             usage_path: str = USAGE_PATH,
             context_ledger_path: str = LEDGER_PATH,
             routes_path: str = ROUTES_PATH,
             global_ledger_path: str = LEDGER_PATH,
             global_status_path: str = STATUS_PATH,
             global_target_path: str = TARGET_ATTEMPT_PATH,
             workers_dir: str = WORKERS_DIR) -> tuple[dict, dict]:
    """Run one bounded batch, merge, and write a heartbeat."""
    paths = worker_paths(worker_id, workers_dir)
    os.makedirs(paths["dir"], exist_ok=True)
    report = run_loop(
        rounds=rounds, max_proposals=max_proposals,
        time_budget=time_budget, ledger_path=ledger_path or paths["ledger"],
        status_path=status_path or paths["status"],
        routes_path=routes_path, target_path=target_path or paths["target"],
        usage_path=usage_path, checker=checker, transport=transport,
        max_requests=max_requests, pool=pool,
        context_ledger_path=context_ledger_path)
    status = merge_all(ledger_path=global_ledger_path,
                       status_path=global_status_path,
                       routes_path=routes_path,
                       target_path=global_target_path,
                       workers_dir=workers_dir)
    return report, status


def _install_stop_handlers(stop: threading.Event) -> None:
    def handler(_signum, _frame):
        stop.set()

    for name in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, name, None)
        if sig is not None:
            try:
                signal.signal(sig, handler)
            except (OSError, ValueError):
                pass


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="persistent abc proof-attempt worker")
    ap.add_argument("--id", default=f"{socket.gethostname()}-{os.getpid()}")
    ap.add_argument("--mathlib", default=os.environ.get("AXIOM_MATHLIB"))
    ap.add_argument("--rounds", type=int, default=0,
                    help="0 means loop forever")
    ap.add_argument("--sleep", type=float, default=20.0)
    ap.add_argument("--time", type=float, default=900.0,
                    help="time budget per bounded batch")
    ap.add_argument("--max-proposals", type=int, default=2)
    ap.add_argument("--max-requests", type=int, default=1)
    ap.add_argument("--lean-timeout", type=float, default=300.0)
    ap.add_argument("--usage", default=USAGE_PATH)
    ap.add_argument("--quota", default=QUOTA_DIR)
    ap.add_argument("--workers-dir", default=WORKERS_DIR)
    ap.add_argument("--ledger", default=None)
    ap.add_argument("--status", default=None)
    ap.add_argument("--target", default=None)
    ap.add_argument("--context-ledger", default=LEDGER_PATH)
    ap.add_argument("--routes", default=ROUTES_PATH)
    a = ap.parse_args(argv)

    started = utc_now()
    stop = threading.Event()
    _install_stop_handlers(stop)
    paths = worker_paths(a.id, a.workers_dir)
    os.makedirs(paths["dir"], exist_ok=True)

    pool = ProviderPool(
        providers=load_providers(),
        usage=SharedUsage(a.usage), quota=QuotaStore(a.quota))
    if not pool.providers:
        print(f"[abc-worker:{a.id}] no LLM providers configured; idle", flush=True)
    else:
        print(f"[abc-worker:{a.id}] providers: "
              + ", ".join(p.name for p in pool.providers), flush=True)

    if not a.mathlib or not os.path.isdir(a.mathlib):
        message = "Mathlib checkout not found; set --mathlib or AXIOM_MATHLIB"
        heartbeat(a.id, pool, None, None, started, 0, error=message,
                  path=paths["heartbeat"])
        print(f"[abc-worker:{a.id}] {message}", flush=True)
        return 2

    iterations = 0
    backoff = 5.0
    try:
        with LeanHarness(STATEMENT_PATH, a.mathlib,
                         timeout=max(30.0, a.lean_timeout)) as harness:
            while not stop.is_set():
                if a.rounds and iterations >= a.rounds:
                    break
                try:
                    report, status = run_once(
                        a.id, pool, harness.check, rounds=1,
                        max_proposals=a.max_proposals,
                        max_requests=a.max_requests,
                        time_budget=a.time,
                        ledger_path=a.ledger, status_path=a.status,
                        target_path=a.target, usage_path=a.usage,
                        context_ledger_path=a.context_ledger,
                        routes_path=a.routes,
                        global_ledger_path=LEDGER_PATH,
                        global_status_path=STATUS_PATH,
                        global_target_path=TARGET_ATTEMPT_PATH,
                        workers_dir=a.workers_dir)
                    iterations += 1
                    backoff = 5.0
                    heartbeat(a.id, pool, report, status, started, iterations,
                              path=paths["heartbeat"])
                    print(f"[abc-worker:{a.id}] batch {iterations}: "
                          f"requests={report.get('requests')} "
                          f"checked={report.get('checked')} "
                          f"rejected={report.get('rejected')} "
                          f"abc=OPEN", flush=True)
                except LeanUnavailable as exc:
                    heartbeat(a.id, pool, None, None, started, iterations,
                              error=str(exc), path=paths["heartbeat"])
                    print(f"[abc-worker:{a.id}] Lean unavailable: {exc}",
                          flush=True)
                    return 2
                except Exception as exc:
                    detail = traceback.format_exc()
                    heartbeat(a.id, pool, None, None, started, iterations,
                              error=detail, path=paths["heartbeat"])
                    print(f"[abc-worker:{a.id}] error: {exc}\n{detail}",
                          flush=True)
                    stop.wait(min(300.0, backoff))
                    backoff = min(300.0, backoff * 2)
                    continue
                if stop.wait(max(0.0, a.sleep) + random.uniform(0, 5)):
                    break
    finally:
        heartbeat(a.id, pool, None, None, started, iterations,
                  error="stopped", path=paths["heartbeat"])
    print(f"[abc-worker:{a.id}] stopped after {iterations} batches; abc=OPEN",
          flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
