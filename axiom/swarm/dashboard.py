"""Build a plain static dashboard: results/index.html (and results/SUMMARY.md)."""
from __future__ import annotations

import argparse
import html
import os
import time

from ..abc_proof import LEAN_ACCEPTED, OPEN, REJECTED
from .common import load_json, load_queue

ABC_OPEN = "abc conjecture: OPEN. No result here proves it."
ABC_REJECTED = "abc conjecture: OPEN. A proof attempt was rejected by Lean (see log)."
ABC_LEAN_ACCEPTED = (
    "LEAN ACCEPTED A PROOF OF Abc.Statement (axioms: {axioms}). "
    "Human review required before any announcement."
)


def abc_banner(proof: dict | None) -> str:
    """Choose the top line from the proof-alarm status file only."""
    if not isinstance(proof, dict):
        proof = {}
    verdict = proof.get("verdict", OPEN)
    if verdict == LEAN_ACCEPTED:
        axioms = proof.get("axioms") or []
        names = ", ".join(str(x) for x in axioms) if axioms else "none"
        return ABC_LEAN_ACCEPTED.format(axioms=names)
    if verdict == REJECTED:
        return ABC_REJECTED
    return ABC_OPEN


def _lean(lean: dict) -> str:
    return lean.get("summary", "Lean not run")


def _last_note(st: dict) -> str:
    return st["history"][-1]["note"] if st.get("history") else ""


def _witness_row(p: dict, st: dict, lean: dict) -> list[str]:
    if not st:
        return [p["id"], "no results yet", "", "", "", "", _lean(lean)]
    return [p["id"], st["status"], st["modulus"],
            f"{st['open_classes']} / {st['relevant_classes']}",
            st["families_verified"], _last_note(st), _lean(lean)]


def _abc_row(p: dict, st: dict, lean: dict) -> list[str]:
    if not st:
        return [p["id"], "no results yet", "", "", "0", "", _lean(lean)]
    searched = st.get("searched", {})
    best = st.get("best_triple") or {}
    note = _last_note(st)
    if best:
        note = (f"best {best.get('a')} + {best.get('b')} = {best.get('c')} "
                f"(rad {best.get('rad')}); {note}").strip("; ")
    return [p["id"], st["status"], f"{int(searched.get('c_max', 0)):,}",
            f"{float(st.get('best_q', 0.0)):.6f}", st.get("records_verified", 0),
            note, _lean(lean)]


def _sunit_row(p: dict, st: dict, lean: dict) -> list[str]:
    if not st:
        return [p["id"], "no results yet", str(p.get("S", "")), "0",
                str(p.get("published_count", "")), "", "", _lean(lean)]
    return [
        p["id"],
        st.get("status", "pending"),
        str(st.get("S", p.get("S", ""))),
        str(st.get("solutions", 0)),
        f"{st.get('published_count', '')}"
        + (" (hash match)" if st.get("published_match") else ""),
        str(st.get("checker", "")),
        str(st.get("height_bound_B", "")),
        _lean(lean),
    ]


def _route_row(p: dict, st: dict) -> list[str]:
    if not st:
        return [p["id"], p.get("route", ""), "unproved idea", p.get("notes", "")]
    return [p["id"], p.get("route", st.get("route", "")),
            st.get("status", "unproved idea"), st.get("note", p.get("notes", ""))]


