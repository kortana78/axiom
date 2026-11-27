#!/usr/bin/env bash
# Hourly result sync. Results are public: no keys, no proof slot, no alarm
# verdict. Conflicts are resolved by rebasing; a failed sync never blocks the
# fleet.
set -uo pipefail

cd /opt/axiom || exit 0
git config user.name "axiom-fleet"
git config user.email "axiom-fleet@users.noreply.github.com"

git fetch -q origin main || exit 0
if ! git rebase origin/main; then
  git rebase --abort || true
  echo "sync: rebase conflict; skipping this hour" >&2
  exit 0
fi

git add -A results/abc_prover results/llm_usage.json 2>/dev/null || exit 0
if git diff --cached --quiet; then
  exit 0
fi
git commit -q -m "abc: fleet proof attempts [skip ci]" || exit 0
git push -q origin main || echo "sync: push failed; retry next hour" >&2
exit 0
