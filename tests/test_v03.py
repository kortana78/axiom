"""AXIOM 0.3 tests: witness construction, residue_cover, prime_reduction.
The new kernel rules must accept what is true and reject what is not."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.blind.problem import parse_prop
from axiom.blind.witness import Engine, detect
from axiom.kernel.inference import Kernel, prime_hypothesis
from axiom.kernel.proof_objects import Proof
from axiom.kernel.propositions import Implies

K = Kernel()
TWO = parse_prop("forall n >= 2: exists x >= 1: exists y >= 1: 2/n = 1/x + 1/y")
ES = parse_prop("forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 4/n = 1/x + 1/y + 1/z")
NONHOM = parse_prop("forall n >= 2: exists x >= 1: exists y >= 1: n + 1 = x + y")


def _cover(goal, M, T=40, D=24):
    eng = Engine(detect(goal))
    covered, open_res = [], []
    for r in range(M):
        polys, kl, _ = eng.search_class(M, r, T, D, deadline=1e18)
        if polys is None:
            open_res.append(r)
            continue
        pr = eng.class_proof(M, r, kl, polys)
        assert K.check(pr)[0]
        covered.append((M, r, kl, pr))
    return eng, covered, open_res


def test_full_proof_by_residue_cover():
    eng, covered, open_res = _cover(TWO, 2)
    assert open_res == []
    ok, msg = K.check(eng.reduction_proof(TWO, 2, covered, []))
    assert ok, msg


def test_residue_cover_rejects_missing_class():
    eng, covered, _ = _cover(TWO, 2)
    bad = eng.reduction_proof(TWO, 2, covered[:1], [])   # drop a class, claim nothing open
    assert not K.check(bad)[0]


def test_es_reduction_mod_12():
    eng, covered, open_res = _cover(ES, 12)
    assert 1 in open_res and len(open_res) <= 3
    assert K.check(eng.reduction_proof(ES, 12, covered, open_res))[0]
    prime_open = [r for r in open_res if r in (1, 5, 7, 11)]
    assert K.check(eng.prime_reduction_proof(ES, 12, covered, prime_open))[0]


def test_prime_reduction_rejects_non_homogeneous():
    eng = Engine(detect(NONHOM))
    pr = eng.prime_reduction_proof(NONHOM, 2, [], [1])
    assert not K.check(pr)[0]


def test_prime_reduction_rejects_uncovered_prime_class():
    eng, covered, open_res = _cover(ES, 12)
    # pretend class 1 is not open
    pr = eng.prime_reduction_proof(ES, 12, covered, [r for r in open_res if r != 1])
    assert not K.check(pr)[0]


def test_pythagorean_witnesses():
    goal = parse_prop("forall n >= 3: exists x >= 1: exists y >= 1: n^2 + x^2 = y^2")
    eng, covered, open_res = _cover(goal, 2)
    assert open_res == []


def test_generic_pattern_grammar():
    import axiom.kernel.inference  # noqa: F401 registers predicates
    from axiom.invention.lemmas import characterise_predicate
    pats = [str(c.prop) for c in characterise_predicate("sigma_odd", 1500)]
    assert any("sq_times_1_or_2" in p for p in pats)


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
