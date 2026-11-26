# S-unit validation record

This file is the literature anchor for the certified S-unit solver.  The
solver and checker contain no published solutions; the known triples live
only here and in `tests/test_sunit.py`.

## Sources

- Rafael von Känel and Benjamin Matschke, *Solving the S-unit equation in two
  unknowns*, arXiv:[1605.06079](https://arxiv.org/abs/1605.06079).  The paper
  states the complete lists for `S = {2}`, `{2,3}`, `{2,3,5}`, `{2,3,5,7}` and
  larger supports.
- Data files, authors' site:
  <https://bmatschke.github.io/solving-classical-diophantine-equations/s-unit-equation/>
  (`solutions_2_3.txt`, `solutions_2_3_5.txt`, `solutions_2_3_5_7.txt`).
  Dataset licence: Creative Commons 3.0 by-nc, Rafael von Känel and Benjamin
  Matschke, 2014.
- The paper notes that the cases `n = 1..6` were previously computed by
  B. M. M. de Weger, *Algorithms for Diophantine equations* (1987),
  Theorem 5.4.  This gives an independent published anchor for the small
  supports.
- Height bound used by the solver: Matschke–von Känel, Proposition 10.2,
  `max(h(x),h(y)) <= (5/2) N_S log N_S + 9 N_S`, with `N_S = prod(S)`.
  The Győry–Yu linear-forms alternative is recorded in every certificate but
  is weaker for these small supports.

## Published counts

| `S` | Published count | Reproduced here | Status |
|---|---:|---:|---|
| `{2}` | 1 | 1 | `VALIDATED` |
| `{2,3}` | 4 | 4 | `VALIDATED` |
| `{2,3,5}` | 17 | 17 | `VALIDATED` |
| `{2,3,5,7}` | 63 | not attempted | not certified by this implementation |
| `{2,3,5,7,11}` | 190 | not attempted | not certified by this implementation |
| up to 16 primes | 1,663,449 | not attempted | not certified by this implementation |

The `{2,3,5,7}` case is the first one where the simple fixed-`q` congruence
method becomes impractical: the `q = 2` block has three free exponent
coordinates and about `2.4e11` box points.  Certifying it would need the
p-adic logarithm/banding or sieve refinements of the paper, not more brute
force.  We stop and report rather than claim it.

## Exact lists

### `S = {2,3}` (4 triples)

```
1 + 1 = 2
1 + 2 = 3
1 + 3 = 4
1 + 8 = 9
```

### `S = {2,3,5}` (17 triples)

```
1 + 1 = 2
1 + 2 = 3
1 + 3 = 4
1 + 4 = 5
1 + 5 = 6
1 + 8 = 9
1 + 9 = 10
1 + 15 = 16
1 + 24 = 25
1 + 80 = 81
2 + 3 = 5
2 + 25 = 27
3 + 5 = 8
3 + 125 = 128
4 + 5 = 9
5 + 27 = 32
9 + 16 = 25
```

Canonical SHA-256 of the sorted `(a,b,c)` list (used by the swarm merge as
a literature anchor without putting the answers in the queue):

```
82b410e12d69558ff626bef6b2331f718bffab167c563b8c326c4f8aaf193de1
```

## Reproduction commands

From the repository root:

```bash
python -m axiom.sunit.hunt --S 2,3 --out /tmp/sunit_2_3.json
python -m axiom.sunit.check --certificate /tmp/sunit_2_3.json --S 2,3
# 4 solutions, checker PASS

python -m axiom.sunit.hunt --S 2,3,5 --out /tmp/sunit_2_3_5.json
python -m axiom.sunit.check --certificate /tmp/sunit_2_3_5.json --S 2,3,5
# 17 solutions, checker PASS
```

Measured locally on the development machine (Python 3.11, single core):

| Step | `S={2,3}` | `S={2,3,5}` |
|---|---:|---:|
| solve (stages a–c) | 0.01 s | 17.1 s |
| independent checker (full-box re-enumeration) | 0.01 s | 11.4 s |
| height bound `B` | 80.876400 | 525.089850 |
| exponent bounds | `{2:116, 3:73}` | `{2:757, 3:477, 5:326}` |
| lattice vectors tested | 1,041 | 1,466,279 |

The exact published-list equality is asserted in `tests/test_sunit.py`.
`python -m pytest tests/test_sunit.py -q` runs those assertions plus tamper
rejection, shard merging, and a source-independence check.

## What the certificate contains

`axiom.sunit.hunt.solve(S)` returns plain JSON data:

- `S`, `version`, `kind`;
- `height_bound`: the formula, source, outward-rounded `B`, logarithms, and
  per-prime exponent bounds;
- one block per `q in S`: the congruence modulus, discrete logarithms, an
  affine coset representative, the homogeneous lattice basis, the LLL-reduced
  basis and unimodular transform, the exponent box and shard interval, the
  number of vectors tested, and the solutions found;
- the merged solution list, count, and completeness flag.

`axiom.sunit.check` recomputes the bound, the discrete logarithms, the
lattice index, the coset congruence, the LLL conditions, and re-enumerates the
entire exponent box with its own arithmetic.  It shares no code with the
solver.

## Status words and honesty

- `VALIDATED`: the independent checker accepted the certificate and the
  solution list matches the published list exactly (count and canonical
  SHA-256).  This is a reproduction, not a new result.
- `CERTIFIED`: the independent checker accepted a complete certificate but
  there is no exact published-list anchor in this repository.  It is a
  finite computation, independently re-checked.
- The Lean export checks each listed triple (`a+b=c`, coprimality, explicit
  factorisations into primes of `S`).  Completeness of the list is **not**
  formalized in Lean.  The Lean file is labelled accordingly.
- None of this proves or disproves the abc conjecture.  It is a complete
  solution of one finite S-unit equation for a fixed small `S`.

## Swarm

`swarm/queue.json` contains `sunit_2_3_5` with one exponent-box shard per
prime.  Workers write untrusted certificate blocks under
`results/sunit_2_3_5/shards/`; merge tiles the shards, runs the independent
checker, writes `certificate.json`, `status.json`, and the Lean export, then
deletes the shards.  A missing or conflicting shard is carried over, not
accepted.
