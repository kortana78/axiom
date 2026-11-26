"""ABC triple hunter: exact arithmetic, search kernels, merge trust model."""
import json
import math
import os
import sys
import tempfile
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.abc import hunt, ideas
from axiom.swarm import dashboard, merge, worker


def _entry(pid="abc_demo", **search):
    cfg = {"c_max": 2000, "smooth_bound": 23, "min_quality": 1.2,
           "max_records": 50,
           "families": {"c_smooth": {"width": 500},
                        "legs_smooth": {"width": 200000}}}
    cfg.update(search)
    return {"id": pid, "kind": "abc", "active": True,
            "statement": "abc search demo", "search": cfg}


def _setup(entry=None):
    d = tempfile.mkdtemp()
    qp = os.path.join(d, "queue.json")
    json.dump({"problems": [entry or _entry()]}, open(qp, "w"))
    return d, qp, os.path.join(d, "results")


def _shards(res, pid="abc_demo"):
    root = os.path.join(res, pid, "shards")
    return sorted(os.path.join(root, f) for f in os.listdir(root) if f.endswith(".json"))


def test_exact_radical_and_known_record():
    assert hunt.radical(1) == 1
    assert hunt.radical(12) == 6
    assert hunt.radical(30030) == 30030
    rec = hunt.make_record(6436341, 2)          # canonical order a <= b
    assert (rec["a"], rec["b"], rec["c"]) == (2, 6436341, 6436343)
    assert rec["rad"] == 15042
    assert rec["factors"]["c"] == {"23": 5}
    assert abs(rec["q"] - 1.6299116841270482) < 1e-12
    assert hunt.validate_triple(1, 2, 3) == (True, "")
    assert not hunt.validate_triple(1, 2, 4)[0]
    assert not hunt.validate_triple(512, 512, 1024)[0]
    try:
        hunt.make_record(512, 512, 1024)
    except ValueError:
        pass
    else:
        raise AssertionError("non-coprime triple accepted")


def test_sieve_and_smooth_numbers():
    rad = hunt.sieve_radical(5000)
    for n in range(1, 5001):
        assert int(rad[n]) == hunt.radical(n)
    smooth = hunt.smooth_upto(7, 200)
    brute = [n for n in range(1, 201)
             if all(int(p) in (2, 3, 5, 7) for p in hunt.factorization(n))]
    assert list(map(int, smooth)) == brute


def test_pair_layout_matches_bruteforce():
    smooth = hunt.smooth_upto(7, 60)
    layout = hunt.pair_layout(smooth, 60)
    brute = [(int(x), int(y)) for i, x in enumerate(smooth)
             for y in smooth[i + 1:] if x + y <= 60]
    assert layout["total"] == len(brute)
    got = []
    for i, j0, j1, _, _ in hunt.pair_slice_blocks(layout, 0, layout["total"]):
        got.extend((int(smooth[i]), int(smooth[j])) for j in range(j0, j1))
    assert got == brute


def test_scanners_find_known_triple():
    c_max = 1000
    rad = hunt.sieve_radical(c_max)
    smooth = hunt.smooth_upto(23, c_max)
    deadline = time.time() + 30
    res = hunt.scan_c_smooth(rad, smooth, 1, 101, c_max,
                             min_quality=1.2, top_n=50, deadline=deadline)
    assert res["complete"]
    assert (3, 125, 128) in {(r["a"], r["b"], r["c"]) for r in res["candidates"]}
    assert all(math.gcd(r["a"], r["b"]) == 1 for r in res["candidates"])

    layout = hunt.pair_layout(smooth, c_max)
    res2 = hunt.scan_legs_smooth(rad, layout, 0, layout["total"],
                                 min_quality=1.2, top_n=50, deadline=deadline + 30)
    assert res2["complete"]
    assert (3, 125, 128) in {(r["a"], r["b"], r["c"]) for r in res2["candidates"]}
    assert all(math.gcd(r["a"], r["b"]) == 1 for r in res2["candidates"])


