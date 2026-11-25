# AXIOM 0.2 research record: hidden_exp_threshold

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "hidden_exp_threshold",
  "domain": "number_theory",
  "formal_statement": "forall n >= 16: n^4 <= 2^n",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 16: n^4 <= 2^n`
- target status after run: **derived**
- time: 0.88 s (stopped_by_controller)
- statement counts: {'derived': 2}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 16']
- terms_to_study: ['n^4', '2^n']
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: ['n^4 <= 2^n']
- predicates: []
- constants: []
- discovered_moduli: [2, 4, 8, 16, 32, 64]
- discovered_offsets: [0, 1]

## Established results (kernel checked)
- `forall n >= 16: n^4 <= 2^n` — rule `exp_induction`, origin: direct proof search
- `forall n in [16, 100]: n^4 <= 2^n` — rule `finite_check`, origin: bounded verification up to 100

## Proof of the target
```
[exp_induction] forall n >= 16: n^4 <= 2^n  {'kernel': 'a^(n+1) = a*a^n >= a*p(n) >= p(n+1)'}
```

## Proof attempts
- total attempts: 1; successful: 1
- direct budget 200: accepted | `forall n >= 16: n^4 <= 2^n`

## Lean
- exported theorems: 0; not yet translatable: 1
- Lean not run.

## Search history (first events)
```
   0.05s  kernel                 accepted                   derived      exp_induction: forall n >= 16: n^4 <= 2^n
   0.05s  kernel                 accepted                   derived      finite_check: forall n in [16, 100]: n^4 <= 2^n
```