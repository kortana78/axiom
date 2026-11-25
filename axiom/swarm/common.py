"""Shared helpers for the AXIOM swarm (workers, merge, dashboard)."""
from __future__ import annotations

import json
import math
import os
from typing import List

import sympy as sp

from ..blind.problem import parse_prop
from ..blind.witness import Engine, detect
from ..kernel.inference import scaling_homogeneous


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path, data):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, default=str)
    os.replace(tmp, path)


def load_queue(path="swarm/queue.json"):
    return load_json(path, {"problems": []})["problems"]


def find_problem(queue, pid):
    for p in queue:
        if p["id"] == pid:
            return p
    raise SystemExit(f"problem {pid} not in queue")


class Setup:
    """Parsed problem: goal, witness engine, and which residues matter."""

    def __init__(self, entry: dict):
        self.entry = entry
        self.goal = parse_prop(entry["statement"])
        shape = detect(self.goal)
        if shape is None:
            raise SystemExit("swarm currently supports: forall n: exists v...: equation")
        self.engine = Engine(shape)
        ok, _ = scaling_homogeneous(self.goal)
        self.prime_mode = ok and self.goal.lower == 2

    def relevant(self, M: int) -> List[int]:
        """Residues that must be covered: all, or only prime-bearing ones
        when the kernel's scaling symmetry rule applies."""
        if not self.prime_mode:
            return list(range(M))
        return [r for r in range(M) if math.gcd(r, M) == 1 or (sp.isprime(r) and M % r == 0)]

    def schedule(self, M: int) -> List[int]:
        mods = [m for m in self.engine.moduli(limit=M) if M % m == 0]
        if M not in mods:
            mods.append(M)
        return mods


def parse_polys(polys):
    k = sp.Symbol("k", integer=True)
    return [sp.expand(sp.sympify(p, locals={"k": k})) for p in polys]


def results_dir(root, pid):
    return os.path.join(root, pid)
