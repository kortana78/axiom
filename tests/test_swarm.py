"""End to end: a swarm worker plus merge fully proves a small existence theorem,
and a tampered shard file is rejected by the kernel at merge time."""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.swarm import merge, worker

Q = {"problems": [{"id": "two_unit", "active": True, "start_modulus": 12,
                   "statement": "forall n >= 2: exists x >= 1: exists y >= 1: 2/n = 1/x + 1/y",
                   "grammar": {"T": 20, "D": 12}}]}


def _setup():
    d = tempfile.mkdtemp()
    qp = os.path.join(d, "queue.json")
    json.dump(Q, open(qp, "w"))
    return d, qp


def test_swarm_proves_small_theorem():
    d, qp = _setup()
    for s in range(2):
        worker.run("two_unit", s, 2, 30, qp, os.path.join(d, "results"))
    st = merge.run("two_unit", qp, os.path.join(d, "results"))
    assert st["status"].startswith("PROVED") and st["open_classes"] == 0


def test_merge_rejects_tampered_family():
    d, qp = _setup()
    res = os.path.join(d, "results")
    data = worker.run("two_unit", 0, 1, 30, qp, res)
    path = os.path.join(res, "two_unit", "shards", "two_unit__shard_000_of_001.json")
    bad = json.load(open(path))
    for c in bad["covered"]:
        c["polys"] = ["k + 1" for _ in c["polys"]]   # wrong witnesses
    json.dump(bad, open(path, "w"))
    st = merge.run("two_unit", qp, res)
    assert st["families_verified"] == 0 and not st["status"].startswith("PROVED")
