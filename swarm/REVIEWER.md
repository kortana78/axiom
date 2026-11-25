# Reviewer instructions (for the scheduled Claude check, or a human)

Each review:
1. Read results/SUMMARY.md, results/*/status.json (history), results/*/lean_status.json.
2. Write a short entry at the top of swarm/REVIEW_LOG.md: time (UTC), per problem the
   open classes, change since last review, Lean summary, anything broken (failed jobs,
   rejected families, Lean errors).
3. Steer only through swarm/queue.json:
   - adjust grammar T, D or start_modulus for a stalled problem
   - set active false for a problem that has stalled for many batches
   - add a new problem in the blind format (statement only, no hints or answers)
4. Never edit results/ by hand and never mark anything proved. Only the kernel merge and
   Lean decide status.
5. If any status says PROVED: stop and flag it loudly at the top of REVIEW_LOG.md, so a human
   checks the Lean output before anyone announces anything.
6. Commit with message "review: <one line>" and push.
