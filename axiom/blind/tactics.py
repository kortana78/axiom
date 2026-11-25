"""Tactics available to the blind engine.

These are the general inference routes only. Problem-specific rules (parity
descent, explicit residue-class families, etc.) are outside the allowlist; a
proof that uses one is rejected by the controller even if the kernel would
accept it.
"""
from __future__ import annotations

from typing import List, Union

from ..kernel.inference import Kernel, class_instance
from ..kernel.proof_objects import Proof
from ..kernel.propositions import (And, BoundedForAll, Divides, Exists, ForAll,
                                   Prop, Var)
from ..reasoning.backward import (Alternative, TacticContext, t_known, t_hints,
                                  t_split_and, t_exists_witness,
                                  t_factor_divisor, t_range_split)

BLIND_ALLOWED_RULES = frozenset({
    "given", "algebraic_identity", "residue_divisibility", "sum_induction",
    "shift_nonneg", "exp_induction", "finite_check", "instantiate",
    "and_intro", "forall_and", "divisibility_combine", "forall_exists_witness",
    "residue_split", "sequence_closed_form", "recurrence_invariant",
    "recurrence_mod_invariant", "range_split", "residue_cover", "prime_reduction",
})

Outcome = Union[Proof, Alternative]


def blind_t_direct(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    """Try each general rule that can close the goal directly."""
    for rule in ("algebraic_identity", "residue_divisibility", "sum_induction",
                 "shift_nonneg", "exp_induction", "finite_check",
                 "sequence_closed_form", "recurrence_mod_invariant"):
        proof = Proof(rule, goal)
        ok, msg = ctx.kernel.check(proof)
        if ok:
            proof.data["kernel"] = msg
            return [proof]
        if not msg.startswith(rule + ": ") and "shape" not in msg:
            ctx.fail(goal, rule, msg)
    return []


def blind_t_residue_split(goal: Prop, ctx: TacticContext) -> List[Outcome]:
    """Split into residue classes using moduli discovered from the problem."""
    if not isinstance(goal, ForAll) or isinstance(goal.body, ForAll):
        return []
    out = []
    for m in ctx.residue_moduli:
        m = int(m)
        if m < 2 or m > 64:
            continue
        subs = []
        for r in range(m):
            first = goal.lower + ((r - goal.lower) % m)
            lo = (first - r) // m
            subs.append(ForAll(Var("k", goal.var.typ),
                               class_instance(goal.body, goal.var, m, r), lo))
        out.append(Alternative(f"residue_split_{m}", subs,
                               lambda ps, g=goal, m=m: Proof(
                                   "residue_split", g, ps, {"modulus": m})))
    return out


BLIND_TACTICS = [t_known, t_hints, blind_t_direct, t_split_and,
                 t_exists_witness, t_factor_divisor, t_range_split,
                 blind_t_residue_split]

# Alternative routes used by strategy mutation. Order changes, exclusion never
# happens: every route still passes through the same kernel.
ROUTES = {
    "balanced": BLIND_TACTICS,
    "residue_first": [t_known, blind_t_residue_split, blind_t_direct,
                      t_factor_divisor, t_split_and, t_range_split, t_hints],
    "factor_first": [t_known, t_factor_divisor, blind_t_direct,
                     blind_t_residue_split, t_split_and, t_range_split, t_hints],
    "range_first": [t_known, t_range_split, blind_t_direct, t_split_and,
                    blind_t_residue_split, t_factor_divisor, t_hints],
    "direct_only": [t_known, t_hints, blind_t_direct],
}
