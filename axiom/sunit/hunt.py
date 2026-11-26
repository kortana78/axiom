"""Certified S-unit equation solver for small supports.

Problem
-------
For a finite set of primes ``S``, find every coprime triple of positive
integers ``a + b = c`` with ``a <= b`` such that every prime factor of
``a*b*c`` lies in ``S``.

This is the positive integral form of the S-unit equation ``x + y = 1``
after clearing denominators.

Method (three stages)
---------------------
(a) Explicit height bound.  Write ``x = a/c`` and ``y = b/c``.  Then
    ``x + y = 1`` and ``x, y`` are S-units.  Matschke--von Kaenel
    (arXiv:1605.06079, Proposition 10.2) prove

        max(h(x), h(y)) <= (5/2) N_S log(N_S) + 9 N_S,   N_S = prod(S).

    Since ``h(a/c) = log c`` for ``0 < a < c``, this bounds ``c``.  It is an
    explicit effective bound of the same logical role as the classical
    linear-forms-in-logarithms bound of Gyory--Yu (2006), and is sharper for
    the small supports treated here.  The LLF alternative is recorded in the
    certificate.  All logarithms are evaluated with 80-digit decimal
    arithmetic and rounded outwards.

(b) Congruence lattice and LLL.  Fix ``q in S`` and suppose ``q | c``.
    Because ``gcd(a, b, c) = 1``, ``q`` divides neither ``a`` nor ``b``, so
    ``a/b`` is a unit modulo ``q``.  From ``a + b = c`` we get

        a/b = prod_{p in S, p != q} p^{gamma_p} == -1 (mod q).

    This is a linear congruence in the exponent vector ``gamma``.  Its
    solution set is a coset of a lattice.  We compute a particular solution
    and a basis of the homogeneous lattice, then LLL-reduce the basis
    (Lenstra--Lenstra--Lovasz 1982; de Weger 1987; Matschke--von Kaenel
    2016, Algorithm 3.7).

(c) Exhaustive enumeration.  Enumerate every lattice point in the exponent
    box ``|gamma_p| <= floor(B / log p)``, reconstruct

        a = prod_{gamma_p > 0} p^{gamma_p},
        b = prod_{gamma_p < 0} p^{-gamma_p},
        c = a + b,

    and keep exactly the triples with ``q | c``, ``c`` S-smooth, and
    ``gcd(a, b) = 1``.  Every solution has at least one ``q | c``, so the
    union over ``q in S`` is complete.

The certificate is plain data.  ``axiom.sunit.check`` is an independent
checker: it shares no code with this module, recomputes the height bound and
the lattice, verifies the LLL data, and re-enumerates the full exponent box
from scratch.

This proves completeness for the finite set ``S`` only.  It says nothing
about the abc conjecture.
"""
from __future__ import annotations

import argparse
import math
import time
from decimal import Decimal, ROUND_CEILING, ROUND_FLOOR, getcontext
from fractions import Fraction
from typing import Dict, Iterable, Iterator, List, Optional, Sequence, Tuple

getcontext().prec = 80

MAX_SUPPORTED_S = 3

# ---------------------------------------------------------------------------
# elementary exact arithmetic
# ---------------------------------------------------------------------------


def factor_exponents(n: int) -> Optional[Dict[int, int]]:
    """Exact prime factorisation by trial division.  ``None`` for ``n <= 0``."""
    if n <= 0:
        return None
    out: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            out[d] = out.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def is_smooth(n: int, S: Sequence[int]) -> bool:
    if n <= 0:
        return False
    for p in S:
        while n % p == 0:
            n //= p
    return n == 1


def smooth_exponents(n: int, S: Sequence[int]) -> Optional[Dict[int, int]]:
    """Exponents of the primes of ``S`` in ``n``, or ``None`` if not smooth."""
    if n <= 0:
        return None
    out: Dict[int, int] = {}
    for p in S:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        out[int(p)] = e
    return out if n == 1 else None


