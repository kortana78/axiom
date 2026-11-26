"""Merge ABC hunter shards: re-verify every triple exactly, keep records.

Trust model: shard files are untrusted. A triple counts only if gcd, the
additive relation and the radical all re-check from scratch. Quality is
computed by the merger, never taken from a shard.
"""
from __future__ import annotations

import glob
import os
import time

from ..swarm.common import load_json, results_dir, save_json
from . import frontier as fr
from . import lean_export
from .hunt import make_record, pair_layout, smooth_upto, verify_record


def _limit(name: str, c_max: int, y: int) -> int:
    if name == "c_smooth":
        return c_max // 2 + 1
    return int(pair_layout(smooth_upto(y, c_max), c_max)["total"])


def _advance(frontier: dict, reports: dict, limits: dict) -> list[str]:
    """Advance cursors only when every shard of the batch finished its slice."""
    notes = []
    for name, state in frontier["families"].items():
        if state.get("exhausted"):
            continue
        rows = [r for r in reports.get(name, []) if r.get("params_ok")]
        if not rows:
            continue
        ofs = {int(r["of"]) for r in rows}
        of = next(iter(ofs)) if len(ofs) == 1 else None
        shard_ids = {int(r["shard"]) for r in rows}
        complete = (of is not None and shard_ids == set(range(of))
                    and all(bool(r["report"].get("complete")) for r in rows))
        cursor = int(state["next"])
        width = int(state["width"])
        expected_hi = min(cursor + width, limits[name])
        covered_hi = max(int(r["report"].get("range", [0, 0])[1]) for r in rows)
        if complete and covered_hi >= expected_hi:
            state["next"] = expected_hi
            budget = max(float(r["budget"]) for r in rows) or 1.0
            slow = any(float(r["elapsed"]) > 0.9 * budget for r in rows)
            if not slow:
                width = min(int(width * 1.2), 5_000_000_000 if name == "legs_smooth" else 5_000_000)
            state["width"] = max(1, width)
            if state["next"] >= limits[name]:
                state["exhausted"] = True
                notes.append(f"{name} exhausted")
            else:
                notes.append(f"{name} advanced to {state['next']}")
        else:
            floor = 1_000_000 if name == "legs_smooth" else 100
            state["width"] = max(floor, int(width * 0.7))
            notes.append(f"{name} incomplete; width {width} -> {state['width']}")
    return notes


def run(entry: dict, root: str = "results") -> dict:
    pid = entry["id"]
    out = results_dir(root, pid)
    old_status = load_json(os.path.join(out, "status.json"), {}) or {}
    frontier, reset = fr.load(entry, root)
    params = frontier["params"]
    c_max, y = params["c_max"], params["smooth_bound"]
    min_q, max_records = params["min_quality"], params["max_records"]
    limits = {
        "c_smooth": c_max // 2 + 1,
        "legs_smooth": _limit("legs_smooth", c_max, y),
    }

    candidates: list = []
    reports: dict = {}
    rejected = 0
    processed = 0
    for path in sorted(glob.glob(os.path.join(out, "shards", "*.json"))):
        d = load_json(path, {}) or {}
        if d.get("kind") != "abc" or d.get("problem") != pid:
            continue
        processed += 1
        for raw in d.get("candidates", []) or []:
            rec = verify_record(raw)
            if rec is None:
                rejected += 1
            else:
                candidates.append(rec)
        data_params = d.get("params") or {}
        params_ok = data_params == fr.identity(params)
        if d.get("scheduler") and params_ok:
            for name, rep in (d.get("families") or {}).items():
                reports.setdefault(name, []).append({
                    "shard": d.get("shard"), "of": d.get("of"),
                    "report": rep, "params_ok": True,
                    "budget": d.get("seconds_budget", 1.0),
                    "elapsed": d.get("elapsed_s", 0.0),
                })

    old_records = []
    old_keys = set()
    for raw in load_json(os.path.join(out, "records.json"), []) or []:
        rec = verify_record(raw)
        if rec is not None:
            old_records.append(rec)
            old_keys.add((rec["a"], rec["b"], rec["c"]))
        else:
            rejected += 1

    by_key = {}
    for rec in old_records + candidates:
        key = (rec["a"], rec["b"], rec["c"])
        if key not in by_key or rec["q"] > by_key[key]["q"]:
            by_key[key] = rec

    records = [r for r in by_key.values() if r["q"] >= min_q]
    records.sort(key=lambda r: (-r["q"], r["c"], r["a"], r["b"]))
    records = records[:max_records]

    notes = _advance(frontier, reports, limits)
    if processed:
        frontier["batch"] = int(frontier.get("batch", 0)) + 1
    fr.save(entry, frontier, root)
    save_json(os.path.join(out, "records.json"), records)
    lean_export.write(records, os.path.join(out, "lean"), pid, entry["statement"])

    best = records[0] if records else None
    new_records = sum(1 for r in records
                      if (r["a"], r["b"], r["c"]) not in old_keys)
    hist = old_status.get("history", [])
    hist.append({
        "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "shards_merged": processed,
        "candidates": len(candidates),
        "rejected": rejected,
        "records": len(records),
        "new_records": new_records,
        "best_q": best["q"] if best else 0.0,
        "note": "; ".join(notes) if notes else ("frontier reset" if reset else ""),
    })
    status = {
        "problem": pid,
        "kind": "abc",
        "statement": entry["statement"],
        "status": (f"search only: {len(records)} verified triples; "
                   f"best q={best['q']:.6f}; no proof of abc"),
        "mode": "abc_triple_hunt",
        "records_verified": len(records),
        "best_q": best["q"] if best else 0.0,
        "best_triple": best,
        "searched": {"c_max": c_max, "smooth_bound": y, "min_quality": min_q},
        "cursors": {name: dict(st) for name, st in frontier["families"].items()},
        "batch": frontier["batch"],
        "history": hist[-200:],
        "next_frontier": dict(fr.identity(params)),
    }
    save_json(os.path.join(out, "status.json"), status)

    for path in sorted(glob.glob(os.path.join(out, "shards", "*.json"))):
        os.remove(path)

    print(f"[merge {pid}] {len(records)} records, {len(candidates)} candidates, "
          f"{rejected} rejected, best q={(best['q'] if best else 0.0):.6f}; "
          f"{'; '.join(notes) if notes else 'no cursor change'}")
    return status
