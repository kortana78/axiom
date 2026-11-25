"""Trusted exact evaluators for named predicates.

These are part of the trusted base: keep them short and obviously correct.
"""
from fractions import Fraction
import math

from .propositions import predicate


@predicate("is_prime")
def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = math.isqrt(n)
    f = 3
    while f <= r:
        if n % f == 0:
            return False
        f += 2
    return True


@predicate("sigma")
def sigma_eq(n: int, value: int) -> bool:
    """sigma(n) == value, sum of divisors."""
    return divisor_sum(n) == value


@predicate("is_perfect")
def is_perfect(n: int) -> bool:
    """A perfect number equals the sum of its proper divisors: sigma(n) = 2n."""
    return n >= 1 and divisor_sum(n) == 2 * n


def divisor_sum(n: int) -> int:
    if n <= 0:
        return 0
    total, d = 0, 1
    while d * d <= n:
        if n % d == 0:
            total += d
            if d * d != n:
                total += n // d
        d += 1
    return total


@predicate("not_quasiperfect")
def not_quasiperfect(n: int) -> bool:
    return n < 1 or divisor_sum(n) != 2 * n + 1


@predicate("prime_between_squares")
def prime_between_squares(n: int) -> bool:
    """There is a prime p with n^2 < p < (n+1)^2."""
    for p in range(n * n + 1, (n + 1) * (n + 1)):
        if is_prime(p):
            return True
    return False


@predicate("collatz_descends")
def collatz_descends(n: int) -> bool:
    """Trajectory of n eventually goes below n (true by convention for n <= 1)."""
    if n <= 1:
        return True
    m, steps = n, 0
    while m >= n:
        m = m // 2 if m % 2 == 0 else 3 * m + 1
        steps += 1
        if steps > 10_000_000:
            raise RuntimeError("step cap reached")
    return True


@predicate("collatz_reaches_one")
def collatz_reaches_one(n: int) -> bool:
    if n < 1:
        return True
    steps = 0
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        steps += 1
        if steps > 10_000_000:
            raise RuntimeError("step cap reached")
    return True


def es_representation(n: int):
    """Find x <= y <= z with 4/n = 1/x + 1/y + 1/z, or None."""
    target = Fraction(4, n)
    for x in range(n // 4 + 1, 3 * n // 4 + 2):
        r1 = target - Fraction(1, x)
        if r1 <= 0:
            continue
        ylo = max(x, math.ceil(1 / r1))
        yhi = math.floor(2 / r1)
        for y in range(ylo, yhi + 1):
            r2 = r1 - Fraction(1, y)
            if r2 > 0 and r2.numerator == 1:
                return x, y, r2.denominator
    return None


@predicate("es_rep")
def es_rep(n: int) -> bool:
    """4/n is a sum of three unit fractions (Erdos-Straus), n >= 2."""
    return n < 2 or es_representation(n) is not None


# ---- predicates used by the pattern miner (characterisation targets)

@predicate("is_square")
def is_square(n: int) -> bool:
    return n >= 0 and math.isqrt(n) ** 2 == n


@predicate("square_or_twice_square")
def square_or_twice_square(n: int) -> bool:
    return is_square(n) or (n % 2 == 0 and is_square(n // 2))


@predicate("is_power_of_two")
def is_power_of_two(n: int) -> bool:
    return n >= 1 and n & (n - 1) == 0


@predicate("sigma_odd")
def sigma_odd(n: int) -> bool:
    return divisor_sum(n) % 2 == 1


@predicate("is_odd")
def is_odd(n: int) -> bool:
    return n % 2 == 1
