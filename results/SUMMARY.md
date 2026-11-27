# AXIOM swarm summary

**abc conjecture: OPEN. No result here proves it.**

proof alarm: OPEN — lean/Abc/Proof.lean is absent; abc remains OPEN

updated 2026-11-27 09:38 UTC

## Witness reductions

| problem | status | modulus | open / relevant | families | last note | Lean |
|---|---|---|---|---|---|---|
| erdos_straus | open: reduction certified | 840 | 6 / 196 | 39 | grammar ceiling reached: modulus refined 840 -> 2520 | Lean accepted 39/39 lemmas |
| sierpinski_5n | open: reduction certified | 2520 | 2 / 580 | 24 | progress at current grammar | Lean accepted 24/24 lemmas |

## ABC triple hunter (search only)

| problem | status | c max | best q | records | last note | Lean |
|---|---|---|---|---|---|---|
| abc | search only: 200 verified triples; best q=1.629912; no proof of abc | 100,000,000 | 1.629912 | 200 | best 2 + 6436341 = 6436343 (rad 15042); c_smooth advanced to 349763 | Lean accepted 200/200 lemmas |

## S-unit certificates (finite completeness, not abc)

| problem | status | S | solutions | published | checker | B | Lean |
|---|---|---|---|---|---|---|---|
| sunit_2_3_5 | VALIDATED | [2, 3, 5] | 17 | 17 (hash match) | PASS | 525.089850 | Lean accepted 18/18 lemmas |

## ABC proof track (all targets unproved)

| target | route | status | note |
|---|---|---|---|
| abc_route_szpiro | Szpiro | unproved idea | unproved idea; any candidate argument must be Lean against lean/Abc/Statement.lean, no sorry, no new axioms |
| abc_route_mason_stothers | Mason-Stothers | unproved idea | polynomial analogue only; Mathlib Polynomial.abc; not a route to the integer statement |
| abc_route_stewart_yu | Stewart-Yu | unproved idea | partial result; far weaker than abc; see swarm/abc_routes.md for citations |
| abc_route_iut | IUT | unproved idea | disputed; described neutrally; no IUT claim is used by this repository |

Every reduction family is re-checked by the Axiom kernel at merge time. ABC records are exact integer triples re-checked by the merger; the hunter does not prove the abc conjecture. S-unit certificates are finite complete lists for a fixed S, independently re-checked; they say nothing about abc. The Lean export checks only the listed triples, not completeness. No result here proves the abc conjecture.

- abc: best record 2 + 6436341 = 6436343, rad(abc) = 15042, q = 1.629911684. Search only; no proof.

