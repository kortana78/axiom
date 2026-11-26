"""Persistent request/token accounting for LLM providers.

The ledger lives at ``results/llm_usage.json``.  It records requests,
prompt/completion tokens, failures, and the last error per provider.  It never
records API keys or prompt bodies.  Daily counters reset when the UTC date
changes.
"""
from __future__ import annotations

import json
import os
import time
from typing import Optional


def _today() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def load_usage(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    data.setdefault("date", _today())
    data.setdefault("providers", {})
    data.setdefault("runs", [])
    if data["date"] != _today():
        data["date"] = _today()
        data["providers"] = {}
    return data


def save_usage(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


class UsageLedger:
    def __init__(self, path: str):
        self.path = path
        self.data = load_usage(path)

    def _provider(self, name: str) -> dict:
        return self.data["providers"].setdefault(name, {
            "requests": 0, "prompt_tokens": 0, "completion_tokens": 0,
            "failures": 0, "last_error": "",
        })

    def requests_today(self, name: str) -> int:
        return int(self._provider(name).get("requests", 0))

    def can_request(self, name: str, limit_per_day: int) -> bool:
        return self.requests_today(name) < int(limit_per_day)

    def record(self, name: str, requests: int = 1, prompt_tokens: int = 0,
               completion_tokens: int = 0, ok: bool = True,
               error: str = "", problem: str = "") -> None:
        p = self._provider(name)
        p["requests"] = int(p.get("requests", 0)) + max(0, int(requests))
        p["prompt_tokens"] = int(p.get("prompt_tokens", 0)) + max(0, int(prompt_tokens))
        p["completion_tokens"] = int(p.get("completion_tokens", 0)) + max(0, int(completion_tokens))
        if not ok:
            p["failures"] = int(p.get("failures", 0)) + 1
            p["last_error"] = str(error)[:500]
        run = {
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "provider": name,
            "problem": problem,
            "requests": max(0, int(requests)),
            "prompt_tokens": max(0, int(prompt_tokens)),
            "completion_tokens": max(0, int(completion_tokens)),
            "ok": bool(ok),
        }
        self.data["runs"] = (self.data.get("runs", []) + [run])[-500:]
        self.save()

    def save(self) -> None:
        save_usage(self.path, self.data)
