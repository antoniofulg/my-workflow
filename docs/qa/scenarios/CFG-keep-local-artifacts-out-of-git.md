---
id: CFG-keep-local-artifacts-out-of-git
area: CFG
title: Keep disposable workflow artifacts out of Git
persona: Workflow adopter
journey: J-adopt-workflow
expected: Git and package output include reviewable workflow sources but exclude local agent config and generated runtimes, while a clean clone can regenerate checkout-local packets and durable feature state remains reviewable.
entry_points: .gitignore; .ignore; .my-workflow.toml.example; .my-workflow.toml; templates/agents/; .claude/agents/; .codex/agents/; .cursor/agents/; package.json; scripts/adopt.py; .specs/features/<feature>/tasks.md; .deep-review/learnings.md; graft/
qa_status: pass
bug_ids: BUG-20260822-adoption-omits-graft-ignores; BUG-20260822-feature-specs-ignored; BUG-20260822-feature-state-gate-conflicts
fix_status: fixed
retest_status: pass
fix_commits: b509b10; a7397d2; 43e9910; a3fc718; 5b5474e
evidence: docs/qa/evidence/2026-08-24-agent-model-routing-local-state/summary.json
last_report: docs/qa/reports/2026-08-24-agent-model-routing-local-state.md
overlaps:
---

Covers tracked example/templates versus ignored local config/runtime packets, package and clean-clone
ownership, selective local-artifact ignores, searchable Graft cards, versioned feature workflow
state, atomic task-state commits, and preservation of unrelated target ignore entries during
adoption. The Graft cache and search-ignore contract passed previously; issue #31's feature-state
migration and Git handoff passed on 2026-08-22 through fresh and legacy adoption, an atomic
task-status commit, a sibling worktree, and a clean clone.
