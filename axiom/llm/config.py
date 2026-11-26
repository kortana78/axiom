"""Configuration for OpenAI-compatible LLM providers.

Primary (single provider) secrets:

    LLM_BASE_URL, LLM_API_KEY, LLM_MODEL

Multiple providers can be supplied as JSON in ``LLM_PROVIDERS``:

    [{"name": "free-a", "base_url": "https://.../v1",
      "api_key_env": "FREE_A_KEY", "model": "model-a",
      "max_requests_per_run": 2, "max_requests_per_day": 20}]

A provider is enabled only when its key, base URL, and model are all present.
No key means the LLM idea job is skipped, never failed.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional


def _int(env: Mapping[str, str], name: str, default: int) -> int:
    try:
        return max(0, int(env.get(name, default)))
    except (TypeError, ValueError):
        return default


def _float(env: Mapping[str, str], name: str, default: float) -> float:
    try:
        return max(0.1, float(env.get(name, default)))
    except (TypeError, ValueError):
        return default


@dataclass
class Provider:
    name: str
    base_url: str
    api_key: str
    model: str
    max_requests_per_run: int = 2
    max_requests_per_day: int = 20
    timeout: float = 60.0
    max_retries: int = 2
    total_timeout: float = 180.0
    response_format: bool = False

    def public(self) -> dict:
        """Provider metadata safe to log (never the key)."""
        return {
            "name": self.name,
            "model": self.model,
            "base_url": self.base_url,
            "max_requests_per_run": self.max_requests_per_run,
            "max_requests_per_day": self.max_requests_per_day,
            "timeout": self.timeout,
            "max_retries": self.max_retries,
            "total_timeout": self.total_timeout,
            "response_format": self.response_format,
        }


def load_providers(env: Optional[Mapping[str, str]] = None) -> List[Provider]:
    env = os.environ if env is None else env
    default_run = _int(env, "LLM_MAX_REQUESTS_PER_RUN", 2)
    default_day = _int(env, "LLM_MAX_REQUESTS_PER_DAY", 20)
    default_timeout = _float(env, "LLM_TIMEOUT", 60.0)
    default_retries = _int(env, "LLM_RETRIES", 2)
    default_total = _float(env, "LLM_TOTAL_TIMEOUT", 180.0)
    default_json = env.get("LLM_RESPONSE_FORMAT", "").lower() in ("1", "true", "yes")

    raw = (env.get("LLM_PROVIDERS") or "").strip()
    if raw:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return []
        if isinstance(data, dict):
            data = data.get("providers", [])
        out: List[Provider] = []
        for i, item in enumerate(data if isinstance(data, list) else []):
            if not isinstance(item, dict):
                continue
            key = str(item.get("api_key", "") or "")
            if not key and item.get("api_key_env"):
                key = str(env.get(str(item["api_key_env"]), "") or "")
            base = str(item.get("base_url", "") or env.get("LLM_BASE_URL", "") or "").strip()
            model = str(item.get("model", "") or env.get("LLM_MODEL", "") or "").strip()
            if not (key and base and model):
                continue
            out.append(Provider(
                name=str(item.get("name", f"provider{i}")),
                base_url=base,
                api_key=key,
                model=model,
                max_requests_per_run=int(item.get("max_requests_per_run", default_run)),
                max_requests_per_day=int(item.get("max_requests_per_day", default_day)),
                timeout=float(item.get("timeout", default_timeout)),
                max_retries=int(item.get("max_retries", default_retries)),
                total_timeout=float(item.get("total_timeout", default_total)),
                response_format=bool(item.get("response_format", default_json)),
            ))
        return out

    key = (env.get("LLM_API_KEY") or "").strip()
    base = (env.get("LLM_BASE_URL") or "").strip()
    model = (env.get("LLM_MODEL") or "").strip()
    if not (key and base and model):
        return []
    return [Provider(
        name=env.get("LLM_PROVIDER_NAME", "default"),
        base_url=base,
        api_key=key,
        model=model,
        max_requests_per_run=default_run,
        max_requests_per_day=default_day,
        timeout=default_timeout,
        max_retries=default_retries,
        total_timeout=default_total,
        response_format=default_json,
    )]
