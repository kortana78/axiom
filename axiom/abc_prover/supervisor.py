"""Supervisor for a persistent fleet of abc proof-attempt workers.

The supervisor starts N worker processes, restarts them if they exit, merges
their ledgers into ``results/abc_prover/ledger.json``, and writes a heartbeat
to ``results/abc_prover/supervisor.json``.  It is designed to run under
systemd with ``Restart=always`` on an Oracle Always Free VPS.

It never writes ``lean/Abc/Proof.lean`` or the abc alarm status.  The fleet's
verdict is always ``NO_PROOF`` and its abc line is always ``OPEN``; only the
Lean alarm can change that.
"""
from __future__ import annotations

import argparse
import calendar
import json
import os
import signal
import subprocess
import sys
import threading
import time
from typing import Dict, List, Optional

from . import (
    LEDGER_PATH,
    NO_PROOF,
    QUOTA_DIR,
    ROUTES_PATH,
    STATUS_PATH,
    SUPERVISOR_PATH,
    TARGET_ATTEMPT_PATH,
    USAGE_PATH,
    WORKERS_DIR,
)
from .ledger import save_json, utc_now
from .merge import counts, merge_all
from .worker import worker_paths


def _read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _age_seconds(stamp: str) -> Optional[float]:
    try:
        then = calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None
    return max(0.0, time.time() - then)


