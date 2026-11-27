"""Provider rotation, shared usage accounting, and daily request quotas.

The original loop used one provider.  A 24/7 fleet needs several free
OpenAI-compatible providers (Groq, OpenRouter, ...) and a hard daily cap per
provider.  This module adds three pieces:

* :class:`SharedUsage` -- a process-safe version of ``llm_usage.json``.
* :class:`QuotaStore` -- atomic per-provider, per-UTC-day reservations.
* :class:`ProviderPool` -- least-used rotation, cooldown after failures, and
  a refusal to exceed a provider's daily cap.

No API key is ever logged or written to a result file.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional

from ..llm.config import Provider, load_providers
from ..llm.usage import load_usage, save_usage
from . import QUOTA_DIR, USAGE_PATH
from .lock import FileLock

_SAFE = re.compile(r"[^A-Za-z0-9_.-]+")


def _today() -> str:
    return time.strftime("%Y-%m-%d", time.gmtime())


def _safe(name: str) -> str:
    return _SAFE.sub("_", name or "provider")[:80]


def _read_json(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _write_json(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)


class SharedUsage:
    """Read-modify-write accounting for ``results/llm_usage.json``.

    The file shape matches :class:`axiom.llm.usage.UsageLedger`, so existing
    dashboards and the CI budget see the fleet's requests.
    """

    def __init__(self, path: str = USAGE_PATH):
        self.path = path
        self.lock_path = path + ".lock"

    def _read(self) -> dict:
        return load_usage(self.path)

    def requests_today(self, name: str) -> int:
        with FileLock(self.lock_path):
            data = self._read()
            return int(data.get("providers", {}).get(name, {}).get("requests", 0))

    def snapshot(self) -> dict:
        with FileLock(self.lock_path):
            return self._read()

    def record(self, name: str, requests: int = 1, prompt_tokens: int = 0,
               completion_tokens: int = 0, ok: bool = True,
               error: str = "", problem: str = "") -> None:
        with FileLock(self.lock_path):
            data = self._read()
            providers = data.setdefault("providers", {})
            p = providers.setdefault(name, {
                "requests": 0, "prompt_tokens": 0, "completion_tokens": 0,
                "failures": 0, "last_error": "",
            })
            p["requests"] = int(p.get("requests", 0)) + max(0, int(requests))
            p["prompt_tokens"] = int(p.get("prompt_tokens", 0)) + max(
                0, int(prompt_tokens))
            p["completion_tokens"] = int(p.get("completion_tokens", 0)) + max(
                0, int(completion_tokens))
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
            data["runs"] = (data.get("runs", []) + [run])[-500:]
            save_usage(self.path, data)


class QuotaStore:
    """Atomic daily reservations, independent of the accounting ledger.

    A reservation is taken *before* the network call.  If the process dies
    mid-request the reservation is not refunded; that is deliberate, because a
    provider may still have counted the request.
    """

    def __init__(self, root: str = QUOTA_DIR,
                 today: Optional[Callable[[], str]] = None):
        self.root = root
        self._today = today or _today

    def _path(self, name: str) -> str:
        return os.path.join(self.root, f"{_safe(name)}-{self._today()}.json")

    def used(self, name: str) -> int:
        with FileLock(os.path.join(self.root, ".quota.lock")):
            return int(_read_json(self._path(name)).get("requests", 0))

    def reserve(self, name: str, limit: int) -> bool:
        """Return True and consume one unit if the provider is under ``limit``.

        A non-positive ``limit`` means unlimited.
        """
        if int(limit) <= 0:
            return True
        with FileLock(os.path.join(self.root, ".quota.lock")):
            path = self._path(name)
            data = _read_json(path)
            used = int(data.get("requests", 0))
            if used >= int(limit):
                return False
            data.update({
                "provider": name,
                "date": self._today(),
                "limit": int(limit),
                "requests": used + 1,
            })
            _write_json(path, data)
            return True

    def snapshot(self) -> List[dict]:
        out: List[dict] = []
        if not os.path.isdir(self.root):
            return out
        for name in sorted(os.listdir(self.root)):
            if not name.endswith(".json") or name.startswith("."):
                continue
            data = _read_json(os.path.join(self.root, name))
            if data:
                out.append(data)
        return out

    def prune(self, keep_days: int = 7) -> int:
        """Delete quota files older than ``keep_days``; return the count."""
        if not os.path.isdir(self.root) or keep_days <= 0:
            return 0
        cutoff = time.time() - keep_days * 86400
        removed = 0
        for name in os.listdir(self.root):
            if not name.endswith(".json"):
                continue
            path = os.path.join(self.root, name)
            try:
                if os.path.getmtime(path) < cutoff:
                    os.remove(path)
                    removed += 1
            except OSError:
                pass
        return removed


@dataclass
class Lease:
    provider: Provider
    reserved_utc: str


class ProviderPool:
    """Least-used rotation with daily quotas and failure cooldowns."""

    def __init__(self, providers: List[Provider], usage: SharedUsage,
                 quota: QuotaStore, clock: Callable[[], float] = time.time,
                 cooldown_base: float = 30.0,
                 cooldown_max: float = 1800.0):
        self.providers = list(providers)
        self.usage = usage
        self.quota = quota
        self.clock = clock
        self.cooldown_base = max(1.0, float(cooldown_base))
        self.cooldown_max = max(self.cooldown_base, float(cooldown_max))
        self._cooldown_until: Dict[str, float] = {}
        self._failures: Dict[str, int] = {}
        self._last_used: Dict[str, float] = {}
        self.last_reason = ""

    def acquire(self) -> Optional[Lease]:
        if not self.providers:
            self.last_reason = "no LLM providers configured"
            return None
        now = self.clock()
        available = [p for p in self.providers
                     if self._cooldown_until.get(p.name, 0.0) <= now]
        if not available:
            self.last_reason = "all providers are cooling down after failures"
            return None

        def order(p: Provider):
            try:
                used = self.usage.requests_today(p.name)
            except Exception:
                used = 0
            return (used, self._last_used.get(p.name, 0.0), p.name)

        for provider in sorted(available, key=order):
            if not self.quota.reserve(provider.name,
                                      provider.max_requests_per_day):
                continue
            self._last_used[provider.name] = now
            self.last_reason = ""
            return Lease(provider=provider,
                         reserved_utc=time.strftime(
                             "%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.last_reason = "all providers are at their daily request cap"
        return None

    def record_success(self, provider: Provider, response) -> None:
        self._failures[provider.name] = 0
        self._cooldown_until[provider.name] = 0.0
        self.usage.record(
            provider.name,
            requests=max(1, int(getattr(response, "attempts", 1) or 1)),
            prompt_tokens=int(getattr(response, "prompt_tokens", 0) or 0),
            completion_tokens=int(
                getattr(response, "completion_tokens", 0) or 0),
            ok=True, problem="abc_proof")

    def record_failure(self, provider: Provider, error: Exception) -> None:
        failures = self._failures.get(provider.name, 0) + 1
        self._failures[provider.name] = failures
        delay = min(self.cooldown_max,
                    self.cooldown_base * (2 ** min(failures - 1, 6)))
        self._cooldown_until[provider.name] = self.clock() + delay
        self.usage.record(
            provider.name,
            requests=max(1, int(provider.max_retries) + 1),
            ok=False, error=str(error), problem="abc_proof")

    def public(self) -> List[dict]:
        now = self.clock()
        out: List[dict] = []
        for provider in self.providers:
            item = provider.public()
            item.update({
                "requests_today": self.usage.requests_today(provider.name),
                "quota_used_today": self.quota.used(provider.name),
                "failures_this_process": self._failures.get(provider.name, 0),
                "cooldown_s": max(
                    0, int(self._cooldown_until.get(provider.name, 0.0) - now)),
            })
            out.append(item)
        return out


def build_pool(providers: Optional[List[Provider]] = None,
               usage_path: str = USAGE_PATH,
               quota_dir: str = QUOTA_DIR) -> ProviderPool:
    """Build a pool from ``LLM_PROVIDERS`` or an explicit provider list."""
    if providers is None:
        providers = load_providers()
    return ProviderPool(providers, SharedUsage(usage_path), QuotaStore(quota_dir))
