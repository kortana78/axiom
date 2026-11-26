"""Work-item scheduler: cap, round-robin, per-runner records, carry-over."""
import json
import os
import sys
import tempfile
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from axiom.swarm import schedule

Q = {"problems": [
    {"id": "w", "active": True, "statement": "forall n >= 2: exists x >= 1: 2/n = 1/x",
     "grammar": {"T": 10, "D": 6}},
    {"id": "s", "kind": "sunit", "active": True, "S": [2, 3],
     "sunit_shards": {"2": 1, "3": 1}, "statement": "S-unit"},
    {"id": "a", "kind": "abc", "active": True, "statement": "abc search"},
    {"id": "r", "kind": "abc_route", "active": True, "statement": "route"},
]}


def _write(d, data=None, name="queue.json"):
    p = os.path.join(d, name)
    json.dump(data or Q, open(p, "w"))
    return p


def test_build_items_cap_and_round_robin():
    d = tempfile.mkdtemp()
    qp = _write(d)
    plan = schedule.build_items(qp, shards=2, max_items=5)
    assert plan["capped"] and len(plan["items"]) == 5
    assert plan["total_available"] > 5
    ids = {i["problem"] for i in plan["items"]}
    assert {"w", "s", "a"} <= ids
    assert "r" not in ids


def test_sunit_items_carry_prime_and_box():
    d = tempfile.mkdtemp()
    qp = _write(d)
    plan = schedule.build_items(qp, shards=2, max_items=100)
    sunit = [i for i in plan["items"] if i["problem"] == "s"]
    assert {i["q"] for i in sunit} == {2, 3}
    assert all(i["of"] == 2 for i in sunit)


def test_idea_items_are_assigned():
    d = tempfile.mkdtemp()
    qp = _write(d, {"problems": [Q["problems"][0]]})
    ideas = {"ideas": [{"order": ["x"], "atoms": ["n"], "mult": [1],
                        "T": 10, "D": 6, "source": "hand"},
                       {"order": ["x"], "atoms": ["nv"], "mult": [1],
                        "T": 10, "D": 6, "source": "hand"}]}
    ip = os.path.join(d, "ideas.json")
    json.dump(ideas, open(ip, "w"))
    plan = schedule.build_items(qp, shards=2, max_items=100,
                                ideas_per_shard=2, idea_paths=[ip])
    assert len(plan["items"]) == 4
    assert all(i["idea"] for i in plan["items"])
    assert {i["idea"]["atoms"][0] for i in plan["items"]} == {"n", "nv"}


def test_runner_records_planned_done_and_carry():
    d = tempfile.mkdtemp()
    qp = _write(d)
    root = os.path.join(d, "results")
    calls = []

    def fake(item, seconds, queue_path, root):
        calls.append(item)
        if len(calls) == 2:
            raise RuntimeError("boom")
        return {"ok": True}

    with mock.patch.object(schedule, "_run_item", fake):
        rec = schedule.run_runner(0, 2, 0.001, qp, root, max_items=4, shards=1)
    assert rec["planned"]
    assert rec["done"] and rec["carried_over"]
    assert rec["errors"]
    assert os.path.exists(os.path.join(root, "schedule", "runner_000.json"))


def test_summarize_merges_runner_files():
    d = tempfile.mkdtemp()
    qp = _write(d)
    root = os.path.join(d, "results")

    def fake(item, seconds, queue_path, root):
        return {"ok": True}

    with mock.patch.object(schedule, "_run_item", fake):
        schedule.run_runner(0, 2, 0.001, qp, root, max_items=2, shards=1)
        schedule.run_runner(1, 2, 0.001, qp, root, max_items=2, shards=1)
    summary = schedule.summarize(root)
    assert summary["runners"] == 2
    assert summary["planned"] >= summary["done"] >= 1
    assert os.path.exists(os.path.join(root, "schedule.json"))


def test_runner_rejects_bad_index():
    d = tempfile.mkdtemp()
    qp = _write(d)
    try:
        schedule.run_runner(2, 2, 1, qp, os.path.join(d, "results"))
    except ValueError:
        pass
    else:
        raise AssertionError("accepted runner index outside range")
