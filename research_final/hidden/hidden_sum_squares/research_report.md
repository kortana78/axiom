# AXIOM 0.2 research record: hidden_sum_squares

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "hidden_sum_squares",
  "domain": "number_theory",
  "formal_statement": "forall n >= 0: Sum[i=1..n](i^2) = n*(n+1)*(2*n+1)/6",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 0: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))`
- target status after run: **derived**
- time: 1.87 s (stopped_by_controller)
- statement counts: {'derived': 3}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 0']
- terms_to_study: []
- sums_to_study: ['Sum[i=1..n](i^2)']
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: []
- discovered_offsets: []

## Established results (kernel checked)
- `forall n >= 0: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))` — rule `sum_induction`, origin: direct proof search
- `forall n >= 1: Sum[i=1..n](i^2) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))` — rule `sum_induction`, origin: proof of invented conjecture
- `forall n in [0, 100]: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))` — rule `finite_check`, origin: bounded verification up to 100

## Proof of the target
```
[sum_induction] forall n >= 0: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))  {'kernel': 'base case and F(n+1) - F(n) = g(n+1)'}
```

## Proof attempts
- total attempts: 2; successful: 2
- conjecture_proof budget 200: accepted | `forall n >= 1: Sum[i=1..n](i^2) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))`
- direct budget 200: accepted | `forall n >= 0: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))`

## Lean
- exported theorems: 1; not yet translatable: 1
- Lean not run.

## Search history (first events)
```
   1.74s  invention              polynomial fit             conjectured  forall n >= 1: Sum[i=1..n](i^2) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))
   1.76s  kernel                 accepted                   derived      sum_induction: forall n >= 1: Sum[i=1..n](i^2) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))
   1.77s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))
   1.87s  kernel                 accepted                   derived      finite_check: forall n in [0, 100]: Sum[i=1..n](i^2) = ((((1/6) * n) * (n + 1)) * ((2 * n) + 1))
```