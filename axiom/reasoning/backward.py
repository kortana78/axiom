"""Backward reasoning: tactics that close a goal or split it into subgoals.

A tactic returns a list whose items are either a finished Proof (already
accepted by the kernel) or an Alternative (subgoals plus a way to build
the proof once the subgoals are proved). The search engine decides order.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Union

import sympy as sp

from ..kernel.expressions import Const, Var
from ..kernel.inference import Kernel, class_instance
from ..kernel.proof_objects import Proof
from ..kernel.propositions import (Prop, And, ForAll, Exists, Divides, Le, Lt,
                                   BoundedForAll, Eq, strip_forall)

DIRECT_RULES = [
    "algebraic_identity", "residue_divisibility", "sum_induction",
    "shift_nonneg", "exp_induction", "finite_check", "sequence_closed_form",
    "recurrence_mod_invariant", "collatz_descent_auto",
]


@dataclass
class Alternative:
    name: str
    subgoals: List[Prop]
    build: Callable[[List[Proof]], Proof]


@dataclass
class TacticContext:
    kernel: Kernel
    known: Dict[str, Proof] = field(default_factory=dict)     # proved results
    hints: Dict[str, List[Proof]] = field(default_factory=dict)  # proofs with invented data
    witnesses: Dict[str, list] = field(default_factory=dict)  # invented Exists witnesses
    failures: list = field(default_factory=list)
    residue_moduli: tuple = ()

    def fail(self, goal, tactic, reason):
        self.failures.append((goal.key(), tactic, reason))


Outcome = Union[Proof, Alternative]


def t_known(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    p = ctx.known.get(goal.key())
    return [p] if p else []


def t_direct(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    for r in DIRECT_RULES:
        if r == "collatz_descent_auto":
            continue
        proof = Proof(r, goal)
        ok, msg = ctx.kernel.check(proof)
        if ok:
            proof.data["kernel"] = msg
            return [proof]
        if not msg.startswith(r + ": ") and "shape" not in msg:
            ctx.fail(goal, r, msg)
    return []


def t_hints(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    out = []
    for proof in ctx.hints.get(goal.key(), []):
        ok, msg = ctx.kernel.check(proof)
        if ok:
            out.append(proof)
        else:
            ctx.fail(goal, "hint:" + proof.rule, msg)
    return out


def t_split_and(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    if isinstance(goal, And):
        return [Alternative("and_intro", list(goal.parts),
                            lambda ps, g=goal: Proof("and_intro", g, ps))]
    if isinstance(goal, ForAll) and isinstance(goal.body, And):
        subs = [ForAll(goal.var, part, goal.lower) for part in goal.body.parts]
        return [Alternative("forall_and", subs, lambda ps, g=goal: Proof("forall_and", g, ps))]
    return []


def t_factor_divisor(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    if not isinstance(goal, ForAll) or not isinstance(goal.body, Divides):
        return []
    d = goal.body.d
    if not isinstance(d, Const) or d.value.denominator != 1:
        return []
    f = sp.factorint(int(d.value))
    if len(f) < 2:
        return []
    p, a = next(iter(f.items()))
    d1, d2 = p ** a, int(d.value) // p ** a
    s1 = ForAll(goal.var, Divides(Const(d1), goal.body.e), goal.lower)
    s2 = ForAll(goal.var, Divides(Const(d2), goal.body.e), goal.lower)
    return [Alternative("divisibility_combine", [s1, s2],
                        lambda ps, g=goal: Proof("divisibility_combine", g, ps))]


def t_range_split(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    """If the inequality only becomes provable from some later point M,
    check [L, M-1] finitely and prove the tail."""
    if not isinstance(goal, ForAll) or not isinstance(goal.body, (Le, Lt, Eq, Divides)):
        return []
    out = []
    for M in range(goal.lower + 1, goal.lower + 25):
        tail = ForAll(goal.var, goal.body, M)
        for r in ("shift_nonneg", "exp_induction"):
            ok, _ = ctx.kernel.check(Proof(r, tail))
            if ok:
                fin = BoundedForAll(goal.var, goal.lower, M - 1, goal.body)
                out.append(Alternative("range_split", [fin, tail],
                                       lambda ps, g=goal: Proof("range_split", g, ps)))
                return out
    return out


def t_exists_witness(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    if not (isinstance(goal, ForAll) and isinstance(goal.body, Exists)):
        return []
    out = []
    ex = goal.body
    for w in ctx.witnesses.get(goal.key(), []):
        s1 = ForAll(goal.var, ex.body.subst({ex.var.name: w}), goal.lower)
        s2 = ForAll(goal.var, Le(Const(ex.lower), w), goal.lower)
        out.append(Alternative("forall_exists_witness", [s1, s2],
                               lambda ps, g=goal, w=w: Proof("forall_exists_witness", g, ps, {"witness": w})))
    return out


def t_residue_split(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    if not isinstance(goal, ForAll) or isinstance(goal.body, (ForAll,)):
        return []
    out = []
    for m in ctx.residue_moduli:
        subs = []
        for r in range(m):
            first = goal.lower + ((r - goal.lower) % m)
            lo = (first - r) // m
            subs.append(ForAll(Var("k", goal.var.typ), class_instance(goal.body, goal.var, m, r), lo))
        out.append(Alternative(f"residue_split_{m}", subs,
                               lambda ps, g=goal, m=m: Proof("residue_split", g, ps, {"modulus": m})))
    return out


DEFAULT_TACTICS = [t_known, t_hints, t_direct, t_split_and, t_exists_witness,
                   t_factor_divisor, t_range_split, t_residue_split]
