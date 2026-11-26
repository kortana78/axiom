"""Certified S-unit solver: published-list validation, tamper rejection, sharding.

Known answers live only in this test file and in ``swarm/sunit_validation.md``;
the solver and checker contain no published triples.
"""
import copy
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.sunit import check, hunt
from axiom.swarm import sunit as swarm_sunit

# Matschke-von Kaenel, arXiv:1605.06079, data files at
# https://bmatschke.github.io/solving-classical-diophantine-equations/
# s-unit-equation/solutions_2_3.txt and solutions_2_3_5.txt
PUBLISHED_2_3 = [
    (1, 1, 2), (1, 2, 3), (1, 3, 4), (1, 8, 9),
]
PUBLISHED_2_3_5 = [
    (1, 1, 2), (1, 2, 3), (1, 3, 4), (1, 4, 5), (1, 5, 6),
    (1, 8, 9), (1, 9, 10), (1, 15, 16), (1, 24, 25), (1, 80, 81),
    (2, 3, 5), (2, 25, 27), (3, 5, 8), (3, 125, 128), (4, 5, 9),
    (5, 27, 32), (9, 16, 25),
]


def test_height_bound_small_supports():
    b23 = hunt.height_bound([2, 3])
    assert b23["N_S"] == 6
    assert b23["exponent_bounds"] == {"2": 116, "3": 73}
    assert float(b23["B"]) > 80.8
    b235 = hunt.height_bound([2, 3, 5])
    assert b235["N_S"] == 30
    assert b235["exponent_bounds"] == {"2": 757, "3": 477, "5": 326}
    assert float(b235["B"]) > 525.0


def test_sunit_single_prime():
    cert = hunt.solve([2])
    assert cert["solutions"] == [[1, 1, 2]]
    assert check.check_certificate(cert, [2])["solutions"] == 1
    empty = hunt.solve([3])
    assert empty["solutions"] == []
    assert check.check_certificate(empty, [3])["solutions"] == 0


def test_sunit_s23_matches_published():
    cert = hunt.solve([2, 3])
    got = {tuple(t) for t in cert["solutions"]}
    assert got == set(PUBLISHED_2_3)
    report = check.check_certificate(cert, [2, 3], PUBLISHED_2_3)
    assert report["status"] == "PASS"
    assert report["solutions"] == 4


def test_sunit_s235_matches_published():
    cert = hunt.solve([2, 3, 5])
    got = {tuple(t) for t in cert["solutions"]}
    assert got == set(PUBLISHED_2_3_5)
    report = check.check_certificate(cert, [2, 3, 5], PUBLISHED_2_3_5)
    assert report["status"] == "PASS"
    assert report["solutions"] == 17


def test_checker_rejects_too_small_height_bound():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    bad["height_bound"]["B"] = "79.000000"
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError as exc:
        assert "height bound too small" in str(exc)
    else:
        raise AssertionError("checker accepted a too-small height bound")


def test_checker_rejects_too_small_exponent_box():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    bad["height_bound"]["exponent_bounds"]["2"] = 100
    for block in bad["blocks"]:
        if block["q"] != 2:
            block["box"]["2"] = 100
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError as exc:
        assert "exponent bound" in str(exc) or "box" in str(exc)
    else:
        raise AssertionError("checker accepted a too-small exponent box")


def test_checker_rejects_missing_solution():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    bad["solutions"] = [t for t in bad["solutions"] if t != [1, 8, 9]]
    bad["solution_count"] = len(bad["solutions"])
    for block in bad["blocks"]:
        block["solutions"] = [t for t in block["solutions"] if t != [1, 8, 9]]
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError as exc:
        assert "missing" in str(exc) or "mismatch" in str(exc)
    else:
        raise AssertionError("checker accepted a missing solution")


def test_checker_rejects_extra_solution():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    bad["solutions"].append([2, 2, 4])
    bad["solutions"].sort()
    bad["solution_count"] = len(bad["solutions"])
    bad["blocks"][0]["solutions"].append([2, 2, 4])
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError as exc:
        assert "extra" in str(exc) or "mismatch" in str(exc)
    else:
        raise AssertionError("checker accepted an extra solution")


def test_checker_rejects_tampered_lattice():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    for block in bad["blocks"]:
        if block["q"] == 3:
            block["lattice_basis"][0][0] += 1
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError as exc:
        assert "lattice" in str(exc) or "index" in str(exc)
    else:
        raise AssertionError("checker accepted a tampered lattice")


