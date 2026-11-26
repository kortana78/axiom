#!/usr/bin/env bash
# Run the AXIOM swarm on any Linux machine (for example an Oracle Cloud
# Always Free VM).  One scheduler process per CPU core works the same capped
# queue of up to 1000 work items.
#
#   WORKERS=4 MINUTES=45 PUSH=1 ./deploy/run_swarm.sh
#
# PUSH=1 commits results/ and the validated idea files, then pushes
# (configure a git remote with a token first).
set -u
cd "$(dirname "$0")/.."
WORKERS=${WORKERS:-$(nproc)}
MINUTES=${MINUTES:-45}
MAX_ITEMS=${MAX_ITEMS:-1000}
SHARDS=${SHARDS:-10}
IDEAS_PER_SHARD=${IDEAS_PER_SHARD:-0}
PUSH=${PUSH:-0}

while true; do
  [ "$PUSH" = "1" ] && git pull --rebase --autostash -q || true
  for i in $(seq 0 $((WORKERS - 1))); do
    python3 -m axiom.swarm.schedule \
      --runner "$i" --runners "$WORKERS" \
      --minutes "$MINUTES" --max-items "$MAX_ITEMS" --shards "$SHARDS" \
      --ideas-per-shard "$IDEAS_PER_SHARD" \
      --idea-file swarm/llm_ideas.json &
  done
  wait
  python3 -m axiom.swarm.schedule --summarize
  python3 -m axiom.swarm.merge
  python3 -m axiom.swarm.dashboard
  if [ "$PUSH" = "1" ]; then
    git add results swarm/llm_ideas.json swarm/sunit_ideas.json swarm/abc_ideas.json 2>/dev/null || true
    git commit -qm "swarm (vm): scheduler batch [skip ci]" || true
    git pull --rebase -q && git push -q || true
  fi
  sleep 60
done
