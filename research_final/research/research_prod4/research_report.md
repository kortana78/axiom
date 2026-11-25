# AXIOM 0.2 research record: research_prod4

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "research_prod4",
  "domain": "number_theory",
  "formal_statement": "study n*(n+1)*(n+2)*(n+3)",
  "definitions": [],
  "assumptions": [],
  "target": "discover"
}
```

- domain: number_theory
- target mode: discover
- target: discover
- target status after run: **None**
- time: 2.11 s (all_strategies_finished)
- statement counts: {'derived': 5}

## Structure discovered from the statement (not supplied)
- bound_variables: []
- terms_to_study: ['(((n * (n + 1)) * (n + 2)) * (n + 3))']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: [2, 4, 8, 3]
- discovered_offsets: [1]

## Established results (kernel checked)
- `forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: (24 | (((n * (n + 1)) * (n + 2)) * (n + 3)) and 8 | (((n * (n + 1)) * (n + 2)) * (n + 3)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: (8 | (((n * (n + 1)) * (n + 2)) * (n + 3)) and 3 | (((n * (n + 1)) * (n + 2)) * (n + 3)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations

## Invented definitions
- factor_2^3 := 8   (term; mutation Q3: prime-power part of a discovered divisor)
- factor_3^1 := 3   (term; mutation Q3: prime-power part of a discovered divisor)

## Strategy mutations applied
- Q3 `new_object` (round 5): introduce shifted sequences and prime-power objects from discovered data
- Q5 `combine_observations` (round 5): combine established divisibilities, closed forms and facts

## Proof attempts
- total attempts: 3; successful: 3
- conjecture_proof budget 200: accepted | `forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))`
- conjecture_proof budget 200: accepted | `forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))`
- conjecture_proof budget 200: accepted | `forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))`

## Lean
- exported theorems: 3; not yet translatable: 2
- Lean not run.

## Search history (first events)
```
   0.01s  invention              gcd of values              conjectured  forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.02s  invention              prime power part of gcd    conjectured  forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.03s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.04s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.07s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.08s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.09s  mutation               Q3 new_object              new_strategy introduce shifted sequences and prime-power objects from discovered data
   0.09s  mutation               Q5 combine_observations    new_strategy combine established divisibilities, closed forms and facts
   0.09s  invention              new definition             defined      factor_2^3 := 8   (term; mutation Q3: prime-power part of a discovered divisor)
   0.09s  invention              new definition             defined      factor_3^1 := 3   (term; mutation Q3: prime-power part of a discovered divisor)
   0.10s  kernel                 accepted                   derived      forall_and: forall n >= 0: (24 | (((n * (n + 1)) * (n + 2)) * (n + 3)) and 8 | (((n * (n + 1)) * (n + 2)) * (n + 3)))
   0.11s  kernel                 accepted                   derived      forall_and: forall n >= 0: (8 | (((n * (n + 1)) * (n + 2)) * (n + 3)) and 3 | (((n * (n + 1)) * (n + 2)) * (n + 3)))
```