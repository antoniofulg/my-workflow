---
id: QAS-enforce-spec-anchored-qa-contracts
area: QAS
title: Enforce spec-anchored QA contracts
persona: Workflow adopter
journey: J-adopt-workflow
expected: Each QA cycle creates a new dated charter, every test case maps to a spec acceptance criterion, and Minor defects close in the active feature run without a fresh proof cycle.
entry_points: docs/guidelines/QA-EXECUTION.md; docs/guidelines/TEST-CONTRACT.md; docs/guidelines/REVIEW-ROUNDS.md; .agents/skills/qa-plan/SKILL.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Covers immutable per-cycle charters, acceptance-criterion-derived test cases, and severity-routed QA
remediation. Minor findings stay in the originating feature context: one remediation batch, one
scoped gate, and the current QA Execute session re-walks the affected journey without a fresh
Technical Verifier, QA session, or deep-review round. Blocker and Major fixes retain the fresh-proof
loop; Cosmetic findings retain the filed-issue shortcut.
