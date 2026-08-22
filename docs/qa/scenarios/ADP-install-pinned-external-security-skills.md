---
id: ADP-install-pinned-external-security-skills
area: ADP
title: Install exactly the reviewed external security skills
persona: Workflow adopter
journey: J-enable-external-security-skills
expected: The unauthorised command makes no changes, while the exact authorized command installs only three skill trees and matching Claude links whose source, path, CLI version, commit, and tree hash match skills-lock.json.
entry_points: scripts/install_security_skills.py; skills-lock.json; .agents/skills/; .claude/skills/
qa_status: pass
bug_ids: BUG-20260822-security-installer-rejects-active-npx
fix_status: fixed
retest_status: pass
fix_commits: 1fa087d; 7795295
evidence: docs/qa/evidence/2026-08-22-external-security-skills/session.md
last_report: docs/qa/reports/2026-08-22-external-security-skills.md
overlaps:
---

Owns the public authorization, provenance, and installed-result promises in `SSK-02`, `SSK-03`,
and `SSK-06`, including visible rejection of moving or unreviewed metadata.
