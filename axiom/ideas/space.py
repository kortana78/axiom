"""The idea space: runnable variations of how AXIOM searches.

An Idea is plain data, so it can be enumerated, mutated, logged, shared
between machines, and written by hand (or by Claude) in swarm/ideas.json.

    order : the unknowns in search order; the LAST one is solved exactly
    atoms : building blocks for witness formulas (see ATOM_KINDS)
    mult  : coefficients c in (c * atom + offset) / divisor
    T, D  : offset and divisor ranges
"""
from __future__ import annotations

import itertools
import json
import random
from dataclasses import asdict, dataclass, field
from typing import Iterator, List

ATOM_KINDS = ["n", "n2", "n3", "v", "nv", "n2v", "vv", "nvv"]
BASE_ATOMS = ["n", "n2", "v", "nv", "vv"]          # the 0.3 grammar


@dataclass
class Idea:
    order: List[str]
    atoms: List[str]
    mult: List[int] = field(default_factory=lambda: [1])
    T: int = 40
    D: int = 24
    note: str = ""
    source: str = "generated"
    tie: bool = False   # later unknowns may use earlier offsets as divisors

    def key(self) -> str:
        return (f"order={''.join(self.order)}|atoms={','.join(sorted(self.atoms))}|"
                f"mult={','.join(map(str, self.mult))}|T={self.T}|D={self.D}" + ("|tie" if self.tie else ""))

    def family(self) -> str:
        """Coarse family used by the bandit (ignores sizes)."""
        return (f"order={''.join(self.order)}|atoms={','.join(sorted(self.atoms))}|mult={len(self.mult)}"
                + ("|tie" if self.tie else ""))

    def cost(self) -> int:
        return len(self.atoms) * len(self.mult) * self.T * self.D

    def to_dict(self):
        return asdict(self)

    @staticmethod
    def from_dict(d) -> "Idea":
        return Idea(order=list(d["order"]), atoms=list(d["atoms"]), mult=list(d.get("mult", [1])),
                    T=int(d.get("T", 40)), D=int(d.get("D", 24)), note=d.get("note", ""),
                    source=d.get("source", "hand"), tie=bool(d.get("tie", False)))


def enumerate_ideas(var_names: List[str], max_extra_atoms: int = 3) -> Iterator[Idea]:
    """All ideas, roughly smallest first: every variable order, then growing
    atom sets on top of the base grammar, then multipliers, then sizes."""
    extras = [a for a in ATOM_KINDS if a not in BASE_ATOMS]
    orders = list(itertools.permutations(var_names))
    sizes = [(40, 24), (80, 48), (160, 96)]
    mults = [[1], [1, 2], [1, 2, 3]]
    for size in sizes:
      for tie in (False, True):
        for mult in mults:
            for k in range(0, max_extra_atoms + 1):
                for add in itertools.combinations(extras, k):
                    for order in orders:
                        yield Idea(list(order), BASE_ATOMS + list(add), list(mult), size[0], size[1],
                                   note="enumerated", tie=tie)


def mutate(idea: Idea, var_names: List[str], rng: random.Random) -> Idea:
    """A nearby idea: swap the order, toggle an atom, change a multiplier or size."""
    d = idea.to_dict()
    choice = rng.randrange(5)
    if choice == 4:
        d["tie"] = not d.get("tie", False)
    if choice == 0 and len(var_names) > 1:
        o = list(d["order"])
        i, j = rng.sample(range(len(o)), 2)
        o[i], o[j] = o[j], o[i]
        d["order"] = o
    elif choice == 1:
        a = rng.choice(ATOM_KINDS)
        atoms = set(d["atoms"])
        atoms.symmetric_difference_update({a})
        d["atoms"] = sorted(atoms or {"n"})
    elif choice == 2:
        d["mult"] = sorted(set(d["mult"]) | {rng.choice([2, 3, 4, 6])})
    elif choice == 3:
        d["T"], d["D"] = int(d["T"] * 1.5), int(d["D"] * 1.5)
    d["note"] = "mutation of " + idea.key()
    d["source"] = "mutated"
    return Idea.from_dict(d)


def load_hand_ideas(path="swarm/ideas.json") -> List[Idea]:
    try:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return []
    out = []
    for d in data.get("ideas", []):
        d = dict(d)
        d.setdefault("source", "hand")
        out.append(Idea.from_dict(d))
    return out
