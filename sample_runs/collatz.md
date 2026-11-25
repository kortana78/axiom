# AXIOM research record: Collatz: every n >= 1 reaches 1

- problem id: collatz
- mathematical status before run: open
- target: `forall n >= 1: collatz_reaches_one(n)`
- target status after run: **undecided_within_budget**
- time used: 3.27 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 1, 'derived': 795}

## Findings
- collatz_k: 16
- collatz_open: 2114
- collatz_open_sample: [27, 32795, 49179, 8219, 40987, 24603, 57371, 4123, 12315, 28699, 61467, 6171, 38939, 55323, 47131, 1051, 33819, 17435, 50203, 9243]

## Established results (kernel checked)
- `forall n in [1, 100]: collatz_reaches_one(n)`
  - rule: finite_check; origin: bounded verification up to 100
- `forall j >= 1: collatz_descends(((2 * j) + 0))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall n in [1, 1000]: collatz_reaches_one(n)`
  - rule: finite_check; origin: bounded verification up to 1000
- `forall j >= 1: collatz_descends(((4 * j) + 1))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((16 * j) + 3))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((32 * j) + 11))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((32 * j) + 23))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((128 * j) + 59))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((128 * j) + 7))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((128 * j) + 15))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 219))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 123))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 199))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 39))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 79))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 175))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((256 * j) + 95))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 923))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 347))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 507))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 583))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 423))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 999))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 975))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 815))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 367))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 287))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 735))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((1024 * j) + 575))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 2587))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 2203))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 1435))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 3675))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 2907))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 1787))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 1019))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 3143))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 3911))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 1703))`
  - rule: collatz_descent; origin: parity-vector descent class
- `forall j >= 1: collatz_descends(((4096 * j) + 935))`
  - rule: collatz_descent; origin: parity-vector descent class
- ... 755 more (see JSON)

## undecided_within_budget
- `forall n >= 1: collatz_reaches_one(n)` (controller) search ended without proof or counterexample; this is NOT a refutation; verified for all cases up to 100000

## Lean
- exported theorems: 0; not yet translatable: 791
- Lean not run.

## Search history (first events)
```
   0.00s  direct_proof           search                     failed       budget 100
   0.00s  kernel                 accepted                   derived      finite_check: forall n in [1, 100]: collatz_reaches_one(n)
   0.03s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((2 * j) + 0))
   0.04s  direct_proof           search                     failed       budget 200
   0.04s  direct_proof           search                     failed       budget 400
   0.05s  kernel                 accepted                   derived      finite_check: forall n in [1, 1000]: collatz_reaches_one(n)
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4 * j) + 1))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((16 * j) + 3))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((32 * j) + 11))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((32 * j) + 23))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((128 * j) + 59))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((128 * j) + 7))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((128 * j) + 15))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 219))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 123))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 199))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 39))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 79))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 175))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((256 * j) + 95))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 923))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 347))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 507))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 583))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 423))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 999))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 975))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 815))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 367))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 287))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 735))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((1024 * j) + 575))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2587))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2203))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1435))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 3675))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2907))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1787))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1019))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 3143))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 3911))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1703))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 935))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 615))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 231))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 3559))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1231))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 463))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 3119))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2351))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1647))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 879))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2031))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2591))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1823))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 2975))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 3295))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 4063))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1087))
   0.05s  kernel                 accepted                   derived      collatz_descent: forall j >= 1: collatz_descends(((4096 * j) + 1855))
... 746 more events
```