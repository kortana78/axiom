# AXIOM research record: Legendre: a prime lies between n^2 and (n+1)^2

- problem id: legendre
- mathematical status before run: open
- target: `forall n >= 1: prime_between_squares(n)`
- target status after run: **undecided_within_budget**
- time used: 2.26 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 1, 'derived': 3}

## Established results (kernel checked)
- `forall n in [1, 100]: prime_between_squares(n)`
  - rule: finite_check; origin: bounded verification up to 100
- `forall n in [1, 1000]: prime_between_squares(n)`
  - rule: finite_check; origin: bounded verification up to 1000
- `forall n in [1, 3000]: prime_between_squares(n)`
  - rule: finite_check; origin: bounded verification up to 3000

## undecided_within_budget
- `forall n >= 1: prime_between_squares(n)` (controller) search ended without proof or counterexample; this is NOT a refutation; verified for all cases up to 3000

## Lean
- exported theorems: 0; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.00s  direct_proof           search                     failed       budget 100
   0.00s  kernel                 accepted                   derived      finite_check: forall n in [1, 100]: prime_between_squares(n)
   0.00s  direct_proof           search                     failed       budget 200
   0.01s  direct_proof           search                     failed       budget 400
   0.03s  kernel                 accepted                   derived      finite_check: forall n in [1, 1000]: prime_between_squares(n)
   0.04s  direct_proof           search                     failed       budget 800
   0.07s  direct_proof           search                     failed       budget 1600
   0.11s  direct_proof           search                     failed       budget 3200
   0.26s  kernel                 accepted                   derived      finite_check: forall n in [1, 3000]: prime_between_squares(n)
   0.28s  direct_proof           search                     failed       budget 6400
   0.30s  direct_proof           search                     failed       budget 12800
   0.32s  direct_proof           search                     failed       budget 25600
   0.32s  direct_proof           stop                       undecided    budget ceiling reached
```