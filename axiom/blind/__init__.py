"""AXIOM 0.2 - Blind Mathematical Discovery.

This package contains no problem-specific mathematics. It receives a problem
specification, analyses its structure, invents its own objects and conjectures,
tests them against the trusted kernel, and mutates its strategies when it stalls.

Reference answers live in ``answers.py`` and are imported only by the
evaluation harness, never by the discovery engine. ``leakage.py`` checks that
separation mechanically.
"""
from .problem import BlindProblem
from .controller import BlindController

__all__ = ["BlindProblem", "BlindController"]
