---
id: QAS-use-graft-context-with-plain-fallback
area: QAS
title: Use optional Graft context with plain-inspection fallback
persona: Workflow operator
journey: J-run-deep-review
expected: Deep Review prompts receive Graft orientation when available and explicit plain-inspection guidance whenever Graft is absent, fails, is stale, or cannot cover selected dot-directories.
entry_points: .agents/skills/deep-review/SKILL.md; .agents/skills/deep-review/scripts/build_jobs.py; .agents/skills/deep-review/scripts/graft_context.py; package.json
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md
last_report: docs/qa/reports/2026-08-22-deep-review-metrics-graft.md
overlaps:
---

Covers the operator-visible part of `DRM-06`: pinned optional Graft preparation before prompt
materialization and non-blocking plain repository inspection for every unsupported path or failure.