def test_checker_rejects_tampered_lll():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    for block in bad["blocks"]:
        if block["q"] == 3:
            block["lll_basis"][0][0] += 1
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError as exc:
        assert "LLL" in str(exc) or "transform" in str(exc)
    else:
        raise AssertionError("checker accepted tampered LLL data")


def test_checker_rejects_non_coprime_extra():
    cert = hunt.solve([2, 3])
    bad = copy.deepcopy(cert)
    bad["solutions"].append([2, 4, 6])
    bad["solutions"].sort()
    bad["solution_count"] = len(bad["solutions"])
    bad["blocks"][0]["solutions"].append([2, 4, 6])
    try:
        check.check_certificate(bad, [2, 3])
    except check.CheckError:
        pass
    else:
        raise AssertionError("checker accepted a non-coprime triple")


def test_shard_merge_covers_full_box():
    # q=2 unsharded, q=3 split into two exponent-box shards.
    c2 = hunt.solve([2, 3], q=2)
    c3a = hunt.solve([2, 3], q=3, shard=0, of=2)
    c3b = hunt.solve([2, 3], q=3, shard=1, of=2)
    merged = hunt.merge_certificates([c2, c3a, c3b])
    assert merged["solution_count"] == 4
    report = check.check_certificate(merged, [2, 3], PUBLISHED_2_3)
    assert report["status"] == "PASS"


def test_merge_rejects_missing_shard():
    c2 = hunt.solve([2, 3], q=2)
    c3a = hunt.solve([2, 3], q=3, shard=0, of=2)
    try:
        hunt.merge_certificates([c2, c3a])
    except ValueError as exc:
        assert "coverage" in str(exc) or "gap" in str(exc)
    else:
        raise AssertionError("merge accepted an incomplete shard set")


def test_merge_rejects_overlapping_shards():
    c2 = hunt.solve([2, 3], q=2)
    c3a = hunt.solve([2, 3], q=3, shard=0, of=2)
    c3b = copy.deepcopy(c3a)
    try:
        hunt.merge_certificates([c2, c3a, c3b])
    except ValueError as exc:
        assert "gap" in str(exc) or "overlap" in str(exc)
    else:
        raise AssertionError("merge accepted overlapping shards")


def test_checker_is_independent():
    import ast
    path = os.path.join(os.path.dirname(__file__), "..", "axiom", "sunit",
                        "check.py")
    tree = ast.parse(open(path, encoding="utf-8").read())
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add(node.module or "")
    assert not any("hunt" in name for name in imported), imported
    assert not any(name.startswith("axiom.sunit") for name in imported), imported


def test_certificate_round_trips_json():
    cert = hunt.solve([2, 3])
    text = json.dumps(cert)
    loaded = json.loads(text)
    report = check.check_certificate(loaded, [2, 3], PUBLISHED_2_3)
    assert report["solutions"] == 4


def test_dedupe_collapses_identical_reruns_but_keeps_conflicts():
    root = tempfile.mkdtemp()
    entry = {"id": "sunit_2", "kind": "sunit", "S": [2],
             "sunit_shards": {"2": 1}, "statement": "S-unit"}
    cert = swarm_sunit.run_worker(entry, 0, 1, 30, root)
    assert swarm_sunit._dedupe([cert, copy.deepcopy(cert)]) == [cert]
    bad = copy.deepcopy(cert)
    bad["blocks"][0]["solutions"] = []
    bad["solution_count"] = 0
    kept = swarm_sunit._dedupe([cert, bad])
    assert len(kept) == 2


def test_merge_requires_hash_anchor_for_validated():
    root = tempfile.mkdtemp()
    entry = {"id": "sunit_2", "kind": "sunit", "S": [2],
             "sunit_shards": {"2": 1}, "published_count": 1,
             "statement": "S-unit"}
    swarm_sunit.run_worker(entry, 0, 1, 30, root)
    st = swarm_sunit.run_merge(entry, root)
    assert st["status"] == "CERTIFIED" and st["checker"] == "PASS"
    assert st["published_match"] is False
    anchored = dict(entry, published_sha256=swarm_sunit.solutions_hash([(1, 1, 2)]))
    swarm_sunit.run_worker(anchored, 0, 1, 30, root)
    st2 = swarm_sunit.run_merge(anchored, root)
    assert st2["status"] == "VALIDATED" and st2["published_match"] is True
    assert st2["solutions"] == 1 and st2["solutions_sha256"] == anchored["published_sha256"]
