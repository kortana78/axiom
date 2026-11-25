"""Template: give AXIOM your own problem.

Run with:
    python -m axiom run --file examples/my_problem_template.py --time 60

Edit the goal and objects below. Anything you do not give AXIOM
(useful lemmas, closed forms) it has to invent itself.
"""
from axiom.kernel.expressions import Const, Pow, Sequence, Sum, Var, parse
from axiom.kernel.propositions import Divides, Eq, ForAll, Le, Pred
from axiom.problems.base import Problem

n, i = Var("n"), Var("i")

PROBLEM = Problem(
    name="my_problem",
    title="Example: does 120 divide n^5 - 5n^3 + 4n, and what else can be found?",
    goal=ForAll(n, Divides(Const(120), parse("n^5 - 5*n^3 + 4*n"))),
    known_status="theorem",
    stage=1,
    # objects AXIOM may study to invent lemmas
    terms=[(parse("n^5 - 5*n^3 + 4*n"), n, 0)],
    sums=[(Sum(i, Const(1), n, parse("i*(i+1)")), n, 0)],
    sequences=[Sequence("u", 2, parse("3*x - 2"))],
    inequalities=[(parse("n^5"), Pow(Const(3), n), n)],
    bounded_limit=5000,
)
