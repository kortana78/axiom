# AXIOM 0.2 research record: odd_perfect_open

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "odd_perfect_open",
  "domain": "number_theory",
  "formal_statement": "forall n >= 1: not ((is_odd(n)) and (is_perfect(n)))",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- target status after run: **undecided_within_budget**
- time: 2.08 s (all_strategies_finished)
- statement counts: {'undecided_within_budget': 2, 'derived': 3}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 1']
- terms_to_study: ['n']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: ['is_odd', 'is_perfect']
- constants: []
- discovered_moduli: []
- discovered_offsets: [0]

## Established results (kernel checked)
- `forall n in [1, 100]: not ((is_odd(n) and is_perfect(n)))` — rule `finite_check`, origin: bounded verification up to 100
- `forall n in [1, 1000]: not ((is_odd(n) and is_perfect(n)))` — rule `finite_check`, origin: bounded verification up to 1000
- `forall n in [1, 2000]: not ((is_odd(n) and is_perfect(n)))` — rule `finite_check`, origin: bounded verification up to 2000

## Findings
- difficulty_scan: {'sampled': 60, 'failing_instances': [], 'diagnosis': 'no small failing instance: obstruction is structural'}

## Strategy mutations applied
- Q1 `difficulty_scan` (round 6): isolate whether the difficulty is a small case or structural
- Q2 `equivalent_statement` (round 6): reformulate by shifting the bound variable or splitting into classes

## Proof attempts
- total attempts: 19; successful: 0
- direct budget 200: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- conjecture_proof budget 200: no proof | `forall n >= 1: (is_odd(n) -> is_odd(n))`
- conjecture_proof budget 400: no proof | `forall n >= 1: (is_odd(n) -> is_odd(n))`
- conjecture_proof budget 800: no proof | `forall n >= 1: (is_odd(n) -> is_odd(n))`
- direct budget 400: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- direct budget 800: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- conjecture_proof budget 1600: no proof | `forall n >= 1: (is_odd(n) -> is_odd(n))`
- conjecture_proof budget 3200: no proof | `forall n >= 1: (is_odd(n) -> is_odd(n))`
- conjecture_proof budget 6400: no proof | `forall n >= 1: (is_odd(n) -> is_odd(n))`
- direct budget 1600: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- direct budget 3200: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- direct budget 6400: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- direct budget 12800: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- direct budget 25600: no proof | `forall n >= 1: not ((is_odd(n) and is_perfect(n)))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not ((is_odd((m + 0)) and is_perfect((m + 0))))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not ((is_odd((m + 1)) and is_perfect((m + 1))))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not ((is_odd((m + 2)) and is_perfect((m + 2))))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not ((is_odd((m + 3)) and is_perfect((m + 3))))`
- equivalent_shift budget 600: no proof | `forall m >= 0: not ((is_odd((m + 4)) and is_perfect((m + 4))))`

## Lean
- exported theorems: 0; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.01s  kernel                 accepted                   derived      finite_check: forall n in [1, 100]: not ((is_odd(n) and is_perfect(n)))
   0.02s  invention              pattern miner              conjectured  forall n >= 1: (is_odd(n) -> is_odd(n))
   0.04s  kernel                 accepted                   derived      finite_check: forall n in [1, 1000]: not ((is_odd(n) and is_perfect(n)))
   0.08s  kernel                 accepted                   derived      finite_check: forall n in [1, 2000]: not ((is_odd(n) and is_perfect(n)))
   0.08s  direct_proof           stop                       undecided    budget ceiling reached
   0.09s  mutation               Q1 difficulty_scan         new_strategy isolate whether the difficulty is a small case or structural
   0.09s  mutation               Q2 equivalent_statement    new_strategy reformulate by shifting the bound variable or splitting into classes
   0.09s  mutation Q1            difficulty                 diagnosed    no small counterexample; obstruction is structural
```