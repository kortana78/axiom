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
- The Lean export has not been run yet, because Lean could not be installed where this was
  built. The first Actions run is its first real test. Expect fixes after that.
