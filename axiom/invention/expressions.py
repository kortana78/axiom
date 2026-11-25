"""Enumeration of candidate expressions (smallest first)."""
from __future__ import annotations

from itertools import product
from typing import Iterator, List

import sympy as sp

from ..kernel.expressions import Expr, from_sympy, sym


def polynomials(var: str, max_degree: int, coeff_range: int) -> Iterator[Expr]:
    """All nonzero polynomials in var with integer coefficients in
    [-coeff_range, coeff_range], ordered by degree then size."""
    x = sym(var)
    for deg in range(max_degree + 1):
        rng = range(-coeff_range, coeff_range + 1)
        for coeffs in product(rng, repeat=deg + 1):
            if coeffs[-1] == 0:
                continue
            e = sum(c * x ** k for k, c in enumerate(coeffs))
            yield from_sympy(e)


def monomials(vars_: List[str], max_degree: int) -> List[sp.Expr]:
    """Monomials x^i n^j with 0 < i + j <= max_degree."""
    syms = [sym(v) for v in vars_]
    out = []
    for degs in product(range(max_degree + 1), repeat=len(syms)):
        if 0 < sum(degs) <= max_degree:
            m = 1
            for s, d in zip(syms, degs):
                m *= s ** d
            out.append(m)
    return out
