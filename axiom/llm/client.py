"""Small OpenAI-compatible chat client with retries and total timeout.

No SDK dependency: only ``urllib`` from the standard library.  The transport
is injectable so tests never touch the network.
"""
from __future__ import annotations

import json
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

from .config import Provider


class LLMError(Exception):
    pass


class TransientError(LLMError):
    pass


@dataclass
class LLMResponse:
    text: str
    model: str
    prompt_tokens: int = 0
    completion_tokens: int = 0
    attempts: int = 1
    raw: Optional[dict] = None


def endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if "/v1" in base:
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def _http_post(url: str, headers: Dict[str, str], payload: dict,
               timeout: float) -> Tuple[int, Dict[str, str], str]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, dict(resp.headers), resp.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        if exc.code == 429 or 500 <= exc.code <= 599:
            raise TransientError(f"HTTP {exc.code}: {text[:300]}") from exc
        raise LLMError(f"HTTP {exc.code}: {text[:300]}") from exc
    except (urllib.error.URLError, TimeoutError, socket.timeout) as exc:
        raise TransientError(f"network: {exc}") from exc


def _content(data: dict) -> str:
    try:
        choice = data["choices"][0]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("response has no choices") from exc
    msg = choice.get("message") or {}
    text = msg.get("content")
    if text is None:
        text = choice.get("text")
    if not isinstance(text, str) or not text.strip():
        # A 200 response with empty content is usually a transient provider
        # glitch or a reasoning-model truncation; retry it like a 5xx.
        raise TransientError("response has no text content")
    return text


def _usage(data: dict) -> Tuple[int, int]:
    u = data.get("usage") or {}
    prompt = int(u.get("prompt_tokens", u.get("input_tokens", 0)) or 0)
    completion = int(u.get("completion_tokens", u.get("output_tokens", 0)) or 0)
    return prompt, completion


def parse_json_text(text: str):
    """Parse JSON, tolerating markdown fences and surrounding prose."""
    s = text.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip()
    starts = [i for i in (s.find("{"), s.find("[")) if i >= 0]
    if not starts:
        raise LLMError("no JSON object or array in response")
    start = min(starts)
    try:
        obj, _end = json.JSONDecoder().raw_decode(s[start:])
    except json.JSONDecodeError as exc:
        raise LLMError(f"invalid JSON: {exc}") from exc
    return obj


class LLMClient:
    def __init__(self, provider: Provider,
                 transport: Optional[Callable] = None,
                 sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.time):
        self.provider = provider
        self.transport = transport or _http_post
        self.sleep = sleep
        self.clock = clock

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.provider.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "axiom-llm-ideas/0.1",
        }

    def chat(self, messages: List[dict], max_tokens: int = 900,
             temperature: float = 0.7) -> LLMResponse:
        payload = {
            "model": self.provider.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if self.provider.response_format:
            payload["response_format"] = {"type": "json_object"}
        url = endpoint(self.provider.base_url)
        deadline = self.clock() + self.provider.total_timeout
        last: Optional[Exception] = None
        for attempt in range(self.provider.max_retries + 1):
            if self.clock() > deadline:
                raise LLMError("LLM total timeout exceeded")
            headers: Dict[str, str] = {}
            try:
                status, headers, text = self.transport(
                    url, self._headers(), payload, self.provider.timeout)
                if status == 429 or 500 <= status <= 599:
                    raise TransientError(f"HTTP {status}: {text[:300]}")
                if status != 200:
                    raise LLMError(f"HTTP {status}: {text[:300]}")
                try:
                    data = json.loads(text)
                except json.JSONDecodeError as exc:
                    raise LLMError(f"response is not JSON: {exc}") from exc
                prompt, completion = _usage(data)
                return LLMResponse(
                    text=_content(data), model=self.provider.model,
                    prompt_tokens=prompt, completion_tokens=completion,
                    attempts=attempt + 1, raw=data)
            except TransientError as exc:
                last = exc
                if attempt >= self.provider.max_retries:
                    break
                try:
                    retry_after = float(headers.get("Retry-After", 0) or 0)
                except (ValueError, TypeError):
                    retry_after = 0.0
                delay = max(retry_after, min(20.0, 1.0 * (2 ** attempt)))
                if self.clock() + delay > deadline:
                    break
                self.sleep(delay)
        raise LLMError(f"LLM request failed after retries: {last}")
