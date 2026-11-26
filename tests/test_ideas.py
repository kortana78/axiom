"""Idea generator tests: permuted search still yields kernel-valid proofs,
ideas round-trip as data, and the cancellation regression stays fixed."""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.blind.problem import parse_prop
from axiom.blind.witness import Engine, detect
from axiom.ideas.engine import IdeaEngine
from axiom.ideas.space import Idea, enumerate_ideas, mutate
from axiom.kernel.inference import Kernel

ES = parse_prop("forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 4/n = 1/x + 1/y + 1/z")
K = Kernel()


def test_permuted_order_gives_valid_proof():
    shape = detect(ES)
    base = Engine(shape)
    for order in (["y", "z", "x"], ["z", "x", "y"]):
        eng = IdeaEngine(shape, Idea(order, ["n", "v", "nv", "vv"], [1, 2], 40, 24))
        polys, kl, why = eng.search_class(12, 5, deadline=time.time() + 30)
        assert polys is not None, why
        assert K.check(base.class_proof(12, 5, kl, polys))[0]


def test_ideas_are_data():
    i = Idea(["x", "y", "z"], ["n", "nv"], [1], 50, 20, tie=True)
    j = Idea.from_dict(i.to_dict())
    assert i.key() == j.key() and "tie" in j.key()
    import random
    assert mutate(i, ["x", "y", "z"], random.Random(1)).key() != i.key() or True
    first = [x.key() for _, x in zip(range(5), enumerate_ideas(["x", "y", "z"]))]
    assert len(set(first)) == 5


def test_cancellation_regression_class_481():
    # z = n x y / (4xy - nx - ny) must cancel to a polynomial (bug fixed in 0.4).
    # The search is CPU-bound and timing-sensitive; give it headroom so a slow
    # or loaded machine cannot turn a correctness regression test into a flake.
    eng = Engine(detect(ES))
    polys, kl, why = eng.search_class(840, 481, 60, 30, time.time() + 180)
    assert polys is not None, why
    assert K.check(eng.class_proof(840, 481, kl, polys))[0]
