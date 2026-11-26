"""Lean-only abc proof alarm.

The abc conjecture is OPEN.  This package contains the *only* code path that
may write ``LEAN_ACCEPTED`` to ``results/abc_proof/status.json``: a successful
``lake env lean`` check of ``lean/Abc/Proof.lean`` against the frozen
``lean/Abc/Statement.lean``.

An LLM, a worker, the dashboard, or a hand-edited status file can never make
the alarm say ``LEAN_ACCEPTED``.  A missing proof file is ``OPEN``.  A changed
statement, a ``sorry``/``admit``, an extra axiom, or a Lean error is
``REJECTED``.
"""
from __future__ import annotations

OPEN = "OPEN"
REJECTED = "REJECTED"
LEAN_ACCEPTED = "LEAN_ACCEPTED"

VERDICTS = (OPEN, REJECTED, LEAN_ACCEPTED)

#: The only axioms a proof of ``Abc.Statement`` may depend on.  In particular,
#: ``native_decide``'s ``Lean.ofReduceBool`` and ``sorryAx`` are rejected.
ALLOWED_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})

STATEMENT_PATH = "lean/Abc/Statement.lean"
PROOF_PATH = "lean/Abc/Proof.lean"
FROZEN_PATH = "swarm/abc_statement.sha256"
STATUS_PATH = "results/abc_proof/status.json"
