# 24/7 abc proof-attempt fleet on Oracle Always Free

This deploys the persistent prover: a supervisor that keeps N Lean workers
alive, rotates across free LLM providers, enforces a shared daily quota, and
publishes checked auxiliary lemmas.

**What it is not:** a prover of abc. A `CHECKED` lemma is a Lean theorem that
does not establish `Abc.Statement`. Only `lean/Abc/Proof.lean`, verified by the
separate `abc-proof-alarm` workflow, can change the alarm. This fleet never
writes that file or that verdict.

## Instance

Oracle Cloud **Always Free Ampere A1**: 4 OCPU / 24 GB RAM, Ubuntu 24.04 ARM64.
Open ports 22 only. Add a ~4 GB swap file; Lean links can spike memory.

## Install

```bash
git clone https://github.com/kortana78/axiom.git /tmp/axiom-setup
cd /tmp/axiom-setup/deploy/oracle
sudo bash install.sh
sudo nano /etc/axiom/abc-prover.env      # replace REPLACE_ME with your own free keys
sudo chmod 600 /etc/axiom/abc-prover.env
sudo systemctl restart axiom-abc-prover
```

The installer creates `/opt/axiom`, a Python venv, an elan/lake install for the
service user, a pinned Mathlib checkout, the env template, and two systemd
units. It does not contain any API key.

## Verify

```bash
python3 -m axiom.abc_prover.supervisor --health
journalctl -u axiom-abc-prover -f
cat results/abc_prover/supervisor.json
cat results/abc_prover/status.json
```

Healthy output looks like `healthy: 3 workers, heartbeat 12s old, abc=OPEN`.
The dashboard top line must still read
`abc conjecture: OPEN. No result here proves it.`

## Operations

```bash
sudo systemctl status axiom-abc-prover
sudo systemctl restart axiom-abc-prover
sudo systemctl stop axiom-abc-prover
sudo systemctl enable --now axiom-abc-sync.timer
```

Per-worker state lives in `results/abc_prover/workers/w1/`, `w2/`, ...:
`ledger.json`, `heartbeat.json`, and `worker.log`. The merged public ledger is
`results/abc_prover/ledger.json`. Logs and quota sidecars are gitignored;
attempts and heartbeats are committed hourly by the sync timer.

## Workers and agents

`ABC_PROVER_WORKERS` in the env file controls worker count. Each worker owns
one Lean harness and one LLM client. On 4 OCPU / 24 GB, **2–3 workers** is the
practical limit; more will thrash Mathlib compilation. `ProviderPool` can hold
any number of free providers, so "more agents" mostly means more provider keys
and more VPS instances, not infinite workers on one box.

Realistic budget sketch:

- One logical LLM request per worker per batch, 20-second idle gap.
- A 3-worker fleet at ~60 s/request makes ~100 requests/hour if nothing stops
  it, but free daily caps stop it far earlier (Groq ~30/day under our cap,
  OpenRouter free models ~50/day, etc.).
- Rotate legitimate free keys from your own accounts. Do not farm accounts or
  evade rate limits; providers ban that and it is not necessary.

## Scaling out

To run many more agents, run the same service on several instances:

1. Give each host its own `ABC_PROVER_WORKERS` and its own provider subset.
2. Point each host's sync at a distinct results path, or merge host ledgers
   centrally before publishing. Do not have two hosts push the same branch
   concurrently.
3. Keep the alarm workflow as the only writer of the alarm verdict.

Even at large scale, the bottleneck is a new mathematical idea. Lemma spam does
not imply abc. The honest purpose of the fleet is to explore auxiliary routes
and record gaps, not to brute-force a famous open problem.

## Security

- Keys live only in `/etc/axiom/abc-prover.env` (mode 600) and are passed via
  `EnvironmentFile`. They are never committed, logged, or written to results.
- The prover modules cannot write `lean/Abc/Proof.lean` or the alarm status;
  there is a test that enforces this by scanning their source.
- To rotate a key, edit the env file and restart the service.
