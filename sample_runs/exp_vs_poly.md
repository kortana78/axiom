# AXIOM research record: When does n^2 <= 2^n and n^3 <= 3^n hold?

- problem id: exp_vs_poly
- mathematical status before run: theorem
- time used: 2.02 s (all_strategies_finished)
- statement counts: {'derived': 3}

## Established results (kernel checked)
- `forall n >= 4: n^2 <= 2^n`
  - rule: exp_induction; origin: proof of invented conjecture
- `forall n >= 0: n^3 <= 3^n`
  - rule: range_split; origin: proof of invented conjecture
- `forall n >= 16: n^4 <= 2^n`
  - rule: exp_induction; origin: proof of invented conjecture

## Lean
- exported theorems: 0; not yet translatable: 3
- Lean not run.

## Search history (first events)
```
   0.00s  invention              threshold scan             conjectured  forall n >= 4: n^2 <= 2^n
   0.00s  kernel                 accepted                   derived      exp_induction: forall n >= 4: n^2 <= 2^n
   0.01s  invention              threshold scan             conjectured  forall n >= 0: n^3 <= 3^n
   0.01s  invention              threshold scan             conjectured  forall n >= 16: n^4 <= 2^n
   0.02s  kernel                 accepted                   derived      range_split: forall n >= 0: n^3 <= 3^n
   0.02s  kernel                 accepted                   derived      exp_induction: forall n >= 16: n^4 <= 2^n
```