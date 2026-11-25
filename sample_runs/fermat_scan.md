# AXIOM research record: For which p does p | n^p - n always hold?

- problem id: fermat_scan
- mathematical status before run: theorem
- time used: 2.02 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 1, 'derived': 10}
- withheld from the system (for rediscovery scoring): ["Fermat's little theorem"]

## Established results (kernel checked)
- `forall n >= 0: 2 | (n^2 - n)`
  - rule: residue_divisibility; origin: instance p = 2 of the generalisation
- `forall n >= 0: 3 | (n^3 - n)`
  - rule: residue_divisibility; origin: instance p = 3 of the generalisation
- `forall n >= 0: 5 | (n^5 - n)`
  - rule: residue_divisibility; origin: instance p = 5 of the generalisation
- `forall n >= 0: 7 | (n^7 - n)`
  - rule: residue_divisibility; origin: instance p = 7 of the generalisation
- `forall n >= 0: 11 | (n^11 - n)`
  - rule: residue_divisibility; origin: instance p = 11 of the generalisation
- `forall n >= 0: 13 | (n^13 - n)`
  - rule: residue_divisibility; origin: instance p = 13 of the generalisation
- `forall n >= 0: 17 | (n^17 - n)`
  - rule: residue_divisibility; origin: instance p = 17 of the generalisation
- `forall n >= 0: 19 | (n^19 - n)`
  - rule: residue_divisibility; origin: instance p = 19 of the generalisation
- `forall n >= 0: 23 | (n^23 - n)`
  - rule: residue_divisibility; origin: instance p = 23 of the generalisation
- `forall n >= 0: 29 | (n^29 - n)`
  - rule: residue_divisibility; origin: instance p = 29 of the generalisation

## undecided_within_budget
- `forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))` (controller) general case needs a rule beyond residue checking; instances proved

## Lean
- exported theorems: 10; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.00s  invention              parameter scan             conjectured  forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
   0.00s  generalization         parameter scan             conjectured  holds exactly for p in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
   0.00s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 2 | (n^2 - n)
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 3 | (n^3 - n)
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 5 | (n^5 - n)
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 7 | (n^7 - n)
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 11 | (n^11 - n)
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 13 | (n^13 - n)
   0.01s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 17 | (n^17 - n)
   0.02s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 19 | (n^19 - n)
   0.02s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 23 | (n^23 - n)
   0.02s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 29 | (n^29 - n)
   0.02s  prove_conjectures      attempt                    failed       forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
   0.02s  prove_conjectures      attempt                    failed       forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
   0.02s  prove_conjectures      attempt                    failed       forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
   0.02s  prove_conjectures      attempt                    failed       forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
   0.02s  prove_conjectures      attempt                    failed       forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
   0.02s  prove_conjectures      attempt                    failed       forall p >= 2: forall n >= 0: (is_prime(p) -> p | (n^p - n))
```