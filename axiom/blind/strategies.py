"""General-purpose discovery strategies used by the blind engine.

None of these knows the name or the answer of the problem it is working on.
They consume only the objects found by blind structural analysis.
"""
from __future__ import annotations

from ..invention import invariants as inv
from ..invention import lemmas
from ..invention.definitions import difference_sequence
from ..kernel.inference import class_instance
from ..kernel.proof_objects import Proof
from ..kernel.propositions import ForAll, Var
from ..reasoning import forward
from ..reasoning.search import ProofSearch
from ..discovery.evaluation import rank
from . import counterexamples as CE
from .tactics import BLIND_TACTICS


def counterexample_hunt(ctl):
    goal = ctl.problem.goal
    if goal is not None:
        ce = CE.find_counterexample(goal)
        if ce is not None:
            ctl.refute(goal, str(ce))
        yield
    while True:
        pending = [c for c in ctl.conjectures.values() if not c.meta.get("tested_hard")]
        if not pending:
            yield
            if ctl.discovery_quiet():
                return
            continue
        for c in pending:
            c.meta["tested_hard"] = True
            ce = CE.find_counterexample(c.prop, small=80, randoms=60, seed=7)
            if ce:
                ctl.refute(c.prop, str(ce))
                c.meta["refuted"] = True
            yield


def invent_from_objects(ctl):
    st = ctl.structure
    for s, n, lower in st.sums:
        for c in lemmas.closed_form_for_sum(s, n, lower):
            ctl.propose(c)
        yield
    for f, n, lower in st.terms:
        for c in lemmas.divisibility_conjectures(f, n, lower):
            ctl.propose(c)
        yield
    for lhs, rhs, n in st.inequalities:
        for c in lemmas.inequality_threshold(lhs, rhs, n):
            ctl.propose(c)
        yield
    for seq in st.sequences:
        for c in lemmas.closed_form_for_sequence(seq):
            ctl.propose(c)
        ctl.define(difference_sequence(seq))
        yield
    for name in st.predicates:
        for c in lemmas.characterise_predicate(name, N=500):
            ctl.propose(c)
        yield


def invent_invariants(ctl):
    for seq in ctl.structure.sequences:
        for proof in inv.invariant_proofs(seq, max_degree=3):
            if ctl.accept(proof, "invariant synthesis"):
                for prop in forward.closed_form_from_invariant(proof):
                    ctl.propose(lemmas.Conjecture(prop, "solved invariant", 0))
            yield
        for c in inv.modular_invariants(seq):
            ctl.propose(c)
        yield


def prove_conjectures(ctl):
    budget = 200
    while True:
        todo = [c for c in ctl.conjectures.values()
                if not c.meta.get("proved") and not c.meta.get("refuted")]
        if not todo:
            yield
            if ctl.discovery_quiet():
                return
            continue
        for c in rank(todo, ctl.goal_key()):
            if c.meta.get("attempt_budget", 0) >= budget:
                continue
            c.meta["attempt_budget"] = budget
            search = ProofSearch(ctl.ctx, tactics=BLIND_TACTICS, max_steps=budget)
            p = search.prove(c.prop, max_depth=4)
            ctl.log_attempt(c.prop, "conjecture_proof", budget, p)
            if p is not None:
                ctl.accept(p, "proof of invented conjecture")
                c.meta["proved"] = True
            yield
        budget *= 2
        if budget > 6400:
            for c in todo:
                if not c.meta.get("proved"):
                    ctl.store.undecided(c.prop, ctl.problem.name, "proof budget exhausted")
            return


def direct_proof(ctl):
    goal = ctl.problem.goal
    if goal is None:
        return
    budget = 200
    while not ctl.goal_proved() and not ctl.goal_refuted:
        search = ProofSearch(ctl.ctx, tactics=BLIND_TACTICS, max_steps=budget)
        p = search.prove(goal, max_depth=5)
        ctl.log_attempt(goal, "direct", budget, p)
        if p is not None:
            ctl.accept(p, "direct proof search")
            return
        budget *= 2
        if budget > 50_000:
            ctl.history.log("direct_proof", "stop", "budget ceiling reached", "undecided")
            return
        yield


def bounded_verification(ctl):
    goal = ctl.problem.goal
    if goal is None or not isinstance(goal, ForAll):
        return
    if goal.lower > ctl.bounded_limit:
        return
    steps, h = [], 100
    while h < ctl.bounded_limit:
        steps.append(h)
        h *= 10
    steps.append(ctl.bounded_limit)
    for hi in steps:
        proof = CE.bounded_proof(goal, hi)
        if proof is None:
            return
        if ctl.accept(proof, f"bounded verification up to {hi}"):
            ctl.bounded_upto = hi
        else:
            ctl.history.log("bounded_verification", "check", f"up to {hi}", "not decidable")
            return
        yield


def forward_reasoning(ctl):
    seen = 0
    while True:
        proved = list(ctl.store.proofs.values())
        if len(proved) != seen:
            seen = len(proved)
            for p in forward.combine_divisibility(proved, ctl.kernel):
                ctl.accept(p, "forward: combine coprime divisors")
        yield
        if ctl.discovery_quiet():
            return


def residue_exploration(ctl):
    """Autonomously split the goal into residue classes using moduli that were
    derived from the problem's own constants and sampled values."""
    goal = ctl.problem.goal
    if goal is None or not isinstance(goal, ForAll) or isinstance(goal.body, ForAll):
        return
    count = 0
    for m in ctl.structure.moduli:
        if m < 2 or m > 16:
            continue
        premises, covered, failed = [], [], []
        for r in range(m):
            first = goal.lower + ((r - goal.lower) % m)
            lo = (first - r) // m
            v = Var("k", goal.var.typ)
            cls = ForAll(v, class_instance(goal.body, goal.var, m, r), lo)
            proof = ProofSearch(ctl.ctx, tactics=BLIND_TACTICS,
                                max_steps=400).prove(cls, max_depth=3)
            if proof is not None and ctl.accept(proof, f"class {r} mod {m}"):
                premises.append(proof)
                covered.append(r)
            else:
                failed.append(r)
            count += 1
            yield
        ctl.findings[f"residue_mod_{m}"] = {
            "covered": len(covered), "open": len(failed), "open_sample": failed[:16]}
        if not failed and len(premises) == m:
            assembled = Proof("residue_split", goal, premises, {"modulus": m})
            if ctl.accept(assembled, f"assembled from all {m} classes"):
                return
    if count == 0:
        yield
