# AXIOM research record: d(0)=1, d(n+1) = d(n)^2 + 3 d(n) + 3: find invariants

- problem id: rec_mod
- mathematical status before run: theorem
- time used: 2.27 s (all_strategies_finished)
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
   0.04s  invention              modular pattern            conjectured  forall n >= 0: 2 | (d(n) - 1)
   0.05s  invention              modular pattern            conjectured  forall n >= 0: 3 | (d(n) - 1)
   0.07s  invention              modular pattern            conjectured  forall n >= 0: 6 | (d(n) - 1)
   0.07s  kernel                 accepted                   derived      recurrence_mod_invariant: forall n >= 0: 2 | (d(n) - 1)
   0.27s  kernel                 accepted                   derived      recurrence_mod_invariant: forall n >= 0: 3 | (d(n) - 1)
   0.27s  kernel                 accepted                   derived      recurrence_mod_invariant: forall n >= 0: 6 | (d(n) - 1)
```