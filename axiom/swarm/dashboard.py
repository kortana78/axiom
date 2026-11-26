"""Build a plain static dashboard: results/index.html (and results/SUMMARY.md)."""
from __future__ import annotations

import argparse
import html
import os
import time

from .common import load_json, load_queue


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
    witness, abc = [], []
    for p in problems:
        st = load_json(os.path.join(root, p["id"], "status.json"), None)
        lean = load_json(os.path.join(root, p["id"], "lean_status.json"), {}) or {}
        if p.get("kind") == "abc" or (st and st.get("kind") == "abc"):
            abc.append((p, st, lean))
        else:
            witness.append((p, st, lean))

    wheaders = ["problem", "status", "modulus", "open / relevant", "families", "last note", "Lean"]
    aheaders = ["problem", "status", "c max", "best q", "records", "last note", "Lean"]
    wrows = [_witness_row(p, st, lean) for p, st, lean in witness]
    arows = [_abc_row(p, st, lean) for p, st, lean in abc]

    updated = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    page = (
        "<!doctype html><html><head><meta charset=utf-8><title>AXIOM swarm</title>"
        "<style>body{font-family:sans-serif;margin:2em}td,th{border:1px solid #999;padding:4px 8px}"
        "table{border-collapse:collapse;margin-bottom:2em}</style></head><body>"
        "<h1>AXIOM swarm</h1>"
        f"<p>updated {updated}</p>"
        "<h2>Witness reductions</h2>"
        + _html_table(wheaders, wrows)
        + "<h2>ABC triple hunter (search only)</h2>"
        + _html_table(aheaders, arows)
        + "<p>Every reduction family is re-checked by the Axiom kernel at merge time. "
        "ABC records are exact integer triples re-checked by the merger (gcd, sum, and "
        "radical); the hunter does not prove the abc conjecture.</p>"
        "</body></html>")
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)

    md = ["# AXIOM swarm summary", "", f"updated {updated}", "",
          "## Witness reductions", ""]
    md += _md_table(wheaders, wrows)
    md += ["", "## ABC triple hunter (search only)", ""]
    md += _md_table(aheaders, arows)
    md += ["", "Every reduction family is re-checked by the Axiom kernel at merge time. "
           "ABC records are exact integer triples re-checked by the merger; the hunter "
           "does not prove the abc conjecture.", ""]
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
