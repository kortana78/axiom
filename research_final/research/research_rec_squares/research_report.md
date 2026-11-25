# AXIOM 0.2 research record: research_rec_squares

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "research_rec_squares",
  "domain": "number_theory",
  "formal_statement": "",
  "definitions": [
    "a(0) = 0; a(n+1) = a(n) + 2*n + 1"
  ],
  "assumptions": [],
  "target": "discover"
}
```

- domain: number_theory
- target mode: discover
- target: discover
- target status after run: **None**
- time: 4.25 s (all_strategies_finished)
- statement counts: {'derived': 7}

## Structure discovered from the statement (not supplied)
- bound_variables: []
- terms_to_study: []
- sums_to_study: []
- sequences_to_study: ['a: a(0)=0, a(n+1) = (((2 * n) + x) + 1) [x=a(n)]']
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: []
- discovered_offsets: []

## Established results (kernel checked)
- `forall n >= 0: a(n) = n^2` — rule `sequence_closed_form`, origin: proof of invented conjecture
- `forall n >= 0: (n^2 + (-1 * a(n))) = 0` — rule `recurrence_invariant`, origin: invariant synthesis
- `forall n >= 0: a_plus_-2(n) = (n^2 + -2)` — rule `sequence_closed_form`, origin: proof of invented conjecture
- `forall n >= 0: a_plus_-1(n) = (n^2 + -1)` — rule `sequence_closed_form`, origin: proof of invented conjecture
- `forall n >= 0: a_plus_1(n) = (n^2 + 1)` — rule `sequence_closed_form`, origin: proof of invented conjecture
- `forall n >= 0: ((n^2 + (-1 * a(n))) = 0 and a(n) = n^2)` — rule `forall_and`, origin: mutation Q5: conjunction of observations
- `forall n >= 0: a_plus_2(n) = (n^2 + 2)` — rule `sequence_closed_form`, origin: proof of invented conjecture

## Invented definitions
- Delta_a := ((((2 * n) + x) + 1) - x)   (term; first difference often exposes hidden polynomial structure)
- a_plus_-2 := a_plus_-2: a_plus_-2(0)=-2, a_plus_-2(n+1) = ((((2 * n) + (x - -2)) + 1) + -2) [x=a_plus_-2(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
- a_plus_-1 := a_plus_-1: a_plus_-1(0)=-1, a_plus_-1(n+1) = ((((2 * n) + (x - -1)) + 1) + -1) [x=a_plus_-1(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
- a_plus_1 := a_plus_1: a_plus_1(0)=1, a_plus_1(n+1) = ((((2 * n) + (x - 1)) + 1) + 1) [x=a_plus_1(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
- a_plus_2 := a_plus_2: a_plus_2(0)=2, a_plus_2(n+1) = ((((2 * n) + (x - 2)) + 1) + 2) [x=a_plus_2(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)

## Strategy mutations applied
- Q3 `new_object` (round 4): introduce shifted sequences and prime-power objects from discovered data
- Q5 `combine_observations` (round 4): combine established divisibilities, closed forms and facts

## Proof attempts
- total attempts: 5; successful: 5
- conjecture_proof budget 200: accepted | `forall n >= 0: a(n) = n^2`
- conjecture_proof budget 400: accepted | `forall n >= 0: a_plus_-2(n) = (n^2 + -2)`
- conjecture_proof budget 400: accepted | `forall n >= 0: a_plus_-1(n) = (n^2 + -1)`
- conjecture_proof budget 400: accepted | `forall n >= 0: a_plus_1(n) = (n^2 + 1)`
- conjecture_proof budget 800: accepted | `forall n >= 0: a_plus_2(n) = (n^2 + 2)`

## Lean
- exported theorems: 0; not yet translatable: 7
- Lean not run.

## Search history (first events)
```
   0.06s  invention              polynomial fit             conjectured  forall n >= 0: a(n) = n^2
   0.06s  invention              new definition             defined      Delta_a := ((((2 * n) + x) + 1) - x)   (term; first difference often exposes hidden polynomial structure)
   0.15s  kernel                 accepted                   derived      recurrence_invariant: forall n >= 0: (n^2 + (-1 * a(n))) = 0
   0.18s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: a(n) = n^2
   0.35s  mutation               Q3 new_object              new_strategy introduce shifted sequences and prime-power objects from discovered data
   0.35s  mutation               Q5 combine_observations    new_strategy combine established divisibilities, closed forms and facts
   0.35s  invention              new definition             defined      a_plus_-2 := a_plus_-2: a_plus_-2(0)=-2, a_plus_-2(n+1) = ((((2 * n) + (x - -2)) + 1) + -2) [x=a_plus_-2(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
   0.39s  invention              polynomial fit             conjectured  forall n >= 0: a_plus_-2(n) = (n^2 + -2)
   0.39s  invention              new definition             defined      a_plus_-1 := a_plus_-1: a_plus_-1(0)=-1, a_plus_-1(n+1) = ((((2 * n) + (x - -1)) + 1) + -1) [x=a_plus_-1(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
   0.45s  invention              polynomial fit             conjectured  forall n >= 0: a_plus_-1(n) = (n^2 + -1)
   0.45s  invention              new definition             defined      a_plus_1 := a_plus_1: a_plus_1(0)=1, a_plus_1(n+1) = ((((2 * n) + (x - 1)) + 1) + 1) [x=a_plus_1(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
   0.51s  invention              polynomial fit             conjectured  forall n >= 0: a_plus_1(n) = (n^2 + 1)
   0.53s  kernel                 accepted                   derived      forall_and: forall n >= 0: ((n^2 + (-1 * a(n))) = 0 and a(n) = n^2)
   1.73s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: a_plus_-2(n) = (n^2 + -2)
   1.74s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: a_plus_-1(n) = (n^2 + -1)
   1.75s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: a_plus_1(n) = (n^2 + 1)
   1.75s  invention              new definition             defined      a_plus_2 := a_plus_2: a_plus_2(0)=2, a_plus_2(n+1) = ((((2 * n) + (x - 2)) + 1) + 2) [x=a_plus_2(n)]   (sequence; mutation Q3: shifted copy of a discovered sequence)
   1.80s  invention              polynomial fit             conjectured  forall n >= 0: a_plus_2(n) = (n^2 + 2)
   2.25s  kernel                 accepted                   derived      sequence_closed_form: forall n >= 0: a_plus_2(n) = (n^2 + 2)
```