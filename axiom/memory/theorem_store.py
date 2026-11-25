"""Persistent theorem store (SQLite).

Each statement has exactly one status. Upgrading CONJECTURED to DERIVED
requires a kernel-checked proof; the store refuses anything else.
"""
from __future__ import annotations

import json
import sqlite3
import time
from typing import Dict, List, Optional

from ..kernel.inference import Kernel
from ..kernel.proof_objects import Proof, Status
from ..kernel.propositions import Prop

SCHEMA = """
CREATE TABLE IF NOT EXISTS statements (
    key TEXT PRIMARY KEY,
    problem TEXT,
    status TEXT,
    origin TEXT,
    rule TEXT,
    proof_json TEXT,
    note TEXT,
    created REAL,
    updated REAL
);
CREATE TABLE IF NOT EXISTS failures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem TEXT, goal TEXT, tactic TEXT, reason TEXT, created REAL
);
"""


class TheoremStore:
    def __init__(self, path: str = ":memory:", kernel: Optional[Kernel] = None):
        self.db = sqlite3.connect(path)
        self.db.executescript(SCHEMA)
        self.kernel = kernel or Kernel()
        self.proofs: Dict[str, Proof] = {}    # in-session proof objects
        self.props: Dict[str, Prop] = {}

    def _upsert(self, key, problem, status, origin, rule=None, proof=None, note=""):
        now = time.time()
        row = self.db.execute("SELECT status FROM statements WHERE key=?", (key,)).fetchone()
        if row and row[0] in (Status.DERIVED.value, Status.VERIFIED.value) and status not in (Status.VERIFIED,):
            return  # never downgrade an established result
        self.db.execute(
            "INSERT INTO statements VALUES (?,?,?,?,?,?,?,?,?) ON CONFLICT(key) DO UPDATE SET "
            "status=excluded.status, origin=excluded.origin, rule=excluded.rule, "
            "proof_json=excluded.proof_json, note=excluded.note, updated=excluded.updated",
            (key, problem, status.value, origin, rule,
             json.dumps(proof.to_dict()) if proof else None, note, now, now))
        self.db.commit()

    def conjecture(self, prop: Prop, problem: str, origin: str, note: str = ""):
        self.props[prop.key()] = prop
        if self.status(prop) is None:
            self._upsert(prop.key(), problem, Status.CONJECTURED, origin, note=note)

    def refute(self, prop: Prop, problem: str, counterexample: str):
        self.props[prop.key()] = prop
        self._upsert(prop.key(), problem, Status.REFUTED, "counterexample engine", note=counterexample)

    def undecided(self, prop: Prop, problem: str, note: str):
        self.props[prop.key()] = prop
        st = self.status(prop)
        if st in (None, Status.CONJECTURED):
            self._upsert(prop.key(), problem, Status.UNDECIDED, "controller", note=note)

    def add_proof(self, proof: Proof, problem: str, origin: str) -> bool:
        ok, msg = self.kernel.check(proof)
        if not ok:
            self.db.execute("INSERT INTO failures(problem, goal, tactic, reason, created) VALUES (?,?,?,?,?)",
                            (problem, proof.conclusion.key(), proof.rule, "kernel rejected: " + msg, time.time()))
            self.db.commit()
            return False
        key = proof.conclusion.key()
        self.proofs[key] = proof
        self.props[key] = proof.conclusion
        self._upsert(key, problem, Status.DERIVED, origin, proof.rule, proof, note=msg)
        return True

    def mark_verified(self, prop: Prop, problem: str, note: str):
        key = prop.key()
        if key in self.proofs:
            self._upsert(key, problem, Status.VERIFIED, "lean", self.proofs[key].rule, self.proofs[key], note)

    def log_failure(self, problem, goal, tactic, reason):
        self.db.execute("INSERT INTO failures(problem, goal, tactic, reason, created) VALUES (?,?,?,?,?)",
                        (problem, goal, tactic, reason, time.time()))

    def status(self, prop: Prop) -> Optional[Status]:
        row = self.db.execute("SELECT status FROM statements WHERE key=?", (prop.key(),)).fetchone()
        return Status(row[0]) if row else None

    def rows(self, problem: Optional[str] = None) -> List[tuple]:
        q = "SELECT key, status, origin, rule, note FROM statements"
        if problem:
            return self.db.execute(q + " WHERE problem=? ORDER BY created", (problem,)).fetchall()
        return self.db.execute(q + " ORDER BY created").fetchall()

    def failures(self, problem: Optional[str] = None, limit: int = 50):
        q = "SELECT goal, tactic, reason FROM failures"
        args = ()
        if problem:
            q += " WHERE problem=?"
            args = (problem,)
        return self.db.execute(q + f" ORDER BY id DESC LIMIT {int(limit)}", args).fetchall()
