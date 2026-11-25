# AXIOM research record: Closed form of 1 + 3 + ... + (2n-1)

- problem id: sum_odd
- mathematical status before run: theorem
- time used: 2.1 s (all_strategies_finished)
- statement counts: {'derived': 1}
- withheld from the system (for rediscovery scoring): ['n^2']

## Established results (kernel checked)
- `forall n >= 0: Sum[i=1..n](((2 * i) + -1)) = n^2`
  - rule: sum_induction; origin: proof of invented conjecture

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.09s  invention              polynomial fit             conjectured  forall n >= 0: Sum[i=1..n](((2 * i) + -1)) = n^2
   0.10s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=1..n](((2 * i) + -1)) = n^2
```