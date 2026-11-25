"""Blind test problems.

This module contains *statements only*. There are no proofs, lemmas, residue
classes, formula templates or difficulty hints. Reference answers are kept in
``answers.py``, which the discovery engine never imports.
"""
from __future__ import annotations

from typing import Dict

# Each value is exactly the blind problem interface: nothing else.
CASES: Dict[str, dict] = {}

# ------------------------------------------------ environment 1: hidden theorems
CASES["hidden_sum_squares"] = {
    "name": "hidden_sum_squares", "domain": "number_theory",
    "formal_statement": "forall n >= 0: Sum[i=1..n](i^2) = n*(n+1)*(2*n+1)/6",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["hidden_sum_cubes"] = {
    "name": "hidden_sum_cubes", "domain": "number_theory",
    "formal_statement": "forall n >= 0: Sum[i=1..n](i^3) = (n*(n+1)/2)^2",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["hidden_div_30"] = {
    "name": "hidden_div_30", "domain": "number_theory",
    "formal_statement": "forall n >= 0: 30 | n^5 - n",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["hidden_div_42"] = {
    "name": "hidden_div_42", "domain": "number_theory",
    "formal_statement": "forall n >= 0: 42 | n^7 - n",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["hidden_exp_threshold"] = {
    "name": "hidden_exp_threshold", "domain": "number_theory",
    "formal_statement": "forall n >= 16: n^4 <= 2^n",
    "definitions": [], "assumptions": [], "target": "prove"}

# ------------------------------------------------ environment 2: research level
CASES["research_sum_squares"] = {
    "name": "research_sum_squares", "domain": "number_theory",
    "formal_statement": "study Sum[i=1..n](i^2)",
    "definitions": [], "assumptions": [], "target": "discover"}
CASES["research_sum_cubes"] = {
    "name": "research_sum_cubes", "domain": "number_theory",
    "formal_statement": "study Sum[i=1..n](i^3)",
    "definitions": [], "assumptions": [], "target": "discover"}
CASES["research_geometric"] = {
    "name": "research_geometric", "domain": "number_theory",
    "formal_statement": "study Sum[i=0..n](2^i)",
    "definitions": [], "assumptions": [], "target": "discover"}
CASES["research_div_n7"] = {
    "name": "research_div_n7", "domain": "number_theory",
    "formal_statement": "study n^7 - n",
    "definitions": [], "assumptions": [], "target": "discover"}
CASES["research_prod4"] = {
    "name": "research_prod4", "domain": "number_theory",
    "formal_statement": "study n*(n+1)*(n+2)*(n+3)",
    "definitions": [], "assumptions": [], "target": "discover"}
CASES["research_rec_squares"] = {
    "name": "research_rec_squares", "domain": "number_theory",
    "formal_statement": "",
    "definitions": ["a(0) = 0; a(n+1) = a(n) + 2*n + 1"],
    "assumptions": [], "target": "discover"}

# ------------------------------------------------ environment 3: open problems
CASES["open_collatz"] = {
    "name": "open_collatz", "domain": "number_theory",
    "formal_statement": "forall n >= 1: collatz_reaches_one(n)",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["open_legendre"] = {
    "name": "open_legendre", "domain": "number_theory",
    "formal_statement": "forall n >= 1: prime_between_squares(n)",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["open_quasiperfect"] = {
    "name": "open_quasiperfect", "domain": "number_theory",
    "formal_statement": "forall n >= 1: not_quasiperfect(n)",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["open_erdos_straus"] = {
    "name": "open_erdos_straus", "domain": "number_theory",
    "formal_statement": "forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 4/n = 1/x + 1/y + 1/z",
    "definitions": [], "assumptions": [], "target": "prove"}

CASES["hidden_two_unit"] = {
    "name": "hidden_two_unit", "domain": "number_theory",
    "formal_statement": "forall n >= 2: exists x >= 1: exists y >= 1: 2/n = 1/x + 1/y",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["hidden_pythagorean_leg"] = {
    "name": "hidden_pythagorean_leg", "domain": "number_theory",
    "formal_statement": "forall n >= 3: exists x >= 1: exists y >= 1: n^2 + x^2 = y^2",
    "definitions": [], "assumptions": [], "target": "prove"}
CASES["open_sierpinski"] = {
    "name": "open_sierpinski", "domain": "number_theory",
    "formal_statement": "forall n >= 2: exists x >= 1: exists y >= 1: exists z >= 1: 5/n = 1/x + 1/y + 1/z",
    "definitions": [], "assumptions": [], "target": "prove"}

ENVIRONMENTS = {
    "hidden": ["hidden_sum_squares", "hidden_sum_cubes", "hidden_div_30",
               "hidden_div_42", "hidden_exp_threshold", "hidden_two_unit",
               "hidden_pythagorean_leg"],
    "research": ["research_sum_squares", "research_sum_cubes", "research_geometric",
                 "research_div_n7", "research_prod4", "research_rec_squares"],
    "open": ["open_collatz", "open_legendre", "open_quasiperfect", "open_erdos_straus",
             "open_sierpinski"],
}