def clean_S(S: Sequence[int]) -> List[int]:
    out = sorted({int(p) for p in S})
    if not out:
        raise ValueError("S must be non-empty")
    for p in out:
        if not is_prime(p):
            raise ValueError(f"S contains a non-prime: {p}")
    if len(out) > MAX_SUPPORTED_S:
        raise NotImplementedError(
            f"certified solver supports |S| <= {MAX_SUPPORTED_S}; got {len(out)}")
    return out


# ---------------------------------------------------------------------------
# stage (a): explicit height bound
# ---------------------------------------------------------------------------


def height_bound(S: Sequence[int]) -> dict:
    """Stage (a): rigorous exponent bounds and the constants used.

    ``B`` is an upper bound for ``log c``.  The stored decimal strings are
    outward-rounded so a checker can recompute them independently.
    """
    S = clean_S(S)
    N = 1
    for p in S:
        N *= p
    log_N_upper = Decimal(N).ln().quantize(Decimal("0.000001"),
                                          rounding=ROUND_CEILING)
    B = (Decimal(5) / 2 * N * log_N_upper + 9 * N).quantize(
        Decimal("0.000001"), rounding=ROUND_CEILING)
    log_lower: Dict[str, str] = {}
    bounds: Dict[str, int] = {}
    for p in S:
        lp = Decimal(p).ln().quantize(Decimal("0.000001"), rounding=ROUND_FLOOR)
        log_lower[str(p)] = str(lp)
        bounds[str(p)] = int((B / lp).to_integral_value(rounding=ROUND_FLOOR))
    return {
        "S": S,
        "N_S": N,
        "formula": "max(h(x),h(y)) <= (5/2)*N_S*log(N_S) + 9*N_S",
        "source": "Matschke-von Kaenel, arXiv:1605.06079, Proposition 10.2",
        "llf_alternative": ("Gyory-Yu 2006, cited in arXiv:1605.06079 "
                            "Section 10.1.2; weaker for these supports"),
        "log_N_upper": str(log_N_upper),
        "B": str(B),
        "log_lower": log_lower,
        "exponent_bounds": bounds,
    }


# ---------------------------------------------------------------------------
# stage (b): congruence lattice, particular solution, LLL
# ---------------------------------------------------------------------------


