# AXIOM 0.2 research record: hidden_sum_cubes

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "hidden_sum_cubes",
  "domain": "number_theory",
  "formal_statement": "forall n >= 0: Sum[i=1..n](i^3) = (n*(n+1)/2)^2",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 0: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)`
- target status after run: **derived**
- time: 1.95 s (stopped_by_controller)
- statement counts: {'derived': 3}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 0']
- terms_to_study: []
- sums_to_study: ['Sum[i=1..n](i^3)']
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: []
- discovered_offsets: []

## Established results (kernel checked)
- `forall n >= 0: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)` — rule `sum_induction`, origin: direct proof search
- `forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))` — rule `sum_induction`, origin: proof of invented conjecture
- `forall n in [0, 100]: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)` — rule `finite_check`, origin: bounded verification up to 100

## Proof of the target
```
[sum_induction] forall n >= 0: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)  {'kernel': 'base case and F(n+1) - F(n) = g(n+1)'}
```

## Proof attempts
- total attempts: 2; successful: 2
- conjecture_proof budget 200: accepted | `forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))`
- direct budget 200: accepted | `forall n >= 0: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)`

## Lean
- exported theorems: 1; not yet translatable: 1
- Lean not run.

## Search history (first events)
```
   1.79s  invention              polynomial fit             conjectured  forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))
   1.81s  kernel                 accepted                   derived      sum_induction: forall n >= 1: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))
   1.84s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)
   1.96s  kernel                 accepted                   derived      finite_check: forall n in [0, 100]: Sum[i=1..n](i^3) = (((1/4) * n^2) * (n + 1)^2)
```