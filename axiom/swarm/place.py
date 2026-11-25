"""Move downloaded artifacts into results/<problem>/ (used by the workflow).

    python -m axiom.swarm.place incoming results

Shard files are named <problem>__*.json. An ideas_log.json sits in an
artifact folder named ideas-<problem>.
"""
import os
import shutil
import sys


def main(src="incoming", dst="results"):
    for root, _, files in os.walk(src):
        for f in files:
            path = os.path.join(root, f)
            if f == "ideas_log.json":
                top = os.path.relpath(path, src).split(os.sep)[0]
                if top.startswith("ideas-"):
                    pid = top[len("ideas-"):]
                    os.makedirs(os.path.join(dst, pid), exist_ok=True)
                    shutil.copy(path, os.path.join(dst, pid, "ideas_log.json"))
            elif f.endswith(".json") and "__" in f:
                pid = f.split("__")[0]
                os.makedirs(os.path.join(dst, pid, "shards"), exist_ok=True)
                shutil.move(path, os.path.join(dst, pid, "shards", f))


if __name__ == "__main__":
    main(*sys.argv[1:3])
