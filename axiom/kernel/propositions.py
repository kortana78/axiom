"""Propositions: equalities, inequalities, divisibility, connectives,
quantifiers and named predicates.

Quantifiers range over integers >= lower (natural-number style), which
covers most elementary number theory statements.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Dict, Tuple

from .expressions import Expr, Var, Const, typecheck, require_integral
from .types import MathTypeError

# Named predicates with trusted, exact Python evaluators (for example
# is_prime). They are part of the trusted base and listed in README.
PREDICATES: Dict[str, Callable[..., bool]] = {}


def predicate(name):
    def deco(fn):
        PREDICATES[name] = fn
        return fn
    return deco


class Prop:
    def evaluate(self, env: Dict[str, Fraction]) -> bool:
        raise NotImplementedError

    def subst(self, m: Dict[str, Expr]) -> "Prop":
        raise NotImplementedError

    def free_vars(self) -> set:
        raise NotImplementedError

    def typecheck(self):
        pass

    def size(self) -> int:
        return 1

    def key(self) -> str:
        return str(self)


@dataclass(frozen=True)
class Eq(Prop):
    lhs: Expr
    rhs: Expr
    def evaluate(self, env): return self.lhs.evaluate(env) == self.rhs.evaluate(env)
    def subst(self, m): return Eq(self.lhs.subst(m), self.rhs.subst(m))
    def free_vars(self): return self.lhs.free_vars() | self.rhs.free_vars()
    def typecheck(self): typecheck(self.lhs); typecheck(self.rhs)
    def size(self): return 1 + self.lhs.size() + self.rhs.size()
    def __str__(self): return f"{self.lhs} = {self.rhs}"


@dataclass(frozen=True)
class Le(Prop):
    lhs: Expr
    rhs: Expr
    def evaluate(self, env): return self.lhs.evaluate(env) <= self.rhs.evaluate(env)
    def subst(self, m): return Le(self.lhs.subst(m), self.rhs.subst(m))
    def free_vars(self): return self.lhs.free_vars() | self.rhs.free_vars()
    def typecheck(self): typecheck(self.lhs); typecheck(self.rhs)
    def size(self): return 1 + self.lhs.size() + self.rhs.size()
    def __str__(self): return f"{self.lhs} <= {self.rhs}"


@dataclass(frozen=True)
class Lt(Prop):
    lhs: Expr
    rhs: Expr
    def evaluate(self, env): return self.lhs.evaluate(env) < self.rhs.evaluate(env)
    def subst(self, m): return Lt(self.lhs.subst(m), self.rhs.subst(m))
    def free_vars(self): return self.lhs.free_vars() | self.rhs.free_vars()
    def typecheck(self): typecheck(self.lhs); typecheck(self.rhs)
    def size(self): return 1 + self.lhs.size() + self.rhs.size()
    def __str__(self): return f"{self.lhs} < {self.rhs}"


@dataclass(frozen=True)
class Divides(Prop):
    d: Expr
    e: Expr
    def evaluate(self, env):
        d, e = self.d.evaluate(env), self.e.evaluate(env)
        if d.denominator != 1 or e.denominator != 1:
            return False
        d, e = int(d), int(e)
        return e == 0 if d == 0 else e % d == 0
    def subst(self, m): return Divides(self.d.subst(m), self.e.subst(m))
    def free_vars(self): return self.d.free_vars() | self.e.free_vars()
    def typecheck(self): require_integral(self.d); require_integral(self.e)
    def size(self): return 1 + self.d.size() + self.e.size()
    def __str__(self): return f"{self.d} | {self.e}"


@dataclass(frozen=True)
class Not(Prop):
    p: Prop
    def evaluate(self, env): return not self.p.evaluate(env)
    def subst(self, m): return Not(self.p.subst(m))
    def free_vars(self): return self.p.free_vars()
    def typecheck(self): self.p.typecheck()
    def size(self): return 1 + self.p.size()
    def __str__(self): return f"not ({self.p})"


@dataclass(frozen=True)
class And(Prop):
    parts: Tuple[Prop, ...]
    def evaluate(self, env): return all(p.evaluate(env) for p in self.parts)
    def subst(self, m): return And(tuple(p.subst(m) for p in self.parts))
    def free_vars(self):
        out = set()
        for p in self.parts: out |= p.free_vars()
        return out
    def typecheck(self):
        for p in self.parts: p.typecheck()
    def size(self): return 1 + sum(p.size() for p in self.parts)
    def __str__(self): return "(" + " and ".join(str(p) for p in self.parts) + ")"


@dataclass(frozen=True)
class Or(Prop):
    parts: Tuple[Prop, ...]
    def evaluate(self, env): return any(p.evaluate(env) for p in self.parts)
    def subst(self, m): return Or(tuple(p.subst(m) for p in self.parts))
    def free_vars(self):
        out = set()
        for p in self.parts: out |= p.free_vars()
        return out
    def typecheck(self):
        for p in self.parts: p.typecheck()
    def size(self): return 1 + sum(p.size() for p in self.parts)
    def __str__(self): return "(" + " or ".join(str(p) for p in self.parts) + ")"


@dataclass(frozen=True)
class Implies(Prop):
    a: Prop
    b: Prop
    def evaluate(self, env): return (not self.a.evaluate(env)) or self.b.evaluate(env)
    def subst(self, m): return Implies(self.a.subst(m), self.b.subst(m))
    def free_vars(self): return self.a.free_vars() | self.b.free_vars()
    def typecheck(self): self.a.typecheck(); self.b.typecheck()
    def size(self): return 1 + self.a.size() + self.b.size()
    def __str__(self): return f"({self.a} -> {self.b})"


@dataclass(frozen=True)
class ForAll(Prop):
    """for all integers var >= lower: body"""
    var: Var
    body: Prop
    lower: int = 0
    def evaluate(self, env):
        raise ValueError("an unbounded ForAll cannot be evaluated; use the counterexample engine")
    def instance(self, value) -> Prop:
        return self.body.subst({self.var.name: Const(value)})
    def subst(self, m):
        m2 = {k: v for k, v in m.items() if k != self.var.name}
        return ForAll(self.var, self.body.subst(m2), self.lower)
    def free_vars(self): return self.body.free_vars() - {self.var.name}
    def typecheck(self): self.body.typecheck()
    def size(self): return 1 + self.body.size()
    def __str__(self): return f"forall {self.var} >= {self.lower}: {self.body}"


@dataclass(frozen=True)
class Exists(Prop):
    """there is an integer var >= lower with body (search bound used only for evaluation)"""
    var: Var
    body: Prop
    lower: int = 0
    search_bound: int = 10_000
    def evaluate(self, env):
        for v in range(self.lower, self.search_bound + 1):
            e2 = dict(env); e2[self.var.name] = Fraction(v)
            if self.body.evaluate(e2):
                return True
        raise ValueError("Exists not decided within search bound")
    def subst(self, m):
        m2 = {k: v for k, v in m.items() if k != self.var.name}
        return Exists(self.var, self.body.subst(m2), self.lower, self.search_bound)
    def free_vars(self): return self.body.free_vars() - {self.var.name}
    def typecheck(self): self.body.typecheck()
    def size(self): return 1 + self.body.size()
    def __str__(self): return f"exists {self.var} >= {self.lower}: {self.body}"


@dataclass(frozen=True)
class BoundedForAll(Prop):
    """for all integers var with lo <= var <= hi: body (decidable)"""
    var: Var
    lo: int
    hi: int
    body: Prop
    def evaluate(self, env):
        for v in range(self.lo, self.hi + 1):
            e2 = dict(env); e2[self.var.name] = Fraction(v)
            if not self.body.evaluate(e2):
                return False
        return True
    def subst(self, m):
        m2 = {k: v for k, v in m.items() if k != self.var.name}
        return BoundedForAll(self.var, self.lo, self.hi, self.body.subst(m2))
    def free_vars(self): return self.body.free_vars() - {self.var.name}
    def typecheck(self): self.body.typecheck()
    def size(self): return 1 + self.body.size()
    def __str__(self): return f"forall {self.var} in [{self.lo}, {self.hi}]: {self.body}"


@dataclass(frozen=True)
class Pred(Prop):
    """Named predicate with a trusted exact evaluator, e.g. is_prime(n)."""
    name: str
    args: Tuple[Expr, ...]
    def evaluate(self, env):
        fn = PREDICATES[self.name]
        vals = []
        for a in self.args:
            v = a.evaluate(env)
            if v.denominator != 1:
                return False
            vals.append(int(v))
        return bool(fn(*vals))
    def subst(self, m): return Pred(self.name, tuple(a.subst(m) for a in self.args))
    def free_vars(self):
        out = set()
        for a in self.args: out |= a.free_vars()
        return out
    def typecheck(self):
        if self.name not in PREDICATES:
            raise MathTypeError(f"unknown predicate {self.name}")
        for a in self.args: require_integral(a)
    def size(self): return 1 + sum(a.size() for a in self.args)
    def __str__(self): return f"{self.name}(" + ", ".join(str(a) for a in self.args) + ")"


def strip_forall(p: Prop):
    """Return ([(var, lower), ...], body)."""
    binders = []
    while isinstance(p, ForAll):
        binders.append((p.var, p.lower))
        p = p.body
    return binders, p


def wrap_forall(binders, body: Prop) -> Prop:
    for var, lower in reversed(binders):
        body = ForAll(var, body, lower)
    return body
