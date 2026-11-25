"""The blind problem interface.

A blind problem is deliberately minimal::

    {
      "name": "Problem_001",
      "domain": "number_theory",
      "formal_statement": "...",
      "definitions": [...],
      "assumptions": [...],
      "target": "prove"
    }

There is no field in which a solution, a lemma, a residue class, a formula
template or a proof strategy could be supplied. ``from_dict`` rejects any
additional key, so the discovery engine cannot receive target-specific help
even by accident.

The statement language is a small subset of first-order arithmetic:

    forall n >= 0: <body>
    <expr> = <expr> | <expr> <= <expr> | <expr> < <expr>
    <int> | <expr>                        (divisibility)
    pred(args)                            (a trusted named predicate)
    (<body> and <body>) | (<body> or <body>) | not (<body>)

Expressions are ordinary closed-form arithmetic plus ``Sum[i=a..b](body)``.
For ``target: "discover"`` the statement names an object to investigate
(``study <expr>``) and no conclusion is supplied at all.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from ..kernel.expressions import Const, Expr, Sequence, Sum, Var, parse as parse_term
from ..kernel.propositions import (
    And, Divides, Eq, ForAll, Implies, Le, Lt, Not, Or, Pred, Prop, PREDICATES,
)

ALLOWED_KEYS = {"name", "domain", "formal_statement", "definitions", "assumptions", "target"}
LEAKY_KEY_WORDS = ("solut", "answer", "lemma", "hint", "residue", "strategy", "withheld",
                   "known_status", "special", "proof_of", "template")


class BlindProblemError(ValueError):
    pass


# ---------------------------------------------------------------- expressions

def _sum_span(text: str):
    """Return (start, end, index, lo, hi, body) for the first Sum[...](...) span."""
    start = text.find("Sum[")
    if start < 0:
        return None
    i = start + 4
    depth = 1
    while i < len(text) and depth:
        if text[i] == "[":
            depth += 1
        elif text[i] == "]":
            depth -= 1
        i += 1
    if depth:
        return None
    header = text[start + 4:i - 1]
    if ".." not in header:
        return None
    head, tail = header.split("..", 1)
    if "=" not in head:
        return None
    index, lo = head.split("=", 1)
    index, lo, hi = index.strip(), lo.strip(), tail.strip()
    j = i
    while j < len(text) and text[j].isspace():
        j += 1
    if j >= len(text) or text[j] != "(":
        return None
    depth, k = 1, j + 1
    while k < len(text) and depth:
        if text[k] == "(":
            depth += 1
        elif text[k] == ")":
            depth -= 1
        k += 1
    if depth:
        return None
    return start, k, index, lo, hi, text[j + 1:k - 1]


def parse_math(text: str) -> Expr:
    """Parse a closed-form term, including ``Sum[i=a..b](body)`` notation."""
    work = text.strip()
    placeholders: Dict[str, Expr] = {}
    counter = 0
    while True:
        span = _sum_span(work)
        if span is None:
            break
        start, end, index, lo, hi, body = span
        obj = Sum(Var(index), parse_math(lo), parse_math(hi), parse_math(body))
        ph = f"__axiom_obj_{counter}__"
        counter += 1
        placeholders[ph] = obj
        work = work[:start] + ph + work[end:]
    expr = parse_term(work)
    for ph, obj in placeholders.items():
        expr = expr.subst({ph: obj})
    return expr


# ---------------------------------------------------------------- propositions

def _strip_outer(text: str) -> str:
    text = text.strip()
    while text.startswith("(") and text.endswith(")"):
        depth = 0
        for i, ch in enumerate(text):
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth == 0 and i != len(text) - 1:
                return text
        text = text[1:-1].strip()
    return text


def _top_split(text: str, token: str) -> Optional[List[str]]:
    """Split on a token occurring outside brackets/parentheses."""
    parts, buf, depth = [], [], 0
    i = 0
    while i < len(text):
        if text[i] in "([{":
            depth += 1
        elif text[i] in ")]}":
            depth -= 1
        if depth == 0 and text.startswith(token, i):
            parts.append("".join(buf))
            buf = []
            i += len(token)
            continue
        buf.append(text[i])
        i += 1
    parts.append("".join(buf))
    return parts if len(parts) > 1 else None


def parse_prop(text: str) -> Prop:
    text = _strip_outer(text)

    parts = _top_split(text, " and ")
    if parts:
        return And(tuple(parse_prop(p) for p in parts))
    parts = _top_split(text, " or ")
    if parts:
        return Or(tuple(parse_prop(p) for p in parts))

    m = re.match(r"^not\s*\((.*)\)$", text, re.S)
    if m:
        return Not(parse_prop(m.group(1)))

    m = re.match(r"^forall\s+(\w+)(?:\s*>=\s*(-?\d+))?\s*:\s*(.*)$", text, re.S)
    if m:
        lower = int(m.group(2)) if m.group(2) is not None else 0
        return ForAll(Var(m.group(1)), parse_prop(m.group(3)), lower)

    m = re.match(r"^exists\s+(\w+)(?:\s*>=\s*(-?\d+))?\s*:\s*(.*)$", text, re.S)
    if m:
        lower = int(m.group(2)) if m.group(2) is not None else 0
        from ..kernel.propositions import Exists
        return Exists(Var(m.group(1)), parse_prop(m.group(3)), lower)

    m = re.match(r"^(\w+)\s*->\s*(.*)$", text, re.S)
    if m:
        return Implies(parse_prop(m.group(1)), parse_prop(m.group(2)))

    parts = _top_split(text, " | ")
    if parts and len(parts) == 2:
        return Divides(parse_math(parts[0]), parse_math(parts[1]))

    for token, cls in ((" <= ", Le), (" < ", Lt), (" = ", Eq)):
        parts = _top_split(text, token)
        if parts and len(parts) == 2:
            return cls(parse_math(parts[0]), parse_math(parts[1]))

    m = re.match(r"^(\w+)\s*\((.*)\)$", text, re.S)
    if m and m.group(1) in PREDICATES:
        args = _top_split(m.group(2), ",") or [m.group(2)]
        return Pred(m.group(1), tuple(parse_math(a) for a in args))

    raise BlindProblemError(f"cannot parse statement {text!r}")


def parse_definition(item) -> Tuple[str, object]:
    """Return (kind, object) for a given definition.

    Accepted forms::

        "a(0) = 0; a(n+1) = a(n) + 2*n + 1"
        {"kind": "sequence", "name": "a", "init": 0, "rule": "x + 2*n + 1"}
        {"kind": "term", "expr": "n^2 + n"}
        "<expression>"                        (an object to study)
    """
    if isinstance(item, dict):
        kind = item.get("kind", "term")
        if kind == "sequence":
            name = item.get("name", "a")
            init = int(item.get("init", 0))
            rule_text = str(item["rule"])
            rule = parse_math(rule_text.replace(f"{name}(n)", "x"))
            return "sequence", Sequence(name, init, rule)
        if kind == "sum":
            body = item.get("body")
            lo = item.get("lower", 1)
            hi = item.get("upper", "n")
            return "term", Sum(Var("i"), parse_math(str(lo)), parse_math(str(hi)),
                               parse_math(str(body)))
        return "term", parse_math(str(item.get("expr", item.get("body", ""))))

    text = str(item).strip()
    m = re.match(r"^(?:sequence\s+)?(\w+)\(0\)\s*=\s*(-?\d+)\s*[,;]\s*\1\(n\+1\)\s*=\s*(.+)$",
                 text, re.S)
    if m:
        name, init, rhs = m.group(1), int(m.group(2)), m.group(3)
        rule = parse_math(rhs.replace(f"{name}(n)", "x"))
        return "sequence", Sequence(name, init, rule)
    return "term", parse_math(text)


# ---------------------------------------------------------------- problem

@dataclass
class BlindProblem:
    name: str
    domain: str
    formal_statement: str
    definitions: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    target: str = "prove"

    # Derived from the specification; never supplied by the caller.
    goal: Optional[Prop] = None
    study: List[Expr] = field(default_factory=list)
    given_sequences: List[Sequence] = field(default_factory=list)
    given_terms: List[Expr] = field(default_factory=list)
    given_assumptions: List[Prop] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "BlindProblem":
        if not isinstance(data, dict):
            raise BlindProblemError("a blind problem must be a JSON object")
        unknown = set(data) - ALLOWED_KEYS
        if unknown:
            leaky = [k for k in unknown if any(w in k.lower() for w in LEAKY_KEY_WORDS)]
            msg = f"blind interface rejects extra keys: {sorted(unknown)}"
            if leaky:
                msg += f" (these would leak target information: {leaky})"
            raise BlindProblemError(msg)
        for key in ("name", "domain", "formal_statement", "target"):
            if key not in data:
                raise BlindProblemError(f"missing required key: {key}")
        target = str(data["target"])
        if target not in ("prove", "discover"):
            raise BlindProblemError("target must be 'prove' or 'discover'")

        p = cls(name=str(data["name"]), domain=str(data["domain"]),
                formal_statement=str(data["formal_statement"]),
                definitions=list(data.get("definitions", [])),
                assumptions=list(data.get("assumptions", [])), target=target)
        p.given_assumptions = [parse_prop(str(a)) for a in p.assumptions]

        for item in p.definitions:
            kind, obj = parse_definition(item)
            if kind == "sequence":
                p.given_sequences.append(obj)
            else:
                p.given_terms.append(obj)

        statement = p.formal_statement.strip()
        if target == "prove":
            p.goal = parse_prop(statement)
        else:
            if statement and not statement.lower().startswith("study "):
                raise BlindProblemError(
                    "a discover problem must name an object: 'study <expression>'")
            obj_text = statement[6:].strip() if statement.lower().startswith("study ") else ""
            if obj_text:
                p.study.append(parse_math(obj_text))
        return p

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "domain": self.domain,
            "formal_statement": self.formal_statement,
            "definitions": self.definitions,
            "assumptions": self.assumptions,
            "target": self.target,
        }

    def __str__(self):
        return f"{self.name} [{self.domain}, {self.target}]: {self.formal_statement}"
