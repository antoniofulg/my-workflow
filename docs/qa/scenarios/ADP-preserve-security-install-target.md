---
id: ADP-preserve-security-install-target
area: ADP
title: Preserve the target when security installation succeeds or fails
persona: Workflow adopter
journey: J-enable-external-security-skills
expected: Installation preserves consumer-owned files and unrelated lock entries byte-for-byte, and any refused or failed run returns non-zero, restores the pre-install target, and reports that the security gate remains unavailable.
entry_points: scripts/install_security_skills.py; skills-lock.json; .agents/skills/; .claude/skills/
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-external-security-skills/session.md
last_report: docs/qa/reports/2026-08-22-external-security-skills.md
overlaps:
---

Owns the user-observable preservation and fail-closed outcomes in `SSK-04` and `SSK-05`. Internal
staging, no-follow validation, environment scrubbing, locking, and rollback mechanics remain owned
by technical verification.
