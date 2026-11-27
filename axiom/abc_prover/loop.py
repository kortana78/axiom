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
)
from .lean import LeanHarness, LeanUnavailable
from .prompt import build_prompt
from .proposals import parse_proposals, signature
from .routes import load_routes, route_names


def _write_target_attempt(path: str, attempt: Dict[str, object]) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(
            "-- Lean-checked target-like lemma proposed by axiom.abc_prover.\n"
            "-- This is NOT lean/Abc/Proof.lean and has NOT been promoted.\n"
            "-- Review it; the abc alarm must verify any proof independently.\n"
            "\n"
            + str(attempt.get("lean", "")).rstrip() + "\n")


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
        max_requests: int = 1) -> Dict[str, object]:
    """Run the bounded loop and return a report.  No proof claim is made."""
    routes = load_routes(routes_path)
    allowed = route_names(routes)
    try:
        with open(STATEMENT_PATH, encoding="utf-8") as fh:
            statement_source = fh.read()
    except OSError:
        statement_source = ""
    ledger = load_ledger(ledger_path)
    attempts = [a for a in (ledger.get("attempts") or [])
                if isinstance(a, dict)]
    checked = [a for a in attempts if a.get("status") == CHECKED]
    failures = [a for a in attempts if a.get("status") == REJECTED]
    seen = {str(a.get("id", "")) for a in attempts}

    if client is None:
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
    else:
        provider = None

    model = getattr(provider, "model", "fake")
    usage = UsageLedger(usage_path) if provider is not None else None
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
            if usage is not None and provider is not None:
                if not usage.can_request(provider.name,
                                         provider.max_requests_per_day):
                    errors.append("daily request limit reached")
                    break
            messages = build_prompt(routes, checked, failures, max_proposals,
                                    statement_source=statement_source)
            try:
                resp = client.chat(messages, max_tokens=3500, temperature=0.3)
            except LLMError as exc:
                if usage is not None and provider is not None:
                    usage.record(provider.name,
                                 requests=int(provider.max_retries) + 1,
                                 ok=False, error=str(exc), problem="abc_proof")
                errors.append(str(exc))
                break
            requests_made += 1
            rounds_done += 1
            if usage is not None and provider is not None:
                usage.record(provider.name, requests=resp.attempts,
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
                attempt = _attempt_from(proposal, result, round_no, model)
                append_attempt(ledger, attempt)
                save_ledger(ledger, ledger_path)
                new_attempts.append(attempt)
                if attempt["status"] == CHECKED:
                    checked.append(attempt)
                    print(f"[abc-prover] CHECKED {attempt['name']} "
                          f"({attempt['route']})")
                    if attempt["target_like"]:
                        target_attempts.append(attempt)
                        _write_target_attempt(target_path, attempt)
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
    print(f"[abc-prover] {len(new_attempts)} checked this run; "
          f"ledger {st['checked']} checked / {st['rejected']} rejected; "
          "abc remains OPEN")
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
    ap.add_argument("--dry-run", action="store_true",
                    help="print the prompt and exit without calling an LLM")
    a = ap.parse_args(argv)
    if a.dry_run:
        routes = load_routes(a.routes)
        print(json.dumps(build_prompt(routes, [], [], a.max_proposals),
                         indent=2, ensure_ascii=False))
        return 0
    report = run(a.rounds, a.max_proposals, a.time, a.mathlib,
                 a.ledger, a.status, a.routes, a.target, a.usage,
                 max_requests=a.max_requests)
    print(json.dumps(report, indent=2, default=str))
    return 0 if report.get("enabled") or report.get("reason") == "no LLM_API_KEY" else 1


if __name__ == "__main__":
    raise SystemExit(main())
