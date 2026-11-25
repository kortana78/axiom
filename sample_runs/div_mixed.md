# AXIOM research record: Find divisors of n(n+1)(n+2)(n+3) and n^4 + 2n^3 + 11n^2 + 10n

- problem id: div_mixed
- mathematical status before run: theorem
- time used: 2.02 s (all_strategies_finished)
- statement counts: {'derived': 6}

## Established results (kernel checked)
- `forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 24 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 8 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 3 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture

## Lean
- exported theorems: 6; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.00s  invention              gcd of values              conjectured  forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.00s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 24 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.01s  invention              gcd of values              conjectured  forall n >= 0: 24 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))
   0.01s  invention              prime power part of gcd    conjectured  forall n >= 0: 8 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))
   0.01s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 8 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 3 | (((n * (n + 1)) * (n + 2)) * (n + 3))
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 24 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))
   0.02s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 8 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))
   0.02s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 3 | (((n^4 + (2 * n^3)) + (11 * n^2)) + (10 * n))
```