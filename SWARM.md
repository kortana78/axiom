# AXIOM swarm: running it 24/7 for free

## How it works

- `swarm/queue.json`: the problems and search settings. This is the only file a reviewer edits.
- Workers (`python -m axiom.swarm.worker`): each takes a shard of the open residue classes and
  searches witness families. Output is plain data and is not trusted.
- Idea generator (`python -m axiom.ideas.run`): proposes search ideas and tests them
  (see below). One runner per problem in Actions; one core on a VM.
- Merge (`python -m axiom.swarm.merge`): rebuilds every family into a proof and re-checks it with
  the kernel, then checks the reduction theorem as a whole. It writes `results/<id>/status.json`
  and updates `frontier.json`:
  - open classes shrank: keep going
  - no progress: enlarge the grammar (T, D x1.5)
  - grammar ceiling: refine the modulus and lift the open classes
- Lean (`python -m axiom.swarm.lean_check`): checks the exported class lemmas against Mathlib.
  Only the class lemmas are formalized; the reduction step is not yet.
- Dashboard: `results/index.html` and `results/SUMMARY.md`.
- Memory: `results/<id>/classes.json` keeps every verified family, so each batch starts where
  the last one stopped.

## ABC triple hunter (search mode)

`swarm/queue.json` also supports search-only entries with `"kind": "abc"`.
They do not fit the witness grammar: the target is not an equation to prove.

- Workers search coprime positive integers `a + b = c` for a high quality
  `q = log(c) / log(rad(a*b*c))`, where `rad` is the product of the distinct
  primes dividing `a*b*c`.
- Two families alternate: `c_smooth` (smooth `c`, window of `a`) and
  `legs_smooth` (both legs smooth). A rad sieve supplies exact radicals; no
  candidate is trusted.
- Merge recomputes `gcd(a,b)`, `a+b=c`, the prime factorizations, the radical
  and `q` from scratch. Invalid or non-coprime triples are rejected. Records
  live in `results/abc/records.json`; the dashboard labels the mode
  "search only".
- The exported Lean file checks only `a+b=c` and `Nat.Coprime a b` for each
  record. The radical/quality computations are exact Python integer checks,
  not Lean proofs, and nothing here proves the abc conjecture.
- Cursors for both families are in `results/abc/frontier.json`. Merge advances
  a cursor only when every shard of the batch finished its slice; unfinished
  slices shrink on the next batch.

## S-unit certificates (`kind: "sunit"`)

`swarm/queue.json` supports finite S-unit entries. The statement is: all
coprime positive `a + b = c` whose `abc` has no prime factor outside `S`.

- Workers solve one fixed prime `q in S` and one exponent-box shard per job.
  The output is an untrusted certificate block (height bound, congruence
  lattice, LLL data, exponent box, solutions).
- Merge tiles the shard boxes, runs `axiom.sunit.check` independently, writes
  `certificate.json`, `status.json`, and a Lean export, then deletes the
  shards. A missing or conflicting shard is carried over, not accepted.
- `VALIDATED` means the checker accepted and the sorted list matches the
  published Matschke–von Känel list exactly (count and SHA-256 anchor).
  `CERTIFIED` means the checker accepted a complete certificate without an
  exact published anchor in this repository.
- `S={2,3,5}` is validated (17 triples, about 17 s to solve and 11 s to
  re-check locally). `S={2,3,5,7}` is **not** certified here: the simple
  fixed-`q` box has about `2.4e11` points and needs the paper's p-adic
  logarithm/sieving refinements.
- The Lean export checks each listed triple (`a+b=c`, coprimality, explicit
  factorisations into primes of `S`). It does not formalize completeness and
  is labelled "computer-assisted, independently re-checked", never "Lean
  verified" for stages a/b.

See `swarm/sunit_validation.md` for sources, exact lists, commands, timings,
and the honest limits.

## ABC proof alarm (`axiom/abc_proof/`)

This is the only path to `LEAN_ACCEPTED`; no worker, LLM, merge step, or
hand-edited status file may set it.

- The frozen statement hash is `swarm/abc_statement.sha256`. Changing
  `lean/Abc/Statement.lean` without deliberately updating the freeze makes the
  alarm `REJECTED`.
- A proof must be `lean/Abc/Proof.lean` and declare exactly
  `theorem Abc.abc_proved : Abc.Statement`.
