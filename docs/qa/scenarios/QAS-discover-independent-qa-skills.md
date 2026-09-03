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
evidence: docs/qa/evidence/2026-08-25-release-0-6-0/retest-contracts.json; docs/qa/evidence/2026-08-25-release-0-6-0/retest-npm-test.log; docs/qa/evidence/2026-08-25-release-0-6-0/retest-removal-contract.log
last_report: docs/qa/reports/2026-08-25-release-0-6-0.md
overlaps:
---

Covers skill discovery, planning/execution separation, scenario-authority routing, adapter reporting,
and the Implementer → fresh Verifier defect handoff. QA retest on 2026-08-25 after fix `1593299`
passed: all six provider templates and generated runtime packets carried the fresh-packet contract
and independent evidence sources after reload.

The `phase-skills` feature rewrites the provider Verifier packets this scenario inspects: the Claude template gains `skills: [wverify]`, and the Cursor and Codex bodies name phase skills in place of retired reference files. The qa-plan/qa-execute routing promise must be reconfirmed against the new packets, so it is reset to `untested` pending the 2026-09-03 cycle. Prior evidence remains historical.
