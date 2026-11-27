"""Bounded LLM -> Lean proof-attempt loop for abc.

    python -m axiom.abc_prover.loop --mathlib /path/to/mathlib4 \
        --rounds 2 --max-proposals 3 --time 900 --max-requests 2

Every proposal is sanitized, compiled against the frozen statement, and
recorded.  A ``CHECKED`` lemma is a Lean theorem, not a proof of abc.  This
module never writes ``lean/Abc/Proof.lean`` and never writes the alarm verdict.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from contextlib import ExitStack
from typing import Dict, List, Optional

from ..abc_proof import STATEMENT_PATH
from ..llm.client import LLMClient, LLMError
from ..llm.config import Provider, load_providers
from ..llm.usage import UsageLedger
from . import (
    CHECKED,
    LEDGER_PATH,
    NO_PROOF,
    QUOTA_DIR,
    REJECTED,
    ROUTES_PATH,
    SKIPPED,
    STATUS_PATH,
    TARGET_ATTEMPT_PATH,
)
from .ledger import (
    append_attempt,
    build_status,
    load_ledger,
    save_json,
    save_ledger,
    stats,
    utc_now,
    write_target_attempt,
)
from .lean import LeanHarness, LeanUnavailable
from .prompt import build_prompt
from .proposals import parse_proposals, signature
from .routes import load_routes, route_names


def _attempt_from(proposal: dict, result: Dict[str, object], round_no: int,
                  model: str) -> Dict[str, object]:
    ok = bool(result.get("ok", result.get("status") == CHECKED))
    status = CHECKED if ok else REJECTED
    return {
        "id": proposal["id"],
        "name": proposal["name"],
        "route": proposal["route"],
        "rationale": proposal.get("rationale", ""),
        "target_like": bool(proposal.get("target_like")),
        "signature": signature(proposal["lean"]),
        "lean": proposal["lean"],
        "status": status,
        "axioms": list(result.get("axioms", []) or []),
        "reason": str(result.get("reason", "")),
        "output_tail": ("" if ok
                        else str(result.get("output", ""))[-2000:]),
        "round": round_no,
        "model": model,
        "seconds": float(result.get("seconds", 0.0) or 0.0),
        "lean_version": str(result.get("lean_version", "unknown")),
        "mathlib_version": str(result.get("mathlib_version", "unknown")),
        "checked_at": utc_now(),
    }


def run(rounds: int = 2, max_proposals: int = 3, time_budget: float = 600.0,
        mathlib: Optional[str] = None, ledger_path: str = LEDGER_PATH,
        status_path: str = STATUS_PATH, routes_path: str = ROUTES_PATH,
        target_path: str = TARGET_ATTEMPT_PATH,
        usage_path: str = "results/llm_usage.json",
        providers: Optional[List[Provider]] = None,
        client=None, checker=None, transport=None,
        max_requests: int = 1, pool=None,
        context_ledger_path: Optional[str] = None,
        seen_ids: Optional[set] = None) -> Dict[str, object]:
    """Run the bounded loop and return a report.  No proof claim is made.

    ``pool`` is a :class:`axiom.abc_prover.pool.ProviderPool`.  When supplied,
    the loop rotates providers per round and the pool enforces shared daily
    caps.  ``context_ledger_path`` lets a worker read the merged fleet ledger
    for prompt context while writing attempts to its own ledger.
    """
    routes = load_routes(routes_path)
    allowed = route_names(routes)
    try:
        with open(STATEMENT_PATH, encoding="utf-8") as fh:
            statement_source = fh.read()
    except OSError:
        statement_source = ""
    ledger = load_ledger(ledger_path)
    local_attempts = [a for a in (ledger.get("attempts") or [])
                      if isinstance(a, dict)]
    context_ledger = (load_ledger(context_ledger_path)
                      if context_ledger_path else ledger)
    context_attempts = [a for a in (context_ledger.get("attempts") or [])
                        if isinstance(a, dict)]
    checked = [a for a in context_attempts if a.get("status") == CHECKED]
    failures = [a for a in context_attempts if a.get("status") == REJECTED]
    seen = {str(a.get("id", "")) for a in local_attempts}
    seen |= {str(a.get("id", "")) for a in context_attempts}
    if seen_ids:
        seen |= {str(x) for x in seen_ids}

    clients: Dict[str, LLMClient] = {}
    provider = None
    model = "fake"
    if client is None and pool is None:
        providers = load_providers() if providers is None else providers
        if not providers:
            status = build_status(ledger, routes)
            status.update(verdict=SKIPPED,
                          note="no LLM_API_KEY configured; no attempts this run")
            save_json(status_path, status)
            print("[abc-prover] skipped: no LLM_API_KEY (not a failure)")
            return {"enabled": False, "reason": "no LLM_API_KEY",
                    "abc": "OPEN", "verdict": NO_PROOF}
        provider = providers[0]
        client = LLMClient(provider, transport=transport)
        model = provider.model
    elif client is not None:
        model = getattr(getattr(client, "provider", None), "model", "fake")

    if pool is not None and not getattr(pool, "providers", []):
        status = build_status(ledger, routes)
        status.update(verdict=SKIPPED,
                      note="no LLM providers configured; no attempts this run")
        save_json(status_path, status)
        print("[abc-prover] skipped: no LLM providers configured")
        return {"enabled": False, "reason": "no LLM providers configured",
                "abc": "OPEN", "verdict": NO_PROOF}

    usage = UsageLedger(usage_path) if (provider is not None and pool is None) else None
    started = time.time()
    deadline = started + max(1.0, float(time_budget))
    errors: List[str] = []
    skipped_duplicates = 0
    new_attempts: List[dict] = []
    requests_made = 0
    rounds_done = 0
    target_attempts: List[dict] = []

    per_run = max(0, int(max_requests))
    if provider is not None:
        per_run = min(per_run, int(provider.max_requests_per_run))

    stack = ExitStack()
    try:
        if checker is None:
            harness = stack.enter_context(
                LeanHarness(STATEMENT_PATH, mathlib, timeout=240.0))
            checker = harness.check
        for round_no in range(1, max(1, int(rounds)) + 1):
            if requests_made >= per_run:
                break
            if time.time() >= deadline:
                errors.append("time budget exhausted")
                break

            active_provider = provider
            active_client = client
            if pool is not None:
                lease = pool.acquire()
                if lease is None:
                    errors.append(str(getattr(pool, "last_reason",
                                              "no provider available")))
                    break
                active_provider = lease.provider
                active_client = clients.get(active_provider.name)
                if active_client is None:
                    active_client = LLMClient(active_provider,
                                              transport=transport)
                    clients[active_provider.name] = active_client
                model = active_provider.model
            if active_client is None:
                errors.append("no LLM client available")
                break
            if usage is not None and active_provider is not None:
                if not usage.can_request(active_provider.name,
                                         active_provider.max_requests_per_day):
                    errors.append("daily request limit reached")
                    break

            messages = build_prompt(routes, checked, failures, max_proposals,
                                    statement_source=statement_source)
            try:
                resp = active_client.chat(messages, max_tokens=3500,
                                          temperature=0.3)
            except LLMError as exc:
                if pool is not None and active_provider is not None:
                    pool.record_failure(active_provider, exc)
                elif usage is not None and active_provider is not None:
                    usage.record(active_provider.name,
                                 requests=int(active_provider.max_retries) + 1,
                                 ok=False, error=str(exc), problem="abc_proof")
                errors.append(str(exc))
                requests_made += 1
                continue
            requests_made += 1
            rounds_done += 1
            if pool is not None and active_provider is not None:
                pool.record_success(active_provider, resp)
            elif usage is not None and active_provider is not None:
                usage.record(active_provider.name, requests=resp.attempts,
                             prompt_tokens=resp.prompt_tokens,
                             completion_tokens=resp.completion_tokens,
                             ok=True, problem="abc_proof")
            proposals, bad = parse_proposals(resp.text, allowed, max_proposals)
            errors.extend(bad[:10])
            if not proposals:
                continue
            for proposal in proposals:
                if time.time() >= deadline:
                    errors.append("time budget exhausted during checks")
                    break
                if proposal["id"] in seen:
                    skipped_duplicates += 1
                    continue
                seen.add(proposal["id"])
                result = checker(proposal["lean"], proposal["name"])
                attempt = _attempt_from(proposal, result, round_no,
                                        getattr(resp, "model", model))
                append_attempt(ledger, attempt)
                save_ledger(ledger, ledger_path)
                new_attempts.append(attempt)
                if attempt["status"] == CHECKED:
                    checked.append(attempt)
                    print(f"[abc-prover] CHECKED {attempt['name']} "
                          f"({attempt['route']})")
                    if attempt["target_like"]:
                        target_attempts.append(attempt)
                        write_target_attempt(target_path, attempt)
                        print("[abc-prover] TARGET-LIKE LEMMA CHECKED; saved to "
                              f"{target_path}")
                        print("[abc-prover] NOT promoted to lean/Abc/Proof.lean; "
                              "the alarm remains OPEN.")
                else:
                    failures.append(attempt)
                    print(f"[abc-prover] REJECTED {attempt['name']}: "
                          f"{str(attempt['reason'])[:160]}")
    except LeanUnavailable as exc:
        errors.append(f"Lean unavailable: {exc}")
        status = build_status(ledger, routes)
        status.update(verdict=SKIPPED,
                      note=f"Lean unavailable: {exc}")
        save_json(status_path, status)
        return {"enabled": False, "reason": str(exc), "abc": "OPEN",
                "verdict": NO_PROOF, "errors": errors}
    finally:
        stack.close()

    ledger = save_ledger(ledger, ledger_path)
    status = build_status(ledger, routes)
    if not new_attempts and not errors:
        status["note"] = ("no new proposals this run; checked lemmas are not "
                          "a proof of Abc.Statement")
    save_json(status_path, status)
    st = stats(ledger)
    report = {
        "enabled": True,
        "abc": "OPEN",
        "verdict": NO_PROOF,
        "rounds": rounds_done,
        "requests": requests_made,
        "new_attempts": len(new_attempts),
        "checked": st["checked"],
        "rejected": st["rejected"],
        "skipped_duplicates": skipped_duplicates,
        "target_attempts": len(target_attempts),
        "errors": errors[-10:],
        "ledger": ledger_path,
        "status": status_path,
        "elapsed_s": round(time.time() - started, 1),
        "note": "Checked lemmas are Lean theorems, not a proof of abc.",
    }
    n_checked = sum(1 for a in new_attempts if a.get("status") == CHECKED)
    print(f"[abc-prover] {n_checked} checked / {len(new_attempts)} attempted "
          f"this run; ledger {st['checked']} checked / {st['rejected']} "
          "rejected; abc remains OPEN")
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="bounded Lean proof-attempt loop for abc")
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--max-proposals", type=int, default=3)
    ap.add_argument("--time", type=float, default=600.0)
    ap.add_argument("--mathlib", default=None)
    ap.add_argument("--max-requests", type=int, default=1)
    ap.add_argument("--ledger", default=LEDGER_PATH)
    ap.add_argument("--status", default=STATUS_PATH)
    ap.add_argument("--routes", default=ROUTES_PATH)
    ap.add_argument("--target", default=TARGET_ATTEMPT_PATH)
    ap.add_argument("--usage", default="results/llm_usage.json")
    ap.add_argument("--quota", default=QUOTA_DIR)
    ap.add_argument("--context-ledger", default=None,
                    help="read prompt context/duplicates from this ledger")
    ap.add_argument("--pool", action="store_true",
                    help="rotate over LLM_PROVIDERS with shared daily quotas")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the prompt and exit without calling an LLM")
    a = ap.parse_args(argv)
    if a.dry_run:
        routes = load_routes(a.routes)
        print(json.dumps(build_prompt(routes, [], [], a.max_proposals),
                         indent=2, ensure_ascii=True))
        return 0
    pool = None
    if a.pool:
        from .pool import build_pool

        pool = build_pool(usage_path=a.usage, quota_dir=a.quota)
    report = run(a.rounds, a.max_proposals, a.time, a.mathlib,
                 a.ledger, a.status, a.routes, a.target, a.usage,
                 max_requests=a.max_requests, pool=pool,
                 context_ledger_path=a.context_ledger)
    print(json.dumps(report, indent=2, default=str))
    return 0 if report.get("enabled") or report.get("reason") == "no LLM_API_KEY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
