"""Exact radical arithmetic and bounded search kernels for abc triples.

The search works on coprime positive integers a < b with c = a + b. It uses
two complementary families:

* ``c_smooth``: c is smooth and a runs through a window. The other leg b is
  arbitrary; its radical comes from a sieve.
* ``legs_smooth``: both legs a and b are smooth. Then c is arbitrary and its
  radical comes from the sieve.

Every candidate is only a suggestion. The merge step recomputes gcd, the
radical from prime factorizations, and the quality from scratch.
"""
from __future__ import annotations

import heapq
import itertools
import math
import time
from typing import Dict, Iterator, List, Optional, Tuple

import numpy as np
import sympy as sp


def primes_upto(n: int) -> List[int]:
    """All primes <= n (small n only)."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(n) + 1):
        if sieve[i]:
            sieve[i * i::i] = b"\x00" * (((n - i * i) // i) + 1)
    return [i for i in range(n + 1) if sieve[i]]


def radical(n: int) -> int:
    """Product of the distinct primes dividing n. radical(1) = 1."""
    n = int(n)
    if n < 1:
        raise ValueError("radical is defined for positive integers")
    if n == 1:
        return 1
    return int(math.prod(int(p) for p in sp.factorint(n)))


def factorization(n: int) -> Dict[int, int]:
    n = int(n)
    if n < 1:
        raise ValueError("factorization is defined for positive integers")
    return {int(p): int(e) for p, e in sp.factorint(n).items()}


def radical_product(*ns: int) -> int:
    """radical of a product, without forming the product first."""
    primes = set()
    for n in ns:
        n = int(n)
        if n < 1:
            raise ValueError("radical is defined for positive integers")
        if n > 1:
            primes.update(int(p) for p in sp.factorint(n))
    return int(math.prod(primes)) if primes else 1


def quality(a: int, b: int, c: Optional[int] = None) -> float:
    """q = log(c) / log(rad(a*b*c))."""
    c = int(a) + int(b) if c is None else int(c)
    rad = radical_product(a, b, c)
    if rad <= 1:
        raise ValueError("radical of the triple is 1")
    return math.log(c) / math.log(rad)


def validate_triple(a: int, b: int, c: int) -> Tuple[bool, str]:
    """Exact checks for a positive, coprime abc triple."""
    try:
        a, b, c = int(a), int(b), int(c)
    except (TypeError, ValueError):
        return False, "not integers"
    if a <= 0 or b <= 0 or c <= 0:
        return False, "not positive"
    if a + b != c:
        return False, "a + b != c"
    if math.gcd(a, b) != 1:
        return False, "not coprime"
    return True, ""


def make_record(a: int, b: int, c: Optional[int] = None) -> dict:
    """Validate a triple and return its exact canonical record.

    The smaller leg is stored first (a <= b). Raises ValueError if the
    triple is not positive, additive and coprime.
    """
    c = int(a) + int(b) if c is None else int(c)
    a, b = int(a), int(b)
    ok, why = validate_triple(a, b, c)
    if not ok:
        raise ValueError(why)
    if a > b:
        a, b = b, a
    fa, fb, fc = factorization(a), factorization(b), factorization(c)
    rad = radical_product(a, b, c)
    q = math.log(c) / math.log(rad)
    return {
        "a": a, "b": b, "c": c,
        "rad": rad,
        "q": q,
        "factors": {
            "a": {str(p): e for p, e in fa.items()},
            "b": {str(p): e for p, e in fb.items()},
            "c": {str(p): e for p, e in fc.items()},
        },
    }


def verify_record(raw: dict) -> Optional[dict]:
    """Rebuild a record from its (a, b, c). Ignore untrusted rad/q fields."""
    try:
        return make_record(int(raw["a"]), int(raw["b"]), int(raw["c"]))
    except (KeyError, TypeError, ValueError):
        return None


def sieve_radical(n_max: int) -> np.ndarray:
    """rad[n] for 0 <= n <= n_max, using a uint32 sieve.

    Memory is 4*(n_max+1) bytes. n_max is capped by the caller; the default
    swarm size (10^8) uses about 400 MB.
    """
    n_max = int(n_max)
    if n_max < 0:
        raise ValueError("n_max must be non-negative")
    dtype = np.uint32 if n_max < 2**32 - 1 else np.uint64
    size = n_max + 1
    rem = np.arange(size, dtype=dtype)
    rem[0] = 1
    rad = np.ones(size, dtype=dtype)
    for p0 in primes_upto(math.isqrt(n_max)):
        p = int(p0)
        idx = np.arange(p, size, p, dtype=np.int64)
        rad[idx] *= dtype(p)
        sub = rem[idx]
        while True:
            divisible = (sub % dtype(p)) == 0
            if not divisible.any():
                break
            sub[divisible] //= dtype(p)
        rem[idx] = sub
    leftover = rem > 1
    rad[leftover] *= rem[leftover]
    return rad


def smooth_upto(y: int, n_max: int) -> np.ndarray:
    """Sorted y-smooth numbers <= n_max."""
    n_max = int(n_max)
    if n_max < 1:
        return np.empty(0, dtype=np.int64)
    out = [1]
    for p in primes_upto(int(y)):
        nxt = []
        for x in out:
            v = x
            while v <= n_max:
                nxt.append(v)
                v *= p
        out = nxt
    out.sort()
    return np.array(out, dtype=np.int64)


def pair_layout(smooth: np.ndarray, c_max: int) -> dict:
    """Index the pairs x < y of smooth numbers with x + y <= c_max.

    Returns counts of pairs per x index, their cumulative sums, and the
    total. The layout is built in O(len(smooth)).
    """
    s = np.asarray(smooth, dtype=np.int64)
    s = s[s <= c_max]
    k = len(s)
    counts = np.zeros(k, dtype=np.int64)
    j = k - 1
    for i in range(k):
        if j <= i:
            break
        si = int(s[i])
        while j > i and si + int(s[j]) > c_max:
            j -= 1
        if j <= i:
            break
        counts[i] = j - i
    cum = np.cumsum(counts)
    return {"counts": counts, "cum": cum,
            "total": int(cum[-1]) if k else 0, "smooth": s}


def pair_slice_blocks(layout: dict, lo: int, hi: int) -> Iterator[Tuple[int, int, int, int, int]]:
    """Yield (i, j0, j1, block_lo, block_hi) covering pair indices [lo, hi)."""
    smooth = layout["smooth"]
    counts, cum = layout["counts"], layout["cum"]
    k = len(smooth)
    lo, hi = int(lo), int(hi)
    while lo < hi and lo < layout["total"]:
        i = int(np.searchsorted(cum, lo, side="right"))
        if i >= k:
            break
        prev = int(cum[i - 1]) if i else 0
        start = lo - prev
        take = min(hi - lo, int(counts[i]) - start)
        if take <= 0:
            lo += 1
            continue
        j0 = i + 1 + start
        yield i, j0, j0 + take, lo, lo + take
        lo += take


def _heap_push(heap: list, top_n: int, counter, rec: dict) -> None:
    if top_n <= 0:
        return
    item = (rec["q"], next(counter), rec)
    if len(heap) < top_n:
        heapq.heappush(heap, item)
    elif item[0] > heap[0][0]:
        heapq.heapreplace(heap, item)


def _heap_sorted(heap: list) -> List[dict]:
    return [rec for _, _, rec in sorted(heap, key=lambda t: (-t[0], t[1]))]


def scan_c_smooth(rad: np.ndarray, smooth: np.ndarray, a_lo: int, a_hi: int,
                  c_max: int, min_quality: float = 1.0, top_n: int = 100,
                  deadline: Optional[float] = None) -> dict:
    """Scan a in [a_lo, a_hi) with c smooth, keeping the best triples.

    Only canonical triples a <= b are tested, hence c >= 2a. The loop is
    anytime: on deadline it returns the next a and complete=False.
    """
    c_max = int(c_max)
    smooth = np.asarray(smooth, dtype=np.int64)
    smooth = smooth[smooth <= c_max]
    a_lo = max(1, int(a_lo))
    a_hi = min(int(a_hi), c_max // 2 + 1)
    heap: list = []
    counter = itertools.count()
    tested = kept = 0
    best_q = 0.0
    a = a_lo
    complete = True
    while a < a_hi:
        if deadline is not None and time.time() > deadline:
            complete = False
            break
        start = int(np.searchsorted(smooth, 2 * a, side="left"))
        if start < len(smooth):
            c = smooth[start:]
            b = c - a
            coprime = np.gcd(c, a) == 1
            b, c = b[coprime], c[coprime]
            if len(c):
                rb, rc = rad[b], rad[c]
                lograd = math.log(int(rad[a])) + np.log(rb) + np.log(rc)
                q = np.log(c) / lograd
                tested += int(len(c))
                qmax = float(q.max())
                if qmax > best_q:
                    best_q = qmax
                for j in np.nonzero(q >= min_quality)[0]:
                    bb, cc = int(b[j]), int(c[j])
                    rec = {"a": a, "b": bb, "c": cc,
                           "rad": int(rad[a]) * int(rb[j]) * int(rc[j]),
                           "q": float(q[j])}
                    _heap_push(heap, top_n, counter, rec)
                    kept += 1
        a += 1
    return {"tested": tested, "kept": kept, "best_q": best_q,
            "candidates": _heap_sorted(heap), "next": a, "complete": complete}


def scan_legs_smooth(rad: np.ndarray, layout: dict, pair_lo: int, pair_hi: int,
                     min_quality: float = 1.0, top_n: int = 100,
                     deadline: Optional[float] = None) -> dict:
    """Scan pairs of smooth legs from the pair index range [pair_lo, pair_hi)."""
    smooth = layout["smooth"]
    pair_lo = max(0, int(pair_lo))
    pair_hi = min(int(pair_hi), int(layout["total"]))
    heap: list = []
    counter = itertools.count()
    tested = kept = 0
    best_q = 0.0
    nxt = pair_lo
    complete = True
    for i, j0, j1, block_lo, block_hi in pair_slice_blocks(layout, pair_lo, pair_hi):
        if deadline is not None and time.time() > deadline:
            nxt, complete = block_lo, False
            break
        a = int(smooth[i])
        b = smooth[j0:j1]
        coprime = np.gcd(b, a) == 1
        b = b[coprime]
        if len(b):
            c = a + b
            rbb, rc = rad[b], rad[c]
            lograd = math.log(int(rad[a])) + np.log(rbb) + np.log(rc)
            q = np.log(c) / lograd
            tested += int(len(c))
            qmax = float(q.max())
            if qmax > best_q:
                best_q = qmax
            for j in np.nonzero(q >= min_quality)[0]:
                bb, cc = int(b[j]), int(c[j])
                rec = {"a": a, "b": bb, "c": cc,
                       "rad": int(rad[a]) * int(rbb[j]) * int(rc[j]),
                       "q": float(q[j])}
                _heap_push(heap, top_n, counter, rec)
                kept += 1
        nxt = block_hi
    return {"tested": tested, "kept": kept, "best_q": best_q,
            "candidates": _heap_sorted(heap), "next": nxt, "complete": complete}
