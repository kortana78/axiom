# AXIOM research record: Closed form of 1^5 + ... + n^5

- problem id: sum_fifth
- mathematical status before run: theorem
- time used: 2.04 s (all_strategies_finished)
- statement counts: {'derived': 1}
- withheld from the system (for rediscovery scoring): ['n^2(n+1)^2(2n^2+2n-1)/12']

## Established results (kernel checked)
- `forall n >= 0: Sum[i=1..n](i^5) = (((((1/6) * n^6) + ((1/2) * n^5)) + ((5/12) * n^4)) + ((-1/12) * n^2))`
  - rule: sum_induction; origin: proof of invented conjecture

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.04s  invention              polynomial fit             conjectured  forall n >= 0: Sum[i=1..n](i^5) = (((((1/6) * n^6) + ((1/2) * n^5)) + ((5/12) * n^4)) + ((-1/12) * n^2))
   0.04s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=1..n](i^5) = (((((1/6) * n^6) + ((1/2) * n^5)) + ((5/12) * n^4)) + ((-1/12) * n^2))
```