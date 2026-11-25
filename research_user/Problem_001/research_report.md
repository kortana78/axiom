# AXIOM 0.2 research record: Problem_001

## Original statement (as given, nothing withheld from the record)
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

- domain: number_theory
- target mode: prove
- target: `forall n >= 0: 6 | (n^3 + (-1 * n))`
- target status after run: **derived**
- time: 0.1 s (stopped_by_controller)
- statement counts: {'derived': 3, 'conjectured': 2}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 0']
- terms_to_study: ['(n^3 + (-1 * n))']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: [6]
- discovered_moduli: [2, 3]
- discovered_offsets: [2]

## Established results (kernel checked)
- `forall n >= 0: 6 | (n^3 + (-1 * n))` — rule `residue_divisibility`, origin: proof of invented conjecture
- `forall n in [0, 100]: 6 | (n^3 + (-1 * n))` — rule `finite_check`, origin: bounded verification up to 100
- `forall k >= 0: 6 | (((2 * k) + 0)^3 + (-1 * ((2 * k) + 0)))` — rule `residue_divisibility`, origin: class 0 mod 2

## Proof of the target
```
[residue_divisibility] forall n >= 0: 6 | (n^3 + (-1 * n))  {'kernel': 'f(n) = f(n mod 6) mod 6, all residues checked'}
```

## Proof attempts
- total attempts: 1; successful: 1
- conjecture_proof budget 200: accepted | `forall n >= 0: 6 | (n^3 + (-1 * n))`

## Lean
- exported theorems: 2; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.03s  invention              gcd of values              conjectured  forall n >= 0: 6 | (n^3 + (-1 * n))
   0.04s  invention              prime power part of gcd    conjectured  forall n >= 0: 2 | (n^3 + (-1 * n))
   0.06s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (n^3 + (-1 * n))
   0.08s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 6 | (n^3 + (-1 * n))
   0.09s  kernel                 accepted                   derived      finite_check: forall n in [0, 100]: 6 | (n^3 + (-1 * n))
   0.12s  kernel                 accepted                   derived      residue_divisibility: forall k >= 0: 6 | (((2 * k) + 0)^3 + (-1 * ((2 * k) + 0)))
```