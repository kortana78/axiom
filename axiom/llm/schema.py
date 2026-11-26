"""Strict validation for LLM-generated ideas.

Witness ideas use the same schema as ``swarm/ideas.json``.  S-unit heuristics
use a separate schema.  ABC search ideas are an extra, narrow schema.  Invalid
entries are dropped and reported; they are never executed or committed.
"""
from __future__ import annotations

import json
from typing import Iterable, List, Optional

from ..ideas.space import ATOM_KINDS

SUNIT_METHODS = (
    "mod_q", "lll", "p_adic_log", "sieving", "banding", "height_bound",
    "linear_forms", "other",
)


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def _int_in(value, lo: int, hi: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{name} must be an integer")
    if not (lo <= value <= hi):
        raise ValueError(f"{name} must be in [{lo}, {hi}]")
    return value


def _str_list(value, name: str, lo: int, hi: int) -> List[str]:
    if not isinstance(value, list) or not all(isinstance(x, str) for x in value):
        raise ValueError(f"{name} must be a list of strings")
    if not (lo <= len(value) <= hi):
        raise ValueError(f"{name} must have length {lo}..{hi}")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} must not repeat entries")
    return list(value)


def validate_witness_idea(d: dict, var_names: Optional[Iterable[str]] = None) -> dict:
    if not isinstance(d, dict):
        raise ValueError("idea must be an object")
    order = _str_list(d.get("order"), "order", 1, 8)
    if var_names is not None and (len(order) != len(list(var_names))
                                  or set(order) != set(var_names)):
        raise ValueError(f"order must be a permutation of {sorted(var_names)}")
    atoms = _str_list(d.get("atoms"), "atoms", 1, len(ATOM_KINDS))
    if not set(atoms) <= set(ATOM_KINDS):
        raise ValueError(f"atoms must be a subset of {ATOM_KINDS}")
    mult = d.get("mult", [1])
    if not isinstance(mult, list) or not mult:
        raise ValueError("mult must be a non-empty list")
    mult = [_int_in(x, 1, 12, "mult entry") for x in mult]
    T = _int_in(d.get("T", 40), 1, 100000, "T")
    D = _int_in(d.get("D", 24), 1, 100000, "D")
    tie = d.get("tie", False)
    if not isinstance(tie, bool):
        raise ValueError("tie must be a boolean")
    note = d.get("note", "")
    if not isinstance(note, str) or len(note) > 500:
        raise ValueError("note must be a string of at most 500 characters")
    return {
        "order": order, "atoms": atoms, "mult": mult, "T": T, "D": D,
        "tie": tie, "note": note,
    }


def validate_sunit_heuristic(d: dict) -> dict:
    if not isinstance(d, dict):
        raise ValueError("heuristic must be an object")
    S = d.get("S")
    if not isinstance(S, list) or not (1 <= len(S) <= 16):
        raise ValueError("S must be a list of 1..16 primes")
    if not all(isinstance(p, int) and not isinstance(p, bool) and _is_prime(p) for p in S):
        raise ValueError("S must contain primes only")
    if len(set(S)) != len(S):
        raise ValueError("S must not repeat primes")
    S = sorted(S)
    method = d.get("method")
    if method not in SUNIT_METHODS:
        raise ValueError(f"method must be one of {SUNIT_METHODS}")
    q = d.get("q")
    if q is not None:
        q = _int_in(q, 2, max(S), "q")
        if q not in S:
            raise ValueError("q must be in S")
    params = d.get("parameters", {})
    if not isinstance(params, dict) or len(params) > 20:
        raise ValueError("parameters must be an object with at most 20 keys")
    clean_params = {}
    for k, v in params.items():
        if not isinstance(k, str) or len(k) > 40:
            raise ValueError("parameter names must be short strings")
        if isinstance(v, list):
            if len(v) > 20 or not all(isinstance(x, (int, float, str, bool)) for x in v):
                raise ValueError("parameter lists must be short scalar lists")
        elif not isinstance(v, (int, float, str, bool)) and v is not None:
            raise ValueError("parameter values must be scalars")
        clean_params[k] = v
    priority = _int_in(d.get("priority", 3), 1, 5, "priority")
    rationale = d.get("rationale", "")
    if not isinstance(rationale, str) or len(rationale) > 1000:
        raise ValueError("rationale must be a string of at most 1000 characters")
    return {
        "S": S, "method": method, "q": q, "parameters": clean_params,
        "priority": priority, "rationale": rationale,
    }


def validate_abc_idea(d: dict) -> dict:
    if not isinstance(d, dict):
        raise ValueError("abc idea must be an object")
    family = d.get("family")
    if family not in ("c_smooth", "legs_smooth"):
        raise ValueError("family must be c_smooth or legs_smooth")
    smooth_bound = _int_in(d.get("smooth_bound", 23), 2, 97, "smooth_bound")
    if not _is_prime(smooth_bound) and smooth_bound not in (4, 8, 9, 16, 25, 27, 32, 49, 64, 81):
        raise ValueError("smooth_bound must be a small prime or prime power")
    window = _int_in(d.get("window", 100000), 1, 1_000_000_000, "window")
    min_quality = d.get("min_quality", 1.2)
    if not isinstance(min_quality, (int, float)) or not (1.0 <= float(min_quality) <= 5.0):
        raise ValueError("min_quality must be in [1, 5]")
    note = d.get("note", "")
    if not isinstance(note, str) or len(note) > 500:
        raise ValueError("note must be a string of at most 500 characters")
    return {
        "family": family, "smooth_bound": smooth_bound, "window": window,
        "min_quality": float(min_quality), "note": note,
    }


def validate_payload_report(payload, kind: str,
                            var_names: Optional[Iterable[str]] = None):
    if kind == "witness":
        items = payload.get("ideas", []) if isinstance(payload, dict) else payload
        validator = lambda d: validate_witness_idea(d, var_names)
    elif kind == "sunit":
        items = payload.get("heuristics", []) if isinstance(payload, dict) else payload
        validator = validate_sunit_heuristic
    elif kind == "abc":
        items = payload.get("ideas", []) if isinstance(payload, dict) else payload
        validator = validate_abc_idea
    else:
        raise ValueError(f"unknown idea kind {kind}")
    if not isinstance(items, list):
        raise ValueError("payload must contain a list")
    out, errors = [], []
    for i, item in enumerate(items):
        try:
            out.append(validator(item))
        except (ValueError, TypeError) as exc:
            errors.append(f"item {i}: {exc}")
    return out, errors


def validate_payload(payload, kind: str, var_names: Optional[Iterable[str]] = None) -> List[dict]:
    return validate_payload_report(payload, kind, var_names)[0]


def schema_text(kind: str) -> str:
    if kind == "witness":
        return json.dumps({
            "ideas": [{
                "order": ["x", "y", "z"], "atoms": ["n", "nv"],
                "mult": [1, 2], "T": 80, "D": 48, "tie": False,
                "note": "short reason",
            }]
        }, indent=2)
    if kind == "sunit":
        return json.dumps({
            "heuristics": [{
                "S": [2, 3, 5, 7], "method": "p_adic_log", "q": 2,
                "parameters": {"precision": 30}, "priority": 3,
                "rationale": "short reason",
            }]
        }, indent=2)
    return json.dumps({
        "ideas": [{
            "family": "legs_smooth", "smooth_bound": 23,
            "window": 300000000, "min_quality": 1.2,
            "note": "short reason",
        }]
    }, indent=2)
