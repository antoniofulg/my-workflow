---
id: QAS-observe-serialized-deep-review-metrics
area: QAS
title: Observe serialized metrics during bounded Deep Review
persona: Workflow operator
journey: J-run-deep-review
expected: Bounded reviewers produce serialized cumulative checkpoints without per-job attribution, valid outputs survive, totals finalize only after full completion, and unavailable telemetry changes neither the review result nor exit behavior.
entry_points: .agents/skills/deep-review/SKILL.md; .agents/skills/deep-review/scripts/run_jobs.py; .agents/skills/deep-review/references/subagent-runtimes.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-25-parallel-deep-review/qa-summary.json; docs/qa/evidence/2026-08-25-parallel-deep-review/metrics.log; docs/qa/evidence/2026-08-25-parallel-deep-review/metrics-partial.log; docs/qa/evidence/2026-08-25-parallel-deep-review/metrics-full-resume.log
last_report: docs/qa/reports/2026-08-25-parallel-deep-review.md
overlaps:
---

Covers `DRM-01` through `DRM-05`, `DRM-07`, and `DRM-08`: snapshots and cumulative
checkpoints, preserved outputs, non-blocking fallback, content-safe persistence, the Codex
allowlist, and honest absence for unsupported telemetry. `PDR-05` changes the execution context:
checkpoint writes remain serialized while reviewer jobs overlap, checkpoints claim no job owner,
and final totals require a complete full scope.
The issue #29 QA cycle reconfirmed the adjacent eight-test Deep Review contract after exercising
walkthrough publication through the public recipe.

The prior report and evidence remain historical. Parallel Deep Review resets the current verdict
until the bounded-run metrics path is walked through the public CLI/manual adapter.

QA on 2026-08-25 confirmed four serialized cumulative checkpoints under overlap, no per-job
attribution, `running` after narrowed `--only`, complete totals after full resume, and unchanged
successful results when telemetry was unavailable.