def primitive_root(q: int) -> int:
    if q == 2:
        return 1
    phi = q - 1
    factors = set(factor_exponents(phi) or {})
    for g in range(2, q):
        if all(pow(g, phi // r, q) != 1 for r in factors):
            return g
    raise ValueError(f"no primitive root found modulo {q}")


def discrete_log_table(q: int) -> Tuple[int, Dict[int, int]]:
    """Return ``(g, table)`` with ``table[g^e mod q] = e`` for ``0 <= e < q-1``."""
    if q == 2:
        return 1, {1: 0}
    g = primitive_root(q)
    table: Dict[int, int] = {}
    x = 1
    for e in range(q - 1):
        table[x] = e
        x = (x * g) % q
    if len(table) != q - 1:
        raise ValueError(f"primitive root {g} does not generate (Z/{q})^*")
    return g, table


def _gcd_many(values: Iterable[int]) -> int:
    g = 0
    for v in values:
        g = math.gcd(g, int(v))
    return g


def _extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Return ``(g, u, v)`` with ``a*u + b*v = g = gcd(a, b)``."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        quot = old_r // r
        old_r, r = r, old_r - quot * r
        old_s, s = s, old_s - quot * s
        old_t, t = t, old_t - quot * t
    return old_r, old_s, old_t


def particular_solution(e: Sequence[int], target: int, M: int) -> Optional[List[int]]:
    """One solution of ``sum e_i x_i == target (mod M)``, or ``None``."""
    n = len(e)
    e = [int(x) % M if M > 1 else 0 for x in e]
    target %= M if M > 1 else 1
    if M <= 1:
        return [0] * n
    d = _gcd_many(list(e) + [M])
    if target % d:
        return None
    ep = [x // d for x in e]
    Mp = M // d
    tp = (target // d) % Mp
    if Mp == 1:
        return [0] * n
    if n == 0:
        return [0] if tp == 0 else None
    if n == 1:
        inv = pow(ep[0] % Mp, -1, Mp)
        return [(tp * inv) % Mp]
    if n == 2:
        g, u, v = _extended_gcd(ep[0], ep[1])
        # gcd(ep[0], ep[1], Mp) = 1, so g is invertible modulo Mp.
        invg = pow(g % Mp, -1, Mp)
        scale = (tp * invg) % Mp
        return [(scale * u) % Mp, (scale * v) % Mp]
    raise NotImplementedError("particular_solution supports at most two unknowns")


def homogeneous_basis(e: Sequence[int], M: int) -> List[List[int]]:
    """A basis of ``{x in Z^n : sum e_i x_i == 0 (mod M)}``."""
    n = len(e)
    if n == 0:
        return []
    if M <= 1:
        return [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    e = [int(x) % M for x in e]
    if n == 1:
        g = math.gcd(e[0], M)
        return [[M // g]]
    if n == 2:
        e1, e2 = e
        if e1 == 0 and e2 == 0:
            return [[1, 0], [0, 1]]
        if e1 == 0:
            g = math.gcd(e2, M)
            return [[1, 0], [0, M // g]]
        g = math.gcd(e1, M)
        e1p, Mp, e2p = e1 // g, M // g, (e2 // g) % (M // g)
        if Mp <= 1:
            return [[1, 0], [0, 1]]
        inv = pow(e1p, -1, Mp)
        x0 = (-e2p * inv) % Mp
        return [[Mp, 0], [x0, 1]]
    raise NotImplementedError("homogeneous_basis supports at most two unknowns")


def lll_reduce(basis: Sequence[Sequence[int]],
               delta: Fraction = Fraction(3, 4)) -> Tuple[List[List[int]], List[List[int]]]:
    """LLL on the rows of an integer basis.

    Returns ``(reduced, transform)`` with ``transform * basis = reduced``.
    Exact rational arithmetic; no floating point.
    """
    B = [[Fraction(int(x)) for x in row] for row in basis]
    n = len(B)
    if n == 0:
        return [], []
    U = [[Fraction(1 if i == j else 0) for j in range(n)] for i in range(n)]

    def gram_schmidt():
        star: List[List[Fraction]] = []
        mu = [[Fraction(0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            v = B[i][:]
            for j in range(i):
                den = sum(star[j][k] ** 2 for k in range(n))
                if den == 0:
                    mu[i][j] = Fraction(0)
                else:
                    mu[i][j] = sum(B[i][k] * star[j][k] for k in range(n)) / den
                v = [v[k] - mu[i][j] * star[j][k] for k in range(n)]
            star.append(v)
        return star, mu

    k = 1
    while k < n:
        star, mu = gram_schmidt()
        for j in range(k - 1, -1, -1):
            if abs(mu[k][j]) > Fraction(1, 2):
                r = int(round(mu[k][j]))
                if r:
                    B[k] = [B[k][i] - r * B[j][i] for i in range(n)]
                    U[k] = [U[k][i] - r * U[j][i] for i in range(n)]
                    star, mu = gram_schmidt()
        lhs = sum(star[k][i] ** 2 for i in range(n))
        rhs = (delta - mu[k][k - 1] ** 2) * sum(star[k - 1][i] ** 2 for i in range(n))
        if lhs >= rhs:
            k += 1
        else:
            B[k], B[k - 1] = B[k - 1], B[k]
            U[k], U[k - 1] = U[k - 1], U[k]
            k = max(k - 1, 1)
    return [[int(x) for x in row] for row in B], [[int(x) for x in row] for row in U]


def _ceil_div(a: int, b: int) -> int:
    return -((-a) // b)


def enumerate_coset(basis: Sequence[Sequence[int]], particular: Sequence[int],
                    u: Sequence[int], deadline: Optional[float] = None,
                    first_range: Optional[Tuple[int, int]] = None
                    ) -> Iterator[Tuple[int, ...]]:
    """All points ``particular + lattice(basis)`` in the box ``|x_i| <= u_i``.

    ``first_range`` optionally restricts the first coordinate to a closed
    interval (used to shard the exponent box).
    """
    n = len(particular)
    if n == 0:
        yield ()
        return
    if n == 1:
        m = int(basis[0][0])
        if m == 0:
            raise ValueError("degenerate one-dimensional lattice")
        m = abs(m)
        x0 = int(particular[0]) % m
        lo = -int(u[0]) if first_range is None else max(-int(u[0]), first_range[0])
        hi = int(u[0]) if first_range is None else min(int(u[0]), first_range[1])
        kmin = _ceil_div(lo - x0, m)
        kmax = (hi - x0) // m
        for k in range(kmin, kmax + 1):
            if deadline is not None and time.time() > deadline:
                return
            yield (x0 + k * m,)
        return
    if n == 2:
        (b11, b12), (b21, b22) = basis
        det = b11 * b22 - b12 * b21
        if det == 0:
            raise ValueError("singular lattice basis")
        x0, y0 = int(particular[0]), int(particular[1])
        lo1 = -int(u[0]) if first_range is None else max(-int(u[0]), first_range[0])
        hi1 = int(u[0]) if first_range is None else min(int(u[0]), first_range[1])
        lo2, hi2 = -int(u[1]), int(u[1])
        # Expand the target box by the particular solution, then invert.
        w1 = max(abs(lo1 - x0), abs(hi1 - x0))
        w2 = max(abs(lo2 - y0), abs(hi2 - y0))
        K1 = _ceil_div(abs(b22) * w1 + abs(b12) * w2, abs(det)) + 1
        K2 = _ceil_div(abs(b21) * w1 + abs(b11) * w2, abs(det)) + 1
        for k1 in range(-K1, K1 + 1):
            if deadline is not None and time.time() > deadline:
                return
            for k2 in range(-K2, K2 + 1):
                x = x0 + k1 * b11 + k2 * b21
                y = y0 + k1 * b12 + k2 * b22
                if lo1 <= x <= hi1 and lo2 <= y <= hi2:
                    yield (x, y)
        return
    raise NotImplementedError("coset enumeration supports at most two unknowns")


# ---------------------------------------------------------------------------
# stage (c): reconstruction and exact filtering
# ---------------------------------------------------------------------------


def _powers(p: int, upto: int) -> List[int]:
    out = [1]
    for _ in range(upto):
        out.append(out[-1] * p)
    return out


def _reconstruct(gamma: Sequence[int], others: Sequence[int],
                 pow_pos: Dict[int, List[int]], pow_neg: Dict[int, List[int]]
                 ) -> Tuple[int, int]:
    a = b = 1
    for p, g in zip(others, gamma):
        if g > 0:
            a *= pow_pos[p][g]
        elif g < 0:
            b *= pow_neg[p][-g]
    return a, b


def scan_block(S: Sequence[int], q: int, bound: dict,
               shard: int = 0, of: int = 1,
               deadline: Optional[float] = None) -> dict:
    """Stages (b)+(c) for one prime ``q`` and one exponent-box shard."""
    S = clean_S(S)
    if q not in S:
        raise ValueError(f"q={q} is not in S")
    if of < 1 or not (0 <= shard < of):
        raise ValueError("require 0 <= shard < of")
    u = {int(p): int(v) for p, v in bound["exponent_bounds"].items()}
    others = [p for p in S if p != q]
    if len(others) > 2:
        raise NotImplementedError("scan_block supports |S| <= 3")

    if not others:
        # Only possible when S = {q}; the candidate is 1 + 1 = 2.
        sols = set()
        if q == 2:
            a, b, c = 1, 1, 2
            ex = smooth_exponents(c, S)
            if ex is not None and all(ex[p] <= u[p] for p in S):
                sols.add((a, b, c))
        return {
            "q": q,
            "modulus": 1,
            "discrete_logs": {},
            "coset_representative": [],
            "lattice_basis": [],
            "lll_basis": [],
            "lll_transform": [],
            "box": {},
            "shard_box": {},
            "vectors_tested": 1,
            "complete": True,
            "solutions": [list(t) for t in sorted(sols)],
        }

    # Exact congruence a/b == -1 (mod q).
    if q == 2:
        M = 1
        e = [0] * len(others)
        target = 0
    else:
        g, table = discrete_log_table(q)
        M = q - 1
        e = [table[int(p) % q] for p in others]
        target = table[q - 1]  # -1 mod q

    particular = particular_solution(e, target, M)
    if particular is None:
        return {
            "q": q,
            "modulus": M,
            "discrete_logs": {str(p): int(x) for p, x in zip(others, e)},
            "coset_representative": None,
            "lattice_basis": [],
            "lll_basis": [],
            "lll_transform": [],
            "box": {str(p): u[p] for p in others},
            "shard_box": {},
            "vectors_tested": 0,
            "complete": True,
            "solutions": [],
        }

    basis = homogeneous_basis(e, M)
    reduced, transform = lll_reduce(basis)

    # Shard the first exponent coordinate, if requested.
    first_range = None
    shard_box: Dict[str, List[int]] = {str(p): [-u[p], u[p]] for p in others}
    if of > 1:
        p1 = others[0]
        lo, hi = -u[p1], u[p1]
        width = hi - lo + 1
        start = lo + (shard * width) // of
        end = lo + ((shard + 1) * width) // of - 1
        first_range = (start, end)
        shard_box[str(p1)] = [start, end]

    pow_pos = {p: _powers(p, u[p]) for p in others}
    pow_neg = pow_pos  # p^e is used for both positive and negative exponents
    sols = set()
    tested = 0
    for gamma in enumerate_coset(reduced, particular, [u[p] for p in others],
                                 deadline, first_range):
        tested += 1
        a, b = _reconstruct(gamma, others, pow_pos, pow_neg)
        if a > b:
            a, b = b, a
        c = a + b
        if c % q:
            continue
        ex = smooth_exponents(c, S)
        if ex is None:
            continue
        if any(ex[p] > u[p] for p in S):
            continue
        if math.gcd(a, b) != 1:
            continue
        sols.add((a, b, c))

    complete = deadline is None or time.time() <= deadline
    return {
        "q": q,
        "modulus": M,
        "discrete_logs": {str(p): int(x) for p, x in zip(others, e)},
        "coset_representative": [int(x) for x in particular],
        "lattice_basis": [[int(x) for x in row] for row in basis],
        "lll_basis": [[int(x) for x in row] for row in reduced],
        "lll_transform": [[int(x) for x in row] for row in transform],
        "box": {str(p): u[p] for p in others},
        "shard_box": shard_box,
        "vectors_tested": tested,
        "complete": complete,
        "solutions": [list(t) for t in sorted(sols)],
    }


def solve(S: Sequence[int], q: Optional[int] = None, shard: int = 0, of: int = 1,
          deadline: Optional[float] = None) -> dict:
    """Full certificate for ``S``, or one block if ``q`` is given.

    Blocks are untrusted until ``axiom.sunit.check`` accepts the certificate.
    """
    S = clean_S(S)
    bound = height_bound(S)
    qs = [q] if q is not None else list(S)
    blocks = [scan_block(S, qq, bound, shard, of, deadline) for qq in qs]
    sols = sorted({tuple(t) for b in blocks for t in b["solutions"]})
    return {
        "kind": "sunit_certificate",
        "version": 1,
        "S": S,
        "height_bound": bound,
        "blocks": blocks,
        "solutions": [list(t) for t in sols],
        "solution_count": len(sols),
        "complete": all(b["complete"] for b in blocks),
        "shard": shard,
        "of": of,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def merge_certificates(certs: Sequence[dict]) -> dict:
    """Merge shard certificates for the same ``S`` and verify box coverage."""
    if not certs:
        raise ValueError("no certificates to merge")
    S = clean_S(certs[0]["S"])
    if any(clean_S(c["S"]) != S for c in certs):
        raise ValueError("certificates disagree on S")
    bound = certs[0]["height_bound"]
    if any(c["height_bound"] != bound for c in certs):
        raise ValueError("certificates disagree on the height bound")
    by_q: Dict[int, List[dict]] = {}
    for cert in certs:
        for block in cert["blocks"]:
            by_q.setdefault(int(block["q"]), []).append(block)
    merged_blocks = []
    for q in S:
        blocks = by_q.get(q, [])
        if not blocks:
            raise ValueError(f"missing block for q={q}")
        base = blocks[0]
        for b in blocks[1:]:
            for key in ("modulus", "discrete_logs", "coset_representative",
                        "lattice_basis", "lll_basis", "lll_transform", "box"):
                if b.get(key) != base.get(key):
                    raise ValueError(f"shards disagree on {key} for q={q}")
        # Verify that the shard boxes cover the full box exactly once.
        u = {int(p): int(v) for p, v in base["box"].items()}
        others = sorted(u)
        if len(others) == 1:
            intervals = [tuple(b["shard_box"][str(others[0])]) for b in blocks]
            intervals.sort()
            cursor = -u[others[0]]
            for lo, hi in intervals:
                if lo != cursor:
                    raise ValueError(f"shard gap/overlap for q={q}")
                cursor = hi + 1
            if cursor != u[others[0]] + 1:
                raise ValueError(f"shard coverage incomplete for q={q}")
        elif len(others) == 2:
            # All shards must share the second coordinate range and tile the first.
            p1, p2 = others
            intervals = []
            for b in blocks:
                box = b["shard_box"]
                if tuple(box[str(p2)]) != (-u[p2], u[p2]):
                    raise ValueError(f"unexpected second-coordinate shard for q={q}")
                intervals.append(tuple(box[str(p1)]))
            intervals.sort()
            cursor = -u[p1]
            for lo, hi in intervals:
                if lo != cursor:
                    raise ValueError(f"shard gap/overlap for q={q}")
                cursor = hi + 1
            if cursor != u[p1] + 1:
                raise ValueError(f"shard coverage incomplete for q={q}")
        merged = dict(base)
        sols = sorted({tuple(t) for b in blocks for t in b["solutions"]})
        merged["solutions"] = [list(t) for t in sols]
        merged["vectors_tested"] = sum(int(b["vectors_tested"]) for b in blocks)
        merged["complete"] = all(bool(b["complete"]) for b in blocks)
        merged["shards"] = len(blocks)
        # After tiling, the merged block covers the full exponent box.
        merged["shard_box"] = {str(p): [-u[p], u[p]] for p in others}
        merged_blocks.append(merged)
    sols = sorted({tuple(t) for b in merged_blocks for t in b["solutions"]})
    return {
        "kind": "sunit_certificate",
        "version": 1,
        "S": S,
        "height_bound": bound,
        "blocks": merged_blocks,
        "solutions": [list(t) for t in sols],
        "solution_count": len(sols),
        "complete": all(b["complete"] for b in merged_blocks),
        "shard": 0,
        "of": 1,
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def validate_triple(a: int, b: int, c: int, S: Sequence[int]) -> Tuple[bool, str]:
    """Exact local check of one triple."""
    S = clean_S(S)
    if a <= 0 or b <= 0 or c <= 0:
        return False, "non-positive entry"
    if a + b != c:
        return False, "a+b != c"
    if a > b:
        return False, "not canonical (a > b)"
    if math.gcd(a, b) != 1:
        return False, "gcd(a,b) != 1"
    for n, name in ((a, "a"), (b, "b"), (c, "c")):
        if not is_smooth(n, S):
            return False, f"{name} is not S-smooth"
    return True, ""


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description="certified S-unit solver")
    ap.add_argument("--S", required=True,
                    help="comma-separated primes, e.g. 2,3,5")
    ap.add_argument("--q", type=int, default=None,
                    help="solve only this block (for sharding)")
    ap.add_argument("--shard", type=int, default=0)
    ap.add_argument("--of", type=int, default=1)
    ap.add_argument("--time", type=float, default=None,
                    help="seconds before the enumeration stops")
    ap.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    S = [int(x) for x in a.S.split(",") if x.strip()]
    deadline = time.time() + a.time if a.time else None
    cert = solve(S, a.q, a.shard, a.of, deadline)
    import json
    import os
    text = json.dumps(cert, indent=2)
    if a.out:
        os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
        with open(a.out, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
