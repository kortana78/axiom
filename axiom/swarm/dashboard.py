"""Build a plain static dashboard: results/index.html (and results/SUMMARY.md)."""
from __future__ import annotations

import argparse
import html
import os
import time

from .common import load_json, load_queue


def build(queue_path="swarm/queue.json", root="results"):
    rows, md = [], ["# AXIOM swarm summary", "",
                    f"updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}", "",
                    "| problem | status | modulus | open / relevant | families | last note |",
                    "|---|---|---|---|---|---|"]
    for p in load_queue(queue_path):
        st = load_json(os.path.join(root, p["id"], "status.json"), None)
        lean = load_json(os.path.join(root, p["id"], "lean_status.json"), {}) or {}
        if not st:
            rows.append(f"<tr><td>{p['id']}</td><td colspan=5>no results yet</td></tr>")
            md.append(f"| {p['id']} | no results yet | | | | |")
            continue
        note = st["history"][-1]["note"] if st.get("history") else ""
        lean_txt = lean.get("summary", "Lean not run")
        rows.append("<tr>" + "".join(f"<td>{html.escape(str(x))}</td>" for x in (
            p["id"], st["status"], st["modulus"], f"{st['open_classes']} / {st['relevant_classes']}",
            st["families_verified"], note, lean_txt)) + "</tr>")
        md.append(f"| {p['id']} | {st['status']} | {st['modulus']} | {st['open_classes']} / "
                  f"{st['relevant_classes']} | {st['families_verified']} | {note} |")
        md.append("")
        md.append(f"- {p['id']}: {st['reduction_statement']}. Open sample: {st['open_sample'][:24]}. Lean: {lean_txt}")
        md.append("")
    page = ("<!doctype html><html><head><meta charset=utf-8><title>AXIOM swarm</title>"
            "<style>body{font-family:sans-serif;margin:2em}td,th{border:1px solid #999;padding:4px 8px}"
            "table{border-collapse:collapse}</style></head><body><h1>AXIOM swarm</h1>"
            f"<p>updated {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}</p>"
            "<table><tr><th>problem</th><th>status</th><th>modulus</th><th>open / relevant</th>"
            "<th>families</th><th>last note</th><th>Lean</th></tr>" + "".join(rows) + "</table>"
            "<p>Every family is re-checked by the Axiom kernel at merge time. "
            "'Lean' shows whether Lean accepted the exported class lemmas.</p></body></html>")
    os.makedirs(root, exist_ok=True)
    with open(os.path.join(root, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(page)
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
