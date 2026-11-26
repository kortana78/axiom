"""One swarm worker: searches witness families for its shard of residues.

    python -m axiom.swarm.worker --problem erdos_straus --shard 3 --of 20 --time 2700

Results are written as plain data (witness polynomials). Nothing a worker
writes is trusted: the merge step rebuilds every proof and re-checks it
with the kernel.
"""
from __future__ import annotations

import argparse
import os
import platform
import time

from .common import Setup, find_problem, load_json, load_queue, results_dir, save_json


def run(pid, shard, of, seconds, queue_path, root, per_class=None):
    entry = find_problem(load_queue(queue_path), pid)
    if entry.get("kind") == "abc":
        from ..abc.worker import run as run_abc
        return run_abc(entry, shard, of, seconds, root)
    st = Setup(entry)
    out_dir = results_dir(root, pid)
    frontier = load_json(os.path.join(out_dir, "frontier.json"), None)
    if frontier is None:
        M = int(entry.get("start_modulus", 840))
        frontier = {"modulus": M, "open": st.relevant(M),
                    "T": entry["grammar"]["T"], "D": entry["grammar"]["D"]}
    M, T, D = frontier["modulus"], frontier["T"], frontier["D"]
    todo = sorted(frontier["open"])
    mine = [r for i, r in enumerate(todo) if i % of == shard]
    schedule = st.schedule(M)
    start = time.time()
    end = start + seconds
    per_class = per_class or max(5.0, min(120.0, seconds / max(1, len(mine)) * 0.8))
    cache, covered, still_open, unattempted = {}, {}, [], []
    for idx, r in enumerate(mine):
        if time.time() > end:
            unattempted = mine[idx:]
            break
        hit = None
        for Mj in schedule:
            key = (Mj, r % Mj)
            if key not in cache:
                deadline = min(end, time.time() + per_class / len(schedule) * (2 if Mj == M else 1))
                polys, kl, why = st.engine.search_class(Mj, r % Mj, T, D, deadline)
                cache[key] = (polys, kl, why)
            polys, kl, why = cache[key]
            if polys is not None:
                hit = (Mj, r % Mj, kl, polys)
                break
        if hit:
            covered[f"{hit[0]}:{hit[1]}"] = {"M": hit[0], "r": hit[1], "kl": hit[2],
                                            "polys": [str(p) for p in hit[3]]}
        else:
            still_open.append(r)
    data = {
        "problem": pid, "modulus": M, "T": T, "D": D, "shard": shard, "of": of,
        "assigned": len(mine), "covered": list(covered.values()),
        "open": still_open, "unattempted": unattempted,
        "elapsed_s": round(time.time() - start, 1), "host": platform.node(),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(out_dir, "shards", f"{pid}__shard_{shard:03d}_of_{of:03d}.json")
    save_json(path, data)
    print(f"[{pid} shard {shard}/{of}] assigned {len(mine)}, covered {len(covered)} families, "
          f"open {len(still_open)}, unattempted {len(unattempted)}, {data['elapsed_s']} s -> {path}")
    return data


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--shard", type=int, required=True)
    ap.add_argument("--of", type=int, required=True)
    ap.add_argument("--time", type=float, default=600)
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    run(a.problem, a.shard, a.of, a.time, a.queue, a.results)


if __name__ == "__main__":
    main()
