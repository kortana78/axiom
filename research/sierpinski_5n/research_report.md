# AXIOM 0.2 research record: sierpinski_5n

## Original statement (as given, nothing withheld from the record)
```json
{
  "name": "sierpinski_5n",
  "domain": "number_theory",
  "formal_statement": "forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 5/n = 1/x + 1/y + 1/z",
  "definitions": [],
  "assumptions": [],
  "target": "prove"
}
```

- domain: number_theory
- target mode: prove
- target: `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))`
- target status after run: **undecided_within_budget**
- time: 426.81 s (time_budget_exhausted)
- statement counts: {'undecided_within_budget': 1, 'derived': 28}

## Structure discovered from the statement (not supplied)
- bound_variables: ['n >= 2']
- terms_to_study: []
- sums_to_study: []
- sequences_to_study: []
- inequalities_to_study: []
- predicates: []
- constants: []
- discovered_moduli: []
- discovered_offsets: []

## Established results (kernel checked)
- `forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 0)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 0 mod 5
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 3)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 3 mod 5
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 4)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 4 mod 5
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 2)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 2 open classes mod 5
- `(forall q_prime >= 2: ((is_prime(q_prime) and (5 | (q_prime - 1) or 5 | (q_prime - 2))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 5 via scaling symmetry
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 6)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 6 mod 10
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 2)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 2 mod 10
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 7)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 7 mod 10
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 1 open classes mod 10
- `(forall q_prime >= 2: ((is_prime(q_prime) and (10 | (q_prime - 1))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 10 via scaling symmetry
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((30 * k) + 11)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 11 mod 30
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((30 * k) + 21)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 21 mod 30
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((30 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 1 open classes mod 30
- `(forall q_prime >= 2: ((is_prime(q_prime) and (30 | (q_prime - 1))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 30 via scaling symmetry
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((60 * k) + 31)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 31 mod 60
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((60 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 1 open classes mod 60
- `(forall q_prime >= 2: ((is_prime(q_prime) and (60 | (q_prime - 1))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 60 via scaling symmetry
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 61)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 61 mod 420
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 121)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 121 mod 420
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 241)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 241 mod 420
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 301)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 301 mod 420
- `forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 361)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))` — rule `forall_exists_witness`, origin: witness construction: class 361 mod 420
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 181)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 2 open classes mod 420
- `(forall q_prime >= 2: ((is_prime(q_prime) and (420 | (q_prime - 1) or 420 | (q_prime - 181))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 420 via scaling symmetry
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((840 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((840 * k) + 421)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((840 * k) + 181)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((840 * k) + 601)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 4 open classes mod 840
- `(forall q_prime >= 2: ((is_prime(q_prime) and (840 | (q_prime - 1) or 840 | (q_prime - 421) or 840 | (q_prime - 181) or 840 | (q_prime - 601))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 840 via scaling symmetry
- `((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 841)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1681)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 421)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1261)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 2101)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 181)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1021)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1861)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 601)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1441)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 2281)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `residue_cover`, origin: reduction: target follows from 12 open classes mod 2520
- `(forall q_prime >= 2: ((is_prime(q_prime) and (2520 | (q_prime - 1) or 2520 | (q_prime - 841) or 2520 | (q_prime - 1681) or 2520 | (q_prime - 421) or 2520 | (q_prime - 1261) or 2520 | (q_prime - 2101) or 2520 | (q_prime - 181) or 2520 | (q_prime - 1021) or 2520 | (q_prime - 1861) or 2520 | (q_prime - 601) or 2520 | (q_prime - 1441) or 2520 | (q_prime - 2281))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)))` — rule `prime_reduction`, origin: prime reduction mod 2520 via scaling symmetry