def _html_table(headers: list[str], rows: list[list[str]]) -> str:
    head = "".join(f"<th>{html.escape(h)}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in row) + "</tr>"
                   for row in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def _md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out += ["| " + " | ".join(str(x) for x in row) + " |" for row in rows]
    return out


def build(queue_path="swarm/queue.json", root="results"):
    problems = load_queue(queue_path)
    witness, abc, sunit, routes = [], [], [], []
    for p in problems:
        st = load_json(os.path.join(root, p["id"], "status.json"), None)
        lean = load_json(os.path.join(root, p["id"], "lean_status.json"), {}) or {}
        kind = p.get("kind") or (st or {}).get("kind")
        if kind == "abc":
            abc.append((p, st, lean))
        elif kind == "sunit":
            sunit.append((p, st, lean))
        elif kind == "abc_route":
            routes.append((p, st))
        else:
            witness.append((p, st, lean))

    wheaders = ["problem", "status", "modulus", "open / relevant", "families", "last note", "Lean"]
    aheaders = ["problem", "status", "c max", "best q", "records", "last note", "Lean"]
    sheaders = ["problem", "status", "S", "solutions", "published", "checker", "B", "Lean"]
    rheaders = ["target", "route", "status", "note"]
    wrows = [_witness_row(p, st, lean) for p, st, lean in witness]
    arows = [_abc_row(p, st, lean) for p, st, lean in abc]
    srows = [_sunit_row(p, st, lean) for p, st, lean in sunit]
    rrows = [_route_row(p, st) for p, st in routes]

    proof = load_json(os.path.join(root, "abc_proof", "status.json"), None)
    if not isinstance(proof, dict):
        proof = {}
    banner = abc_banner(proof)
    proof_verdict = str(proof.get("verdict", OPEN))
    proof_reason = str(proof.get("reason", "no proof-alarm status yet"))
    accepted = proof_verdict == LEAN_ACCEPTED
    footer = (
        "Lean accepted a proof of Abc.Statement; human review is required before "
        "any announcement." if accepted else
        "No result here proves the abc conjecture."
    )

    updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    page = (
        "<!doctype html><html><head><meta charset=utf-8><title>AXIOM swarm</title>"
        "<style>body{font-family:sans-serif;margin:2em}td,th{border:1px solid #999;padding:4px 8px}"
        "table{border-collapse:collapse;margin-bottom:2em}"
        ".open{font-weight:bold;color:#a00}</style></head><body>"
        "<h1>AXIOM swarm</h1>"
        f"<p class=open>{html.escape(banner)}</p>"
        f"<p>proof alarm: {html.escape(proof_verdict)} — {html.escape(proof_reason)}</p>"
        f"<p>updated {updated}</p>"
        "<h2>Witness reductions</h2>"
        + _html_table(wheaders, wrows)
        + "<h2>ABC triple hunter (search only)</h2>"
        + _html_table(aheaders, arows)
        + "<h2>S-unit certificates (finite completeness, not abc)</h2>"
        + _html_table(sheaders, srows)
        + "<h2>ABC proof track (all targets unproved)</h2>"
        + _html_table(rheaders, rrows)
        + "<p>Every reduction family is re-checked by the Axiom kernel at merge time. "
        "ABC records are exact integer triples re-checked by the merger (gcd, sum, and "
        "radical). S-unit lists are independently re-enumerated by `axiom.sunit.check`; "
        "the Lean export checks only the listed triples, not completeness. "
        + footer + "</p>"
        "</body></html>")
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)

    md = ["# AXIOM swarm summary", "", f"**{banner}**", "",
          f"proof alarm: {proof_verdict} — {proof_reason}", "",
          f"updated {updated}", "", "## Witness reductions", ""]
    md += _md_table(wheaders, wrows)
    md += ["", "## ABC triple hunter (search only)", ""]
    md += _md_table(aheaders, arows)
    md += ["", "## S-unit certificates (finite completeness, not abc)", ""]
    md += _md_table(sheaders, srows)
    md += ["", "## ABC proof track (all targets unproved)", ""]
    md += _md_table(rheaders, rrows)
    md += ["", "Every reduction family is re-checked by the Axiom kernel at merge time. "
           "ABC records are exact integer triples re-checked by the merger; the hunter "
           "does not prove the abc conjecture. S-unit certificates are finite complete "
           "lists for a fixed S, independently re-checked; they say nothing about abc. "
           "The Lean export checks only the listed triples, not completeness. "
           + footer, ""]
    for p, st, _lean_st in abc:
        if not st:
            continue
        best = st.get("best_triple")
        if best:
            md.append(f"- {p['id']}: best record {best['a']} + {best['b']} = {best['c']}, "
                      f"rad(abc) = {best['rad']}, q = {best['q']:.9f}. Search only; no proof.")
            md.append("")
    with open(os.path.join(root, "SUMMARY.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", default="swarm/queue.json")
    ap.add_argument("--results", default="results")
    a = ap.parse_args(argv)
    build(a.queue, a.results)


if __name__ == "__main__":
    main()
