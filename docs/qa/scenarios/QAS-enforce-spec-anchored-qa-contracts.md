---
id: QAS-enforce-spec-anchored-qa-contracts
area: QAS
title: Enforce spec-anchored QA contracts
persona: Workflow adopter
journey: J-adopt-workflow
expected: Each QA cycle creates a new dated charter, every test case maps to a spec acceptance criterion, and filed-issue QA runs only when the fix changes a public promise.
entry_points: docs/guidelines/QA-EXECUTION.md; docs/guidelines/TEST-CONTRACT.md; docs/guidelines/REVIEW-ROUNDS.md; .agents/skills/qa-plan/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-spec-anchored-qa-contracts/session.md
last_report: docs/qa/reports/2026-08-22-spec-anchored-qa-contracts.md
overlaps:
---

Covers the public planning contract for immutable per-cycle charters, acceptance-criterion-derived
test cases, and conditional QA in the filed-issue shortcut. The current pass independently re-read
all contract authorities after reload and ran the focused structural test.