## Findings
- witness_moduli_schedule: [5, 10, 30, 60, 420, 840, 2520]
- witness_examples: {'n = 5k + 0': ['k + 1', 'k**2 + 2*k + 1', 'k**3 + 2*k**2 + k'], 'n = 5k + 3': ['k + 1', '5*k**2 + 8*k + 3', '5*k**2 + 8*k + 3'], 'n = 5k + 4': ['k + 1', '5*k**2 + 9*k + 5', '25*k**4 + 90*k**3 + 126*k**2 + 81*k + 20'], 'n = 10k + 6': ['10*k + 6', '5*k + 3', '5*k + 3'], 'n = 10k + 2': ['10*k + 2', '5*k + 1', '5*k + 1'], 'n = 10k + 7': ['2*k + 2', '10*k**2 + 17*k + 7', '20*k**2 + 34*k + 14']}
- reduction: {'modulus': 2520, 'open_classes': 12, 'of': 2520, 'open_sample': [1, 841, 1681, 421, 1261, 2101, 181, 1021, 1861, 601, 1441, 2281], 'statement': 'target holds for all n >= 2 if it holds on the open classes'}
- prime_reduction: {'modulus': 2520, 'open_prime_classes': [1, 841, 1681, 421, 1261, 2101, 181, 1021, 1861, 601, 1441, 2281], 'count': 12, 'statement': 'target holds for all n >= 2 if it holds for every prime in these classes'}
- obstruction_diagnosis: ['every open residue is 1 mod 2', 'every open residue is 1 mod 3', 'every open residue is 1 mod 4', 'every open residue is 1 mod 5', 'every open residue is 1 mod 6', 'every open residue is 1 mod 10', 'every open residue is 1 mod 12']

## Proof attempts
- total attempts: 8; successful: 0
- direct budget 200: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 400: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 800: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 1600: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 3200: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 6400: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 12800: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `
- direct budget 25600: no proof | `forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / `

## Lean
- exported theorems: 0; not yet translatable: 28
- Lean not run.

## Search history (first events)
```
   1.72s  kernel                 rejected                   rejected     forall n in [2, 100]: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / n^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   1.72s  bounded_verification   check                      not decidable up to 100
   1.84s  witness                start                      planned      base 5, moduli [5, 10, 30, 60, 420, 840, 2520]
   1.87s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 0)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   2.02s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 3)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   2.05s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 4)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   2.07s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((5 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k >=
   2.08s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (5 | (q_prime - 1) or 5 | (q_prime - 2))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1
   2.08s  witness                pass                       partial      mod 5: 2 open, grammar T=24 D=12
   2.56s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 6)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   2.56s  direct_proof           stop                       undecided    budget ceiling reached
   2.58s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 2)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   2.67s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 7)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   2.69s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((10 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >
   2.71s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (10 | (q_prime - 1))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((
   2.71s  witness                pass                       partial      mod 10: 1 open, grammar T=38 D=19
   7.31s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((30 * k) + 11)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   7.34s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((30 * k) + 21)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
   7.37s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((30 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >
   7.40s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (30 | (q_prime - 1))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((
   7.40s  witness                pass                       partial      mod 30: 1 open, grammar T=60 D=30
  12.48s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((60 * k) + 31)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
  12.51s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((60 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))) -> forall n >
  12.54s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (60 | (q_prime - 1))) -> exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / q_prime^1)) = (((
  12.54s  witness                pass                       partial      mod 60: 1 open, grammar T=96 D=48
  24.46s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 61)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
  30.18s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 121)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
  38.11s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 241)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
  40.43s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 301)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
  46.19s  kernel                 accepted                   derived      forall_exists_witness: forall k >= 0: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 361)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1))
  46.25s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((420 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k 
  46.29s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (420 | (q_prime - 1) or 420 | (q_prime - 181))) -> exists x >= 1: exists y >= 1: exists z >= 1: (
  46.29s  witness                pass                       partial      mod 420: 2 open, grammar T=153 D=76
  74.55s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((840 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k 
  74.60s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (840 | (q_prime - 1) or 840 | (q_prime - 421) or 840 | (q_prime - 181) or 840 | (q_prime - 601)))
  74.60s  witness                pass                       partial      mod 840: 4 open, grammar T=244 D=121
 171.61s  kernel                 accepted                   derived      residue_cover: ((forall k >= 1: exists x >= 1: exists y >= 1: exists z >= 1: (5 * (1 / ((2520 * k) + 1)^1)) = (((1 / z^1) + (1 / y^1)) + (1 / x^1)) and forall k
 171.66s  kernel                 accepted                   derived      prime_reduction: (forall q_prime >= 2: ((is_prime(q_prime) and (2520 | (q_prime - 1) or 2520 | (q_prime - 841) or 2520 | (q_prime - 1681) or 2520 | (q_prime - 4
 171.66s  witness                pass                       partial      mod 2520: 12 open, grammar T=390 D=193
 281.22s  witness                pass                       partial      mod 2520: 12 open, grammar T=624 D=308
 403.50s  witness                pass                       partial      mod 2520: 12 open, grammar T=998 D=492
```