---
id: CFG-keep-local-artifacts-out-of-git
area: CFG
title: Keep disposable workflow artifacts out of Git
persona: Workflow adopter
journey: J-adopt-workflow
expected: Git ignores generated Deep Review, feature-planning, and Graft cache trees while durable workflow sources remain eligible for review and Graft cards remain searchable.
entry_points: .gitignore; .ignore; scripts/adopt.py; .specs/AD-INDEX.md; .deep-review/learnings.md; graft/
qa_status: pass
bug_ids: BUG-20260822-adoption-omits-graft-ignores
fix_status: fixed
retest_status: pass
fix_commits: b509b10
evidence: docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md; docs/qa/evidence/2026-08-22-deep-review-learnings-retest/session.md
last_report: docs/qa/reports/2026-08-22-deep-review-learnings-retest.md
overlaps:
---

Covers selective local-artifact ignores, searchable Graft cards, local task-state semantics,
removal of historical disposable feature files, and preservation of unrelated target ignore entries
during adoption. Retested after `b509b10`; the Graft cache and search-ignore contract now passes.
Issue #28's adjacent canary on 2026-08-22 reconfirmed generated Deep Review, feature, and Graft cache
artifacts stay ignored while durable learnings remain trackable and Graft cards remain searchable.
