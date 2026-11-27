"""Bounded Lean proof-attempt loop for the abc conjecture.

This package proposes small auxiliary Lean lemmas, checks each one with Lean,
and records the result.  A ``CHECKED`` lemma is a theorem the kernel accepted;
it is **not** a proof of ``Abc.Statement``.  The package never writes
``lean/Abc/Proof.lean`` and never writes the alarm verdict.

Only :mod:`axiom.abc_proof.check` may write ``LEAN_ACCEPTED``.
"""
from __future__ import annotations

CHECKED = "CHECKED"
REJECTED = "REJECTED"
SKIPPED = "SKIPPED"
NO_PROOF = "NO_PROOF"

#: Ledger of every proposal and its Lean result.
LEDGER_PATH = "results/abc_prover/ledger.json"
#: Honest summary of the loop; ``abc`` is always ``OPEN`` here.
STATUS_PATH = "results/abc_prover/status.json"
#: A checked lemma whose type mentions ``Abc.Statement`` is copied here only.
#: It is never copied to ``lean/Abc/Proof.lean`` automatically.
TARGET_ATTEMPT_PATH = "results/abc_prover/target_attempt.lean"
#: Known routes and gaps shown to the model.
ROUTES_PATH = "swarm/abc_prover_routes.json"

#: Per-worker ledgers and heartbeats for the persistent fleet.
WORKERS_DIR = "results/abc_prover/workers"
#: Supervisor heartbeat and worker roster.
SUPERVISOR_PATH = "results/abc_prover/supervisor.json"
#: Atomic per-provider daily request reservations.
QUOTA_DIR = "results/abc_prover/quota"
#: Shared request/token accounting (also used by the rest of the swarm).
USAGE_PATH = "results/llm_usage.json"

#: A single proposal larger than this is rejected before Lean runs.
MAX_LEAN_CHARS = 12000
