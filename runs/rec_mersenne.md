# AXIOM research record: c(0)=0, c(n+1) = 2c(n) + 1

- problem id: rec_mersenne
- mathematical status before run: theorem
- time used: 2.48 s (all_strategies_finished)
- statement counts: {'derived': 1}

## Established results (kernel checked)
- `forall n >= 0: c(n) = (2^n + -1)`
  - rule: sequence_closed_form; origin: proof of invented conjecture

## Invented definitions
- Delta_c := (((2 * x) + 1) - x)   (term; first difference often exposes hidden polynomial structure)

## Lean
- exported theorems: 0; not yet translatable: 1
- Lean not run.

## Search history (first events)
```
   0.38s  invention              exponential fit            conjectured  forall n >= 0: c(n) = (2^n + -1)
   0.38s  invention              new definition             defined      Delta_c := (((2 * x) + 1) - x)   (term; first difference often exposes hidden polynomial structure)
   0.48s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: c(n) = (2^n + -1)
```