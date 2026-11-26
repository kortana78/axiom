"""Idea-generator mode for ABC: a small portfolio search over families.

The worker follows the persistent frontier. The idea job deliberately
explores other smoothness bounds and random windows, then writes candidates
as an ordinary untrusted shard. Scores persist in ideas_log.json so later
runs can favour families that produced high-quality triples.
"""
from __future__ import annotations

import math
import os
import random
import time

from ..swarm.common import load_json, results_dir, save_json
from . import frontier as fr
from .hunt import (pair_layout, scan_c_smooth, scan_legs_smooth, sieve_radical,
                   smooth_upto)


def _ucb(stats: dict, key: str, total: int) -> float:
    s = stats.get(key)
    if not s or s.get("tries", 0) == 0:
        return float("inf")
    return s.get("reward", 0.0) / s["tries"] + math.sqrt(
        2 * math.log(max(total, 2)) / s["tries"])


def run(entry: dict, seconds: float, root: str = "results", tag: str = "ideas",
        seed: float | None = None) -> dict:
    pid = entry["id"]
    out = results_dir(root, pid)
    params = fr.search_params(entry)
    c_max = int(params["ideas_c_max"])
    min_q = params["min_quality"]
    deadline = time.time() + float(seconds)
    start = time.time()
    rng = random.Random(seed if seed is not None else time.time())
    log = load_json(os.path.join(out, "ideas_log.json"),
                    {"tried": {}, "families": {}, "winners": []})
    for key, default in (("tried", {}), ("families", {}), ("winners", [])):
        log.setdefault(key, default)

    ys = sorted({2, 3, 5, 7, 11, 13, 17, 19, 23, params["smooth_bound"]})
    variants = [{"mode": mode, "y": y, "c_max": c_max}
                for mode in ("c_smooth", "legs_smooth") for y in ys if y <= 97]
    attempts = []
    candidates = {}
    rad = sieve_radical(c_max)
    smooth_cache: dict = {}
    layout_cache: dict = {}

    while time.time() < deadline - 2:
        total_tries = sum(int(s.get("tries", 0)) for s in log["families"].values())
        scored = sorted(variants, key=lambda v: -_ucb(
            log["families"], f"abc:{v['mode']}:y={v['y']}", total_tries))
        variant = rng.choice(scored[:3])
        y, mode = int(variant["y"]), variant["mode"]
        smooth = smooth_cache.get(y)
        if smooth is None:
            smooth = smooth_cache[y] = smooth_upto(y, c_max)
        remaining = max(1.0, deadline - time.time())
        attempt_deadline = min(deadline - 1.0, time.time() + max(3.0, remaining * 0.35))
        if mode == "c_smooth":
            hi_limit = c_max // 2 + 1
            width = min(hi_limit, max(2000, int(remaining * 500)))
            lo = rng.randint(1, max(1, hi_limit - width))
            res = scan_c_smooth(rad, smooth, lo, min(hi_limit, lo + width), c_max,
                                min_quality=min_q, top_n=100, deadline=attempt_deadline)
            window = [lo, min(hi_limit, lo + width)]
        else:
            layout = layout_cache.get(y)
            if layout is None:
                layout = layout_cache[y] = pair_layout(smooth, c_max)
            total = int(layout["total"])
            if total <= 0:
                continue
            width = min(total, max(1_000_000, total // 40))
            lo = rng.randint(0, max(0, total - width))
            res = scan_legs_smooth(rad, layout, lo, min(total, lo + width),
                                   min_quality=min_q, top_n=100, deadline=attempt_deadline)
            window = [lo, min(total, lo + width)]
        key = f"abc:{mode}:y={y}"
        fam = log["families"].setdefault(key, {"tries": 0, "reward": 0.0, "hits": 0})
        fam["tries"] += 1
        fam["reward"] += float(res["best_q"])
        fam["hits"] += int(res["kept"])
        log["tried"][key] = {
            "hits": int(res["kept"]), "tested": int(res["tested"]),
            "seconds": round(time.time() - (deadline - remaining), 1),
            "source": "abc", "note": f"{mode}, smooth_bound={y}, c_max={c_max}",
        }
        attempts.append({"mode": mode, "y": y, "window": window,
                         "tested": int(res["tested"]), "kept": int(res["kept"]),
                         "best_q": float(res["best_q"]), "complete": bool(res["complete"])})
        if res["kept"]:
            log["winners"] = (log["winners"] + [{
                "mode": mode, "y": y, "c_max": c_max, "source": "abc"}])[-50:]
        for rec in res["candidates"]:
            rec = dict(rec)
            rec["family"] = key
            candidates[(rec["a"], rec["b"], rec["c"])] = rec

    save_json(os.path.join(out, "ideas_log.json"), log)
    data = {
        "problem": pid, "kind": "abc", "scheduler": False,
        "source": "abc ideas", "params": fr.identity(params),
        "candidates": sorted(candidates.values(),
                             key=lambda r: (-r["q"], r["c"], r["a"], r["b"])),
        "attempts": attempts,
        "elapsed_s": round(time.time() - start, 1),
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(out, "shards", f"{pid}__{tag}_{int(start)}.json")
    save_json(path, data)
    print(f"[abc ideas {pid}] {len(attempts)} attempts, {len(data['candidates'])} candidates "
          f"-> {path}")
    return data
