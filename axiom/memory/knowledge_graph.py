"""Mathematical knowledge graph: statements, definitions and dependencies."""
from __future__ import annotations

try:
    import networkx as nx
except ImportError:  # pragma: no cover
    nx = None

from ..kernel.proof_objects import Proof


class KnowledgeGraph:
    def __init__(self):
        self.g = nx.DiGraph() if nx else None
        self._edges = []
        self._nodes = {}

    def add_node(self, key: str, kind: str, **attrs):
        self._nodes[key] = dict(kind=kind, **attrs)
        if self.g is not None:
            self.g.add_node(key, kind=kind, **attrs)

    def add_edge(self, src: str, dst: str, relation: str):
        self._edges.append((src, dst, relation))
        if self.g is not None:
            self.g.add_edge(src, dst, relation=relation)

    def add_proof(self, proof: Proof):
        key = proof.conclusion.key()
        self.add_node(key, "theorem", rule=proof.rule)
        for p in proof.premises:
            self.add_proof(p)
            self.add_edge(p.conclusion.key(), key, "used_in")

    def dependencies(self, key: str):
        if self.g is None or key not in self.g:
            return []
        return list(nx.ancestors(self.g, key))

    def summary(self) -> dict:
        kinds = {}
        for v in self._nodes.values():
            kinds[v["kind"]] = kinds.get(v["kind"], 0) + 1
        return {"nodes": len(self._nodes), "edges": len(self._edges), "by_kind": kinds}
