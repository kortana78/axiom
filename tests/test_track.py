"""ABC proof-track statement, route notes, and the permanent dashboard line."""
import json
import os
import re
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.swarm import dashboard

ROOT = os.path.join(os.path.dirname(__file__), "..")


def test_lean_statement_has_exact_definitions_and_no_sorry():
    src = open(os.path.join(ROOT, "lean", "Abc", "Statement.lean"), encoding="utf-8").read()
    for needle in ("def rad", "def quality", "def Statement", "def FinitelyMany",
                   "Nat.Coprime", "rad (a * b * c)", "1 + ε"):
        assert needle in src, needle
    code = re.sub(r"/-.*?-/", "", src, flags=re.S)
    assert "sorry" not in code
    assert "\naxiom " not in code


def test_abc_routes_are_cited_and_honest():
    src = open(os.path.join(ROOT, "swarm", "abc_routes.md"), encoding="utf-8").read()
    assert "OPEN" in src and "No result here proves it" in src
    for needle in ("Mason", "Stothers", "Szpiro", "Stewart", "IUT",
                   "Mochizuki", "disputed", "Polynomial.abc"):
        assert needle in src, needle


def test_sunit_validation_records_published_lists():
    src = open(os.path.join(ROOT, "swarm", "sunit_validation.md"), encoding="utf-8").read()
    for needle in ("1 + 8 = 9", "3 + 125 = 128", "17", "82b410e12d",
                   "VALIDATED", "{2,3,5,7}", "not attempted"):
        assert needle in src, needle


def test_dashboard_always_shows_abc_open_and_handles_sunit():
    d = tempfile.mkdtemp()
    q = os.path.join(d, "queue.json")
    json.dump({"problems": [
        {"id": "s", "kind": "sunit", "active": True, "S": [2, 3, 5],
         "published_count": 17, "statement": "S-unit"},
        {"id": "r", "kind": "abc_route", "active": True, "route": "Szpiro",
         "statement": "route", "notes": "unproved"},
        {"id": "w", "active": True, "statement": "forall n >= 2: exists x >= 1: 2/n = 1/x",
         "grammar": {"T": 10, "D": 6}},
    ]}, open(q, "w"))
    root = os.path.join(d, "results")
    os.makedirs(os.path.join(root, "s", "lean"), exist_ok=True)
    json.dump({"kind": "sunit", "status": "VALIDATED", "S": [2, 3, 5],
               "solutions": 17, "published_count": 17, "published_match": True,
               "checker": "PASS", "height_bound_B": "525.089850"},
              open(os.path.join(root, "s", "status.json"), "w"))
    dashboard.build(q, root)
    html = open(os.path.join(root, "index.html"), encoding="utf-8").read()
    md = open(os.path.join(root, "SUMMARY.md"), encoding="utf-8").read()
    for text in (html, md):
        assert "abc conjecture: OPEN. No result here proves it." in text
        assert "S-unit certificates" in text
        assert "ABC proof track" in text


def test_sunit_modules_do_not_contain_published_triples():
    for name in ("hunt.py", "check.py", "lean_export.py"):
        src = open(os.path.join(ROOT, "axiom", "sunit", name), encoding="utf-8").read()
        for triple in ("1 + 8 = 9", "3 + 125 = 128", "[1, 8, 9]", "(1, 8, 9)"):
            assert triple not in src, (name, triple)
