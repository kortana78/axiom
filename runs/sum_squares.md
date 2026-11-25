# AXIOM research record: Closed form of 1^2 + ... + n^2

- problem id: sum_squares
- mathematical status before run: theorem
- time used: 2.14 s (all_strategies_finished)
- statement counts: {'derived': 1}
- withheld from the system (for rediscovery scoring): ['n(n+1)(2n+1)/6']

## Established results (kernel checked)
- `forall n >= 0: Sum[i=1..n]((i * i)) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))`
  - rule: sum_induction; origin: proof of invented conjecture

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.12s  invention              polynomial fit             conjectured  forall n >= 0: Sum[i=1..n]((i * i)) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))
   0.14s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=1..n]((i * i)) = ((((1/3) * n^3) + ((1/2) * n^2)) + ((1/6) * n))
```