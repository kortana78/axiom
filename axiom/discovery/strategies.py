"""Competing strategies. Each is a generator: it does one unit of work,
then yields so the fair scheduler can give time to the others."""
from __future__ import annotations

from ..invention import constructions, generalization, invariants, lemmas
from ..invention.definitions import difference_sequence
from ..kernel.expressions import Const, Var
from ..kernel.inference import class_instance
from ..kernel.proof_objects import Proof
from ..kernel.propositions import BoundedForAll, ForAll
from ..reasoning import forward
from ..reasoning.search import ProofSearch
from .counterexamples import bounded_proof, find_counterexample
from .evaluation import rank


def direct_proof(ctl):
    """Attack the main goal with growing search budgets."""
    goal = ctl.problem.goal
    if goal is None:
        return
    budget = 100
    while not ctl.goal_proved():
        search = ProofSearch(ctl.ctx, max_steps=budget)
        p = search.prove(goal, max_depth=5)
        if p is not None:
            ctl.accept(p, "direct proof search")
            return
        ctl.history.log("direct_proof", "search", f"budget {budget}", "failed")
        budget *= 2
        if budget > 50_000:
            ctl.history.log("direct_proof", "stop", "budget ceiling reached", "undecided")
            return
        yield


def counterexample_hunt(ctl):
    goal = ctl.problem.goal
    if goal is not None:
        ce = find_counterexample(goal, small=60, randoms=20, big=10 ** 4)
        if ce is not None and ce != {}:
            ctl.store.refute(goal, ctl.problem.name, str(ce))
            ctl.history.log("counterexample_hunt", "refute goal", str(ce), "refuted")
            ctl.goal_refuted = True
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
            ce = find_counterexample(c.prop, small=120, randoms=80, seed=7)
            if ce:
                ctl.store.refute(c.prop, ctl.problem.name, str(ce))
                ctl.history.log("counterexample_hunt", "refute", str(c.prop), "refuted")
                c.meta["refuted"] = True
            yield


def invent_from_data(ctl):
    p = ctl.problem
    for s, n, lower in p.sums:
        for c in lemmas.closed_form_for_sum(s, n, lower):
            ctl.propose(c)
        yield
    for f, n, lower in p.terms:
        for c in lemmas.divisibility_conjectures(f, n, lower):
            ctl.propose(c)
        yield
    for lhs, rhs, n in p.inequalities:
        for c in lemmas.inequality_threshold(lhs, rhs, n):
            ctl.propose(c)
        yield
    for seq in p.sequences:
        for c in lemmas.closed_form_for_sequence(seq):
            ctl.propose(c)
        d = difference_sequence(seq)
        ctl.define(d)
        yield
    for name in p.predicates:
        for c in lemmas.characterise_predicate(name, N=3000):
            ctl.propose(c)
        yield


def invent_invariants(ctl):
    for seq in ctl.problem.sequences:
        for proof in invariants.invariant_proofs(seq, max_degree=3):
            if ctl.accept(proof, "invariant synthesis"):
                for prop in forward.closed_form_from_invariant(proof):
                    ctl.propose(lemmas.Conjecture(prop, "solved invariant for a(n)", 0))
            yield
        for c in invariants.modular_invariants(seq):
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
            search = ProofSearch(ctl.ctx, max_steps=budget)
            p = search.prove(c.prop, max_depth=4)
            if p is not None and ctl.accept(p, "proof of invented conjecture"):
                c.meta["proved"] = True
            else:
                ctl.history.log("prove_conjectures", "attempt", str(c.prop), "failed")
            yield
        budget *= 2
        if budget > 6400:
            for c in todo:
                if not c.meta.get("proved"):
                    ctl.store.undecided(c.prop, ctl.problem.name, "proof budget exhausted")
            return


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


