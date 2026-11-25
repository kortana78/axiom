"""Print the GitHub Actions job matrix: active problems x shards.

    python -m axiom.swarm.plan --shards 10
"""
from __future__ import annotations

import argparse
import json

from .common import load_queue


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--shards", type=int, default=10)
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--problems", action="store_true", help="print the active problem list instead")
    a = ap.parse_args(argv)
    if a.problems:
        print(json.dumps([p["id"] for p in load_queue(a.queue) if p.get("active")]))
        return
    probs = [p["id"] for p in load_queue(a.queue) if p.get("active")]
    if not probs:
        print(json.dumps({"include": []}))
        return
    per = max(1, a.shards // len(probs))
    inc = [{"problem": pid, "shard": s, "of": per} for pid in probs for s in range(per)]
    print(json.dumps({"include": inc}))


if __name__ == "__main__":
    main()
