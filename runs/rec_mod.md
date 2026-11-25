# AXIOM research record: d(0)=1, d(n+1) = d(n)^2 + 3 d(n) + 3: find invariants

- problem id: rec_mod
- mathematical status before run: theorem
- time used: 4.0 s (time_budget_exhausted)
- statement counts: {'derived': 3}

## Established results (kernel checked)
- `forall n >= 0: 2 | (d(n) - 1)`
  - rule: recurrence_mod_invariant; origin: proof of invented conjecture
- `forall n >= 0: 3 | (d(n) - 1)`
  - rule: recurrence_mod_invariant; origin: proof of invented conjecture
- `forall n >= 0: 6 | (d(n) - 1)`
  - rule: recurrence_mod_invariant; origin: proof of invented conjecture

## Invented definitions
- Delta_d := (((x^2 + (3 * x)) + 3) - x)   (term; first difference often exposes hidden polynomial structure)

## Lean
- exported theorems: 0; not yet translatable: 3
- Lean not run.

## Search history (first events)
```
   0.00s  invention              new definition             defined      Delta_d := (((x^2 + (3 * x)) + 3) - x)   (term; first difference often exposes hidden polynomial structure)
   0.49s  invention              modular pattern            conjectured  forall n >= 0: 2 | (d(n) - 1)
   0.59s  invention              modular pattern            conjectured  forall n >= 0: 3 | (d(n) - 1)
   0.69s  invention              modular pattern            conjectured  forall n >= 0: 6 | (d(n) - 1)
   0.71s  kernel                 accepted                   derived      recurrence_mod_invariant: forall n >= 0: 2 | (d(n) - 1)
   2.06s  kernel                 accepted                   derived      recurrence_mod_invariant: forall n >= 0: 3 | (d(n) - 1)
   2.07s  kernel                 accepted                   derived      recurrence_mod_invariant: forall n >= 0: 6 | (d(n) - 1)
```