---
id: QAS-discover-independent-qa-skills
area: QAS
title: Discover independent QA skills through the existing Verifier
persona: Workflow adopter
journey: J-adopt-workflow
expected: The adopted tree exposes qa-plan and qa-execute, and every provider routes each phase through its existing Verifier contract.
entry_points: .agents/skills/qa-plan/SKILL.md; .agents/skills/qa-execute/SKILL.md; .cursor/agents/verifier.md; .claude/agents/verifier.md; .codex/agents/verifier.toml
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-20-workflow-0.3.0/session.md
last_report: docs/qa/reports/2026-08-20-workflow-0.3.0.md
overlaps:
---

Covers skill discovery, planning/execution separation, scenario-authority routing, adapter reporting,
and the Implementer → fresh Verifier defect handoff.
