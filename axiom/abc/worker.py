"""One ABC hunter worker. Candidates are untrusted data for the merger."""
from __future__ import annotations

import os
import platform
import time

from ..swarm.common import results_dir, save_json
from . import frontier as fr
from .hunt import pair_layout, scan_c_smooth, scan_legs_smooth, sieve_radical, smooth_upto


def _slice(cursor: int, width: int, shard: int, of: int) -> tuple[int, int]:
    lo = cursor + (width * shard) // of
    hi = cursor + (width * (shard + 1)) // of
    return int(lo), int(hi)


def run(entry: dict, shard: int, of: int, seconds: float, root: str = "results") -> dict:
    pid = entry["id"]
    out = results_dir(root, pid)
    frontier, _ = fr.load(entry, root)
    params = frontier["params"]
    c_max, y = params["c_max"], params["smooth_bound"]
    min_q = params["min_quality"]
    top_n = max(20, min(200, params["max_records"]))
    start = time.time()
    deadline = start + float(seconds)

    rad = sieve_radical(c_max)
    smooth = smooth_upto(y, c_max)
    layout = pair_layout(smooth, c_max)

    reports: dict = {}
    candidates: dict = {}
    helpers = {
        "c_smooth": lambda lo, hi, dl: scan_c_smooth(
            rad, smooth, lo, hi, c_max, min_quality=min_q, top_n=top_n, deadline=dl),
        "legs_smooth": lambda lo, hi, dl: scan_legs_smooth(
            rad, layout, lo, hi, min_quality=min_q, top_n=top_n, deadline=dl),
    }
    limits = {
        "c_smooth": c_max // 2 + 1,
        "legs_smooth": int(layout["total"]),
    }

    order = ("legs_smooth", "c_smooth")
    for name in order:
        state = frontier["families"][name]
        cursor, width = int(state["next"]), int(state["width"])
        lo, hi = _slice(cursor, width, shard, of)
        hi = min(hi, limits[name])
        if state.get("exhausted") or lo >= limits[name]:
            reports[name] = {"range": [lo, min(hi, limits[name])], "next": limits[name],
                             "complete": True, "exhausted": True,
                             "tested": 0, "kept": 0, "best_q": 0.0}
            continue
        now = time.time()
        if now >= deadline:
            res = {"next": lo, "complete": False, "tested": 0, "kept": 0,
                   "best_q": 0.0, "candidates": []}
        else:
            if name == "legs_smooth":
                fam_deadline = min(deadline, now + 0.25 * (deadline - now))
            else:
                fam_deadline = max(now, deadline - 5.0)
            res = helpers[name](lo, hi, fam_deadline)
        reports[name] = {"range": [lo, hi], "next": int(res["next"]),
                         "complete": bool(res["complete"]), "tested": int(res["tested"]),
                         "kept": int(res["kept"]), "best_q": float(res["best_q"]),
                         "exhausted": False}
        for rec in res["candidates"]:
            rec = dict(rec)
            rec["family"] = name
            candidates[(rec["a"], rec["b"], rec["c"])] = rec

    data = {
        "problem": pid, "kind": "abc", "scheduler": True,
        "shard": int(shard), "of": int(of), "params": fr.identity(params),
        "families": reports,
        "candidates": sorted(candidates.values(),
                             key=lambda r: (-r["q"], r["c"], r["a"], r["b"])),
        "seconds_budget": float(seconds),
        "elapsed_s": round(time.time() - start, 1),
        "host": platform.node(),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(out, "shards", f"{pid}__shard_{shard:03d}_of_{of:03d}.json")
    save_json(path, data)
    total_kept = sum(r["kept"] for r in reports.values())
    print(f"[abc shard {shard}/{of}] candidates {len(data['candidates'])}, kept {total_kept}, "
          f"{data['elapsed_s']} s -> {path}")
    return data
