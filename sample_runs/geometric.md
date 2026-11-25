# AXIOM research record: Closed form of 1 + 2 + 4 + ... + 2^n

- problem id: geometric
- mathematical status before run: theorem
- time used: 2.24 s (all_strategies_finished)
- statement counts: {'derived': 1}
- withheld from the system (for rediscovery scoring): ['2^(n+1) - 1']

## Established results (kernel checked)
- `forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)`
  - rule: sum_induction; origin: proof of invented conjecture

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.24s  invention              exponential fit            conjectured  forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)
   0.24s  kernel                 accepted                   derived      sum_induction: forall n >= 0: Sum[i=0..n](2^i) = ((2 * 2^n) + -1)
```