class Supervisor:
    def __init__(self, workers: int = 2, mathlib: Optional[str] = None,
                 root: str = ".", sleep: float = 20.0,
                 time_budget: float = 900.0, max_proposals: int = 2,
                 max_requests: int = 1, workers_dir: str = WORKERS_DIR,
                 usage: str = USAGE_PATH, quota: str = QUOTA_DIR,
                 status_path: str = SUPERVISOR_PATH,
                 ledger_path: str = LEDGER_PATH,
                 prover_status_path: str = STATUS_PATH,
                 routes_path: str = ROUTES_PATH,
                 target_path: str = TARGET_ATTEMPT_PATH,
                 merge_interval: float = 30.0,
                 restart_delay: float = 10.0):
        self.workers = max(1, int(workers))
        self.mathlib = mathlib
        self.root = os.path.abspath(root)
        self.sleep = max(1.0, float(sleep))
        self.time_budget = max(30.0, float(time_budget))
        self.max_proposals = max(1, int(max_proposals))
        self.max_requests = max(1, int(max_requests))
        self.workers_dir = workers_dir
        self.usage = usage
        self.quota = quota
        self.status_path = status_path
        self.ledger_path = ledger_path
        self.prover_status_path = prover_status_path
        self.routes_path = routes_path
        self.target_path = target_path
        self.merge_interval = max(5.0, float(merge_interval))
        self.restart_delay = max(1.0, float(restart_delay))
        self.stop = threading.Event()
        self.started_utc = utc_now()
        self.children: Dict[str, dict] = {}
        self.restarts: Dict[str, int] = {}
        self._last_merge = 0.0

    def _ids(self) -> List[str]:
        return [f"w{i}" for i in range(1, self.workers + 1)]

    def _cmd(self, worker_id: str) -> List[str]:
        cmd = [
            sys.executable, "-m", "axiom.abc_prover.worker",
            "--id", worker_id,
            "--sleep", str(self.sleep),
            "--time", str(self.time_budget),
            "--max-proposals", str(self.max_proposals),
            "--max-requests", str(self.max_requests),
            "--workers-dir", self.workers_dir,
            "--usage", self.usage,
            "--quota", self.quota,
            "--routes", ROUTES_PATH,
        ]
        if self.mathlib:
            cmd += ["--mathlib", self.mathlib]
        return cmd

    def _spawn(self, worker_id: str) -> None:
        paths = worker_paths(worker_id, self.workers_dir)
        os.makedirs(paths["dir"], exist_ok=True)
        log = open(paths["log"], "a", encoding="utf-8", buffering=1)
        try:
            proc = subprocess.Popen(
                self._cmd(worker_id), cwd=self.root, stdout=log,
                stderr=subprocess.STDOUT, env=os.environ.copy())
        except Exception:
            log.close()
            raise
        self.children[worker_id] = {
            "proc": proc,
            "log": log,
            "started_utc": utc_now(),
        }
        self.restarts.setdefault(worker_id, 0)
        print(f"[abc-supervisor] started {worker_id} pid={proc.pid}", flush=True)

    def _reap_and_restart(self) -> None:
        for worker_id in self._ids():
            rec = self.children.get(worker_id)
            if rec is None:
                self._spawn(worker_id)
                continue
            code = rec["proc"].poll()
            if code is None:
                continue
            try:
                rec["log"].close()
            except OSError:
                pass
            self.restarts[worker_id] = self.restarts.get(worker_id, 0) + 1
            print(f"[abc-supervisor] {worker_id} exited code={code}; "
                  f"restart #{self.restarts[worker_id]}", flush=True)
            if self.stop.is_set():
                continue
            self.stop.wait(self.restart_delay)
            if not self.stop.is_set():
                self._spawn(worker_id)

    def _worker_status(self, worker_id: str) -> dict:
        paths = worker_paths(worker_id, self.workers_dir)
        hb = _read_json(paths["heartbeat"])
        rec = self.children.get(worker_id) or {}
        proc = rec.get("proc")
        return {
            "id": worker_id,
            "pid": getattr(proc, "pid", None),
            "running": bool(proc is not None and proc.poll() is None),
            "restarts": int(self.restarts.get(worker_id, 0)),
            "heartbeat_utc": hb.get("updated_utc", ""),
            "heartbeat_age_s": _age_seconds(str(hb.get("updated_utc", ""))),
            "iterations": int(hb.get("iterations", 0) or 0),
            "requests": int((hb.get("last_report") or {}).get("requests", 0) or 0),
            "checked_lemmas": int(hb.get("checked_lemmas", 0) or 0),
            "rejected_lemmas": int(hb.get("rejected_lemmas", 0) or 0),
            "error": str(hb.get("error", ""))[:300],
        }

    def status(self) -> dict:
        error = ""
        try:
            merged = merge_all(
                ledger_path=self.ledger_path,
                status_path=self.prover_status_path,
                routes_path=self.routes_path, target_path=self.target_path,
                workers_dir=self.workers_dir)
        except Exception as exc:
            error = f"merge failed: {exc}"
            c = counts(self.ledger_path)
            merged = {
                "checked_lemmas": c["checked"],
                "rejected_lemmas": c["rejected"],
                "target_attempts": 0,
            }
        workers = [self._worker_status(wid) for wid in self._ids()]
        data = {
            "abc": "OPEN",
            "verdict": NO_PROOF,
            "supervisor_pid": os.getpid(),
            "host": os.environ.get("HOSTNAME", ""),
            "started_utc": self.started_utc,
            "updated_utc": utc_now(),
            "workers_requested": self.workers,
            "workers_running": sum(1 for w in workers if w["running"]),
            "workers": workers,
            "checked_lemmas": int(merged.get("checked_lemmas", 0) or 0),
            "rejected_lemmas": int(merged.get("rejected_lemmas", 0) or 0),
            "target_attempts": int(merged.get("target_attempts", 0) or 0),
            "merge_error": error,
            "note": ("Persistent auxiliary-lemma fleet. A checked lemma is not "
                     "a proof of Abc.Statement. The abc alarm is the only judge."),
        }
        save_json(self.status_path, data)
        self._last_merge = time.time()
        return data

    def run(self) -> int:
        print(f"[abc-supervisor] starting {self.workers} workers in {self.root}",
              flush=True)
        for worker_id in self._ids():
            self._spawn(worker_id)
        self.status()
        try:
            while not self.stop.is_set():
                self._reap_and_restart()
                if time.time() - self._last_merge >= self.merge_interval:
                    try:
                        self.status()
                    except Exception as exc:
                        print(f"[abc-supervisor] status error: {exc}", flush=True)
                self.stop.wait(2.0)
        finally:
            print("[abc-supervisor] stopping workers", flush=True)
            for rec in self.children.values():
                proc = rec.get("proc")
                if proc is not None and proc.poll() is None:
                    proc.terminate()
            deadline = time.time() + 20.0
            for rec in self.children.values():
                proc = rec.get("proc")
                if proc is None:
                    continue
                try:
                    proc.wait(timeout=max(0.1, deadline - time.time()))
                except subprocess.TimeoutExpired:
                    proc.kill()
                try:
                    rec["log"].close()
                except OSError:
                    pass
            try:
                self.status()
            except Exception as exc:
                print(f"[abc-supervisor] final status error: {exc}", flush=True)
        return 0


