# AXIOM research record: Erdos-Straus: 4/n = 1/x + 1/y + 1/z for every n >= 2

- problem id: erdos_straus
- mathematical status before run: open
- target: `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (4 / n) = (((1 / x) + (1 / y)) + (1 / z))`
- target status after run: **undecided_within_budget**
- time used: 37.26 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 1, 'derived': 835}
- notes: Polynomial identities cannot cover square residue classes (Mordell); expect those to stay open.

## Findings
- es_modulus: 840
- es_covered: 832 items: [0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40] ...
- es_uncovered: [1, 121, 169, 241, 289, 361, 409, 529]
- es_example_families: {'n = 840k + 0': 'x = 210*k + 1, y = 176400*k**2 + 840*k, z = 58800*k**2 + 280*k (k >= 1)', 'n = 840k + 2': 'x = 210*k + 1, y = 176400*k**2 + 1260*k + 2, z = 176400*k**2 + 1260*k + 2 (k >= 0)', 'n = 840k + 3': 'x = 210*k + 1, y = 176400*k**2 + 1470*k + 4, z = 31116960000*k**4 + 518616000*k**3 + 3395700*k**2 + 10290*k + 12 (k >= 0)', 'n = 840k + 4': 'x = 210*k + 2, y = 88200*k**2 + 1260*k + 4, z = 88200*k**2 + 1260*k + 4 (k >= 0)', 'n = 840k + 5': 'x = 210*k + 2, y = 176400*k**2 + 2730*k + 10, z = 88200*k**2 + 1365*k + 5 (k >= 0)', 'n = 840k + 6': 'x = 210*k + 2, y = 176400*k**2 + 2940*k + 12, z = 176400*k**2 + 2940*k + 12 (k >= 0)'}

## Established results (kernel checked)
- `forall n in [2, 100]: es_rep(n)`
  - rule: finite_check; origin: bounded verification up to 100
- `forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 0)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 0
- `forall n in [2, 1000]: es_rep(n)`
  - rule: finite_check; origin: bounded verification up to 1000
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 2)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 2
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 3)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 3
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 4)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 4
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 5)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 5
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 6)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 6
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 7)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 7
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 8)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 8
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 9)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 9
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 10)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 10
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 11)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 11
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 12)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 12
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 13)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 13
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 14)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 14
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 15)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 15
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 16)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 16
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 17)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 17
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 18)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 18
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 19)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 19
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 20)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 20
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 21)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 21
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 22)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 22
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 23)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 23
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 24)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 24
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 25)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 25
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 26)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 26
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 27)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 27
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 28)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 28
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 29)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 29
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 30)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 30
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 31)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 31
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 32)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 32
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 33)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 33
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 34)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 34
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 35)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 35
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 36)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 36
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 37)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 37
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 38)) = (((1 / x) + (1 / y)) + (1 / z))`
  - rule: forall_exists_witness; origin: representation search: polynomial family for n = 840k + 38
- ... 795 more (see JSON)

## undecided_within_budget
- `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (4 / n) = (((1 / x) + (1 / y)) + (1 / z))` (controller) search ended without proof or counterexample; this is NOT a refutation; verified for all cases up to 3000

