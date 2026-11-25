# AXIOM research record: a(0)=0, a(n+1) = a(n) + 2n + 1: find what a(n) is

- problem id: rec_squares
- mathematical status before run: theorem
- time used: 2.11 s (all_strategies_finished)
- statement counts: {'derived': 2}
- withheld from the system (for rediscovery scoring): ['a(n) - n^2 is invariant']

## Established results (kernel checked)
- `forall n >= 0: (n^2 + (-1 * a(n))) = 0`
  - rule: recurrence_invariant; origin: invariant synthesis
- `forall n >= 0: a(n) = n^2`
  - rule: sequence_closed_form; origin: proof of invented conjecture

## Invented definitions
- Delta_a := ((((2 * n) + x) + 1) - x)   (term; first difference often exposes hidden polynomial structure)

## Lean
- exported theorems: 0; not yet translatable: 2
- Lean not run.

## Search history (first events)
```
   0.00s  invention              polynomial fit             conjectured  forall n >= 0: a(n) = n^2
   0.00s  invention              new definition             defined      Delta_a := ((((2 * n) + x) + 1) - x)   (term; first difference often exposes hidden polynomial structure)
   0.03s  kernel                 accepted                   derived      recurrence_invariant: forall n >= 0: (n^2 + (-1 * a(n))) = 0
   0.11s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: a(n) = n^2
```