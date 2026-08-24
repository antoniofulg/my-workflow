---
id: CFG-keep-local-artifacts-out-of-git
area: CFG
title: Keep disposable workflow artifacts out of Git
persona: Workflow adopter
journey: J-adopt-workflow
expected: Git ignores generated Deep Review and Graft cache trees while feature workflow state travels through worktrees and CI, task status commits atomically with its task, other durable sources remain reviewable, and Graft cards remain searchable.
entry_points: .gitignore; .ignore; scripts/adopt.py; AGENTS.md; .agents/skills/tlc-spec-driven/references/implement.md; .specs/features/<feature>/tasks.md; .deep-review/learnings.md; graft/
qa_status: untested
bug_ids: BUG-20260822-adoption-omits-graft-ignores; BUG-20260822-feature-specs-ignored; BUG-20260822-feature-state-gate-conflicts
fix_status: fixed
retest_status: pass
fix_commits: b509b10; a7397d2; 43e9910; a3fc718; 5b5474e
evidence:
last_report:
overlaps:
---

Covers selective local-artifact ignores, searchable Graft cards, versioned feature workflow state,
atomic task-state commits, and preservation of unrelated target ignore entries during adoption. The
Graft cache and search-ignore contract passed previously; issue #31's feature-state migration and
Git handoff passed on 2026-08-22 through fresh and legacy adoption, an atomic task-status commit, a
sibling worktree, and a clean clone.