## Recorded failures (kept on purpose)
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 529`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 409`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 361`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 289`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 241`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 169`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 121`
- es_family: no integer-polynomial family within search bounds | goal `n = 840k + 1`

## Lean
- exported theorems: 0; not yet translatable: 832
- Lean not run.

## Search history (first events)
```
   4.64s  direct_proof           search                     failed       budget 100
   4.64s  kernel                 accepted                   derived      finite_check: forall n in [2, 100]: es_rep(n)
   4.66s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 0)) = (((1 / x) + (1 / y)) + (1 / z))
   4.66s  direct_proof           search                     failed       budget 200
   4.67s  direct_proof           search                     failed       budget 400
   5.19s  kernel                 accepted                   derived      finite_check: forall n in [2, 1000]: es_rep(n)
   5.21s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 2)) = (((1 / x) + (1 / y)) + (1 / z))
   5.23s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 3)) = (((1 / x) + (1 / y)) + (1 / z))
   5.24s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 4)) = (((1 / x) + (1 / y)) + (1 / z))
   5.25s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 5)) = (((1 / x) + (1 / y)) + (1 / z))
   5.27s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 6)) = (((1 / x) + (1 / y)) + (1 / z))
   5.29s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 7)) = (((1 / x) + (1 / y)) + (1 / z))
   5.30s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 8)) = (((1 / x) + (1 / y)) + (1 / z))
   5.32s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 9)) = (((1 / x) + (1 / y)) + (1 / z))
   5.33s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 10)) = (((1 / x) + (1 / y)) + (1 / z))
   5.35s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 11)) = (((1 / x) + (1 / y)) + (1 / z))
   5.36s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 12)) = (((1 / x) + (1 / y)) + (1 / z))
   5.38s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 13)) = (((1 / x) + (1 / y)) + (1 / z))
   5.39s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 14)) = (((1 / x) + (1 / y)) + (1 / z))
   5.41s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 15)) = (((1 / x) + (1 / y)) + (1 / z))
   5.43s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 16)) = (((1 / x) + (1 / y)) + (1 / z))
   5.45s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 17)) = (((1 / x) + (1 / y)) + (1 / z))
   5.46s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 18)) = (((1 / x) + (1 / y)) + (1 / z))
   5.49s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 19)) = (((1 / x) + (1 / y)) + (1 / z))
   5.50s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 20)) = (((1 / x) + (1 / y)) + (1 / z))
   5.51s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 21)) = (((1 / x) + (1 / y)) + (1 / z))
   5.52s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 22)) = (((1 / x) + (1 / y)) + (1 / z))
   5.55s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 23)) = (((1 / x) + (1 / y)) + (1 / z))
   5.56s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 24)) = (((1 / x) + (1 / y)) + (1 / z))
   5.58s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 25)) = (((1 / x) + (1 / y)) + (1 / z))
   5.59s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 26)) = (((1 / x) + (1 / y)) + (1 / z))
   5.62s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 27)) = (((1 / x) + (1 / y)) + (1 / z))
   5.63s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 28)) = (((1 / x) + (1 / y)) + (1 / z))
   5.64s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 29)) = (((1 / x) + (1 / y)) + (1 / z))
   5.65s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 30)) = (((1 / x) + (1 / y)) + (1 / z))
   5.68s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 31)) = (((1 / x) + (1 / y)) + (1 / z))
   5.69s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 32)) = (((1 / x) + (1 / y)) + (1 / z))
   5.72s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 33)) = (((1 / x) + (1 / y)) + (1 / z))
   5.73s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 34)) = (((1 / x) + (1 / y)) + (1 / z))
   5.77s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 35)) = (((1 / x) + (1 / y)) + (1 / z))
   5.79s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 36)) = (((1 / x) + (1 / y)) + (1 / z))
   5.81s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 37)) = (((1 / x) + (1 / y)) + (1 / z))
   5.82s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 38)) = (((1 / x) + (1 / y)) + (1 / z))
   5.84s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 39)) = (((1 / x) + (1 / y)) + (1 / z))
   5.86s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 40)) = (((1 / x) + (1 / y)) + (1 / z))
   5.87s  direct_proof           search                     failed       budget 800
   5.92s  direct_proof           search                     failed       budget 1600
   5.98s  direct_proof           search                     failed       budget 3200
  20.86s  kernel                 accepted                   derived      finite_check: forall n in [2, 3000]: es_rep(n)
  20.87s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 41)) = (((1 / x) + (1 / y)) + (1 / z))
  20.88s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 42)) = (((1 / x) + (1 / y)) + (1 / z))
  20.90s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 43)) = (((1 / x) + (1 / y)) + (1 / z))
  20.92s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 44)) = (((1 / x) + (1 / y)) + (1 / z))
  20.94s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 45)) = (((1 / x) + (1 / y)) + (1 / z))
  20.95s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 46)) = (((1 / x) + (1 / y)) + (1 / z))
  20.99s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 47)) = (((1 / x) + (1 / y)) + (1 / z))
  21.01s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 48)) = (((1 / x) + (1 / y)) + (1 / z))
  21.03s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 49)) = (((1 / x) + (1 / y)) + (1 / z))
  21.04s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 50)) = (((1 / x) + (1 / y)) + (1 / z))
  21.07s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (4 / ((840 * k) + 51)) = (((1 / x) + (1 / y)) + (1 / z))
... 786 more events
```