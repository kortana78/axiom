# AXIOM 0.2 research record: research_div_n7

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "research_div_n7",
  "domain": "number_theory",
  "formal_statement": "study n^7 - n",
  "definitions": [],
  "assumptions": [],
  "target": "discover"
}
```

- domain: number_theory
- target mode: discover
- target: discover
- target status after run: **None**
- time: 2.2 s (all_strategies_finished)
- statement counts: {'derived': 13}

## Structure discovered from the statement (not supplied)
- bound_variables: []
- terms_to_study: ['(n^7 + (-1 * n))']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: [2, 3, 7]
- discovered_offsets: [3]

## Established results (kernel checked)
- `forall n >= 0: 42 | (n^7 + (-1 * n))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: 2 | (n^7 + (-1 * n))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: 3 | (n^7 + (-1 * n))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: 7 | (n^7 + (-1 * n))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n >= 0: 6 | (n^7 + (-1 * n))` — rule `divisibility_combine`, origin: forward: combine coprime divisors
- `forall n >= 0: 14 | (n^7 + (-1 * n))` — rule `divisibility_combine`, origin: forward: combine coprime divisors
- `forall n >= 0: 21 | (n^7 + (-1 * n))` — rule `divisibility_combine`, origin: forward: combine coprime divisors
- `forall n >= 0: (42 | (n^7 + (-1 * n)) and 2 | (n^7 + (-1 * n)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: (2 | (n^7 + (-1 * n)) and 3 | (n^7 + (-1 * n)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: (3 | (n^7 + (-1 * n)) and 7 | (n^7 + (-1 * n)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: (7 | (n^7 + (-1 * n)) and 6 | (n^7 + (-1 * n)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: (6 | (n^7 + (-1 * n)) and 14 | (n^7 + (-1 * n)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: (14 | (n^7 + (-1 * n)) and 21 | (n^7 + (-1 * n)))` — rule `forall_and`, origin: mutation Q5: conjunction of observations

## Invented definitions
- factor_2^1 := 2   (term; mutation Q3: prime-power part of a discovered divisor)
- factor_3^1 := 3   (term; mutation Q3: prime-power part of a discovered divisor)
- factor_7^1 := 7   (term; mutation Q3: prime-power part of a discovered divisor)

## Strategy mutations applied
- Q3 `new_object` (round 5): introduce shifted sequences and prime-power objects from discovered data
- Q5 `combine_observations` (round 5): combine established divisibilities, closed forms and facts

## Proof attempts
- total attempts: 4; successful: 4
- conjecture_proof budget 200: accepted | `forall n >= 0: 42 | (n^7 + (-1 * n))`
- conjecture_proof budget 200: accepted | `forall n >= 0: 2 | (n^7 + (-1 * n))`
- conjecture_proof budget 200: accepted | `forall n >= 0: 3 | (n^7 + (-1 * n))`
- conjecture_proof budget 200: accepted | `forall n >= 0: 7 | (n^7 + (-1 * n))`

## Lean
- exported theorems: 4; not yet translatable: 9
- Lean not run.

## Search history (first events)
```
   0.00s  invention              gcd of values              conjectured  forall n >= 0: 42 | (n^7 + (-1 * n))
   0.02s  invention              prime power part of gcd    conjectured  forall n >= 0: 2 | (n^7 + (-1 * n))
   0.02s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (n^7 + (-1 * n))
   0.03s  invention              prime power part of gcd    conjectured  forall n >= 0: 7 | (n^7 + (-1 * n))
   0.04s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 42 | (n^7 + (-1 * n))
   0.05s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 2 | (n^7 + (-1 * n))
   0.06s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 3 | (n^7 + (-1 * n))
   0.07s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 7 | (n^7 + (-1 * n))
   0.08s  kernel                 accepted                   derived      divisibility_combine: forall n >= 0: 6 | (n^7 + (-1 * n))
   0.09s  kernel                 accepted                   derived      divisibility_combine: forall n >= 0: 14 | (n^7 + (-1 * n))
   0.10s  kernel                 accepted                   derived      divisibility_combine: forall n >= 0: 21 | (n^7 + (-1 * n))
   0.11s  mutation               Q3 new_object              new_strategy introduce shifted sequences and prime-power objects from discovered data
   0.11s  mutation               Q5 combine_observations    new_strategy combine established divisibilities, closed forms and facts
   0.12s  invention              new definition             defined      factor_2^1 := 2   (term; mutation Q3: prime-power part of a discovered divisor)
   0.12s  invention              new definition             defined      factor_3^1 := 3   (term; mutation Q3: prime-power part of a discovered divisor)
   0.12s  invention              new definition             defined      factor_7^1 := 7   (term; mutation Q3: prime-power part of a discovered divisor)
   0.14s  kernel                 accepted                   derived      forall_and: forall n >= 0: (42 | (n^7 + (-1 * n)) and 2 | (n^7 + (-1 * n)))
   0.14s  kernel                 accepted                   derived      forall_and: forall n >= 0: (2 | (n^7 + (-1 * n)) and 3 | (n^7 + (-1 * n)))
   0.16s  kernel                 accepted                   derived      forall_and: forall n >= 0: (3 | (n^7 + (-1 * n)) and 7 | (n^7 + (-1 * n)))
   0.17s  kernel                 accepted                   derived      forall_and: forall n >= 0: (7 | (n^7 + (-1 * n)) and 6 | (n^7 + (-1 * n)))
   0.18s  kernel                 accepted                   derived      forall_and: forall n >= 0: (6 | (n^7 + (-1 * n)) and 14 | (n^7 + (-1 * n)))
   0.20s  kernel                 accepted                   derived      forall_and: forall n >= 0: (14 | (n^7 + (-1 * n)) and 21 | (n^7 + (-1 * n)))
```