- The `abc-proof-check` CI job runs on every push and every scheduled run. It
  rejects `sorry`, `admit`, and axiom declarations, compiles with
  `lake env lean`, and requires `#print axioms Abc.abc_proved` to list only
  `propext`, `Classical.choice`, `Quot.sound`.
- The status file is `results/abc_proof/status.json` with verdict `OPEN`,
  `REJECTED`, or `LEAN_ACCEPTED`. The dashboard top line reads only that file.
- On `LEAN_ACCEPTED`, the workflow opens the issue
  "Lean accepted a proof of abc" with the full status file.
- A missing proof is `OPEN`; a changed statement is `REJECTED`; a Lean error,
  a non-allowed axiom, or a wrong target theorem is `REJECTED`.

## ABC proof-attempt loop (`axiom/abc_prover/`)

This is a bounded LLM -> Lean loop, not an abc prover:

```bash
python -m axiom.abc_prover.loop --mathlib /path/to/mathlib4 \
    --rounds 2 --max-proposals 3 --time 900 --max-requests 2
```

- The model receives the honest route graph (`swarm/abc_prover_routes.json`),
  previously checked lemmas, and recent Lean errors.
- Every proposal is sanitized: `sorry`, `admit`, axiom/constant declarations,
  imports, namespaces, `set_option`, `native_decide`, and metaprogramming are
  rejected before Lean runs.
- A proposal that compiles with only `propext`, `Classical.choice`, and
  `Quot.sound` is recorded as `CHECKED` in `results/abc_prover/ledger.json`.
- `CHECKED` is not a proof of `Abc.Statement`. The loop never writes
  `lean/Abc/Proof.lean` and never writes the alarm verdict. A target-like lemma
  is saved to `results/abc_prover/target_attempt.lean` for human review.
- The dashboard adds an "ABC proof attempts" table; the top line remains the
  alarm's `OPEN`/`REJECTED`/`LEAN_ACCEPTED` banner.
- `.github/workflows/abc-prover.yml` runs the loop weekly and on manual
  dispatch, under the shared `results/llm_usage.json` budget. It fails if the
  prover touches `lean/Abc/Proof.lean` or `results/abc_proof/status.json`.

## The idea generator (`axiom/ideas/`)

AXIOM searches; the idea generator decides what to search. An idea is plain data
(`axiom/ideas/space.py`):

- `order`: the unknowns in search order; the last one is solved exactly
- `atoms`: building blocks for witness formulas: n, n2, n3, v, nv, n2v, vv, nvv
- `mult`: coefficients for the atoms
- `T`, `D`: offset and divisor ranges
- `tie`: later unknowns may use earlier offsets as divisors

Proposal order each run (`python -m axiom.ideas.run --problem <id> --time <s>`):

1. hand-written ideas in `swarm/ideas.json` (this is where Claude or you lead)
2. mutations of ideas that already paid off
3. enumerated ideas, chosen by a UCB bandit over idea families

Every hit is written as a shard file and re-checked by the kernel at merge, like any worker
output. Scores live in `results/<id>/ideas_log.json`, so the swarm learns which kinds of ideas
work. Each found family records the idea that produced it, and hand-written ideas are tagged
`source: hand`, so it stays clear what the engine found alone.

Results so far (local runs):
- Erdos-Straus: open classes mod 840 went 12 -> 8 -> 6, and the 6 left are exactly the perfect
  squares mod 840, where polynomial witnesses are impossible (Mordell). This rediscovers the
  classical reduction blind. It is not new mathematics.
- Sierpinski 5/n: 12 classes mod 840 open after short runs, 3 of them squares.
- Finding a bug: one search was stuck because exact checks used `together` without `cancel`.
  Fixed, with a regression test. Every 0.3 run had lost families to it.

## Free-LLM proposals (`axiom/llm/`)

The `llm-ideas` workflow job asks an OpenAI-compatible free model for search
ideas. It is capped (2 requests per run, 20 per day by default), retries with
backoff, and logs requests/tokens to `results/llm_usage.json`.