def test_worker_merge_end_to_end():
    d, qp, res = _setup()
    data = worker.run("abc_demo", 0, 1, 30, qp, res)
    assert data["kind"] == "abc" and data["scheduler"]
    st = merge.run("abc_demo", qp, res)
    assert st["kind"] == "abc"
    assert st["status"].startswith("search only")
    assert "PROVED" not in st["status"]
    assert st["records_verified"] >= 1
    assert st["best_q"] >= 1.426
    triples = {(r["a"], r["b"], r["c"]) for r in
               json.load(open(os.path.join(res, "abc_demo", "records.json")))}
    assert (3, 125, 128) in triples
    for r in json.load(open(os.path.join(res, "abc_demo", "records.json"))):
        again = hunt.make_record(r["a"], r["b"], r["c"])
        assert again["rad"] == r["rad"]
        assert abs(again["q"] - r["q"]) < 1e-12

    frontier = json.load(open(os.path.join(res, "abc_demo", "frontier.json")))
    assert frontier["families"]["c_smooth"]["next"] == 501
    assert frontier["families"]["legs_smooth"]["exhausted"]

    lean = open(os.path.join(res, "abc_demo", "lean", "abc_demo.lean")).read()
    assert "theorem rec_000_add" in lean
    assert "Nat.Coprime" in lean
    assert "sorry" not in lean
    dashboard.build(qp, res)
    summary = open(os.path.join(res, "SUMMARY.md")).read()
    assert "ABC triple hunter (search only)" in summary
    assert "search only" in summary


def test_merge_rejects_tampered_candidates():
    d, qp, res = _setup()
    worker.run("abc_demo", 0, 1, 30, qp, res)
    path = _shards(res)[0]
    bad = json.load(open(path))
    found = False
    for c in bad["candidates"]:
        if (c["a"], c["b"], c["c"]) == (3, 125, 128):
            c["c"] = 129
            found = True
    assert found
    bad["candidates"].append({"a": 512, "b": 512, "c": 1024, "rad": 2, "q": 10.0})
    json.dump(bad, open(path, "w"))
    st = merge.run("abc_demo", qp, res)
    records = json.load(open(os.path.join(res, "abc_demo", "records.json")))
    assert st["history"][-1]["rejected"] >= 2
    assert all(r["c"] != 129 for r in records)
    assert all(not (r["a"] == r["b"] == 512) for r in records)


def test_incomplete_shard_does_not_advance():
    d, qp, res = _setup()
    worker.run("abc_demo", 0, 1, 30, qp, res)
    path = _shards(res)[0]
    data = json.load(open(path))
    data["families"]["c_smooth"]["complete"] = False
    data["families"]["c_smooth"]["next"] = 10
    json.dump(data, open(path, "w"))
    st = merge.run("abc_demo", qp, res)
    frontier = json.load(open(os.path.join(res, "abc_demo", "frontier.json")))
    assert frontier["families"]["c_smooth"]["next"] == 1
    assert frontier["families"]["c_smooth"]["width"] < 500
    assert "incomplete" in st["history"][-1]["note"]


def test_abc_ideas_write_an_untrusted_shard():
    d, qp, res = _setup(_entry("abc_ideas", c_max=1000))
    data = ideas.run({"id": "abc_ideas", "kind": "abc",
                      "statement": "abc search demo",
                      "search": {"c_max": 1000, "smooth_bound": 23,
                                 "min_quality": 1.2, "max_records": 50,
                                 "ideas_c_max": 1000}},
                     seconds=4, root=res, seed=7)
    assert data["kind"] == "abc" and not data["scheduler"]
    assert data["attempts"]
    assert _shards(res, "abc_ideas")
    log = json.load(open(os.path.join(res, "abc_ideas", "ideas_log.json")))
    assert log["families"]