def bounded_verification(ctl):
    goal = ctl.problem.bounded_goal or ctl.problem.goal
    if goal is None or not isinstance(goal, ForAll):
        return
    if goal.lower > ctl.problem.bounded_limit:
        return
    limit = ctl.problem.bounded_limit
    steps, h = [], 100
    while h < limit:
        steps.append(h)
        h *= 10
    steps.append(limit)
    for hi in steps:
        proof = bounded_proof(goal, hi)
        if proof is None:
            return
        if ctl.accept(proof, f"bounded verification up to {hi}"):
            ctl.bounded_upto = hi
        else:
            # rejection is not refutation: look for an actual failing case
            bad = None
            for v in range(goal.lower, hi + 1):
                try:
                    if not goal.instance(v).evaluate({}):
                        bad = v
                        break
                except Exception:
                    continue
            if bad is not None:
                ctl.store.refute(ctl.problem.goal, ctl.problem.name, f"fails at {goal.var} = {bad}")
                ctl.history.log("bounded_verification", "check", f"fails at {bad}", "refuted")
                ctl.goal_refuted = True
            else:
                ctl.history.log("bounded_verification", "check", f"up to {hi}", "not decidable by evaluation")
            return
        yield


def fermat_scan(ctl):
    for c in generalization.fermat_style_generalisation(30):
        ctl.propose(c, prove_now=False)
        ctl.history.log("generalization", "parameter scan", c.note, "conjectured")
        n = Var("n")
        from ..kernel.expressions import Pow, Sub
        from ..kernel.propositions import Divides
        for q in c.meta["instances"]:
            inst = ForAll(n, Divides(Const(q), Sub(Pow(n, Const(q)), n)), 0)
            ctl.accept(Proof("residue_divisibility", inst), f"instance p = {q} of the generalisation")
            yield
        ctl.store.undecided(c.prop, ctl.problem.name,
                            "general case needs a rule beyond residue checking; instances proved")
        c.meta["proved"] = False
        c.meta["general_open"] = True


def es_families(ctl):
    M = ctl.problem.params.get("modulus", 840)
    covered, uncovered = [], []
    examples = {}
    for r in range(M):
        fam = constructions.es_family(M, r)
        if fam is not None and len(examples) < 6:
            examples[f"n = {M}k + {r}"] = f"x = {fam[0]}, y = {fam[1]}, z = {fam[2]} (k >= {fam[3]})"
        if fam is not None:
            proof = constructions.es_class_proof(M, r, fam)
            if ctl.accept(proof, f"representation search: polynomial family for n = {M}k + {r}"):
                covered.append(r)
            else:
                uncovered.append(r)
        else:
            uncovered.append(r)
            ctl.store.log_failure(ctl.problem.name, f"n = {M}k + {r}", "es_family",
                                  "no integer-polynomial family within search bounds")
        if r % 20 == 0:
            yield
    ctl.findings["es_modulus"] = M
    ctl.findings["es_covered"] = covered
    ctl.findings["es_uncovered"] = uncovered
    ctl.findings["es_example_families"] = examples
    ctl.history.log("es_families", "coverage", f"{len(covered)}/{M} classes mod {M}",
                    "partial" if uncovered else "complete")
    if not uncovered:
        # every class covered: assemble the full theorem with residue_split
        goal = ctl.problem.goal
        prems = []
        for r in range(M):
            prems.append(ctl.store.proofs[constructions.es_class_statement(M, r, 0 if r >= 2 else 1).key()])
        ctl.accept(Proof("residue_split", goal, prems, {"modulus": M}), "assembled from all classes")
    yield


def collatz_descent(ctl):
    K = ctl.problem.params.get("max_k", 16)
    proofs, open_res = constructions.collatz_open_classes(K)
    for idx, p in enumerate(proofs):
        ctl.accept(p, "parity-vector descent class")
        if idx % 200 == 0:
            yield
    ctl.findings["collatz_k"] = K
    ctl.findings["collatz_open"] = len(open_res)
    ctl.findings["collatz_open_sample"] = open_res[:20]
    ctl.history.log("collatz_descent", "coverage",
                    f"{len(open_res)} of {2 ** K} classes mod 2^{K} still open "
                    f"({100 * len(open_res) / 2 ** K:.2f}%)", "partial")
    yield


SPECIAL = {"fermat_scan": fermat_scan, "es_families": es_families, "collatz_descent": collatz_descent}
