# AXIOM research record: Closed form of 1^3 + ... + n^3

- problem id: sum_cubes
- mathematical status before run: theorem
- time used: 2.03 s (all_strategies_finished)
- statement counts: {'derived': 1}
- withheld from the system (for rediscovery scoring): ['(n(n+1)/2)^2']

## Established results (kernel checked)
- `forall n >= 0: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))`
  - rule: sum_induction; origin: proof of invented conjecture

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.03s  invention              polynomial fit             conjectured  forall n >= 0: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))
   0.03s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=1..n](i^3) = ((((1/4) * n^4) + ((1/2) * n^3)) + ((1/4) * n^2))
```