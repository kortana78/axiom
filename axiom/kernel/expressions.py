"""Typed mathematical expressions (terms).

Expressions are immutable trees. They can be evaluated exactly (with
Fractions), converted to SymPy for algebra, type checked, substituted
into and measured. Mathematical statements are never stored as loose
strings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, Tuple

import sympy as sp

from .types import MType, MathTypeError, join, is_integral


def lift(x) -> "Expr":
    if isinstance(x, Expr):
        return x
    if isinstance(x, (int, Fraction)):
        return Const(x)
    raise TypeError(f"cannot lift {x!r} to an expression")


_SYMBOLS: Dict[str, sp.Symbol] = {}


def sym(name: str) -> sp.Symbol:
    if name not in _SYMBOLS:
        _SYMBOLS[name] = sp.Symbol(name, integer=True)
    return _SYMBOLS[name]


class Expr:
    """Base class for terms."""

    # operator sugar (never overload ==, structural equality is used)
    def __add__(self, o): return Add(self, lift(o))
    def __radd__(self, o): return Add(lift(o), self)
    def __sub__(self, o): return Sub(self, lift(o))
    def __rsub__(self, o): return Sub(lift(o), self)
    def __mul__(self, o): return Mul(self, lift(o))
    def __rmul__(self, o): return Mul(lift(o), self)
    def __truediv__(self, o): return Div(self, lift(o))
    def __rtruediv__(self, o): return Div(lift(o), self)
    def __pow__(self, o): return Pow(self, lift(o))
    def __neg__(self): return Mul(Const(-1), self)

    # interface
    def children(self) -> Tuple["Expr", ...]:
        return ()

    def to_sympy(self):
        raise NotImplementedError

    def evaluate(self, env: Dict[str, Fraction]) -> Fraction:
        raise NotImplementedError

    def type_of(self) -> MType:
        raise NotImplementedError

    def subst(self, mapping: Dict[str, "Expr"]) -> "Expr":
        raise NotImplementedError

    def free_vars(self) -> set:
        out = set()
        for c in self.children():
            out |= c.free_vars()
        return out

    def size(self) -> int:
        return 1 + sum(c.size() for c in self.children())

    def is_closed_form(self) -> bool:
        """True if the term uses only + - * / ^ on variables and constants."""
        return all(c.is_closed_form() for c in self.children())


@dataclass(frozen=True)
class Var(Expr):
    name: str
    typ: MType = MType.NAT

    def to_sympy(self): return sym(self.name)
    def evaluate(self, env):
        if self.name not in env:
            raise KeyError(f"unbound variable {self.name}")
        return Fraction(env[self.name])
    def type_of(self): return self.typ
    def subst(self, m): return m.get(self.name, self)
    def free_vars(self): return {self.name}
    def __str__(self): return self.name


@dataclass(frozen=True)
class Const(Expr):
    value: Fraction

    def __post_init__(self):
        object.__setattr__(self, "value", Fraction(self.value))

    def to_sympy(self): return sp.Rational(self.value.numerator, self.value.denominator)
    def evaluate(self, env): return self.value
    def type_of(self):
        if self.value.denominator != 1:
            return MType.RAT
        return MType.NAT if self.value >= 0 else MType.INT
    def subst(self, m): return self
    def __str__(self):
        v = self.value
        return str(v.numerator) if v.denominator == 1 else f"({v.numerator}/{v.denominator})"


@dataclass(frozen=True)
class Add(Expr):
    a: Expr
    b: Expr
    def children(self): return (self.a, self.b)
    def to_sympy(self): return self.a.to_sympy() + self.b.to_sympy()
    def evaluate(self, env): return self.a.evaluate(env) + self.b.evaluate(env)
    def type_of(self): return join(self.a.type_of(), self.b.type_of())
    def subst(self, m): return Add(self.a.subst(m), self.b.subst(m))
    def __str__(self): return f"({self.a} + {self.b})"


@dataclass(frozen=True)
class Sub(Expr):
    a: Expr
    b: Expr
    def children(self): return (self.a, self.b)
    def to_sympy(self): return self.a.to_sympy() - self.b.to_sympy()
    def evaluate(self, env): return self.a.evaluate(env) - self.b.evaluate(env)
    def type_of(self): return join(join(self.a.type_of(), self.b.type_of()), MType.INT)
    def subst(self, m): return Sub(self.a.subst(m), self.b.subst(m))
    def __str__(self): return f"({self.a} - {self.b})"


@dataclass(frozen=True)
class Mul(Expr):
    a: Expr
    b: Expr
    def children(self): return (self.a, self.b)
    def to_sympy(self): return self.a.to_sympy() * self.b.to_sympy()
    def evaluate(self, env): return self.a.evaluate(env) * self.b.evaluate(env)
    def type_of(self): return join(self.a.type_of(), self.b.type_of())
    def subst(self, m): return Mul(self.a.subst(m), self.b.subst(m))
    def __str__(self): return f"({self.a} * {self.b})"


@dataclass(frozen=True)
class Div(Expr):
    a: Expr
    b: Expr
    def children(self): return (self.a, self.b)
    def to_sympy(self): return self.a.to_sympy() / self.b.to_sympy()
    def evaluate(self, env):
        d = self.b.evaluate(env)
        if d == 0:
            raise ZeroDivisionError("division by zero")
        return self.a.evaluate(env) / d
    def type_of(self):
        join(self.a.type_of(), self.b.type_of())
        return MType.RAT
    def subst(self, m): return Div(self.a.subst(m), self.b.subst(m))
    def __str__(self): return f"({self.a} / {self.b})"


@dataclass(frozen=True)
class Pow(Expr):
    base: Expr
    exp: Expr
    def children(self): return (self.base, self.exp)
    def to_sympy(self): return self.base.to_sympy() ** self.exp.to_sympy()
    def evaluate(self, env):
        e = self.exp.evaluate(env)
        if e.denominator != 1 or e < 0:
            raise ValueError("exponent must be a natural number")
        b = self.base.evaluate(env)
        if e > 5000 and abs(b) > 1:
            raise OverflowError("power too large to evaluate exactly")
        return b ** int(e)
    def type_of(self):
        if self.exp.type_of() != MType.NAT:
            raise MathTypeError(f"exponent of {self} must be Nat")
        return self.base.type_of()
    def subst(self, m): return Pow(self.base.subst(m), self.exp.subst(m))
    def is_closed_form(self):
        # exponent must be a constant for polynomial reasoning; a^n is
        # still a valid term but handled by dedicated rules
        return self.base.is_closed_form() and isinstance(self.exp, Const)
    def __str__(self): return f"{self.base}^{self.exp}"


@dataclass(frozen=True)
class Sum(Expr):
    """sum_{index = lo}^{hi} body"""
    index: Var
    lo: Expr
    hi: Expr
    body: Expr
    def children(self): return (self.lo, self.hi, self.body)
    def to_sympy(self):
        return sp.Sum(self.body.to_sympy(), (self.index.to_sympy(), self.lo.to_sympy(), self.hi.to_sympy()))
    def evaluate(self, env):
        lo, hi = self.lo.evaluate(env), self.hi.evaluate(env)
        total = Fraction(0)
        i = int(lo)
        while i <= hi:
            e2 = dict(env); e2[self.index.name] = Fraction(i)
            total += self.body.evaluate(e2)
            i += 1
        return total
    def type_of(self):
        return self.body.type_of()
    def subst(self, m):
        m2 = {k: v for k, v in m.items() if k != self.index.name}
        return Sum(self.index, self.lo.subst(m2), self.hi.subst(m2), self.body.subst(m2))
    def free_vars(self):
        return (self.lo.free_vars() | self.hi.free_vars() | (self.body.free_vars() - {self.index.name}))
    def is_closed_form(self): return False
    def __str__(self): return f"Sum[{self.index}={self.lo}..{self.hi}]({self.body})"


@dataclass(frozen=True)
class Sequence:
    """A recursively defined sequence a_0 = init, a_{n+1} = rule(x=a_n, n).

    The rule is an expression in the placeholder variables x and n.
    """
    name: str
    init: int
    rule: Expr

    def values(self, upto: int):
        return list(_seq_values(self, upto))

    def values_mod(self, m: int, upto: int):
        """Residues mod m, valid when the rule has integer coefficients."""
        x = self.init % m
        out = [x]
        for n in range(upto):
            v = self.rule.evaluate({"x": Fraction(x), "n": Fraction(n)})
            x = int(v) % m
            out.append(x)
        return out

    def __str__(self):
        return f"{self.name}: {self.name}(0)={self.init}, {self.name}(n+1) = {self.rule} [x={self.name}(n)]"


_SEQ_CACHE: Dict[tuple, list] = {}
MAX_BITS = 100_000


def _seq_values(seq: "Sequence", upto: int):
    key = (seq.name, seq.init, str(seq.rule))
    vals = _SEQ_CACHE.setdefault(key, [Fraction(seq.init)])
    while len(vals) <= upto:
        v = seq.rule.evaluate({"x": vals[-1], "n": Fraction(len(vals) - 1)})
        if v.numerator.bit_length() > MAX_BITS:
            raise OverflowError("sequence value too large to evaluate exactly")
        vals.append(v)
    return vals[: upto + 1]


@dataclass(frozen=True)
class SeqTerm(Expr):
    seq: Sequence
    index: Expr
    def children(self): return (self.index,)
    def to_sympy(self): return sp.Function(self.seq.name)(self.index.to_sympy())
    def evaluate(self, env):
        i = self.index.evaluate(env)
        if i.denominator != 1 or i < 0:
            raise ValueError("sequence index must be a natural number")
        return self.seq.values(int(i))[int(i)]
    def type_of(self): return MType.INT
    def subst(self, m): return SeqTerm(self.seq, self.index.subst(m))
    def is_closed_form(self): return False
    def __str__(self): return f"{self.seq.name}({self.index})"


# ---------------------------------------------------------------- helpers

def from_sympy(e, types: Dict[str, MType] | None = None) -> Expr:
    """Convert a SymPy expression back to an Axiom term."""
    types = types or {}
    e = sp.sympify(e)
    if e.is_Symbol:
        return Var(e.name, types.get(e.name, MType.NAT))
    if e.is_Integer:
        return Const(int(e))
    if e.is_Rational:
        return Const(Fraction(int(e.p), int(e.q)))
    if e.is_Add:
        args = [from_sympy(a, types) for a in e.as_ordered_terms()]
        out = args[0]
        for a in args[1:]:
            out = Add(out, a)
        return out
    if e.is_Mul:
        args = [from_sympy(a, types) for a in e.args]
        out = args[0]
        for a in args[1:]:
            out = Mul(out, a)
        return out
    if e.is_Pow:
        b, x = e.args
        if x.is_Integer and int(x) < 0:
            return Div(Const(1), Pow(from_sympy(b, types), Const(-int(x))))
        return Pow(from_sympy(b, types), from_sympy(x, types))
    raise ValueError(f"cannot convert {e} to an Axiom expression")


def parse(text: str, types: Dict[str, MType] | None = None) -> Expr:
    """Parse a closed-form term, for example parse('n^3 - n')."""
    loc = {}
    for name in "abcdeijkmnpqrstuvwxyz":
        loc[name] = sym(name)
    e = sp.sympify(text.replace("^", "**"), locals=loc)
    return from_sympy(e, types)


def simplify(e: Expr, types=None) -> Expr:
    if not e.is_closed_form():
        return e
    return from_sympy(sp.expand(e.to_sympy()), types)


def typecheck(e: Expr) -> MType:
    try:
        return e.type_of()
    except MathTypeError:
        raise
    except Exception as exc:  # pragma: no cover
        raise MathTypeError(str(exc))


def require_integral(e: Expr):
    t = typecheck(e)
    if not is_integral(t):
        raise MathTypeError(f"{e} has type {t}, expected an integer type")
