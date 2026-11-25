"""A witness engine configured by an Idea.

Search runs over the unknowns in the idea's order (the last is solved
exactly); the witnesses are then put back in the statement's order, so
the proof and the kernel check are unchanged.
"""
from __future__ import annotations

import sympy as sp

from ..blind.witness import Engine, Shape
from .space import Idea


class IdeaEngine(Engine):
    def __init__(self, shape: Shape, idea: Idea):
        names = [v for v, _ in shape.vars]
        if sorted(idea.order) != sorted(names):
            raise ValueError(f"idea order {idea.order} does not match unknowns {names}")
        lows = dict(shape.vars)
        self.original = shape
        perm_shape = Shape(shape.n, shape.lower, [(v, lows[v]) for v in idea.order], shape.body, shape.eq)
        super().__init__(perm_shape)
        self.idea = idea
        self.perm = [idea.order.index(v) for v in names]   # original position -> search position

    def _atoms(self, i, nv, wv):
        N, kinds = self.N, set(self.idea.atoms)
        out = []
        if "n" in kinds:
            out.append((N, nv))
        if "n2" in kinds:
            out.append((N * N, [a * a for a in nv]))
        if "n3" in kinds:
            out.append((N ** 3, [a ** 3 for a in nv]))
        for j in range(i):
            if "v" in kinds:
                out.append((self.V[j], wv[j]))
            if "nv" in kinds:
                out.append((N * self.V[j], [a * b for a, b in zip(nv, wv[j])]))
            if "n2v" in kinds:
                out.append((N * N * self.V[j], [a * a * b for a, b in zip(nv, wv[j])]))
        for j in range(i):
            for l in range(j, i):
                if "vv" in kinds:
                    out.append((self.V[j] * self.V[l], [a * b for a, b in zip(wv[j], wv[l])]))
                if "nvv" in kinds:
                    out.append((N * self.V[j] * self.V[l], [a * b * c for a, b, c in zip(nv, wv[j], wv[l])]))
        # coefficient multipliers
        res = []
        for c in self.idea.mult:
            for s, vals in out:
                res.append((c * s, [c * v for v in vals]))
        return res

    def _candidates(self, i, nv, wv, T, D, lo):
        """Base grammar, or with `tie`: for later unknowns, divisors come from
        the earlier offsets (and small numbers), which keeps deep offsets cheap."""
        if not self.idea.tie or i == 0:
            out = self._grammar(i, nv, wv, T, D, lo, None)
        else:
            prev = self._offsets.get(tuple(wv[i - 1]), 1)
            divs = sorted({d for d in (abs(prev), 2 * abs(prev)) if d > 0} | set(range(1, min(D, 12) + 1)))
            out = self._grammar(i, nv, wv, T, D, lo, divs)
        return out

    def _grammar(self, i, nv, wv, T, D, lo, divs):
        out = []
        for rank, (a_sym, a_val) in enumerate(self._atoms(i, nv, wv)):
            for d in (divs or range(1, D + 1)):
                res = {v % d for v in a_val}
                if len(res) != 1:
                    continue
                c0 = (-res.pop()) % d - d
                while c0 <= T:
                    vals = [(v + c0) // d for v in a_val]
                    if min(vals) >= lo:
                        self._offsets[tuple(vals)] = c0
                        out.append((rank * 3 + d + 2 * abs(c0) + (1 if c0 < 0 else 0), (a_sym + c0) / d, vals))
                    c0 += d
        out.sort(key=lambda t: t[0])
        return out

    def search_class(self, M, r, T=None, D=None, deadline=None):
        self._offsets = {}
        polys, kl, why = super().search_class(M, r, T or self.idea.T, D or self.idea.D, deadline)
        if polys is None:
            return None, kl, why
        return [polys[self.perm[i]] for i in range(len(polys))], kl, why
