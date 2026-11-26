"""LLM idea proposals: untrusted, schema-checked, and never proof results.

    python -m axiom.llm.ideas --problem erdos_straus --time 300
    python -m axiom.llm.ideas --all --max-problems 10 --time 300

The model receives the problem statement, the current frontier/status, and a
short list of failed ideas.  It never receives published solution lists and
never writes `results/` proof data, the kernel, or the checker.  Its output is
validated against the witness schema (`swarm/ideas.json`), the S-unit
heuristics schema, or the narrow ABC search schema, tagged with
`source = "llm:<model>"`, and written to a proposals file for the next batch.

If no API key is configured the command prints a skip message and exits 0.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Iterable, List, Optional

from ..ideas.space import ATOM_KINDS
from ..swarm.common import find_problem, load_json, load_queue
from .client import LLMClient, LLMError, parse_json_text
from .config import Provider, load_providers
from .schema import schema_text, validate_payload_report
from .usage import UsageLedger

SYSTEM = (
    "You are a mathematical search-idea generator. You do not prove theorems. "
    "You propose concrete, testable search strategies only. Return JSON only, "
    "with no markdown and no commentary. Never claim a problem is solved. "
    "Never invent known answers or cite unpublished proofs."
)


def _out_default(kind: str) -> str:
    if kind == "sunit":
        return "swarm/sunit_ideas.json"
    if kind == "abc":
        return "swarm/abc_ideas.json"
    return "swarm/llm_ideas.json"


def _context(pid: str, entry: dict, root: str) -> dict:
    out = os.path.join(root, pid)
    status = load_json(os.path.join(out, "status.json"), {}) or {}
    frontier = load_json(os.path.join(out, "frontier.json"), {}) or {}
    log = load_json(os.path.join(out, "ideas_log.json"), {}) or {}
    tried = log.get("tried", {}) if isinstance(log, dict) else {}
    failures = [k for k, v in tried.items()
                if isinstance(v, dict) and int(v.get("hits", 0)) == 0][-8:]
    ctx = {
        "id": pid,
        "kind": entry.get("kind", "witness"),
        "statement": entry.get("statement", ""),
        "status": status,
        "frontier": frontier,
        "recent_failures": failures,
    }
    if entry.get("kind") == "sunit":
        ctx["S"] = entry.get("S", [])
        ctx["published_count"] = entry.get("published_count")
        ctx["limitations"] = (
            "The current exact solver handles |S| <= 3 with a fixed-q congruence "
            "lattice and LLL. Larger S needs a better method (p-adic logarithms, "
            "sieving, banding, or a sharper height bound)."
        )
    elif entry.get("kind") == "abc":
        ctx["search"] = entry.get("search", {})
        ctx["best_q"] = status.get("best_q")
        ctx["records"] = status.get("records_verified")
    else:
        try:
            from ..swarm.common import Setup
            st = Setup(entry)
            ctx["variables"] = [v for v, _ in st.engine.s.vars]
        except (Exception, SystemExit):
            ctx["variables"] = []
        ctx["atom_kinds"] = ATOM_KINDS
    return ctx


def _prompt(ctx: dict, kind: str, previous_error: str = "") -> list[dict]:
    schema = schema_text(kind)
    payload = {
        "problem": ctx["id"],
        "kind": kind,
        "statement": ctx["statement"],
        "current_state": ctx["status"],
        "frontier": ctx["frontier"],
        "recent_failed_ideas": ctx["recent_failures"],
    }
    if kind == "witness":
        payload["variables"] = ctx.get("variables", [])
        payload["atom_kinds"] = ctx.get("atom_kinds", ATOM_KINDS)
        rules = (
            "Propose 2-4 witness-search ideas. `order` must be a permutation of "
            "the variables. `atoms` must be a non-empty subset of atom_kinds. "
            "`mult` are positive integers, `T` and `D` are positive integers. "
            "Do not claim any idea proves the statement."
        )
    elif kind == "sunit":
        payload["S"] = ctx.get("S", [])
        payload["published_count"] = ctx.get("published_count")
        payload["limitations"] = ctx.get("limitations", "")
        rules = (
            "Propose 2-3 S-unit solver heuristics. `S` must contain primes. "
            "`method` must be one of mod_q, lll, p_adic_log, sieving, banding, "
            "height_bound, linear_forms, other. `q` is optional and must be in S. "
            "Parameters must be short JSON scalars. Do not claim a proof."
        )
    else:
        payload["search"] = ctx.get("search", {})
        payload["best_q"] = ctx.get("best_q")
        payload["records"] = ctx.get("records")
        rules = (
            "Propose 2-3 ABC search ideas. `family` is c_smooth or legs_smooth. "
            "`smooth_bound` is a small prime/prime power, `window` a positive "
            "integer, `min_quality` in [1,5]. Search ideas only; abc remains open."
        )
    user = (
        "Here is the current state as JSON:\n"
        + json.dumps(payload, indent=2, default=str)
        + "\n\nReturn JSON exactly matching this schema example:\n"
        + schema
        + "\n\nRules:\n- " + rules
        + "\n- Never output known solutions, proofs, or claims of success."
    )
    if previous_error:
        user += f"\n- The previous response was rejected: {previous_error}. Fix the schema."
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": user}]


def _idea_key(kind: str, d: dict) -> str:
    if kind == "witness":
        core = {k: d.get(k) for k in ("order", "atoms", "mult", "T", "D", "tie")}
    elif kind == "sunit":
        core = {k: d.get(k) for k in ("S", "method", "q", "parameters")}
    else:
        core = {k: d.get(k) for k in ("family", "smooth_bound", "window", "min_quality")}
    return json.dumps(core, sort_keys=True, default=str)


def _merge_into(path: str, kind: str, new: Iterable[dict]) -> dict:
    key = "heuristics" if kind == "sunit" else "ideas"
    existing = load_json(path, {}) or {}
    items = existing.get(key, []) if isinstance(existing, dict) else []
    if not isinstance(items, list):
        items = []
    seen = {_idea_key(kind, d) for d in items if isinstance(d, dict)}
    added = 0
    for d in new:
        k = _idea_key(kind, d)
        if k in seen:
            continue
        seen.add(k)
        items.append(d)
        added += 1
    items = items[-100:]
    data = {
        "comment": ("LLM proposals only. Untrusted; validate through the swarm. "
                    "No entry proves anything."),
        "kind": kind,
        "updated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        key: items,
    }
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    os.replace(tmp, path)
    return {"path": path, "added": added, "total": len(items)}


def run(pid: str, seconds: float = 300.0, queue_path: str = "swarm/queue.json",
        root: str = "results", out_path: Optional[str] = None,
        providers: Optional[List[Provider]] = None,
        transport=None, max_requests: int = 2) -> dict:
    entry = find_problem(load_queue(queue_path), pid)
    kind = entry.get("kind", "witness")
    if kind == "abc_route":
        print(f"[llm {pid}] proof-track entry; no LLM search ideas")
        return {"problem": pid, "enabled": False, "reason": "abc_route"}
    providers = load_providers() if providers is None else providers
    if not providers:
        print(f"[llm {pid}] skipped: no LLM_API_KEY (not a failure)")
        return {"problem": pid, "enabled": False, "reason": "no LLM_API_KEY"}

    out_path = out_path or _out_default(kind)
    ctx = _context(pid, entry, root)
    ledger = UsageLedger(os.path.join(root, "llm_usage.json"))
    start = time.time()
    deadline = start + max(1.0, float(seconds))
    accepted: List[dict] = []
    errors: List[str] = []
    provider_reports = []

    for provider in providers:
        client = LLMClient(provider, transport=transport)
        made = 0
        provider_errors: List[str] = []
        while made < min(int(max_requests), int(provider.max_requests_per_run)):
            if time.time() >= deadline:
                break
            if not ledger.can_request(provider.name, provider.max_requests_per_day):
                provider_errors.append("daily request limit reached")
                break
            messages = _prompt(ctx, kind, provider_errors[-1] if provider_errors else "")
            try:
                resp = client.chat(messages)
            except LLMError as exc:
                # Count the worst case so a flaky provider cannot exceed the
                # daily cap by hiding retries inside the client.
                ledger.record(provider.name,
                              requests=provider.max_retries + 1, ok=False,
                              error=str(exc), problem=pid)
                provider_errors.append(str(exc))
                made += 1
                continue
            made += 1
            ledger.record(provider.name, requests=resp.attempts,
                          prompt_tokens=resp.prompt_tokens,
                          completion_tokens=resp.completion_tokens,
                          ok=True, problem=pid)
            try:
                payload = parse_json_text(resp.text)
                valid, bad = validate_payload_report(
                    payload, kind,
                    (ctx.get("variables") or None) if kind == "witness" else None)
            except (LLMError, ValueError) as exc:
                provider_errors.append(str(exc))
                errors.append(f"{provider.name}: {exc}")
                continue
            for d in valid:
                d["source"] = f"llm:{provider.model}"
                accepted.append(d)
            errors.extend(f"{provider.name}: {e}" for e in bad)
            provider_errors.extend(bad)
        provider_reports.append({
            "provider": provider.public(), "requests": made,
            "errors": provider_errors[-5:],
        })

    merged = _merge_into(out_path, kind, accepted) if accepted else {
        "path": out_path, "added": 0, "total": 0}
    result = {
        "problem": pid, "kind": kind, "enabled": True,
        "providers": provider_reports, "accepted": len(accepted),
        "errors": errors[-20:], "output": merged,
        "elapsed_s": round(time.time() - start, 1),
        "note": "proposals only; no proof and no results edit",
    }
    print(f"[llm {pid}] {len(accepted)} valid {kind} ideas -> {merged['path']} "
          f"({len(errors)} rejected)")
    return result


def run_all(seconds: float = 300.0, queue_path: str = "swarm/queue.json",
            root: str = "results", max_problems: int = 10,
            max_requests: int = 2, providers: Optional[List[Provider]] = None,
            transport=None) -> dict:
    problems = [p for p in load_queue(queue_path)
                if p.get("active") and p.get("kind") != "abc_route"]
    problems = problems[:max(0, int(max_problems))]
    if not problems:
        return {"enabled": False, "reason": "no active problems", "problems": []}
    per = max(20.0, float(seconds) / len(problems))
    reports = [run(p["id"], per, queue_path, root, providers=providers,
                   transport=transport, max_requests=max_requests)
               for p in problems]
    return {
        "enabled": any(r.get("enabled") for r in reports),
        "problems": reports,
        "max_problems": max_problems,
        "note": "LLM proposals only; never proof results",
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="validated LLM idea proposals")
    ap.add_argument("--problem", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--time", type=float, default=300.0)
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--results", default="results")
    ap.add_argument("--max-problems", type=int, default=10)
    ap.add_argument("--max-requests", type=int, default=2)
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.all:
        result = run_all(a.time, a.queue, a.results, a.max_problems, a.max_requests)
    elif a.problem:
        result = run(a.problem, a.time, a.queue, a.results, out_path=a.out,
                     max_requests=a.max_requests)
    else:
        ap.error("use --problem <id> or --all")
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
