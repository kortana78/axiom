"""Persistent search frontier for the ABC triple hunter."""
from __future__ import annotations

import copy
import os

from ..swarm.common import load_json, save_json

FAMILIES = ("c_smooth", "legs_smooth")

DEFAULT_SEARCH = {
    "c_max": 100_000_000,
    "smooth_bound": 23,
    "min_quality": 1.2,
    "max_records": 200,
    "families": {
        "c_smooth": {"width": 240_000},
        "legs_smooth": {"width": 300_000_000},
    },
}

MAX_C_MAX = 150_000_000


def search_params(entry: dict) -> dict:
    raw = dict(DEFAULT_SEARCH)
    raw.update(entry.get("search", {}) or {})
    c_max = int(raw["c_max"])
    if c_max < 10 or c_max > MAX_C_MAX:
        raise SystemExit(f"abc: c_max must be between 10 and {MAX_C_MAX}")
    y = int(raw["smooth_bound"])
    if y < 2 or y > 97:
        raise SystemExit("abc: smooth_bound must be between 2 and 97")
    families = {}
    for name in FAMILIES:
        cfg = (raw.get("families") or {}).get(name, {})
        width = int(cfg.get("width", DEFAULT_SEARCH["families"][name]["width"]))
        families[name] = {"width": max(1, width)}
    return {
        "c_max": c_max,
        "smooth_bound": y,
        "min_quality": float(raw.get("min_quality", 1.2)),
        "max_records": max(1, int(raw.get("max_records", 200))),
        "families": families,
        "ideas_c_max": min(c_max, max(10, int(raw.get("ideas_c_max", 10_000_000)))),
    }


def identity(params: dict) -> dict:
    """Parameters that determine the coordinate system of the cursors."""
    return {k: params[k] for k in ("c_max", "smooth_bound", "min_quality")}


def initial(entry: dict) -> dict:
    params = search_params(entry)
    return {
        "kind": "abc",
        "params": params,
        "families": {
            name: {"next": 1 if name == "c_smooth" else 0,
                   "width": params["families"][name]["width"],
                   "exhausted": False}
            for name in FAMILIES
        },
        "batch": 0,
    }


def load(entry: dict, root: str) -> tuple[dict, bool]:
    """Load the frontier, resetting it if the queue's parameters changed."""
    out = os.path.join(root, entry["id"])
    fresh = initial(entry)
    old = load_json(os.path.join(out, "frontier.json"), None)
    if not old or old.get("kind") != "abc":
        return fresh, True
    try:
        same = identity(old.get("params") or {}) == identity(fresh["params"])
    except KeyError:
        same = False
    if not same:
        return fresh, True
    merged = copy.deepcopy(fresh)
    merged["batch"] = int(old.get("batch", 0))
    for name in FAMILIES:
        if name in (old.get("families") or {}):
            st = old["families"][name]
            merged["families"][name]["next"] = max(0, int(st.get("next", 0)))
            merged["families"][name]["width"] = max(1, int(st.get("width", merged["families"][name]["width"])))
            merged["families"][name]["exhausted"] = bool(st.get("exhausted", False))
    return merged, False


def save(entry: dict, frontier: dict, root: str) -> None:
    out = os.path.join(root, entry["id"])
    save_json(os.path.join(out, "frontier.json"), frontier)
