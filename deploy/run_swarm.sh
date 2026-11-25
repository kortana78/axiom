#!/usr/bin/env bash
# Run the AXIOM swarm 24/7 on any Linux machine (for example an Oracle Cloud
# Always Free VM). One worker per CPU core by default.
#
#   WORKERS=4 MINUTES=50 PUSH=1 ./deploy/run_swarm.sh
#
# PUSH=1 commits results/ and pushes (configure a git remote with a token first).
set -u
cd "$(dirname "$0")/.."
WORKERS=${WORKERS:-$(nproc)}
MINUTES=${MINUTES:-50}
PUSH=${PUSH:-0}
while true; do
  [ "$PUSH" = "1" ] && git pull --rebase --autostash -q || true
  PIDS=$(python3 -c "from axiom.swarm.common import load_queue; print(' '.join(p['id'] for p in load_queue() if p.get('active')))")
  N=$(echo $PIDS | wc -w); [ "$N" -eq 0 ] && { sleep 600; continue; }
  SECS=$(( MINUTES * 60 / N ))
  for pid in $PIDS; do
    # one core runs the idea generator, the rest run normal workers
    W=$(( WORKERS > 1 ? WORKERS - 1 : 1 ))
    for i in $(seq 0 $((W-1))); do
      python3 -m axiom.swarm.worker --problem "$pid" --shard "$i" --of "$W" --time "$SECS" &
    done
    [ "$WORKERS" -gt 1 ] && python3 -m axiom.ideas.run --problem "$pid" --time "$SECS" &
    wait
  done
  python3 -m axiom.swarm.merge && python3 -m axiom.swarm.dashboard
  if [ "$PUSH" = "1" ]; then
    git add results && git commit -qm "swarm (vm): merge batch [skip ci]" && git pull --rebase -q && git push -q || true
  fi
done
