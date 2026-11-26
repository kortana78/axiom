"""Print the GitHub Actions job matrix: active problems x shards.

    python -m axiom.swarm.plan --shards 10

S-unit problems declare ``sunit_shards`` (one entry per prime); each declared
item is a separate job so the merge can verify that the exponent boxes tile.
The remaining jobs are split evenly over the witness problems.
"""
from __future__ import annotations

import argparse
import json

from .common import load_queue


def _sunit_count(p) -> int:
    plan = p.get("sunit_shards") or {}
    n = sum(max(1, int(v)) for v in plan.values())
    if n:
        return n
    return max(1, len(p.get("S", [])))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", type=int, default=10)
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--problems", action="store_true", help="print the active problem list instead")
    a = ap.parse_args(argv)
    all_probs = [p for p in load_queue(a.queue)
                 if p.get("active") and p.get("kind") != "abc_route"]
    if a.problems:
        # The legacy idea runner only understands witness problems. S-unit
        # and ABC entries have their own idea paths; abc_route is a proof
        # track note, not a search job.
        print(json.dumps([p["id"] for p in all_probs
                          if p.get("kind") not in ("sunit",)]))
        return
    probs = all_probs
    if not probs:
        print(json.dumps({"include": []}))
        return
    sunit = [p for p in probs if p.get("kind") == "sunit"]
    base = [p for p in probs if p.get("kind") != "sunit"]
    inc = []
    sunit_total = sum(_sunit_count(p) for p in sunit)
    for p in sunit:
        n = _sunit_count(p)
        inc += [{"problem": p["id"], "shard": s, "of": n} for s in range(n)]
    remaining = max(0, a.shards - sunit_total)
    per = max(1, remaining // len(base)) if base else 0
    for i, p in enumerate(base):
        n = per + (1 if i < remaining - per * len(base) else 0)
        inc += [{"problem": p["id"], "shard": s, "of": n} for s in range(n)]
    print(json.dumps({"include": inc}))


if __name__ == "__main__":
    main()
