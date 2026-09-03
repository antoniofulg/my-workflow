---
id: DOC-read-explicit-workflow-provenance
area: DOC
title: Read explicit credits and a product-neutral workflow scope
persona: Repository reader
journey: J-review-workflow-release
expected: The README, pack guide, and QA skills distinguish bundled local adaptations from their linked sources and from three separately authorized, pinned external security skills without naming a consuming product or stack.
entry_points: README.md; docs/workflow/pack.md; skills-lock.json; .agents/skills/qa-plan/SKILL.md; .agents/skills/qa-execute/SKILL.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-external-security-skills/session.md; docs/qa/evidence/2026-08-22-version-feature-specs-handoff/session.md; docs/qa/evidence/2026-08-22-ponytail-full-cycle/session.md; docs/qa/evidence/2026-08-22-explicit-remote-approval/session.md; docs/qa/evidence/2026-08-22-version-feature-state-by-default/session.md; docs/qa/evidence/2026-08-22-spec-anchored-qa-contracts/session.md; docs/qa/evidence/2026-08-23-release-0-3-6/session.md
last_report: docs/qa/reports/2026-08-23-release-0-3-6.md
overlaps:
---

Covers public provenance, authorship, clean-room adaptation language, the bundled-versus-external
security-skill boundary in `SSK-07`, and the reusable package's stack-agnostic scope. The current
pass re-read the credits, both QA skill provenance statements, the three immutable external-skill
entries, and the product-neutral introduction as the QA-contract journey's adjacent canary.

The `phase-skills` feature changes the bundled-capability list a reader evaluates: `docs/workflow/pack.md` now declares eleven local capabilities including the five phase skills, `README.md` names the router plus its phase skills, and `docs/workflow/roadmap.md` is new. Reset to `untested` pending the 2026-09-03 cycle. Prior evidence remains historical.
