# AXIOM research record: Prove 30 | n^5 - n

- problem id: div_n5
- mathematical status before run: theorem
- target: `forall n >= 0: 30 | (n^5 + (-1 * n))`
- target status after run: **derived**
- time used: 0.0 s (stopped_by_controller)
- statement counts: {'derived': 2, 'conjectured': 3}

## Established results (kernel checked)
- `forall n >= 0: 30 | (n^5 + (-1 * n))`
  - rule: residue_divisibility; origin: proof of invented conjecture
- `forall n in [0, 100]: 30 | (n^5 + (-1 * n))`
  - rule: finite_check; origin: bounded verification up to 100

## conjectured
- `forall n >= 0: 2 | (n^5 + (-1 * n))` (prime power part of gcd) 
- `forall n >= 0: 3 | (n^5 + (-1 * n))` (prime power part of gcd) 
- `forall n >= 0: 5 | (n^5 + (-1 * n))` (prime power part of gcd) 

## Proof of the target
```
[residue_divisibility] forall n >= 0: 30 | (n^5 + (-1 * n))  {'kernel': 'f(n) = f(n mod 30) mod 30, all residues checked'}
```

## Lean
- exported theorems: 1; not yet translatable: 0
- Lean not run.

## Search history (first events)
```
   0.00s  invention              gcd of values              conjectured  forall n >= 0: 30 | (n^5 + (-1 * n))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 2 | (n^5 + (-1 * n))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 3 | (n^5 + (-1 * n))
   0.00s  invention              prime power part of gcd    conjectured  forall n >= 0: 5 | (n^5 + (-1 * n))
   0.00s  kernel                 accepted                   derived      residue_divisibility: forall n >= 0: 30 | (n^5 + (-1 * n))
   0.00s  kernel                 accepted                   derived      finite_check: forall n in [0, 100]: 30 | (n^5 + (-1 * n))
```