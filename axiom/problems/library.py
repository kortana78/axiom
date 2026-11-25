"""Problem library: known results (stages 1 and 2) and open problems (stage 4)."""
from __future__ import annotations

from ..kernel.expressions import Const, Pow, Sequence, Sum, Var, parse
from ..kernel.propositions import Divides, ForAll, Le, Pred
from ..invention.constructions import ES_STATEMENT
from .base import Problem

n, i = Var("n"), Var("i")


def _sum_problem(name, title, body, lower_index=1, withheld=""):
    s = Sum(i, Const(lower_index), n, body)
    return Problem(name, title, None, "theorem", 1, sums=[(s, n, 0)], withheld=[withheld])


PROBLEMS = {}


def add(p: Problem):
    PROBLEMS[p.name] = p
    return p


# ---------------- Stage 1: rediscover known mathematics (lemmas withheld)
add(_sum_problem("sum_squares", "Closed form of 1^2 + ... + n^2", i * i,
                 withheld="n(n+1)(2n+1)/6"))
add(_sum_problem("sum_cubes", "Closed form of 1^3 + ... + n^3", Pow(i, Const(3)),
                 withheld="(n(n+1)/2)^2"))
add(_sum_problem("sum_fifth", "Closed form of 1^5 + ... + n^5", Pow(i, Const(5)),
                 withheld="n^2(n+1)^2(2n^2+2n-1)/12"))
add(_sum_problem("sum_odd", "Closed form of 1 + 3 + ... + (2n-1)", parse("2*i - 1"), withheld="n^2"))
add(_sum_problem("geometric", "Closed form of 1 + 2 + 4 + ... + 2^n", Pow(Const(2), i), lower_index=0,
                 withheld="2^(n+1) - 1"))

add(Problem("div_n5", "Prove 30 | n^5 - n", ForAll(n, Divides(Const(30), parse("n^5 - n"))),
            "theorem", 1, terms=[(parse("n^5 - n"), n, 0)]))
add(Problem("div_n7", "Find and prove the best constant divisor of n^7 - n", None, "theorem", 1,
            terms=[(parse("n^7 - n"), n, 0)], withheld=["42 | n^7 - n"]))
add(Problem("div_mixed", "Find divisors of n(n+1)(n+2)(n+3) and n^4 + 2n^3 + 11n^2 + 10n", None,
            "theorem", 1, terms=[(parse("n*(n+1)*(n+2)*(n+3)"), n, 0),
                                 (parse("n^4 + 2*n^3 + 11*n^2 + 10*n"), n, 0)]))
add(Problem("exp_vs_poly", "When does n^2 <= 2^n and n^3 <= 3^n hold?", None, "theorem", 1,
            inequalities=[(parse("n^2"), Pow(Const(2), n), n), (parse("n^3"), Pow(Const(3), n), n),
                          (parse("n^4"), Pow(Const(2), n), n)]))

# ---------------- Stage 2: invention required (invariants, new objects)
add(Problem("rec_squares", "a(0)=0, a(n+1) = a(n) + 2n + 1: find what a(n) is", None, "theorem", 2,
            sequences=[Sequence("a", 0, parse("x + 2*n + 1"))], withheld=["a(n) - n^2 is invariant"]))
add(Problem("rec_triangular", "b(0)=0, b(n+1) = b(n) + n", None, "theorem", 2,
            sequences=[Sequence("b", 0, parse("x + n"))]))
add(Problem("rec_mersenne", "c(0)=0, c(n+1) = 2c(n) + 1", None, "theorem", 2,
            sequences=[Sequence("c", 0, parse("2*x + 1"))]))
add(Problem("rec_mod", "d(0)=1, d(n+1) = d(n)^2 + 3 d(n) + 3: find invariants", None, "theorem", 2,
            sequences=[Sequence("d", 1, parse("x^2 + 3*x + 3"))]))
add(Problem("fermat_scan", "For which p does p | n^p - n always hold?", None, "theorem", 2,
            special=["fermat_scan"], withheld=["Fermat's little theorem"]))

# ---------------- Stage 4: open problems
add(Problem("erdos_straus", "Erdos-Straus: 4/n = 1/x + 1/y + 1/z for every n >= 2", ES_STATEMENT,
            "open", 4, special=["es_families"], bounded_limit=3000, params={"modulus": 840},
            bounded_goal=ForAll(n, Pred("es_rep", (n,)), 2),
            notes="Polynomial identities cannot cover square residue classes (Mordell); expect those to stay open."))
add(Problem("collatz", "Collatz: every n >= 1 reaches 1", ForAll(n, Pred("collatz_reaches_one", (n,)), 1),
            "open", 4, special=["collatz_descent"], bounded_limit=100000, params={"max_k": 16}))
add(Problem("legendre", "Legendre: a prime lies between n^2 and (n+1)^2", ForAll(n, Pred("prime_between_squares", (n,)), 1),
            "open", 4, bounded_limit=3000))
add(Problem("quasiperfect", "No n has sigma(n) = 2n + 1", ForAll(n, Pred("not_quasiperfect", (n,)), 1),
            "open", 4, predicates=["sigma_odd"], bounded_limit=20000))
