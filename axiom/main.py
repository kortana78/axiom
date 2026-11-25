"""AXIOM command line.

0.1 (kept):
  python -m axiom list
  python -m axiom run sum_squares --time 20
  python -m axiom benchmark --time 15

0.2 (blind discovery):
  python -m axiom blind list
  python -m axiom blind audit
  python -m axiom blind run hidden_div_42 --time 30
  python -m axiom blind solve problem.json --time 30
  python -m axiom blind benchmark --time 20
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys

from .discovery.controller import Controller
from .problems.library import PROBLEMS
from .blind.controller import BlindController
from .blind.evaluation import benchmark
from .blind.leakage import audit_leakage
from .blind.library import CASES, ENVIRONMENTS
from .blind.problem import BlindProblem, BlindProblemError


def _load_file(path):
    spec = importlib.util.spec_from_file_location("axiom_user_problem", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.PROBLEM


def _print_summary(s):
    print(f"\n== {s['problem']}: {s['formal_statement']}")
    if s["goal"]:
        print(f"   target: {s['goal']}")
        print(f"   target status: {s['goal_status']}")
    print(f"   counts: {s['counts']}   time: {s['elapsed_s']} s ({s['stop_reason']})")
    if s["invented_and_proved"]:
        print("   invented AND proved:")
        for k in s["invented_and_proved"][:12]:
            print(f"     - {k}")
    for k, v in s["findings"].items():
        if isinstance(v, list) and len(v) > 25:
            v = f"{len(v)} items, first: {v[:25]}"
        print(f"   {k}: {v}")
    if s["mutations"]:
        print(f"   strategy mutations: {[m['name'] for m in s['mutations']]}")
    if s["bounded_upto"]:
        print(f"   verified for every case up to {s['bounded_upto']}")


def _run_blind(args):
    if getattr(args, "json_file", None):
        with open(args.json_file, encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        if args.problem not in CASES:
            sys.exit(f"unknown blind problem {args.problem}; try: python -m axiom blind list")
        data = CASES[args.problem]
    try:
        problem = BlindProblem.from_dict(data)
    except BlindProblemError as exc:
        sys.exit(f"blind interface rejected the problem: {exc}")
    ctl = BlindController(problem, time_budget=args.time, research_dir=args.research,
                          lean=args.lean, mutation=not args.no_mutation)
    s = ctl.run()
    path = ctl.write_record()
    _print_summary(s)
    print(f"   research record: {path}")


def cmd_run(args):
    if args.file:
        problem = _load_file(args.file)
    else:
        if args.problem not in PROBLEMS:
            sys.exit(f"unknown problem {args.problem}; try: python -m axiom list")
        problem = PROBLEMS[args.problem]
    for kv in args.param or []:
        k, v = kv.split("=", 1)
        problem.params[k] = int(v) if v.lstrip("-").isdigit() else v
    ctl = Controller(problem, time_budget=args.time, db_path=args.db, explore=args.explore)
    s = ctl.run()
    path = ctl.write_record(args.out, try_lean=args.lean)
    _print_summary(s)
    print(f"   research record: {path}")


def cmd_list(_):
    for name, p in PROBLEMS.items():
        print(f"{name:<16} stage {p.stage}  [{p.known_status:<7}] {p.title}")


def cmd_benchmark(args):
    """Stages 1 and 2: rediscover known results with the lemmas withheld."""
    results = []
    for name, p in PROBLEMS.items():
        if p.stage > 2:
            continue
        ctl = Controller(p, time_budget=args.time)
        s = ctl.run()
        ctl.write_record(args.out)
        ok = (s["goal_status"] == "derived") if p.goal is not None else (bool(s["invented_and_proved"]) or s["counts"].get("derived", 0) > 0)
        results.append((name, ok, len(s["invented_and_proved"]), s["elapsed_s"]))
        print(f"{name:<16} {'PASS' if ok else 'FAIL'}  invented+proved: {len(s['invented_and_proved']):<3} {s['elapsed_s']} s")
    passed = sum(1 for r in results if r[1])
    print(f"\n{passed}/{len(results)} benchmark problems solved without the withheld lemmas")


def cmd_blind_list(_):
    for env, keys in ENVIRONMENTS.items():
        print(f"[{env}]")
        for key in keys:
            p = CASES[key]
            print(f"  {key:<24} target={p['target']:<8} {p['formal_statement'] or '(definitions only)'}")


def cmd_blind_audit(_):
    print(audit_leakage().render())


def cmd_blind_benchmark(args):
    benchmark(environments=args.env, time_budget=args.time,
              research_root=args.research, mutation=not args.no_mutation)


def main(argv=None):
    ap = argparse.ArgumentParser(prog="axiom", description="AXIOM mathematical discovery and proof engine")
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("run", help="AXIOM 0.1 run")
    r.add_argument("problem", nargs="?")
    r.add_argument("--file")
    r.add_argument("--time", type=float, default=30)
    r.add_argument("--param", action="append")
    r.add_argument("--out", default="runs")
    r.add_argument("--db", default=":memory:")
    r.add_argument("--lean", action="store_true")
    r.add_argument("--explore", action="store_true")
    r.set_defaults(fn=cmd_run)

    l = sub.add_parser("list", help="list AXIOM 0.1 problems")
    l.set_defaults(fn=cmd_list)

    b = sub.add_parser("benchmark", help="AXIOM 0.1 benchmark")
    b.add_argument("--time", type=float, default=15)
    b.add_argument("--out", default="runs")
    b.set_defaults(fn=cmd_benchmark)

    bl = sub.add_parser("blind", help="AXIOM 0.2 blind discovery")
    bsub = bl.add_subparsers(dest="blind_cmd", required=True)

    br = bsub.add_parser("run", help="run a named blind problem")
    br.add_argument("problem")
    br.add_argument("--time", type=float, default=30)
    br.add_argument("--research", default="research")
    br.add_argument("--lean", action="store_true")
    br.add_argument("--no-mutation", action="store_true")
    br.set_defaults(fn=_run_blind)

    bs = bsub.add_parser("solve", help="solve a blind problem from a JSON file")
    bs.add_argument("json_file")
    bs.add_argument("--time", type=float, default=30)
    bs.add_argument("--research", default="research")
    bs.add_argument("--lean", action="store_true")
    bs.add_argument("--no-mutation", action="store_true")
    bs.set_defaults(fn=_run_blind)

    bli = bsub.add_parser("list", help="list blind test problems")
    bli.set_defaults(fn=cmd_blind_list)

    ba = bsub.add_parser("audit", help="run the leakage audit")
    ba.set_defaults(fn=cmd_blind_audit)

    bb = bsub.add_parser("benchmark", help="run the blind benchmark")
    bb.add_argument("--env", action="append", choices=list(ENVIRONMENTS))
    bb.add_argument("--time", type=float, default=20)
    bb.add_argument("--research", default="research")
    bb.add_argument("--no-mutation", action="store_true")
    bb.add_argument("--lean", action="store_true")
    bb.set_defaults(fn=cmd_blind_benchmark)

    args = ap.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
