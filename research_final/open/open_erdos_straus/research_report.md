# AXIOM 0.2 research record: open_erdos_straus

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "open_erdos_straus",
  "domain": "number_theory",
  "formal_statement": "forall n >= 2: es_rep(n)",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 2: es_rep(n)`
- target status after run: **undecided_within_budget**
- time: 3.06 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 1, 'derived': 2}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 2']
- terms_to_study: ['n']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: ['es_rep']
- constants: []
- discovered_moduli: []
- discovered_offsets: [1]

## Established results (kernel checked)
- `forall n in [2, 100]: es_rep(n)` — rule `finite_check`, origin: bounded verification up to 100
- `forall n in [2, 200]: es_rep(n)` — rule `finite_check`, origin: bounded verification up to 200

## Findings
- difficulty_scan: {'sampled': 60, 'failing_instances': [], 'diagnosis': 'no small failing instance: obstruction is structural'}

## Strategy mutations applied
- Q1 `difficulty_scan` (round 5): isolate whether the difficulty is a small case or structural
- Q2 `equivalent_statement` (round 5): reformulate by shifting the bound variable or splitting into classes

## Proof attempts
- total attempts: 12; successful: 0
- direct budget 200: no proof | `forall n >= 2: es_rep(n)`
- direct budget 400: no proof | `forall n >= 2: es_rep(n)`
- direct budget 800: no proof | `forall n >= 2: es_rep(n)`
- direct budget 1600: no proof | `forall n >= 2: es_rep(n)`
- direct budget 3200: no proof | `forall n >= 2: es_rep(n)`
- direct budget 6400: no proof | `forall n >= 2: es_rep(n)`
- direct budget 12800: no proof | `forall n >= 2: es_rep(n)`
- direct budget 25600: no proof | `forall n >= 2: es_rep(n)`
- equivalent_shift budget 600: no proof | `forall m >= 0: es_rep((m + 1))`
- equivalent_shift budget 600: no proof | `forall m >= 0: es_rep((m + 2))`
- equivalent_shift budget 600: no proof | `forall m >= 0: es_rep((m + 3))`
- equivalent_shift budget 600: no proof | `forall m >= 0: es_rep((m + 4))`

## Lean
- exported theorems: 0; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.05s  kernel                 accepted                   derived      finite_check: forall n in [2, 100]: es_rep(n)
   1.06s  kernel                 accepted                   derived      finite_check: forall n in [2, 200]: es_rep(n)
   1.07s  direct_proof           stop                       undecided    budget ceiling reached
   1.07s  mutation               Q1 difficulty_scan         new_strategy isolate whether the difficulty is a small case or structural
   1.07s  mutation               Q2 equivalent_statement    new_strategy reformulate by shifting the bound variable or splitting into classes
   1.07s  mutation Q1            difficulty                 diagnosed    no small counterexample; obstruction is structural
```