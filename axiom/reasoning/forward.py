"""Forward reasoning: derive consequences of what is already established.

Outputs are either kernel-checked proofs (DERIVED) or new candidate
statements to investigate (CONJECTURED).
"""
from __future__ import annotations

import math
from itertools import combinations
from typing import List, Tuple

import sympy as sp

from ..kernel.expressions import Const, SeqTerm, Var, from_sympy, sym
from ..kernel.inference import Kernel
from ..kernel.proof_objects import Proof
from ..kernel.propositions import Divides, Eq, ForAll, Prop


def combine_divisibility(proved: List[Proof], kernel: Kernel) -> List[Proof]:
    """From d1 | f and d2 | f with gcd 1, derive d1*d2 | f."""
    out = []
    divs = [p for p in proved if isinstance(p.conclusion, ForAll)
            and isinstance(p.conclusion.body, Divides)
            and isinstance(p.conclusion.body.d, Const)]
    for a, b in combinations(divs, 2):
        ca, cb = a.conclusion, b.conclusion
        if ca.var != cb.var or ca.lower != cb.lower or ca.body.e != cb.body.e:
            continue
        da, db = int(ca.body.d.value), int(cb.body.d.value)
        if math.gcd(da, db) != 1:
            continue
        concl = ForAll(ca.var, Divides(Const(da * db), ca.body.e), ca.lower)
        proof = Proof("divisibility_combine", concl, [a, b])
        if kernel.check(proof)[0]:
            out.append(proof)
    return out


def instantiate_all(proof: Proof, values) -> List[Proof]:
    out = []
    c = proof.conclusion
    if not isinstance(c, ForAll):
        return out
    for v in values:
        if v >= c.lower:
            out.append(Proof("instantiate", c.instance(v), [proof], {"value": v}))
    return out


def closed_form_from_invariant(inv_proof: Proof) -> List[Prop]:
    """If I(a(n), n) = c is proved and I is linear in x, solve for a(n).
    The result is a conjecture to be proved independently."""
    out = []
    c = inv_proof.conclusion
    if inv_proof.rule != "recurrence_invariant":
        return out
    I, seq = inv_proof.data["I"], inv_proof.data["seq"]
    c0 = c.body.rhs
    X = sym("x")
    sols = sp.solve(sp.Eq(I.to_sympy(), c0.to_sympy()), X)
    for s in sols:
        if X in s.free_symbols:
            continue
        g = from_sympy(sp.expand(s))
        out.append(ForAll(Var("n"), Eq(SeqTerm(seq, Var("n")), g), 0))
    return out
