---
id: CFG-keep-local-artifacts-out-of-git
area: CFG
title: Keep disposable workflow artifacts out of Git
persona: Workflow adopter
journey: J-adopt-workflow
expected: Git ignores generated Deep Review and Graft cache trees while versioned feature workflow state and other durable sources remain eligible for review and Graft cards remain searchable.
entry_points: .gitignore; .ignore; scripts/adopt.py; .specs/AD-INDEX.md; .deep-review/learnings.md; graft/
qa_status: untested
bug_ids: BUG-20260822-adoption-omits-graft-ignores; BUG-20260822-feature-specs-ignored
fix_status: pending
retest_status: untested
fix_commits:
evidence: docs/qa/evidence/2026-08-22-deep-review-metrics-graft/session.md; docs/qa/evidence/2026-08-22-deep-review-learnings-retest/session.md
last_report: docs/qa/reports/2026-08-22-deep-review-learnings-retest.md
overlaps:
---

Covers selective local-artifact ignores, searchable Graft cards, versioned feature workflow state,
and preservation of unrelated target ignore entries during adoption. The Graft cache and
search-ignore contract passed previously; issue #31's feature-state migration remains untested.
