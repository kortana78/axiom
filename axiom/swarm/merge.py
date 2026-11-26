"""Merge shard results, re-check everything with the kernel, update the frontier.

    python -m axiom.swarm.merge --problem erdos_straus

Trust model: shard files are untrusted data. Every class family is rebuilt
into a proof and checked by the kernel before it counts. The reduction
theorem (residue_cover or prime_reduction) is then checked as a whole.
If no relevant class is open and the reduction passes, the target is PROVED
by the Axiom kernel (and still needs Lean for VERIFIED).
"""
from __future__ import annotations

import argparse
import glob
import os
import time

from ..kernel.inference import Kernel
from ..kernel.proof_objects import Proof
from .common import (Setup, find_problem, load_json, load_queue, parse_polys,
                     results_dir, save_json)
from . import lean_export

T_MAX = 400


def run(pid, queue_path="swarm/queue.json", root="results"):
    entry = find_problem(load_queue(queue_path), pid)
    if entry.get("kind") == "abc":
        from ..abc.merge import run as run_abc
        return run_abc(entry, root)
    st = Setup(entry)
    K = Kernel()
    out = results_dir(root, pid)
    old_status = load_json(os.path.join(out, "status.json"), {}) or {}
    frontier = load_json(os.path.join(out, "frontier.json"), None)
    if frontier is None:
        M0 = int(entry.get("start_modulus", 840))
        frontier = {"modulus": M0, "open": st.relevant(M0),
                    "T": entry["grammar"]["T"], "D": entry["grammar"]["D"]}
    M = frontier["modulus"]

    # 1. gather class families: accumulated library + new shard files
    library = load_json(os.path.join(out, "classes.json"), []) or []
    shard_files = sorted(glob.glob(os.path.join(out, "shards", "*.json")))
    unattempted = set()
    for f in shard_files:
        d = load_json(f, {})
        if d.get("modulus") != M:
            continue
        library.extend(d.get("covered", []))
        unattempted |= set(d.get("unattempted", []))

    # 2. re-check every family with the kernel (dedupe by class)
    valid, seen, rejected = [], set(), 0
    for c in library:
        key = (int(c["M"]), int(c["r"]))
        if key in seen:
            continue
        try:
            polys = parse_polys(c["polys"])
            proof = st.engine.class_proof(key[0], key[1], int(c["kl"]), polys)
            ok, _ = K.check(proof)
        except Exception:
            ok = False
        if ok:
            seen.add(key)
            valid.append({"M": key[0], "r": key[1], "kl": int(c["kl"]), "polys": c["polys"], "proof": proof})
        else:
            rejected += 1

    # 3. coverage at the frontier modulus
    goal, L = st.goal, st.goal.lower
    open_res, used = [], {}
    for r in st.relevant(M):
        first = L + ((r - L) % M)
        hit = next((v for v in valid if M % v["M"] == 0 and r % v["M"] == v["r"] % v["M"]
                    and first >= v["M"] * v["kl"] + v["r"]), None)
        if hit is None:
            open_res.append(r)
        else:
            used[(hit["M"], hit["r"])] = hit
    covered = [(v["M"], v["r"], v["kl"], v["proof"]) for v in used.values()]

    # 4. kernel-check the reduction theorem
    if st.prime_mode:
        red = st.engine.prime_reduction_proof(goal, M, covered, open_res)
        kind = "prime_reduction"
    else:
        red = st.engine.reduction_proof(goal, M, covered, open_res)
        kind = "residue_cover"
    red_ok, red_msg = K.check(red)
    proved = red_ok and not open_res

    # 5. frontier escalation: grow the grammar while it helps, then refine modulus
    prev_open = set(frontier.get("open", []))
    T, D = frontier["T"], frontier["D"]
    progress = len(open_res) < len(prev_open)
    new_frontier = {"modulus": M, "open": open_res, "T": T, "D": D}
    note = "progress at current grammar" if progress else ""
    if not progress and not unattempted and not proved:
        if T < T_MAX:
            new_frontier["T"], new_frontier["D"] = int(T * 1.5), int(D * 1.5)
            note = "no progress: grammar enlarged"
        else:
            nxt = next((m for m in st.engine.moduli(limit=M * 30) if m > M and m % M == 0), None)
            if nxt is None:
                nxt = M * 2
            new_frontier = {"modulus": nxt, "T": entry["grammar"]["T"], "D": entry["grammar"]["D"],
                            "open": sorted(r + M * t for r in open_res for t in range(nxt // M)
                                           if r + M * t in set(st.relevant(nxt)))}
            note = f"grammar ceiling reached: modulus refined {M} -> {nxt}"
    save_json(os.path.join(out, "frontier.json"), new_frontier)
    save_json(os.path.join(out, "classes.json"),
              [{k: v[k] for k in ("M", "r", "kl", "polys")} for v in valid])
    for f in shard_files:
        os.remove(f)

    hist = old_status.get("history", [])
    hist.append({"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "modulus": M,
                 "open": len(open_res), "relevant": len(st.relevant(M)), "T": T, "D": D,
                 "shards_merged": len(shard_files), "rejected_families": rejected, "note": note})
    status = {
        "problem": pid, "statement": entry["statement"],
        "status": "PROVED (axiom kernel; Lean pending)" if proved else "open: reduction certified" if red_ok else "open",
        "modulus": M, "mode": kind,
        "relevant_classes": len(st.relevant(M)), "open_classes": len(open_res),
        "open_sample": open_res[:60], "families_verified": len(valid),
        "reduction_kernel_check": red_msg,
        "reduction_statement": ("target holds for all n >= %d if it holds for every prime in the open classes mod %d"
                                if kind == "prime_reduction" else
                                "target holds for all n >= %d if it holds on the open classes mod %d") % (L, M),
        "next_frontier": {k: new_frontier[k] for k in ("modulus", "T", "D")} | {"open": len(new_frontier["open"])},
        "history": hist[-200:],
    }
    save_json(os.path.join(out, "status.json"), status)
    lean_export.write(st, valid, os.path.join(out, "lean"), pid)
    print(f"[merge {pid}] mod {M}: {len(open_res)}/{len(st.relevant(M))} classes open, "
          f"{len(valid)} families verified, {rejected} rejected; reduction ok={red_ok}; {note}")
    if proved:
        print(f"[merge {pid}] *** ALL CLASSES COVERED: target proved by the Axiom kernel. Run Lean. ***")
    return status


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", action="append")
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    ids = a.problem or [p["id"] for p in load_queue(a.queue) if p.get("active")]
    for pid in ids:
        run(pid, a.queue, a.results)


if __name__ == "__main__":
    main()
