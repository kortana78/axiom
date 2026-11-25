"""Reference answers for blind evaluation.

IMPORTANT: this module is imported only by ``blind.evaluation`` and the
leakage audit. No discovery-facing module imports it. The leakage audit checks
that mechanically before any benchmark is allowed to run.

The ``signature`` fields are strings that must never appear in discovery-facing
source code or in discover-mode problem inputs.
"""
from __future__ import annotations

CASES = {
    # Environment 1: the statement contains the theorem, the proof is withheld.
    "hidden_sum_squares": {"reference": "n*(n+1)*(2*n+1)/6", "signature": "(2*n+1)/6"},
    "hidden_sum_cubes": {"reference": "(n*(n+1)/2)^2", "signature": "(n*(n+1)/2)^2"},
    "hidden_div_30": {"reference": "30", "signature": "30 | n^5 - n"},
    "hidden_div_42": {"reference": "42", "signature": "42 | n^7 - n"},
    "hidden_exp_threshold": {"reference": "16", "signature": "n^4 <= 2^n"},

    # Environment 2: the answer is absent from the input; it must be invented.
    "research_sum_squares": {"reference": "n*(n+1)*(2*n+1)/6",
                             "signature": "n*(n+1)*(2*n+1)/6"},
    "research_sum_cubes": {"reference": "(n*(n+1)/2)^2",
                           "signature": "(n*(n+1)/2)^2"},
    "research_geometric": {"reference": "2^(n+1) - 1", "signature": "2^(n+1) - 1"},
    "research_div_n7": {"reference": "42", "signature": "42 | n^7 - n"},
    "research_prod4": {"reference": "24", "signature": "24 | n*(n+1)*(n+2)*(n+3)"},
    "research_rec_squares": {"reference": "n^2", "signature": "a(n) = n^2"},

    # Environment 3: no reference proof exists; honest non-solution is expected.
    "open_collatz": {"reference": None, "signature": "parity_vector"},
    "open_legendre": {"reference": None, "signature": None},
    "open_quasiperfect": {"reference": None, "signature": None},
    "open_erdos_straus": {"reference": None, "signature": "es_family"},
    "open_sierpinski": {"reference": None, "signature": None},
    "hidden_two_unit": {"reference": "x = y = n", "signature": "x = y = n"},
    "hidden_pythagorean_leg": {"reference": "(n^2-1)/2, (n^2+1)/2", "signature": "(n^2+1)/2"},
}

# Strategy hints from 0.1 that must not reappear anywhere in blind discovery.
STRATEGY_HINTS = ("es_family", "collatz_descent", "parity_vector", "Mordell",
                  "mod 840", "modulus=840", "max_k")
