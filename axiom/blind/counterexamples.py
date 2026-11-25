"""Generic counterexample search for the blind engine.

The 0.1 counterexample engine contains hard-coded names of particular open
problems to cap expensive evaluations. Blind 0.2 deliberately does not: cost
is estimated from measured evaluation time instead, so the engine has no
problem-specific knowledge here.
"""
from __future__ import annotations

import random
import time
from fractions import Fraction
from itertools import product
from typing import Dict, Optional

from ..kernel.proof_objects import Proof
from ..kernel.propositions import BoundedForAll, ForAll, Prop, strip_forall


def find_counterexample(prop: Prop, small: int = 40, randoms: int = 40,
                        big: int = 10 ** 4, seed: int = 0,
                        time_limit: float = 1.5) -> Optional[Dict[str, int]]:
    binders, body = strip_forall(prop)
    if not binders:
        try:
            return None if prop.evaluate({}) else {}
        except Exception:
            return None
    rng = random.Random(seed)
    per_var = max(3, int(small ** (1 / len(binders))) + 1)
    pools = []
    for var, lower in binders:
        vals = list(range(lower, lower + per_var))
        vals += [rng.randint(lower, lower + big) for _ in range(max(1, randoms // len(binders)))]
        pools.append(vals)

    start = time.time()
    checks = 0
    for combo in product(*pools):
        if time.time() - start > time_limit:
            return None
        env = {var.name: Fraction(v) for (var, _), v in zip(binders, combo)}
        try:
            checks += 1
            if checks > 8 and time.time() - start > time_limit:
                return None
            if not body.evaluate(env):
                return {var.name: v for (var, _), v in zip(binders, combo)}
        except Exception:
            continue
    return None


def bounded_proof(prop: Prop, hi: int) -> Optional[Proof]:
    if not isinstance(prop, ForAll) or isinstance(prop.body, ForAll):
        return None
    return Proof("finite_check", BoundedForAll(prop.var, prop.lower, hi, prop.body))
