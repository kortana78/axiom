# AXIOM 0.2 research record: open_quasiperfect

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "open_quasiperfect",
  "domain": "number_theory",
  "formal_statement": "forall n >= 1: not_quasiperfect(n)",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 1: not_quasiperfect(n)`
- target status after run: **undecided_within_budget**
- time: 2.02 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 1, 'derived': 2}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 1']
- terms_to_study: ['n']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: ['not_quasiperfect']
- constants: []
- discovered_moduli: []
- discovered_offsets: [0]

## Established results (kernel checked)
- `forall n in [1, 100]: not_quasiperfect(n)` — rule `finite_check`, origin: bounded verification up to 100
- `forall n in [1, 200]: not_quasiperfect(n)` — rule `finite_check`, origin: bounded verification up to 200

## Findings
- difficulty_scan: {'sampled': 60, 'failing_instances': [], 'diagnosis': 'no small failing instance: obstruction is structural'}

## Strategy mutations applied
- Q1 `difficulty_scan` (round 5): isolate whether the difficulty is a small case or structural
- Q2 `equivalent_statement` (round 5): reformulate by shifting the bound variable or splitting into classes

## Proof attempts
- total attempts: 13; successful: 0
- direct budget 200: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 400: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 800: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 1600: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 3200: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 6400: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 12800: no proof | `forall n >= 1: not_quasiperfect(n)`
- direct budget 25600: no proof | `forall n >= 1: not_quasiperfect(n)`
- equivalent_shift budget 600: no proof | `forall m >= 0: not_quasiperfect((m + 0))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not_quasiperfect((m + 1))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not_quasiperfect((m + 2))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not_quasiperfect((m + 3))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not_quasiperfect((m + 4))`

## Lean
- exported theorems: 0; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.02s  kernel                 accepted                   derived      finite_check: forall n in [1, 100]: not_quasiperfect(n)
   0.03s  kernel                 accepted                   derived      finite_check: forall n in [1, 200]: not_quasiperfect(n)
   0.03s  direct_proof           stop                       undecided    budget ceiling reached
   0.03s  mutation               Q1 difficulty_scan         new_strategy isolate whether the difficulty is a small case or structural
   0.03s  mutation               Q2 equivalent_statement    new_strategy reformulate by shifting the bound variable or splitting into classes
   0.03s  mutation Q1            difficulty                 diagnosed    no small counterexample; obstruction is structural
```