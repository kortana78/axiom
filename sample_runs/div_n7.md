# AXIOM research record: Find and prove the best constant divisor of n^7 - n

- problem id: div_n7
- mathematical status before run: theorem
- time used: 2.01 s (all_strategies_finished)
- statement counts: {'derived': 7}
- withheld from the system (for rediscovery scoring): ['42 | n^7 - n']

## Established results (kernel checked)
- `forall n >= 0: 42 | (n^7 + (-1 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 2 | (n^7 + (-1 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 3 | (n^7 + (-1 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 7 | (n^7 + (-1 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n >= 0: 6 | (n^7 + (-1 * n))`
  - rule: divisibility_combine; origin: forward: combine coprime divisors
- `forall n >= 0: 14 | (n^7 + (-1 * n))`
  - rule: divisibility_combine; origin: forward: combine coprime divisors
- `forall n >= 0: 21 | (n^7 + (-1 * n))`
  - rule: divisibility_combine; origin: forward: combine coprime divisors

## Lean
- exported theorems: 4; not yet translatable: 3
- Lean not run.

## Search history (first events)
```
   0.00s  invention              gcd of values              conjectured  forall n >= 0: 42 | (n^7 + (-1 * n))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 2 | (n^7 + (-1 * n))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (n^7 + (-1 * n))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 7 | (n^7 + (-1 * n))
   0.00s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 42 | (n^7 + (-1 * n))
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 2 | (n^7 + (-1 * n))
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 3 | (n^7 + (-1 * n))
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 7 | (n^7 + (-1 * n))
   0.01s  kernel                 accepted                   derived      divisibility_combine: forall n >= 0: 6 | (n^7 + (-1 * n))
   0.01s  kernel                 accepted                   derived      divisibility_combine: forall n >= 0: 14 | (n^7 + (-1 * n))
   0.01s  kernel                 accepted                   derived      divisibility_combine: forall n >= 0: 21 | (n^7 + (-1 * n))
```