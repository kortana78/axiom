# AXIOM 0.4: Swarm, Idea Generator, Certified Reductions

0.4 adds the swarm (parallel workers on GitHub Actions or a free VM, kernel-checked merge,
Lean check job, dashboard) and the idea generator. It also includes a search-only ABC
triple hunter whose records are re-verified exactly at merge time. See SWARM.md.

0.4 also has a certified S-unit solver with an independent checker, a free-LLM
idea adapter, a capped work-item scheduler, and an ABC proof track. The abc
conjecture remains **OPEN**; no result in this repository proves it.

## Certified S-unit solver (`axiom/sunit/`)

For a finite set of primes `S`, the solver finds every coprime positive
`a + b = c` with every prime factor of `abc` in `S`. It uses an explicit height
bound, a congruence lattice with LLL reduction, and exhaustive enumeration.
The certificate is plain data: `S`, stage-a constants, stage-b lattice/LLL
data, and the stage-c solution list.

```bash
python -m axiom.sunit.hunt --S 2,3,5 --out /tmp/sunit_2_3_5.json
python -m axiom.sunit.check --certificate /tmp/sunit_2_3_5.json --S 2,3,5
```

`axiom.sunit.check` shares no code with the solver. It recomputes the bound,
the discrete logarithms, the lattice index and LLL conditions, and
re-enumerates the whole exponent box. Published-list validation is recorded in
`swarm/sunit_validation.md`; `S={2,3}` (4 triples) and `S={2,3,5}` (17
triples) reproduce the Matschke–von Känel lists exactly. `S={2,3,5,7}` is not
certified by this implementation: its `q=2` box has about `2.4e11` points, so
we stop and report rather than claim it.

Status words are `VALIDATED` (checker accepts and the list matches a published
anchor exactly) and `CERTIFIED` (checker accepts a complete certificate with
no exact published anchor here). The Lean export checks each listed triple
(`a+b=c`, coprimality, explicit S-smooth factorisations); it does **not**
formalize completeness and is never called a Lean proof of completeness.

## LLM ideas (`axiom/llm/`)

An OpenAI-compatible adapter proposes search ideas only. It reads the current
`status.json`, `frontier.json`, `ideas_log.json`, and recent failures; it
never receives published solution lists and never writes proof results, the
kernel, or the checker.

```bash
LLM_BASE_URL=https://.../v1 LLM_API_KEY=... LLM_MODEL=... \
  python -m axiom.llm.ideas --problem erdos_straus --time 300
python -m axiom.llm.ideas --all --max-problems 10 --time 300
```

Secrets are `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`; multiple providers can
be supplied as JSON in `LLM_PROVIDERS`. With no key the command skips and
exits 0. Requests are capped per run and per day, retried with backoff, and
logged in `results/llm_usage.json`. Output is validated against the
`swarm/ideas.json` schema (witness), a separate S-unit heuristics schema, and
a narrow ABC search schema; accepted entries are tagged `source = "llm:<model>"`
and written to `swarm/llm_ideas.json`, `swarm/sunit_ideas.json`, or
`swarm/abc_ideas.json`. They still go through workers, merge, the kernel, and
Lean.

## Work-item scheduler (`axiom/swarm/schedule.py`)

A batch is at most 1000 items `(problem, shard or exponent box, idea)`. Runners
take items round-robin; each item writes its own shard file; each runner
records planned/done/carried-over in `results/schedule/runner_<i>.json`, and
`--summarize` writes `results/schedule.json`. The VM script launches one
runner per CPU core:

```bash
WORKERS=4 MINUTES=45 ./deploy/run_swarm.sh
```

## ABC proof track

`lean/Abc/Statement.lean` fixes the exact statement (`Abc.Statement`) with the
radical, quality, and finitely-many-exceptions forms. `swarm/abc_routes.md`
records known routes and partial results with citations (Szpiro,
Mason–Stothers, Stewart–Yu, explicit abc, IUT described neutrally) and their
status. Queue entries of kind `abc_route` are proof-track targets, not search
jobs. A candidate argument is accepted only as a Lean proof of
`Abc.Statement` with no `sorry` and no new axioms, plus human review.

### Lean-only proof alarm

The alarm lives in `axiom/abc_proof/`. The frozen SHA-256 of the statement is
in `swarm/abc_statement.sha256`; changing `lean/Abc/Statement.lean` without
deliberately updating that file makes the alarm `REJECTED`. A proof must be
placed at `lean/Abc/Proof.lean`:

```lean
import Abc.Statement

theorem Abc.abc_proved : Abc.Statement := by
  -- complete proof required
```

`python -m axiom.abc_proof.check --mathlib /path/to/mathlib4` compiles the
proof against the frozen statement, rejects `sorry`, `admit`, and axiom
declarations, and accepts only the axiom list
`propext, Classical.choice, Quot.sound`. The CI job `abc-proof-check` runs on
every push and every scheduled run. The dashboard top line is chosen only from
`results/abc_proof/status.json`:

