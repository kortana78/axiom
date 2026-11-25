"""Mathematical types used by the expression language.

The type system is deliberately small: natural numbers, integers,
rationals and propositions. Every expression has a type, and badly
typed expressions are rejected before any proof search starts.
"""
from enum import Enum


class MathTypeError(Exception):
    """Raised when an expression or proposition is badly typed."""


class MType(Enum):
    NAT = "Nat"
    INT = "Int"
    RAT = "Rat"
    PROP = "Prop"

    def __str__(self):
        return self.value


_NUMERIC_ORDER = {MType.NAT: 0, MType.INT: 1, MType.RAT: 2}


def is_numeric(t: MType) -> bool:
    return t in _NUMERIC_ORDER


def is_integral(t: MType) -> bool:
    return t in (MType.NAT, MType.INT)


def join(a: MType, b: MType) -> MType:
    """Smallest numeric type containing both a and b."""
    if not (is_numeric(a) and is_numeric(b)):
        raise MathTypeError(f"cannot combine types {a} and {b}")
    return a if _NUMERIC_ORDER[a] >= _NUMERIC_ORDER[b] else b
