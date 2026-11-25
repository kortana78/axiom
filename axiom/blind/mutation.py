"""Strategy Mutation.

When every general strategy has stalled, the engine does not simply enlarge
its search budget. It asks six meta-questions and turns the answers into new,
concrete strategies which are run against the same trusted verifier:

  1. What assumptions are making this problem difficult?
  2. Can I formulate an equivalent statement?
  3. Can I introduce a new mathematical object?
  4. Can I prove a stronger intermediate proposition?
  5. Can I combine two previously unrelated observations?
  6. Can I construct an entirely different proof route?

The questions are generic. No answer, lemma, residue class or proof plan is
supplied by the problem; the mutations are produced from the objects the
engine discovered itself.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Iterator, List, Optional

import sympy as sp

from ..invention import lemmas
from ..invention.definitions import Definition, shifted_sequence
from ..kernel.expressions import Const, Var
from ..kernel.inference import class_instance
from ..kernel.proof_objects import Proof
from ..kernel.propositions import (And, Divides, ForAll, Le, Lt, Prop)
from ..reasoning import forward
from ..reasoning.search import ProofSearch
from .tactics import BLIND_TACTICS, ROUTES


@dataclass
class Mutation:
    question: int
    name: str
    rationale: str
    generator: Callable[[object], Iterator[None]]


class StrategyMutation:
    def __init__(self, ctl):
        self.ctl = ctl
        self.applied = set()

    def mutate(self) -> List[Mutation]:
        out: List[Mutation] = []
        for q, fn in enumerate((self._q1_difficulty, self._q2_equivalent,
                                self._q3_new_object, self._q4_stronger,
                                self._q5_combine, self._q6_route), 1):
            m = fn()
            if m is not None and (q, m.name) not in self.applied:
                self.applied.add((q, m.name))
                out.append(m)
        return out[:2]

    # ---------------------------------------------------------- question 1
    def _q1_difficulty(self) -> Optional[Mutation]:
        ctl = self.ctl
        goal = ctl.problem.goal
        if goal is None or not isinstance(goal, ForAll):
            return None
        failures = []
        for v in range(goal.lower, min(goal.lower + 60, 10 ** 4)):
            try:
                if not goal.instance(v).evaluate({}):
                    failures.append(v)
            except Exception:
                continue
        ctl.findings["difficulty_scan"] = {
            "sampled": 60,
            "failing_instances": failures[:20],
            "diagnosis": ("counterexample found" if failures else
                          "no small failing instance: obstruction is structural"),
        }
        if failures:
            ctl.refute(goal, f"fails at {goal.var} = {failures[0]}")
            return None

        def gen(ctl):
            ctl.history.log("mutation Q1", "difficulty",
                            "no small counterexample; obstruction is structural", "diagnosed")
            yield

        return Mutation(1, "difficulty_scan",
                        "isolate whether the difficulty is a small case or structural", gen)

    # ---------------------------------------------------------- question 2
    def _q2_equivalent(self) -> Optional[Mutation]:
        ctl = self.ctl
        goal = ctl.problem.goal
        if goal is None or not isinstance(goal, ForAll):
            return None
        offsets = list(ctl.structure.offsets)[:4]
        for o in (1, 2, 3, 4):
            if o not in offsets:
                offsets.append(o)
        if not offsets:
            return None

        def gen(ctl):
            for L in offsets[:5]:
                v = Var("m", goal.var.typ)
                shifted = ForAll(v, goal.body.subst({goal.var.name: v + Const(L)}), 0)
                p = ProofSearch(ctl.ctx, tactics=BLIND_TACTICS,
                                max_steps=600).prove(shifted, max_depth=4)
                ctl.log_attempt(shifted, "equivalent_shift", 600, p)
                if p is not None and ctl.accept(p, f"equivalent statement shifted by {L}"):
                    ctl.findings.setdefault("equivalent_statements", []).append(str(shifted))
                yield
            for m in ctl.structure.moduli:
                if m > 12:
                    continue
                old = ctl.ctx.residue_moduli
                ctl.ctx.residue_moduli = (m,)
                p = ProofSearch(ctl.ctx, tactics=ROUTES["residue_first"],
                                max_steps=1200).prove(goal, max_depth=4)
                ctl.ctx.residue_moduli = old
                ctl.log_attempt(goal, f"residue_route_mod_{m}", 1200, p)
                if p is not None:
                    ctl.accept(p, f"class route with modulus {m}")
                yield

        return Mutation(2, "equivalent_statement",
                        "reformulate by shifting the bound variable or splitting into classes",
                        gen)

    # ---------------------------------------------------------- question 3
    def _q3_new_object(self) -> Optional[Mutation]:
        ctl = self.ctl
        if not ctl.structure.sequences and not ctl.structure.terms:
            return None

        def gen(ctl):
            for seq in list(ctl.structure.sequences):
                for c in (-2, -1, 1, 2):
                    new = shifted_sequence(seq, c)
                    ctl.define(Definition(new.name, "sequence", new,
                                          "mutation Q3: shifted copy of a discovered sequence",
                                          parent=seq.name))
                    for conj in lemmas.closed_form_for_sequence(new):
                        ctl.propose(conj)
                    yield
            for term, v, lower in list(ctl.structure.terms):
                g = 0
                for i in range(lower, lower + 30):
                    try:
                        val = term.evaluate({v.name: Fraction(i)})
                    except Exception:
                        break
                    if val.denominator != 1:
                        break
                    import math
                    g = math.gcd(g, int(val))
                if g <= 1:
                    continue
                for p, a in sp.factorint(g).items():
                    obj = Const(p ** a)
                    ctl.define(Definition(f"factor_{p}^{a}", "term", obj,
                                          "mutation Q3: prime-power part of a discovered divisor"))
                    ctl.propose(lemmas.Conjecture(
                        ForAll(v, Divides(obj, term), lower), "mutation Q3: new prime-power object", 30))
                    yield

        return Mutation(3, "new_object",
                        "introduce shifted sequences and prime-power objects from discovered data",
                        gen)

    # ---------------------------------------------------------- question 4
    def _q4_stronger(self) -> Optional[Mutation]:
        ctl = self.ctl
        goal = ctl.problem.goal
        if goal is None or not isinstance(goal, ForAll):
            return None

        def gen(ctl):
            body = goal.body
            if isinstance(body, Divides) and isinstance(body.d, Const):
                d = int(body.d.value)
                for p, a in sp.factorint(d).items():
                    if p ** a == d:
                        continue
                    stronger = ForAll(goal.var, Divides(Const(p ** a), body.e), goal.lower)
                    ctl.propose(lemmas.Conjecture(stronger, "mutation Q4: stronger factor", 0))
                    yield
            if isinstance(body, (Le, Lt)):
                for L in list(ctl.structure.offsets)[:5]:
                    if L <= goal.lower:
                        continue
                    tail = ForAll(goal.var, body, L)
                    ctl.propose(lemmas.Conjecture(tail, "mutation Q4: stronger tail", 0))
                    yield
            if not isinstance(body, (Divides, Le, Lt)):
                yield

        return Mutation(4, "stronger_intermediate",
                        "prove easier prime-power factors and tail statements first", gen)

    # ---------------------------------------------------------- question 5
    def _q5_combine(self) -> Optional[Mutation]:
        ctl = self.ctl

        def gen(ctl):
            proofs = list(ctl.store.proofs.values())
            for p in forward.combine_divisibility(proofs, ctl.kernel):
                ctl.accept(p, "mutation Q5: combine two divisibility observations")
            # Combine a proved closed form with a proved divisibility of its
            # left-hand side; the resulting statement is checked independently.
            eqs = [p for p in proofs if isinstance(p.conclusion, ForAll)
                   and hasattr(p.conclusion.body, "lhs")]
            divs = [p for p in proofs if isinstance(p.conclusion, ForAll)
                    and isinstance(p.conclusion.body, Divides)]
            for eq in eqs:
                for dv in divs:
                    if eq.conclusion.body.lhs.key() != dv.conclusion.body.e.key():
                        continue
                    rhs = eq.conclusion.body.rhs
                    combined = ForAll(eq.conclusion.var,
                                      Divides(dv.conclusion.body.d, rhs), eq.conclusion.lower)
                    proof = Proof("residue_divisibility", combined)
                    if ctl.accept(proof, "mutation Q5: closed form + divisor"):
                        ctl.findings.setdefault("combinations", []).append(str(combined))
            # Assemble two established universal facts into a conjunction.
            for i, a in enumerate(proofs):
                for b in proofs[i + 1:]:
                    ca, cb = a.conclusion, b.conclusion
                    if not (isinstance(ca, ForAll) and isinstance(cb, ForAll)):
                        continue
                    if ca.var.name != cb.var.name or ca.lower != cb.lower:
                        continue
                    if ca.body.key() == cb.body.key():
                        continue
                    conj = ForAll(ca.var, And((ca.body, cb.body)), ca.lower)
                    proof = Proof("forall_and", conj, [a, b])
                    if ctl.accept(proof, "mutation Q5: conjunction of observations"):
                        break
            yield

        return Mutation(5, "combine_observations",
                        "combine established divisibilities, closed forms and facts", gen)

    # ---------------------------------------------------------- question 6
    def _q6_route(self) -> Optional[Mutation]:
        ctl = self.ctl
        if ctl.problem.goal is None:
            return None

        def gen(ctl):
            for name in ("residue_first", "factor_first", "range_first", "direct_only"):
                tactics = ROUTES[name]
                p = ProofSearch(ctl.ctx, tactics=tactics, max_steps=900,
                                ).prove(ctl.problem.goal, max_depth=5)
                ctl.log_attempt(ctl.problem.goal, f"route_{name}", 900, p)
                if p is not None:
                    ctl.accept(p, f"mutation Q6: proof route {name}")
                yield

        return Mutation(6, "alternative_route",
                        "change the proof route (order of general inference rules)", gen)