- Secrets: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`; optionally
  `LLM_PROVIDERS` as JSON for several free providers.
- No key: the job prints a skip message and succeeds. It does not fail the
  batch and does not write a proposal file.
- The model sees the statement, status/frontier, idea log, and recent
  failures. It never sees published solution lists.
- Output is validated against the `swarm/ideas.json` schema (witness), a
  separate S-unit heuristics schema, or a narrow ABC search schema. Accepted
  entries are tagged `source = "llm:<model>"` and written to
  `swarm/llm_ideas.json`, `swarm/sunit_ideas.json`, or
  `swarm/abc_ideas.json`.
- Proposals are untrusted: witness ideas are picked up by the ordinary idea
  generator and must survive worker search, merge, the kernel, and Lean. The
  model never marks anything proved and never edits `results/`, the kernel,
  or the checker.

## Work-item scheduler and the VM

`axiom.swarm.schedule` builds a batch of at most 1000 items
`(problem, shard or exponent box, idea)`, assigns them round-robin to runners,
and records planned/done/carried-over in `results/schedule/runner_<i>.json`.
Each item writes its own shard file. `--summarize` merges the records into
`results/schedule.json`.

```bash
python -m axiom.swarm.schedule --runner 0 --runners 4 --minutes 45
python -m axiom.swarm.schedule --summarize
```

`deploy/run_swarm.sh` launches one scheduler process per CPU core on the same
queue, then summarizes, merges, and builds the dashboard. It is still a
moderate batch loop, not a claim that more compute solves the open problems.

## ABC proof track (`kind: "abc_route"`)

`lean/Abc/Statement.lean` is the exact statement every abc-track claim must
refer to: radical, quality, the Masser–Oesterlé `K(ε)` form, and the
finitely-many-exceptions form. `swarm/abc_routes.md` records the known routes
(Szpiro, Mason–Stothers, Stewart–Tijdeman, Stewart–Yu, explicit abc, IUT
described neutrally) with citations and status.

- `abc_route` queue entries are proof-track targets, not search jobs.
- A candidate argument is accepted only as a Lean proof of `Abc.Statement`
  with no `sorry`, no new axioms, `#print axioms` reviewed, and human review.
- Rejected or unaccepted arguments are recorded as unverified ideas in
  `swarm/abc_routes.md`; they never enter `results/` as proved.
- The dashboard always shows: **abc conjecture: OPEN. No result here proves
  it.** Only a Lean proof of the exact statement with standard axioms plus
  human review may change that line.

## Option A: GitHub Actions (free for public repos)

1. Push this folder to a public GitHub repo.
2. Settings > Actions > General > Workflow permissions: "Read and write".
3. Actions tab > axiom-swarm > Run workflow. After that it runs every 6 hours.

Defaults: 10 shards x 45 minutes every 6 hours. The free plan allows up to 20 concurrent jobs
of up to 6 hours each, but GitHub's terms forbid use that burdens their servers
disproportionately. Running flat out around the clock risks the account. Increase gradually.

## Option B: an always-free VM (true 24/7)

Oracle Cloud's Always Free tier offers ARM VMs with several cores. Sign-up needs a card for
verification. On the VM:

```
sudo apt-get install -y python3-pip git
git clone https://github.com/<you>/axiom && cd axiom
pip install -r requirements.txt
WORKERS=$(nproc) MINUTES=50 ./deploy/run_swarm.sh          # or install deploy/axiom-swarm.service
```

Use PUSH=1 with a git remote that has a token, so results reach GitHub.

## Option C: Render

Render's free compute (0.1 CPU, 750 hours a month shared by all services) is too small for the
workers. `render.yaml` publishes `results/` as a free static dashboard.

## The reviewer loop

A scheduled Claude session reads the results, writes `swarm/REVIEW_LOG.md`, and steers through
`swarm/queue.json`, following `swarm/REVIEWER.md`. It never edits results and never declares
anything proved: only the kernel merge and Lean decide.

## Honest limits

- More workers make the search wider, not smarter. The remaining Erdos-Straus classes include
  ones where no polynomial family can exist (Mordell), so they need new kinds of witnesses
  (version 0.4), not just more compute.
- S-unit certificates are finite results for a fixed `S`. They do not prove or
  disprove abc, and `S={2,3,5,7}` is explicitly not certified by this
  implementation.
- The LLM adapter proposes ideas; it does not reason reliably and cannot
  prove anything. Its output is schema-checked but still untrusted.
- The scheduler's 1000-item cap is a batch size, not a claim of completeness.
  More workers widen the search; they do not make an open problem solved.
- The ABC proof track is a formal statement plus documented routes. No
  candidate proof is accepted, and the dashboard's OPEN line is permanent
  until a Lean proof of `Abc.Statement` with standard axioms is human-reviewed.
