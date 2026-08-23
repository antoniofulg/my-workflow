---
id: QAS-observe-serialized-deep-review-metrics
area: QAS
title: Observe metrics without changing serial Deep Review results
persona: Workflow operator
journey: J-run-deep-review
expected: Reviewer jobs and retries run one at a time, valid outputs survive, compatible telemetry produces content-safe totals, and unavailable telemetry changes neither the review result nor exit behavior.
entry_points: .agents/skills/deep-review/SKILL.md; .agents/skills/deep-review/scripts/run_jobs.py; .agents/skills/deep-review/references/subagent-runtimes.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md; docs/qa/evidence/2026-08-22-deep-review-walkthrough-upsert/session.md
last_report: docs/qa/reports/2026-08-22-deep-review-walkthrough-upsert.md
overlaps:
---

Covers `DRM-01` through `DRM-05`, `DRM-07`, and `DRM-08`: snapshots and cumulative
checkpoints, preserved outputs, non-blocking fallback, serial execution, content-safe persistence,
the Codex allowlist, and honest absence for unsupported telemetry.
The issue #29 QA cycle reconfirmed the adjacent eight-test Deep Review contract after exercising
walkthrough publication through the public recipe.
