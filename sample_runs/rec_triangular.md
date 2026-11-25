# AXIOM research record: b(0)=0, b(n+1) = b(n) + n

- problem id: rec_triangular
- mathematical status before run: theorem
- time used: 2.03 s (all_strategies_finished)
- statement counts: {'derived': 2}

## Established results (kernel checked)
- `forall n >= 0: ((n^2 + (-1 * n)) + (-2 * b(n))) = 0`
  - rule: recurrence_invariant; origin: invariant synthesis
- `forall n >= 0: b(n) = (((1/2) * n^2) + ((-1/2) * n))`
  - rule: sequence_closed_form; origin: proof of invented conjecture

## Invented definitions
- Delta_b := ((n + x) - x)   (term; first difference often exposes hidden polynomial structure)

## Lean
- exported theorems: 0; not yet translatable: 2
- Lean not run.

## Search history (first events)
```
   0.01s  invention              polynomial fit             conjectured  forall n >= 0: b(n) = (((1/2) * n^2) + ((-1/2) * n))
   0.01s  invention              new definition             defined      Delta_b := ((n + x) - x)   (term; first difference often exposes hidden polynomial structure)
   0.02s  kernel                 accepted                   derived      recurrence_invariant: forall n >= 0: ((n^2 + (-1 * n)) + (-2 * b(n))) = 0
   0.03s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: b(n) = (((1/2) * n^2) + ((-1/2) * n))
```