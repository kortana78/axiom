"""Swarm integration for the certified S-unit solver.

A sunit queue entry looks like::

    {
      "id": "sunit_2_3_5",
      "kind": "sunit",
      "S": [2, 3, 5],
      "active": true,
      "sunit_shards": {"2": 1, "3": 1, "5": 1},
      "published_count": 17,
      "published_source": "...",
      "statement": "..."
    }

Workers write one certificate block per exponent-box shard.  The merge groups
the blocks by prime, checks that the shard boxes tile the full box, combines
them, and runs the independent checker.  Nothing a worker writes is trusted.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import time

from .common import find_problem, load_json, load_queue, results_dir, save_json
from ..sunit import check, hunt


def solutions_hash(solutions) -> str:
    """Canonical hash of a sorted solution list (answers stay in the test/doc)."""
    text = "\n".join(f"{int(a)},{int(b)},{int(c)}"
                     for a, b, c in sorted(tuple(int(x) for x in t) for t in solutions))
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def sunit_items(entry) -> list[tuple[int, int, int]]:
    """The ``(q, shard, of)`` work items declared by the queue entry."""
    S = [int(p) for p in entry["S"]]
    plan = entry.get("sunit_shards") or {}
    items: list[tuple[int, int, int]] = []
    for q in S:
        n = max(1, int(plan.get(str(q), plan.get(q, 1))))
        for k in range(n):
            items.append((q, k, n))
    return items


def run_worker(entry, shard, of, seconds, root):
    S = [int(p) for p in entry["S"]]
    items = sunit_items(entry)
    if not items:
        raise ValueError("sunit entry has no work items")
    q, k, n = items[shard % len(items)]
    deadline = time.time() + seconds
    t0 = time.time()
    cert = hunt.solve(S, q=q, shard=k, of=n, deadline=deadline)
    out = results_dir(root, entry["id"])
    path = os.path.join(out, "shards",
                        f"{entry['id']}__q{q}_shard_{k:03d}_of_{n:03d}"
                        f"__job_{shard:03d}_of_{of:03d}.json")
    save_json(path, cert)
    print(f"[{entry['id']} shard {shard}/{of}] q={q} box {k}/{n}: "
          f"{cert['solution_count']} solutions, {sum(b['vectors_tested'] for b in cert['blocks'])} "
          f"vectors, {round(time.time() - t0, 1)} s -> {path}")
    return cert


def _dedupe(certs):
    """Drop byte-identical reruns of the same work item.

    Conflicting reruns (same block box, different solutions) are kept so the
    merge's overlap check rejects them instead of silently choosing a winner.
    """
    seen = {}
    out = []
    for cert in certs:
        blocks = cert.get("blocks", [])
        sig = tuple((int(b["q"]), json.dumps(b.get("shard_box", {}), sort_keys=True))
                    for b in blocks)
        body = json.dumps(blocks, sort_keys=True)
        if sig in seen and seen[sig] == body:
            continue
        seen.setdefault(sig, body)
        out.append(cert)
    return out


def run_merge(entry, root="results"):
    pid = entry["id"]
    S = [int(p) for p in entry["S"]]
    out = results_dir(root, pid)
    shard_files = sorted(glob.glob(os.path.join(out, "shards", "*.json")))
    if not shard_files:
        print(f"[merge {pid}] no sunit shard files yet; carried over")
        old = load_json(os.path.join(out, "status.json"), {}) or {}
        return old | {"problem": pid, "kind": "sunit", "status": "pending: no shards",
                      "abc_status": "abc conjecture: OPEN. No result here proves it."}
    certs = [load_json(f, {}) for f in shard_files]
    certs = [c for c in certs if c.get("kind") == "sunit_certificate"]
    certs = _dedupe(certs)
    try:
        merged = hunt.merge_certificates(certs)
        report = check.check_certificate(merged, S)
    except (ValueError, check.CheckError) as exc:
        print(f"[merge {pid}] pending: {exc}; shards carried over")
        old = load_json(os.path.join(out, "status.json"), {}) or {}
        return old | {"problem": pid, "kind": "sunit",
                      "status": f"pending: {exc}",
                      "abc_status": "abc conjecture: OPEN. No result here proves it."}
    published_count = entry.get("published_count")
    published_hash = entry.get("published_sha256")
    got_hash = solutions_hash(merged["solutions"])
    if published_hash is not None and got_hash == str(published_hash).lower():
        status_word = "VALIDATED"
        published_match = True
    else:
        status_word = "CERTIFIED"
        published_match = False
    cert_path = os.path.join(out, "certificate.json")
    save_json(cert_path, merged)
    status = {
        "problem": pid,
        "kind": "sunit",
        "statement": entry.get("statement", ""),
        "status": status_word,
        "S": S,
        "solutions": merged["solution_count"],
        "published_count": published_count,
        "published_source": entry.get("published_source", ""),
        "solutions_sha256": got_hash,
        "published_sha256": published_hash,
        "published_match": published_match,
        "checker": report["status"],
        "height_bound_B": merged["height_bound"]["B"],
        "exponent_bounds": merged["height_bound"]["exponent_bounds"],
        "lattice_blocks": len(merged["blocks"]),
        "vectors_tested": sum(int(b.get("vectors_tested", 0)) for b in merged["blocks"]),
        "lean": "solution list exported; completeness is computer-assisted, not Lean-verified",
        "abc_status": "abc conjecture: OPEN. No result here proves it.",
        "history": (load_json(os.path.join(out, "status.json"), {}) or {}).get("history", []) + [{
            "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "shards": len(shard_files),
            "solutions": merged["solution_count"],
            "checker": report["status"],
            "status": status_word,
        }],
    }
    status["history"] = status["history"][-200:]
    save_json(os.path.join(out, "status.json"), status)
    try:
        from ..sunit import lean_export
        lean_export.write(merged, os.path.join(out, "lean"), pid)
    except Exception as exc:  # Lean export is optional; never hide the checker result
        status["lean_export_error"] = str(exc)
        save_json(os.path.join(out, "status.json"), status)
    for f in shard_files:
        os.remove(f)
    print(f"[merge {pid}] {status_word}: {merged['solution_count']} solutions "
          f"(published {published_count}, hash match={published_match}); "
          f"checker {report['status']}; B={merged['height_bound']['B']}")
    return status


def run(pid, queue_path="swarm/queue.json", root="results"):
    entry = find_problem(load_queue(queue_path), pid)
    return run_merge(entry, root)
