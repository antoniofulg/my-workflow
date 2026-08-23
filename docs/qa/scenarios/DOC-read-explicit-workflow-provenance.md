---
id: DOC-read-explicit-workflow-provenance
area: DOC
title: Read explicit provenance and remote-delivery authority
persona: Repository reader
journey: J-review-workflow-release
expected: The README, pack guide, and autonomous skill distinguish bundled local adaptations from their linked sources and state that readiness never authorizes push, pull request, or merge without separate approval.
entry_points: README.md; docs/workflow/pack.md; skills-lock.json; .agents/skills/qa-plan/SKILL.md; .agents/skills/qa-execute/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/reports/2026-08-22-explicit-remote-approval.md; docs/qa/evidence/2026-08-22-external-security-skills/session.md; docs/qa/evidence/2026-08-22-version-feature-specs-handoff/session.md; docs/qa/evidence/2026-08-22-ponytail-full-cycle/session.md
last_report: docs/qa/reports/2026-08-22-explicit-remote-approval.md
overlaps:
---

Covers public provenance, authorship, clean-room adaptation language, the bundled-versus-external
security-skill boundary in `SSK-07`, the reusable package's stack-agnostic scope, and the remote
delivery boundary in issue #25. The current pass was obtained after reading the canonical sources and
running the cross-file contract tests on this tree.