def health(status_path: str = SUPERVISOR_PATH, max_age: float = 300.0) -> tuple[bool, str]:
    data = _read_json(status_path)
    if not data:
        return False, f"{status_path} is missing or unreadable"
    age = _age_seconds(str(data.get("updated_utc", "")))
    if age is None:
        return False, "supervisor heartbeat has no valid timestamp"
    if age > max_age:
        return False, f"supervisor heartbeat is stale ({age:.0f}s old)"
    if data.get("abc") != "OPEN" or data.get("verdict") != NO_PROOF:
        return False, "prover status is not the expected OPEN/NO_PROOF"
    if int(data.get("workers_running", 0)) <= 0:
        return False, "no workers are running"
    return True, (f"healthy: {data.get('workers_running')} workers, "
                  f"heartbeat {age:.0f}s old, abc=OPEN")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="24/7 abc proof-attempt supervisor")
    ap.add_argument("--workers", type=int,
                    default=int(os.environ.get("ABC_PROVER_WORKERS", "2")))
    ap.add_argument("--mathlib", default=os.environ.get("AXIOM_MATHLIB"))
    ap.add_argument("--root", default=".")
    ap.add_argument("--sleep", type=float, default=20.0)
    ap.add_argument("--time", type=float, default=900.0)
    ap.add_argument("--max-proposals", type=int, default=2)
    ap.add_argument("--max-requests", type=int, default=1)
    ap.add_argument("--workers-dir", default=WORKERS_DIR)
    ap.add_argument("--usage", default=USAGE_PATH)
    ap.add_argument("--quota", default=QUOTA_DIR)
    ap.add_argument("--status", default=SUPERVISOR_PATH)
    ap.add_argument("--merge-interval", type=float, default=30.0)
    ap.add_argument("--restart-delay", type=float, default=10.0)
    ap.add_argument("--max-hours", type=float, default=0.0,
                    help="0 means run until stopped")
    ap.add_argument("--health", action="store_true",
                    help="check the supervisor heartbeat and exit")
    ap.add_argument("--max-age", type=float, default=300.0)
    a = ap.parse_args(argv)

    if a.health:
        ok, message = health(a.status, a.max_age)
        print(("[abc-supervisor] " + message), flush=True)
        return 0 if ok else 1

    if a.workers < 1:
        print("[abc-supervisor] --workers must be at least 1", file=sys.stderr)
        return 2
    try:
        cpus = os.cpu_count() or 1
    except Exception:
        cpus = 1
    if a.workers > cpus * 2:
        print(f"[abc-supervisor] warning: {a.workers} workers on {cpus} CPUs; "
              "Lean checks will thrash", file=sys.stderr, flush=True)

    sup = Supervisor(
        workers=a.workers, mathlib=a.mathlib, root=a.root, sleep=a.sleep,
        time_budget=a.time, max_proposals=a.max_proposals,
        max_requests=a.max_requests, workers_dir=a.workers_dir,
        usage=a.usage, quota=a.quota, status_path=a.status,
        merge_interval=a.merge_interval, restart_delay=a.restart_delay)

    def handler(_signum, _frame):
        sup.stop.set()

    for name in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, name, None)
        if sig is not None:
            try:
                signal.signal(sig, handler)
            except (OSError, ValueError):
                pass

    if a.max_hours > 0:
        timer = threading.Timer(max(1.0, a.max_hours * 3600.0), sup.stop.set)
        timer.daemon = True
        timer.start()
    return sup.run()


if __name__ == "__main__":
    raise SystemExit(main())
