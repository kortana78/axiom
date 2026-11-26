"""Idea generator loop: propose ideas, let AXIOM search with them, keep score.

    python -m axiom.ideas.run --problem erdos_straus --time 1800

Order of proposals:
  1. hand-written ideas in swarm/ideas.json (Claude or a human)
  2. a UCB bandit over idea families, using scores from earlier runs
  3. fresh ideas from the enumeration, and mutations of ideas that paid off

Each idea is tried on a sample of the currently open classes. Families it
finds are written as a shard file; the merge step re-checks them with the
kernel like any other worker output. Scores persist in
results/<id>/ideas_log.json, so the swarm learns which kinds of ideas work.
"""
from __future__ import annotations

import argparse
import math
import os
import random
import time

from ..swarm.common import Setup, find_problem, load_json, load_queue, results_dir, save_json
from .engine import IdeaEngine
from .space import Idea, enumerate_ideas, load_hand_ideas, mutate


def _ucb(stats, family, total):
    s = stats.get(family)
    if not s or s["tries"] == 0:
        return float("inf")
    return s["reward"] / s["tries"] + math.sqrt(2 * math.log(max(total, 2)) / s["tries"])


def run(pid, seconds, queue_path="swarm/queue.json", root="results", ideas_path="swarm/ideas.json",
        per_idea=None, sample=12, seed=None, tag="ideas", only=None):
    entry = find_problem(load_queue(queue_path), pid)
    if entry.get("kind") == "abc":
        from ..abc.ideas import run as run_abc_ideas
        return run_abc_ideas(entry, seconds, root, tag=tag)
    if entry.get("kind") == "sunit":
        print(f"[ideas {pid}] S-unit certificates are deterministic; use axiom.sunit.heuristics")
        return {"problem": pid, "kind": "sunit", "skipped": True}
    if entry.get("kind") == "abc_route":
        print(f"[ideas {pid}] proof-track entry: use the Lean route, not the witness idea loop")
        return {"problem": pid, "kind": "abc_route", "skipped": True}
    st = Setup(entry)
    out = results_dir(root, pid)
    frontier = load_json(os.path.join(out, "frontier.json"), None)
    if frontier is None:
        M = int(entry.get("start_modulus", 840))
        frontier = {"modulus": M, "open": st.relevant(M)}
    M, open_res = frontier["modulus"], list(frontier["open"])
    log = load_json(os.path.join(out, "ideas_log.json"), {"tried": {}, "families": {}, "winners": []})
    names = [v for v, _ in st.engine.s.vars]
    rng = random.Random(seed if seed is not None else time.time())
    hand = [i for i in load_hand_ideas(ideas_path) if i.key() not in log["tried"]]
    enum = enumerate_ideas(names)
    start, end = time.time(), time.time() + seconds
    per_idea = per_idea or max(20.0, seconds / 12)
    found, covered_now = {}, set()

    def next_idea():
        while hand:
            return hand.pop(0)
        winners = [Idea.from_dict(w) for w in log["winners"][-20:]]
        if winners and rng.random() < 0.35:
            return mutate(rng.choice(winners), names, rng)
        # bandit: take the best-scoring untried idea among a few enumerated candidates
        cands = []
        for _ in range(30):
            try:
                cand = next(enum)
            except StopIteration:
                break
            if cand.key() not in log["tried"]:
                cands.append(cand)
        if not cands:
            return mutate(Idea(names, ["n", "v", "nv", "vv"]), names, rng)
        total = sum(s["tries"] for s in log["families"].values())
        cands.sort(key=lambda c: -_ucb(log["families"], c.family(), total))
        return cands[0]

    while time.time() < end and open_res:
        idea = next_idea()
        if idea.key() in log["tried"]:
            continue
        try:
            eng = IdeaEngine(st.engine.original if hasattr(st.engine, "original") else st.engine.s, idea)
        except ValueError:
            continue
        targets = [r for r in (only or open_res) if r not in covered_now and r in open_res]
        rng.shuffle(targets)
        targets = targets[:sample]
        if not targets:
            break
        t0, hits = time.time(), 0
        for r in targets:
            if time.time() > end:
                break
            per_class = max(2.0, per_idea / max(1, len(targets)))
            for Mj in st.schedule(M):
                polys, kl, why = eng.search_class(Mj, r % Mj, deadline=min(end, time.time() + per_class))
                if polys is not None:
                    found[f"{Mj}:{r % Mj}"] = {"M": Mj, "r": r % Mj, "kl": kl,
                                               "polys": [str(p) for p in polys], "idea": idea.key()}
                    covered_now.add(r)
                    hits += 1
                    break
        dt = max(0.1, time.time() - t0)
        reward = hits / len(targets) if targets else 0.0
        fam = log["families"].setdefault(idea.family(), {"tries": 0, "reward": 0.0, "hits": 0})
        fam["tries"] += 1
        fam["reward"] += reward
        fam["hits"] += hits
        log["tried"][idea.key()] = {"hits": hits, "tested": len(targets), "seconds": round(dt, 1),
                                    "source": idea.source, "note": idea.note}
        if hits:
            log["winners"].append(idea.to_dict())
        print(f"[ideas {pid}] {idea.source:<9} {idea.key()}  -> {hits}/{len(targets)} open classes covered ({dt:.0f}s)")
    save_json(os.path.join(out, "ideas_log.json"), log)
    data = {"problem": pid, "modulus": M, "covered": list(found.values()), "open": [],
            "unattempted": [], "source": "idea generator",
            "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    path = os.path.join(out, "shards", f"{pid}__{tag}_{int(start)}.json")
    save_json(path, data)
    print(f"[ideas {pid}] {len(found)} new families from {len(log['tried'])} ideas tried so far -> {path}")
    return data


def run_one(pid, seconds, idea_dict, queue_path="swarm/queue.json",
            root="results", sample=12, tag="idea"):
    """Test exactly one idea on a sample of the current open classes.

    Used by the work-item scheduler.  The output is an ordinary untrusted shard
    file; merge re-checks every family with the kernel.
    """
    entry = find_problem(load_queue(queue_path), pid)
    if entry.get("kind") not in (None, "witness"):
        raise ValueError(f"single-idea runner is for witness problems, not {entry.get('kind')}")
    st = Setup(entry)
    out = results_dir(root, pid)
    frontier = load_json(os.path.join(out, "frontier.json"), None)
    if frontier is None:
        M = int(entry.get("start_modulus", 840))
        frontier = {"modulus": M, "open": st.relevant(M)}
    M, open_res = frontier["modulus"], list(frontier["open"])
    log = load_json(os.path.join(out, "ideas_log.json"),
                    {"tried": {}, "families": {}, "winners": []})
    for key, default in (("tried", {}), ("families", {}), ("winners", [])):
        log.setdefault(key, default)
    idea = Idea.from_dict(dict(idea_dict))
    eng = IdeaEngine(st.engine.original if hasattr(st.engine, "original") else st.engine.s, idea)
    targets = open_res[:max(1, int(sample))]
    start = time.time()
    end = start + max(1.0, float(seconds))
    found, hits = {}, 0
    for r in targets:
        if time.time() > end:
            break
        for Mj in st.schedule(M):
            polys, kl, why = eng.search_class(
                Mj, r % Mj, deadline=min(end, time.time() + max(2.0, seconds / max(1, len(targets)))))
            if polys is not None:
                found[f"{Mj}:{r % Mj}"] = {
                    "M": Mj, "r": r % Mj, "kl": kl,
                    "polys": [str(p) for p in polys], "idea": idea.key(),
                }
                hits += 1
                break
    fam = log["families"].setdefault(idea.family(), {"tries": 0, "reward": 0.0, "hits": 0})
    fam["tries"] += 1
    fam["reward"] += hits / len(targets) if targets else 0.0
    fam["hits"] += hits
    log["tried"][idea.key()] = {
        "hits": hits, "tested": len(targets), "seconds": round(time.time() - start, 1),
        "source": idea.source, "note": idea.note,
    }
    if hits:
        log["winners"].append(idea.to_dict())
    save_json(os.path.join(out, "ideas_log.json"), log)
    data = {
        "problem": pid, "modulus": M, "covered": list(found.values()),
        "open": [], "unattempted": [], "source": "scheduler idea",
        "idea": idea.key(), "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    path = os.path.join(out, "shards", f"{pid}__{tag}_{int(start)}.json")
    save_json(path, data)
    return data


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--problem", required=True)
    ap.add_argument("--time", type=float, default=900)
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--results", default="results")
    ap.add_argument("--ideas", default="swarm/ideas.json")
    ap.add_argument("--tag", default="ideas")
    ap.add_argument("--only", help="comma separated residues to target")
    a = ap.parse_args(argv)
    only = [int(x) for x in a.only.split(",")] if a.only else None
    run(a.problem, a.time, a.queue, a.results, a.ideas, tag=a.tag, only=only)


if __name__ == "__main__":
    main()
