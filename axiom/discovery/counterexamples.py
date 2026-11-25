"""Counterexample engine: fast falsification before expensive proof."""
from __future__ import annotations

import random
from fractions import Fraction
from itertools import product
from typing import Dict, Optional

from ..kernel.proof_objects import Proof
from ..kernel.propositions import BoundedForAll, ForAll, Prop, strip_forall


def find_counterexample(prop: Prop, small: int = 40, randoms: int = 60, big: int = 10 ** 6,
                        seed: int = 0) -> Optional[Dict[str, int]]:
    """Search for an assignment that falsifies a (possibly nested) ForAll.
    Returns the assignment or None. Unevaluable instances are skipped."""
    binders, body = strip_forall(prop)
    if not binders:
        try:
            return None if prop.evaluate({}) else {}
        except Exception:
            return None
    rng = random.Random(seed)
    key = prop.key()
    if "Sum[" in key or "(" in key and any(t in key for t in ("collatz", "es_rep", "prime_between", "quasiperfect", "sigma")):
        big = min(big, 400)          # these are expensive to evaluate at huge n
    if _has_sequence(prop):
        big = min(big, 300)
    per_var = max(3, int(small ** (1 / len(binders))) + 1)
    pools = []
    for var, lower in binders:
        vals = list(range(lower, lower + per_var))
        vals += [rng.randint(lower, lower + big) for _ in range(max(1, randoms // len(binders)))]
        pools.append(vals)
    for combo in product(*pools):
        env = {var.name: Fraction(v) for (var, _), v in zip(binders, combo)}
        try:
            if not body.evaluate(env):
                return {var.name: v for (var, _), v in zip(binders, combo)}
        except Exception:
            continue
    return None


def _has_sequence(prop) -> bool:
    from ..kernel.expressions import SeqTerm
    found = []

    def walk(x):
        if isinstance(x, SeqTerm):
            found.append(x)
            return
        for attr in getattr(x, "__dataclass_fields__", {}):
            v = getattr(x, attr)
            if isinstance(v, tuple):
                for item in v:
                    walk(item)
            elif hasattr(v, "__dataclass_fields__"):
                walk(v)
    walk(prop)
    return bool(found)


def bounded_proof(prop: Prop, hi: int) -> Optional[Proof]:
    """Kernel-checkable proof that a single-variable ForAll holds up to hi."""
    if not isinstance(prop, ForAll) or isinstance(prop.body, ForAll):
        return None
    stmt = BoundedForAll(prop.var, prop.lower, hi, prop.body)
    return Proof("finite_check", stmt)
