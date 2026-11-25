# AXIOM 0.2 research record: research_sum_cubes

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "research_sum_cubes",
  "domain": "number_theory",
  "formal_statement": "study Sum[i=1..n](i^3)",
  "definitions": [],
  "assumptions": [],
  "target": "discover"
}
```

- domain: number_theory
- target mode: discover
- target: discover
- target status after run: **None**
- time: 2.23 s (all_strategies_finished)
- statement counts: {'derived': 1}

## Structure discovered from the statement (not supplied)
- bound_variables: []
- terms_to_study: []
- sums_to_study: ['Sum[i=1..n](i^3)']
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: []
- discovered_offsets: []

## Established results (kernel checked)
- `forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))` — rule `sum_induction`, origin: proof of invented conjecture

## Strategy mutations applied
- Q5 `combine_observations` (round 4): combine established divisibilities, closed forms and facts

## Proof attempts
- total attempts: 1; successful: 1
- conjecture_proof budget 200: accepted | `forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))`

## Lean
- exported theorems: 0; not yet translatable: 1
- Lean not run.

## Search history (first events)
```
   0.21s  invention              polynomial fit             conjectured  forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))
   0.22s  kernel                 accepted                   derived      sum_induction: forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))
   1.96s  mutation               Q5 combine_observations    new_strategy combine established divisibilities, closed forms and facts
```