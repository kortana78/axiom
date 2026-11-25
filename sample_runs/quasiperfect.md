# AXIOM research record: No n has sigma(n) = 2n + 1

- problem id: quasiperfect
- mathematical status before run: open
- target: `forall n >= 1: not_quasiperfect(n)`
- target status after run: **undecided_within_budget**
- time used: 2.42 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 2, 'derived': 4}

## Established results (kernel checked)
- `forall n in [1, 100]: not_quasiperfect(n)`
  - rule: finite_check; origin: bounded verification up to 100
- `forall n in [1, 1000]: not_quasiperfect(n)`
  - rule: finite_check; origin: bounded verification up to 1000
- `forall n in [1, 10000]: not_quasiperfect(n)`
  - rule: finite_check; origin: bounded verification up to 10000
- `forall n in [1, 20000]: not_quasiperfect(n)`
  - rule: finite_check; origin: bounded verification up to 20000

## undecided_within_budget
- `forall n >= 1: not_quasiperfect(n)` (controller) search ended without proof or counterexample; this is NOT a refutation; verified for all cases up to 20000
- `forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))` (controller) proof budget exhausted

## Lean
- exported theorems: 0; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.02s  invention              pattern miner              conjectured  forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.02s  prove_conjectures      attempt                    failed       forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.02s  direct_proof           search                     failed       budget 100
   0.02s  kernel                 accepted                   derived      finite_check: forall n in [1, 100]: not_quasiperfect(n)
   0.04s  prove_conjectures      attempt                    failed       forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.05s  prove_conjectures      attempt                    failed       forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.05s  prove_conjectures      attempt                    failed       forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.06s  direct_proof           search                     failed       budget 200
   0.07s  direct_proof           search                     failed       budget 400
   0.07s  kernel                 accepted                   derived      finite_check: forall n in [1, 1000]: not_quasiperfect(n)
   0.09s  prove_conjectures      attempt                    failed       forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.10s  prove_conjectures      attempt                    failed       forall n >= 1: (sigma_odd(n) -> square_or_twice_square(n))
   0.12s  direct_proof           search                     failed       budget 800
   0.15s  direct_proof           search                     failed       budget 1600
   0.18s  direct_proof           search                     failed       budget 3200
   0.23s  kernel                 accepted                   derived      finite_check: forall n in [1, 10000]: not_quasiperfect(n)
   0.25s  direct_proof           search                     failed       budget 6400
   0.27s  direct_proof           search                     failed       budget 12800
   0.29s  direct_proof           search                     failed       budget 25600
   0.29s  direct_proof           stop                       undecided    budget ceiling reached
   0.42s  kernel                 accepted                   derived      finite_check: forall n in [1, 20000]: not_quasiperfect(n)
```