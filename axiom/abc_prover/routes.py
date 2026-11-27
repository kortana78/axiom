"""Load and summarize the honest abc route graph."""
from __future__ import annotations

import json
from typing import Dict, List

from . import ROUTES_PATH


def load_routes(path: str = ROUTES_PATH) -> Dict[str, object]:
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("routes file must be a JSON object")
    nodes = data.get("nodes")
    if not isinstance(nodes, dict) or not nodes:
        raise ValueError("routes file must contain a non-empty `nodes` object")
    edges = data.get("edges", [])
    if not isinstance(edges, list):
        raise ValueError("routes `edges` must be a list")
    return data


def route_names(routes: Dict[str, object]) -> List[str]:
    return sorted(str(k) for k in (routes.get("nodes") or {}))


def route_brief(routes: Dict[str, object]) -> List[dict]:
    out: List[dict] = []
    for name, node in (routes.get("nodes") or {}).items():
        if not isinstance(node, dict):
            node = {}
        out.append({
            "name": name,
            "kind": node.get("kind", ""),
            "status": node.get("status", ""),
            "note": node.get("note", ""),
        })
    return out


def open_gaps(routes: Dict[str, object]) -> List[str]:
    """Nodes that are not known theorems or formalized foundations."""
    gaps: List[str] = []
    for name, node in (routes.get("nodes") or {}).items():
        if not isinstance(node, dict):
            continue
        if node.get("status") not in ("known", "formalized"):
            gaps.append(str(name))
    return sorted(gaps)
