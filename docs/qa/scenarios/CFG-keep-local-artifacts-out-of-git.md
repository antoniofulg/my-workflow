---
id: CFG-keep-local-artifacts-out-of-git
area: CFG
title: Keep disposable workflow artifacts out of Git
persona: Workflow adopter
journey: J-adopt-workflow
expected: Git ignores generated Deep Review and feature-planning trees while durable learnings, decisions, and consumer ignore rules remain eligible for review.
entry_points: .gitignore; scripts/adopt.py; .specs/AD-INDEX.md; .deep-review/learnings.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-21-configurable-workflow/adoption-session.md
last_report: docs/qa/reports/2026-08-21-configurable-workflow.md
overlaps:
---

Covers selective local-artifact ignores, local task-state semantics, removal of historical disposable
feature files, and preservation of unrelated target ignore entries during adoption.
