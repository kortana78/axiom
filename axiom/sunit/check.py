"""Independent checker for ``axiom.sunit.hunt`` certificates.

This module deliberately shares no code with the solver.  It has its own
factorisation, smoothness test, height-bound computation, discrete
logarithms, lattice-basis construction, LLL verification, and full exponent
box enumeration.

It checks four things:

1. the height bound and exponent boxes are large enough;
2. the congruence lattice, coset representative and LLL data are correct;
3. the solution list is exactly the set obtained by re-enumerating the full
   exponent box from scratch (not just the lattice points the solver used);
4. every solution satisfies ``a + b = c``, coprimality, ``a <= b`` and
   S-smoothness.

The checker never trusts worker output and never writes to ``results/``.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from decimal import Decimal, ROUND_FLOOR, getcontext
from fractions import Fraction
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

getcontext().prec = 90

Triple = Tuple[int, int, int]


class CheckError(Exception):
    pass


def _fail(msg: str) -> None:
    raise CheckError(msg)


# ---------------------------------------------------------------------------
# basic arithmetic (independent implementation)
# ---------------------------------------------------------------------------


def _factor(n: int) -> Dict[int, int]:
    if n <= 0:
        _fail(f"factorisation of non-positive {n}")
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


def _prime(n: int) -> bool:
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


def _smooth_exp(n: int, S: Sequence[int]) -> Optional[Dict[int, int]]:
    if n <= 0:
        return None
    out: Dict[int, int] = {}
    for p in S:
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        out[p] = e
    return out if n == 1 else None


def _clean_S(S: Sequence[int]) -> List[int]:
    if not S:
        _fail("empty S")
    out = sorted(set(int(p) for p in S))
    for p in out:
        if not _prime(p):
            _fail(f"non-prime in S: {p}")
    return out


# ---------------------------------------------------------------------------
# height bound
# ---------------------------------------------------------------------------


def _bound_lower(S: Sequence[int]) -> Tuple[Decimal, Dict[int, Decimal]]:
    N = 1
    for p in S:
        N *= p
    logN = Decimal(N).ln().quantize(Decimal("0.000001"), rounding=ROUND_FLOOR)
    B = (Decimal(5) / 2 * N * logN + 9 * N).quantize(
        Decimal("0.000001"), rounding=ROUND_FLOOR)
    logs = {p: Decimal(p).ln().quantize(Decimal("0.000001"), rounding=ROUND_FLOOR)
            for p in S}
    return B, logs


# ---------------------------------------------------------------------------
# discrete logarithms and lattices
# ---------------------------------------------------------------------------


def _primitive_root(q: int) -> int:
    if q == 2:
        return 1
    phi = q - 1
    factors = set(_factor(phi))
    for g in range(2, q):
        if all(pow(g, phi // r, q) != 1 for r in factors):
            return g
    _fail(f"no primitive root modulo {q}")
    return 1


def _dlog_table(q: int) -> Tuple[int, Dict[int, int]]:
    if q == 2:
        return 1, {1: 0}
    g = _primitive_root(q)
    table: Dict[int, int] = {}
    x = 1
    for e in range(q - 1):
        table[x] = e
        x = (x * g) % q
    if len(table) != q - 1:
        _fail(f"bad primitive root modulo {q}")
    return g, table


def _gcd_all(values: Iterable[int]) -> int:
    g = 0
    for v in values:
        g = math.gcd(g, int(v))
    return g


def _index_1d(e0: int, M: int) -> int:
    return M // math.gcd(e0 % M if M else 0, M) if M else 1


def _index_2d(e0: int, e1: int, M: int) -> int:
    if M <= 1:
        return 1
    return M // _gcd_all([e0 % M, e1 % M, M])


def _det2(A: Sequence[Sequence[int]]) -> int:
    return int(A[0][0]) * int(A[1][1]) - int(A[0][1]) * int(A[1][0])


def _matmul2(A: Sequence[Sequence[int]], B: Sequence[Sequence[int]]) -> List[List[int]]:
    return [[sum(int(A[i][k]) * int(B[k][j]) for k in range(2)) for j in range(2)]
            for i in range(2)]


def _lll_conditions(B: Sequence[Sequence[int]], delta: Fraction = Fraction(3, 4)) -> None:
    """Exact size-reduction and Lovasz conditions for a 2-row basis."""
    b1 = [Fraction(int(x)) for x in B[0]]
    b2 = [Fraction(int(x)) for x in B[1]]
    n1 = sum(x * x for x in b1)
    if n1 == 0:
        _fail("zero first LLL basis vector")
    mu = sum(b1[i] * b2[i] for i in range(2)) / n1
    if abs(mu) > Fraction(1, 2):
        _fail(f"LLL size reduction fails: |mu|={float(abs(mu))}")
    n2 = sum(x * x for x in b2)
    star2 = n2 - mu * mu * n1
    if star2 < (delta - mu * mu) * n1:
        _fail("LLL Lovasz condition fails")


# ---------------------------------------------------------------------------
# full-box enumeration (independent of the solver's lattice enumeration)
# ---------------------------------------------------------------------------


def _pow_table(p: int, upto: int) -> List[int]:
    out = [1]
    for _ in range(upto):
        out.append(out[-1] * p)
    return out


def _mod_tables(p: int, q: int, upto: int) -> Tuple[List[int], List[int]]:
    pos = [1]
    for _ in range(upto):
        pos.append((pos[-1] * p) % q)
    neg = [1]
    for _ in range(upto):
        neg.append((neg[-1] * pow(p, -1, q)) % q)
    return pos, neg


def _term_mod(pos: List[int], neg: List[int], g: int) -> int:
    return pos[g] if g >= 0 else neg[-g]


def _enumerate_box(S: Sequence[int], q: int, u: Dict[int, int],
                   deadline=None) -> Set[Triple]:
    """Re-enumerate the entire exponent box and return exact solutions."""
    import time
    others = [p for p in S if p != q]
    if not others:
        out: Set[Triple] = set()
        if q == 2:
            ex = _smooth_exp(2, S)
            if ex is not None and all(ex[p] <= u[p] for p in S):
                out.add((1, 1, 2))
        return out

    if len(others) == 1:
        p1 = others[0]
        big1 = _pow_table(p1, u[p1])
        if q == 2:
            pos1, neg1 = [1], [1]
        else:
            pos1, neg1 = _mod_tables(p1, q, u[p1])
        out = set()
        for g1 in range(-u[p1], u[p1] + 1):
            if deadline is not None and time.time() > deadline:
                return out
            if q != 2 and _term_mod(pos1, neg1, g1) != q - 1:
                continue
            a = big1[g1] if g1 > 0 else 1
            b = big1[-g1] if g1 < 0 else 1
            c = a + b
            if c % q:
                continue
            ex = _smooth_exp(c, S)
            if ex is None or any(ex[p] > u[p] for p in S):
                continue
            if math.gcd(a, b) != 1:
                continue
            out.add((min(a, b), max(a, b), c))
        return out

    if len(others) != 2:
        _fail("checker supports |S| <= 3")
    p1, p2 = others
    big1 = _pow_table(p1, u[p1])
    big2 = _pow_table(p2, u[p2])
    if q == 2:
        pos1 = neg1 = pos2 = neg2 = [1]
    else:
        pos1, neg1 = _mod_tables(p1, q, u[p1])
        pos2, neg2 = _mod_tables(p2, q, u[p2])
    out = set()
    for g1 in range(-u[p1], u[p1] + 1):
        if deadline is not None and time.time() > deadline:
            return out
        a1 = big1[g1] if g1 > 0 else 1
        b1 = big1[-g1] if g1 < 0 else 1
        m1 = _term_mod(pos1, neg1, g1) if q != 2 else 1
        for g2 in range(-u[p2], u[p2] + 1):
            if q != 2:
                m = (m1 * _term_mod(pos2, neg2, g2)) % q
                if m != q - 1:
                    continue
            a = a1 * (big2[g2] if g2 > 0 else 1)
            b = b1 * (big2[-g2] if g2 < 0 else 1)
            c = a + b
            if c % q:
                continue
            ex = _smooth_exp(c, S)
            if ex is None or any(ex[p] > u[p] for p in S):
                continue
            if math.gcd(a, b) != 1:
                continue
            out.add((min(a, b), max(a, b), c))
    return out


# ---------------------------------------------------------------------------
# certificate checks
# ---------------------------------------------------------------------------


def _check_block(S: Sequence[int], block: dict, bound: dict,
                 full: bool) -> Set[Triple]:
    q = int(block.get("q"))
    if q not in S:
        _fail(f"block q={q} not in S")
    others = [p for p in S if p != q]
    u = {int(p): int(v) for p, v in bound["exponent_bounds"].items()}

    # The block's box must be exactly the certificate's exponent box.
    box = {int(p): int(v) for p, v in block.get("box", {}).items()}
    expected_box = {p: u[p] for p in others}
    if box != expected_box:
        _fail(f"block q={q} box {box} != expected {expected_box}")

    if not others:
        if block.get("modulus") != 1:
            _fail(f"block q={q}: modulus should be 1")
        sols = {tuple(t) for t in block.get("solutions", [])}
        full_sols = _enumerate_box(S, q, u)
        if full and sols != full_sols:
            _fail(f"block q={q}: solutions differ from full box")
        if not full and not sols <= full_sols:
            _fail(f"block q={q}: shard solution not in full box")
        return full_sols

    M = int(block.get("modulus"))
    if q == 2:
        if M != 1:
            _fail("block q=2 must use modulus 1")
        e = [0] * len(others)
        target = 0
    else:
        if M != q - 1:
            _fail(f"block q={q}: modulus {M} != q-1")
        _g, table = _dlog_table(q)
        e = [table[int(p) % q] for p in others]
        target = table[q - 1]
        logged = {int(p): int(v) for p, v in block.get("discrete_logs", {}).items()}
        if logged != {p: e[i] for i, p in enumerate(others)}:
            _fail(f"block q={q}: discrete logs are wrong")

    # Coset representative.
    part = block.get("coset_representative")
    if part is None:
        _fail(f"block q={q}: null coset representative")
    if len(part) != len(others):
        _fail(f"block q={q}: coset representative has wrong length")
    lhs = sum(int(e[i]) * int(part[i]) for i in range(len(others))) % M if M > 1 else 0
    if M > 1 and lhs != target % M:
        _fail(f"block q={q}: coset representative does not satisfy congruence")

    # Homogeneous lattice basis.
    basis = [[int(x) for x in row] for row in block.get("lattice_basis", [])]
    if len(basis) != len(others):
        _fail(f"block q={q}: lattice basis has wrong rank")
    for row in basis:
        if M > 1 and sum(int(e[i]) * row[i] for i in range(len(others))) % M != 0:
            _fail(f"block q={q}: lattice basis vector not in lattice")
    if len(others) == 1:
        want = _index_1d(e[0], M)
        got = abs(basis[0][0])
        if got != want:
            _fail(f"block q={q}: 1D lattice index {got} != {want}")
    else:
        want = _index_2d(e[0], e[1], M)
        got = abs(_det2(basis))
        if got != want:
            _fail(f"block q={q}: 2D lattice index {got} != {want}")

    # LLL output and transform.
    lll = [[int(x) for x in row] for row in block.get("lll_basis", [])]
    U = [[int(x) for x in row] for row in block.get("lll_transform", [])]
    if len(lll) != len(others) or len(U) != len(others):
        _fail(f"block q={q}: LLL data has wrong rank")
    if len(others) == 1:
        if abs(U[0][0]) != 1:
            _fail(f"block q={q}: LLL transform not unimodular")
        if U[0][0] * basis[0][0] != lll[0][0]:
            _fail(f"block q={q}: LLL transform does not reproduce basis")
        if abs(lll[0][0]) != abs(basis[0][0]):
            _fail(f"block q={q}: LLL changed the 1D lattice")
    else:
        if abs(_det2(U)) != 1:
            _fail(f"block q={q}: LLL transform not unimodular")
        prod = _matmul2(U, basis)
        if prod != lll:
            _fail(f"block q={q}: LLL transform does not reproduce basis")
        _lll_conditions(lll)
        for row in lll:
            if M > 1 and sum(int(e[i]) * row[i] for i in range(2)) % M != 0:
                _fail(f"block q={q}: LLL vector not in lattice")

    # Re-enumerate the full box and compare.
    full_sols = _enumerate_box(S, q, u)
    sols = {tuple(int(x) for x in t) for t in block.get("solutions", [])}
    if full:
        if sols != full_sols:
            missing = sorted(full_sols - sols)
            extra = sorted(sols - full_sols)
            _fail(f"block q={q}: solution set mismatch; missing={missing[:5]} "
                  f"extra={extra[:5]}")
    else:
        if not sols <= full_sols:
            _fail(f"block q={q}: shard contains a solution not in the full box")
    return full_sols


def check_certificate(cert: dict, expected_S: Optional[Sequence[int]] = None,
                      published: Optional[Sequence[Triple]] = None,
                      deadline=None) -> dict:
    """Validate a certificate.  Raises ``CheckError`` on any problem."""
    if cert.get("kind") != "sunit_certificate":
        _fail("not a sunit certificate")
    if int(cert.get("version", 0)) != 1:
        _fail("unsupported certificate version")
    S = _clean_S(cert.get("S", []))
    if expected_S is not None and _clean_S(expected_S) != S:
        _fail(f"S mismatch: certificate {S}, expected {list(expected_S)}")
    if len(S) > 3:
        _fail("checker supports |S| <= 3")

    bound = cert.get("height_bound")
    if not isinstance(bound, dict):
        _fail("missing height bound")
    if bound.get("S") != S:
        _fail("height bound S mismatch")
    if int(bound.get("N_S", 0)) != math.prod(S):
        _fail("height bound N_S mismatch")
    try:
        cert_B = Decimal(str(bound["B"]))
    except Exception:
        _fail("height bound B is not a decimal")
    B_lower, logs = _bound_lower(S)
    if cert_B < B_lower:
        _fail(f"height bound too small: certificate {cert_B} < required {B_lower}")
    u_cert = {int(p): int(v) for p, v in bound.get("exponent_bounds", {}).items()}
    if set(u_cert) != set(S):
        _fail("exponent bounds do not cover S")
    for p in S:
        need = int((cert_B / logs[p]).to_integral_value(rounding=ROUND_FLOOR))
        if u_cert[p] < need:
            _fail(f"exponent bound for {p} too small: {u_cert[p]} < {need}")

    blocks = cert.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        _fail("missing blocks")
    if sorted(int(b.get("q")) for b in blocks) != S:
        _fail("blocks do not cover S exactly once")
    full = int(cert.get("of", 1)) == 1 and int(cert.get("shard", 0)) == 0
    all_sols: Set[Triple] = set()
    for block in blocks:
        all_sols |= _check_block(S, block, bound, full)

    cert_sols = {tuple(int(x) for x in t) for t in cert.get("solutions", [])}
    if full and cert_sols != all_sols:
        missing = sorted(all_sols - cert_sols)
        extra = sorted(cert_sols - all_sols)
        _fail(f"certificate solution set mismatch; missing={missing[:5]} "
              f"extra={extra[:5]}")
    if not full and not cert_sols <= all_sols:
        _fail("shard certificate contains a solution not in the full box")
    if int(cert.get("solution_count", -1)) != len(cert_sols):
        _fail("solution_count does not match solutions")

    for a, b, c in cert_sols:
        if a <= 0 or b <= 0 or c <= 0:
            _fail(f"non-positive triple {(a, b, c)}")
        if a + b != c:
            _fail(f"bad sum {(a, b, c)}")
        if a > b:
            _fail(f"non-canonical triple {(a, b, c)}")
        if math.gcd(a, b) != 1:
            _fail(f"not coprime {(a, b, c)}")
        for n, name in ((a, "a"), (b, "b"), (c, "c")):
            ex = _smooth_exp(n, S)
            if ex is None:
                _fail(f"{name} not S-smooth in {(a, b, c)}")
            if any(ex[p] > u_cert[p] for p in S):
                _fail(f"{name} exponent exceeds box in {(a, b, c)}")

    if published is not None:
        pub = {tuple(int(x) for x in t) for t in published}
        if cert_sols != pub:
            missing = sorted(pub - cert_sols)
            extra = sorted(cert_sols - pub)
            _fail(f"published list mismatch; missing={missing[:5]} extra={extra[:5]}")

    return {
        "status": "PASS",
        "S": S,
        "solutions": len(cert_sols),
        "B": str(cert_B),
        "exponent_bounds": u_cert,
        "full": full,
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="independent S-unit certificate checker")
    ap.add_argument("--certificate", required=True)
    ap.add_argument("--S", default=None, help="comma-separated expected primes")
    ap.add_argument("--published", default=None,
                    help="JSON file with a list of [a,b,c] triples")
    a = ap.parse_args(argv)
    with open(a.certificate, encoding="utf-8") as fh:
        cert = json.load(fh)
    expected = None
    if a.S:
        expected = [int(x) for x in a.S.split(",") if x.strip()]
    published = None
    if a.published:
        with open(a.published, encoding="utf-8") as fh:
            published = json.load(fh)
    try:
        report = check_certificate(cert, expected, published)
    except CheckError as exc:
        print(f"FAIL: {exc}")
        return 1
    print("PASS " + json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