- `OPEN`: **abc conjecture: OPEN. No result here proves it.**
- `REJECTED`: **abc conjecture: OPEN. A proof attempt was rejected by Lean (see log).**
- `LEAN_ACCEPTED`: **LEAN ACCEPTED A PROOF OF Abc.Statement (axioms: ...). Human review required before any announcement.** The workflow opens a GitHub issue with the full status file.

No LLM, worker, script, or hand-edited status file can set `LEAN_ACCEPTED`;
only a successful Lean check can. A missing `Proof.lean` is `OPEN`.

### Proof-attempt loop

The bounded loop in `axiom/abc_prover/` asks the configured LLM for small
Lean lemmas, rejects `sorry`/`admit`/axioms/imports/metaprogramming before
Lean, compiles each proposal against the frozen statement, and records the
result in `results/abc_prover/ledger.json`:

```bash
python -m axiom.abc_prover.loop --mathlib /path/to/mathlib4 \
    --rounds 2 --max-proposals 3 --time 900 --max-requests 2
```

`CHECKED` means Lean accepted an auxiliary lemma with only the allowed axioms.
It is **not** a proof of abc. The loop never writes `lean/Abc/Proof.lean` and
never writes the alarm verdict. A checked lemma whose type mentions
`Abc.Statement` is saved to `results/abc_prover/target_attempt.lean` for human
review, never promoted automatically. The dashboard shows the attempt counts;
the top line still comes only from the alarm.

# (0.3 notes) Blind Mathematical Discovery with Certified Reductions

## What is new in 0.3

0.2 made the engine blind. 0.3 gives the blind engine real tools for existence problems,
plus two new kernel rules that turn partial progress into proved theorems.

- Transparent statements. Open problems are given as explicit formulas, not as black box
  predicates. In 0.2 Erdos-Straus was `es_rep(n)`, which left nothing to reason about (0 classes).
- Blind witness construction (`blind/witness.py`). For any target
  `forall n >= L: exists v1 ... vk: LHS = RHS`:
  - moduli come from the statement (lcm of its coefficients with 1..j)
  - per residue class, search integer polynomial witnesses from a generic grammar
    `(atom + c) / d`, atoms built from n and earlier witnesses
  - the last variable is solved exactly when possible
  - open classes are lifted to the next modulus and retried with a larger grammar (anytime)
- New kernel rule `residue_cover`: target follows from its truth on the listed open classes.
  With no open classes this is a complete proof.
- New kernel rule `prime_reduction`: if the equation is scale invariant in (n, witnesses)
  (checked by the kernel), a solution for a prime factor scales to n, so the target
  follows from its truth on primes in the open classes.
- Obstruction diagnosis: generic properties shared by the open classes.
- Generic pattern grammar replaces the hand picked list (removed the quasiperfect specific
  `square_or_twice_square`). It still rediscovers sigma(n) odd <=> n is a square or twice a square.

Blind results (no problem specific code):
- complete proofs: 2/n = 1/x + 1/y; for every n >= 3 a Pythagorean triple with leg n
- Erdos-Straus and Sierpinski 5/n: kernel certified reductions to primes in a few residue
  classes (see research/ and the run notes). Not solved.

Run: `python -m axiom blind solve problem.json --time 600`

---

# (0.2 notes) Blind Mathematical Discovery

AXIOM is a small symbolic research engine. There is no language model inside.
It invents candidate mathematics from a problem statement, tries to break it,
proves what survives with a small trusted kernel, and records everything,
including failures.

**0.2 is a fundamental change from 0.1.** The engine is no longer given
problem-specific modules, handcrafted approaches, preselected residue classes,
formula templates, proof strategies, or hints about which cases are hard. It
receives an unfamiliar problem and has to discover the mathematics itself.

| AXIOM 0.1 | AXIOM 0.2 |
|---|---|
| Has problem-specific modules | Receives an unfamiliar problem specification |
| Contains handcrafted approaches | Generates its own approaches |
| Knows particular residue classes to investigate | Discovers useful residue classes itself |
| Uses supplied problem knowledge | Uses general mathematical foundations |
| Runs predefined experiments | Designs and conducts experiments autonomously |

It still needs mathematics to reason with — definitions, axioms, inference
rules and general results. What is removed is knowledge *about the particular
problem that gives away its solution*.

## Quick start (0.2)

```
pip install sympy networkx
python -m axiom blind audit                         # leakage audit first
python -m axiom blind list                          # blind test problems
python -m axiom blind solve examples/blind_problem.json --time 30
python -m axiom blind run hidden_div_42 --time 30
python -m axiom blind benchmark --time 20           # three test environments
python tests/test_blind.py
```

Give it your own problem as a JSON file:

