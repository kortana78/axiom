"""Tiny public status beacon for the 24/7 abc prover fleet.

This is monitoring only. The workers run on the VPS; Render has neither the
RAM nor the CPU for Lean + Mathlib. The beacon reads the supervisor heartbeat
that the VPS publishes to the public repository and reports its age.

Deploy on Render as a free Python web service. Point a free uptime monitor at
``/healthz`` every few minutes. If the heartbeat goes stale, the monitor tells
you the fleet stopped; nothing here restarts it.
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

STATUS_URL = os.environ.get(
    "AXIOM_STATUS_URL",
    "https://raw.githubusercontent.com/kortana78/axiom/main/"
    "results/abc_prover/supervisor.json")
MAX_AGE = float(os.environ.get("AXIOM_MAX_AGE", "21600"))
PORT = int(os.environ.get("PORT", "8000"))
CACHE_SECONDS = 60.0

_cache = {"at": 0.0, "data": None, "error": ""}


def _fetch() -> tuple[dict | None, str]:
    now = time.time()
    if _cache["data"] is not None and now - _cache["at"] < CACHE_SECONDS:
        return _cache["data"], _cache["error"]
    data = None
    error = ""
    try:
        with urllib.request.urlopen(STATUS_URL, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        if not isinstance(data, dict):
            data = None
            error = "heartbeat is not a JSON object"
    except Exception as exc:
        error = str(exc)[:300]
    _cache.update(at=now, data=data, error=error)
    return data, error


def _age(stamp: str) -> float | None:
    try:
        import calendar

        then = calendar.timegm(time.strptime(stamp, "%Y-%m-%dT%H:%M:%SZ"))
    except (TypeError, ValueError):
        return None
    return max(0.0, time.time() - then)


def health() -> tuple[int, dict]:
    data, error = _fetch()
    if data is None:
        return 503, {"ok": False, "error": error or "no heartbeat data",
                     "status_url": STATUS_URL}
    age = _age(str(data.get("updated_utc", "")))
    workers = int(data.get("workers_running", 0) or 0)
    ok = (age is not None and age <= MAX_AGE and workers > 0
          and data.get("abc") == "OPEN"
          and data.get("verdict") == "NO_PROOF")
    return (200 if ok else 503), {
        "ok": ok,
        "status_url": STATUS_URL,
        "heartbeat_utc": data.get("updated_utc"),
        "age_s": None if age is None else round(age, 1),
        "workers_running": workers,
        "checked_lemmas": data.get("checked_lemmas", 0),
        "rejected_lemmas": data.get("rejected_lemmas", 0),
        "abc": data.get("abc"),
        "note": "Auxiliary lemmas only; a checked lemma is not a proof of abc.",
    }


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        path = urlsplit(self.path).path
        if path == "/healthz":
            code, payload = health()
            self._send(code, payload)
            return
        self._send(200, {
            "service": "axiom-abc-pulse",
            "role": "monitoring only; workers run on the VPS",
            "healthz": "/healthz",
            "status_url": STATUS_URL,
        })

    def log_message(self, fmt: str, *args) -> None:
        print(f"[pulse] {fmt % args}", flush=True)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"[pulse] listening on 0.0.0.0:{PORT}; watching {STATUS_URL}",
          flush=True)
    server.serve_forever()
