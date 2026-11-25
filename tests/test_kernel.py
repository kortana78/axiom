"""Kernel soundness tests: true things accepted, false things rejected.
Run with:  python -m pytest -q   (or python tests/test_kernel.py)"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.kernel.expressions import Const, Pow, Sequence, SeqTerm, Sub, Sum, Var, parse
from axiom.kernel.inference import Kernel
from axiom.kernel.proof_objects import Proof
from axiom.kernel.propositions import BoundedForAll, Divides, Eq, ForAll, Le, Lt, Pred
from axiom.invention.constructions import collatz_open_classes, es_class_proof, es_family

K = Kernel()
n, i = Var("n"), Var("i")


def ok(rule, prop, **data):
    return K.check(Proof(rule, prop, [], data))[0]


def test_divisibility():
    assert ok("residue_divisibility", ForAll(n, Divides(Const(6), parse("n^3 - n"))))
    assert not ok("residue_divisibility", ForAll(n, Divides(Const(7), parse("n^3 - n"))))
    # rational coefficients are not allowed even if integer valued
    assert not ok("residue_divisibility", ForAll(n, Divides(Const(1), parse("n*(n+1)/2"))))


def test_sum_induction():
    s = Sum(i, Const(1), n, i * i)
    assert ok("sum_induction", ForAll(n, Eq(s, parse("n*(n+1)*(2*n+1)/6"))))
    assert not ok("sum_induction", ForAll(n, Eq(s, parse("n*(n+1)*(2*n+1)/5"))))
    g = Sum(i, Const(0), n, Pow(Const(2), i))
    assert ok("sum_induction", ForAll(n, Eq(g, Pow(Const(2), n) * 2 - 1)))


def test_inequalities():
    assert ok("exp_induction", ForAll(n, Le(parse("n^2"), Pow(Const(2), n)), 4))
    assert not ok("exp_induction", ForAll(n, Le(parse("n^2"), Pow(Const(2), n)), 0))
    assert ok("shift_nonneg", ForAll(n, Le(parse("2*n+1"), parse("n^2")), 3))
    assert not ok("shift_nonneg", ForAll(n, Le(parse("2*n+1"), parse("n^2")), 0))


def test_sequences():
    a = Sequence("a", 0, parse("x + 2*n + 1"))
    assert ok("sequence_closed_form", ForAll(n, Eq(SeqTerm(a, n), parse("n^2"))))
    assert not ok("sequence_closed_form", ForAll(n, Eq(SeqTerm(a, n), parse("n^2 + 1"))))
    d = Sequence("d", 1, parse("x^2 + 3*x + 3"))
    assert ok("recurrence_mod_invariant", ForAll(n, Divides(Const(6), Sub(SeqTerm(d, n), Const(1)))))
    assert not ok("recurrence_mod_invariant", ForAll(n, Divides(Const(4), Sub(SeqTerm(d, n), Const(1)))))


def test_finite_check():
    assert ok("finite_check", BoundedForAll(n, 1, 500, Pred("prime_between_squares", (n,))))
    assert not ok("finite_check", BoundedForAll(n, 1, 50, Pred("is_prime", (n,))))


def test_erdos_straus_family():
    fam = es_family(24, 5)
    assert fam is not None
    assert K.check(es_class_proof(24, 5, fam))[0]


def test_collatz_classes():
    proofs, open_res = collatz_open_classes(10)
    assert all(K.check(p)[0] for p in proofs)
    assert 27 in open_res


def test_unknown_rule_rejected():
    assert not ok("trust_me", ForAll(n, Divides(Const(7), parse("n"))))


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
            print("ok", name)