```json
{
  "name": "Problem_001",
  "domain": "number_theory",
  "formal_statement": "forall n >= 0: 6 | n^3 - n",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

There is no field for a solution, a lemma, a residue class, a formula template
or a proof strategy — `BlindProblem.from_dict` rejects extra keys, so the
engine cannot receive target-specific help even by accident.

Use `"target": "discover"` with `"formal_statement": "study <expression>"`
when the problem has no supplied conclusion (for example
`study Sum[i=1..n](i^2)`, or `"study n^7 - n"`). Recurrences are given as
definitions, e.g. `"a(0) = 0; a(n+1) = a(n) + 2*n + 1"`.

## The blind autonomous discovery loop

```
receive unfamiliar problem
  -> analyse structure (objects, assumptions, quantifiers, relationships)
  -> invent (lemmas, invariants, definitions)
  -> explore (cases, transformations, constructions)
  -> test hypotheses (symbolic deduction, computation, counterexamples)
  -> attempt proof construction
  -> independent verification (kernel, plus optional Lean export)
  -> if unsuccessful: analyse the failure and mutate the strategy
```

The engine invents its own experiments. Residue classes and shift offsets are
derived from constants in the problem and from sampled values
(`blind/analysis.py`); they are never preselected by a problem module.

### Strategy Mutation (`blind/mutation.py`)

When all general strategies stall, the engine does not merely grow the search
budget. It asks six generic questions and turns the answers into new strategies,
each checked by the same trusted verifier:

1. What assumptions are making this problem difficult?
2. Can I formulate an equivalent statement?
3. Can I introduce a new mathematical object?
4. Can I prove a stronger intermediate proposition?
5. Can I combine two previously unrelated observations?
6. Can I construct an entirely different proof route?

Every mutation is recorded in the research record with the question that
produced it. Failed routes are kept so the system does not rediscover them.

## Research memory

Every run writes `research/<problem>/`:

```
original_statement.json   definitions.json      conjectures.json
invented_lemmas.json      counterexamples.json  proof_attempts.json
failed_strategies.json    discoveries.json      final_proof.lean
research_report.md        axiom.db              (persistent SQLite store)
```

On later runs, previous discoveries are re-read and **re-verified by the
kernel** before they are used. Statuses are never interchangeable:

- `known`: given assumption
- `conjectured`: proposed, unproved
- `refuted`: a checked counterexample exists
- `derived`: proof accepted by the Axiom kernel
- `verified`: proof also accepted by Lean
- `undecided_within_budget`: search ran out; this is NOT a refutation

## Blind testing and the leakage audit

```
python -m axiom blind benchmark --time 20
```

Three environments:

| Environment | Question |
|---|---|
| `hidden` | Can it prove known theorems when only the statement is given? |
| `research` | Can it invent useful intermediate lemmas and constructions? |
| `open` | Can it investigate honestly without claiming a false solution? |

Reference answers live in `blind/answers.py`, which is imported **only** by
the evaluation harness. `python -m axiom blind audit` checks that no answer
signature or 0.1 strategy hint appears in discovery-facing source, that blind
inputs conform to the minimal schema, that no discovery module imports the
answer/evaluation/legacy problem modules, and that only general kernel rules
are reachable. The benchmark refuses to run if the audit fails.

The audit explicitly reports legacy 0.1 files that still contain
problem-specific mathematics (`kernel/inference.py`, `kernel/predicates.py`,
`invention/constructions.py`, `discovery/strategies.py`, `problems/library.py`).
They are gated: the blind controller's rule allowlist and tactic set make them
unreachable, and any proof using a forbidden rule is rejected.

## What 0.2 does (verified)

- Proves hidden theorems from their statements alone: sums of i^2/i^3,
  divisibility of n^5-n and n^7-n, exponential thresholds.
- Invents the mathematical content when no conclusion is supplied: closed
  forms of sums and geometric series, the best constant divisor of n^7-n and
  of products of consecutive integers, closed forms of recurrences.
- Records strategy mutations (new objects, stronger intermediates, combined
  observations) in the research record.
- Investigates open problems (Collatz, Legendre, quasiperfect, Erdos-Straus)
  with bounded verification and counterexample search, and honestly leaves
  them undecided. None is claimed solved.

The current blind benchmark: **15/15 cases pass** with an 8 s per-case budget
(5 hidden, 6 research, 4 open).

## Layout

```
axiom/
  kernel/        typed terms, propositions, proof objects, trusted inference rules
  reasoning/     backward tactics, forward consequences, matching, rewriting, search
  invention/     data-driven conjectures, invariant synthesis, generalisation, definitions
  discovery/     0.1 controller and special strategies (not used by blind 0.2)
  verification/  Lean 4 export and Lean bridge
  memory/        SQLite theorem store, knowledge graph, search history
  problems/      0.1 problem format and library
  blind/         0.2: problem interface, analysis, loop, mutation, memory,
                 evaluation harness, leakage audit
  main.py        command line (0.1 and `blind` commands)
```

## Trusted base

`kernel/inference.py`, SymPy polynomial arithmetic, and the predicate
evaluators in `kernel/predicates.py`. Lean export is the route to removing
that trust. Generated `.lean` files contain no `sorry`; rules without a Lean
translation are listed as not exported rather than asserted.

## Roadmap

- 0.3: unification-driven lemma application from the store; rewriting search
- 0.4: richer invention (rational/modular families, auxiliary sequences)
- 0.5: learned move ranking from search history (order only, never exclusion)
- 1.0: Lean verification for every kernel rule
