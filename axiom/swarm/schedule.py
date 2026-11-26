"""Work-item scheduler for the swarm.

One batch is a list of items `(problem, shard or exponent box, idea)`, capped
at 1000.  A runner is one process; items are assigned round-robin.  Each item
writes its own shard file through the ordinary worker path.  A runner records
planned/done/carried-over in `results/schedule/runner_<i>.json`; the summary
command merges those records into `results/schedule.json`.

    python -m axiom.swarm.schedule --runner 0 --runners 4 --minutes 45
    python -m axiom.swarm.schedule --summarize
"""
from __future__ import annotations

import argparse
import json
import os
import time
from typing import Dict, List, Optional

from .common import find_problem, load_json, load_queue, save_json
from .sunit import sunit_items


def _load_idea_pool(paths: List[str]) -> List[dict]:
    out: List[dict] = []
    for path in paths:
        data = load_json(path, {}) or {}
        items = data.get("ideas", []) if isinstance(data, dict) else []
        for d in items:
            if isinstance(d, dict):
                out.append(d)
    return out


def _per_problem(entry: dict, shards: int, ideas: List[dict],
                 ideas_per_shard: int) -> List[dict]:
    pid = entry["id"]
    kind = entry.get("kind", "witness")
    if kind == "sunit":
        items = sunit_items(entry)
        return [{"problem": pid, "kind": "sunit", "shard": i, "of": len(items),
                 "q": q, "box": k, "boxes": n, "idea": None}
                for i, (q, k, n) in enumerate(items)]
    n = max(1, int(shards))
    if kind == "abc":
        return [{"problem": pid, "kind": "abc", "shard": i, "of": n, "idea": None}
                for i in range(n)]
    out = []
    for i in range(n):
        for j in range(max(0, int(ideas_per_shard))):
            idea = ideas[(i + j * n) % len(ideas)] if ideas else None
            out.append({"problem": pid, "kind": "witness", "shard": i, "of": n,
                        "idea": idea})
    if not out:
        out = [{"problem": pid, "kind": "witness", "shard": i, "of": n, "idea": None}
               for i in range(n)]
    return out


def build_items(queue_path="swarm/queue.json", shards=10, max_items=1000,
                ideas_per_shard=0, idea_paths=None) -> dict:
    probs = [p for p in load_queue(queue_path)
             if p.get("active") and p.get("kind") != "abc_route"]
    ideas = _load_idea_pool(idea_paths or []) if ideas_per_shard else []
    if not ideas:
        ideas_per_shard = 0
    buckets: Dict[str, List[dict]] = {}
    for p in probs:
        buckets[p["id"]] = _per_problem(p, shards, ideas, ideas_per_shard)
    # Round-robin so a cap never starves a problem completely.
    items: List[dict] = []
    cursors = {pid: 0 for pid in buckets}
    while len(items) < max(1, int(max_items)):
        progressed = False
        for pid, bucket in buckets.items():
            i = cursors[pid]
            if i < len(bucket):
                items.append(bucket[i])
                cursors[pid] = i + 1
                progressed = True
                if len(items) >= max_items:
                    break
        if not progressed:
            break
    total = sum(len(b) for b in buckets.values())
    return {
        "items": items,
        "total_available": total,
        "capped": total > len(items),
        "max_items": int(max_items),
        "shards_per_problem": int(shards),
        "ideas_per_shard": int(ideas_per_shard),
    }


def _item_key(item: dict) -> str:
    return json.dumps(item, sort_keys=True, default=str)


def _run_item(item: dict, seconds: float, queue_path: str, root: str) -> dict:
    from .worker import run as run_worker
    if item.get("kind") == "witness" and item.get("idea"):
        from ..ideas.run import run_one
        return run_one(item["problem"], seconds, item["idea"], queue_path, root,
                       tag=f"idea_s{item['shard']:03d}")
    return run_worker(item["problem"], int(item["shard"]), int(item["of"]),
                      seconds, queue_path, root)


def run_runner(index: int, runners: int, minutes: float,
               queue_path="swarm/queue.json", root="results",
               max_items=1000, shards=10, ideas_per_shard=0,
               idea_paths=None) -> dict:
    if runners < 1 or not (0 <= index < runners):
        raise ValueError("require 0 <= runner < runners")
    plan = build_items(queue_path, shards, max_items, ideas_per_shard, idea_paths)
    mine = plan["items"][index::runners]
    deadline = time.time() + max(0.1, float(minutes)) * 60.0
    done, carried, errors = [], [], []
    for pos, item in enumerate(mine):
        if time.time() >= deadline:
            carried.append(item)
            continue
        remaining = max(1.0, deadline - time.time())
        # Share the remaining batch time over the remaining items instead of
        # letting the first item consume the whole runner.
        left = max(1, len(mine) - pos)
        budget = min(remaining, max(2.0, remaining / left))
        try:
            _run_item(item, budget, queue_path, root)
            done.append(item)
        except (Exception, SystemExit) as exc:  # keep the batch alive
            errors.append({"item": item, "error": str(exc)[:500]})
            carried.append(item)
    record = {
        "runner": index, "runners": runners,
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "minutes": float(minutes), "planned": mine, "done": done,
        "carried_over": carried, "errors": errors,
        "total_available": plan["total_available"],
        "capped": plan["capped"], "max_items": plan["max_items"],
    }
    path = os.path.join(root, "schedule", f"runner_{index:03d}.json")
    save_json(path, record)
    print(f"[schedule runner {index}/{runners}] planned {len(mine)}, done {len(done)}, "
          f"carried {len(carried)}, errors {len(errors)} -> {path}")
    return record


def summarize(root="results") -> dict:
    files = []
    sdir = os.path.join(root, "schedule")
    if os.path.isdir(sdir):
        files = sorted(os.path.join(sdir, f) for f in os.listdir(sdir)
                       if f.startswith("runner_") and f.endswith(".json"))
    records = [load_json(f, {}) or {} for f in files]
    planned = [i for r in records for i in r.get("planned", [])]
    done = [i for r in records for i in r.get("done", [])]
    carried = [i for r in records for i in r.get("carried_over", [])]
    errors = [e for r in records for e in r.get("errors", [])]
    summary = {
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runners": len(records),
        "planned": len(planned),
        "done": len(done),
        "carried_over": len(carried),
        "errors": len(errors),
        "capped": any(bool(r.get("capped")) for r in records),
        "max_items": max((int(r.get("max_items", 0)) for r in records), default=0),
        "carried_items": carried[:1000],
        "error_items": errors[:100],
    }
    save_json(os.path.join(root, "schedule.json"), summary)
    print(f"[schedule] planned {summary['planned']}, done {summary['done']}, "
          f"carried {summary['carried_over']}, errors {summary['errors']}")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="AXIOM work-item scheduler")
    ap.add_argument("--runner", type=int, default=None)
    ap.add_argument("--runners", type=int, default=1)
    ap.add_argument("--minutes", type=float, default=45.0)
    ap.add_argument("--max-items", type=int, default=1000)
    ap.add_argument("--shards", type=int, default=10)
    ap.add_argument("--ideas-per-shard", type=int, default=0)
    ap.add_argument("--idea-file", action="append", default=None)
    ap.add_argument("--summarize", action="store_true")
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    if a.summarize:
        summarize(a.results)
        return
    if a.runner is None:
        ap.error("use --runner <i> or --summarize")
    run_runner(a.runner, a.runners, a.minutes, a.queue, a.results,
               a.max_items, a.shards, a.ideas_per_shard, a.idea_file)


if __name__ == "__main__":
    main()
