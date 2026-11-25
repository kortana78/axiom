# AXIOM 0.2 research record: research_geometric

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "research_geometric",
  "domain": "number_theory",
  "formal_statement": "study Sum[i=0..n](2^i)",
  "definitions": [],
  "assumptions": [],
  "target": "discover"
}
```

- domain: number_theory
- target mode: discover
- target: discover
- target status after run: **None**
- time: 3.2 s (all_strategies_finished)
- statement counts: {'derived': 1}

## Structure discovered from the statement (not supplied)
- bound_variables: []
- terms_to_study: []
- sums_to_study: ['Sum[i=0..n](2^i)']
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: []
- discovered_offsets: []

## Established results (kernel checked)
- `forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)` — rule `sum_induction`, origin: proof of invented conjecture

## Strategy mutations applied
- Q5 `combine_observations` (round 4): combine established divisibilities, closed forms and facts

## Proof attempts
- total attempts: 1; successful: 1
- conjecture_proof budget 200: accepted | `forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)`

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   1.19s  invention              exponential fit            conjectured  forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)
   1.20s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)
   2.73s  mutation               Q5 combine_observations    new_strategy combine established divisibilities, closed forms and facts
```