---
id: QAS-list-seven-w-entries
area: QAS
title: List exactly seven workflow entries in the /w menu
persona: Workflow adopter
journey: J-adopt-workflow
expected: The /w menu and the pack guide each show exactly the same seven workflow entries, every entry's one-line hint starts with the phase name and states its argument, and roadmap slice 2 is marked done.
entry_points: .agents/skills/wspecify/SKILL.md; .agents/skills/wdesign/SKILL.md; .agents/skills/wtasks/SKILL.md; .agents/skills/wimplement/SKILL.md; .agents/skills/wverify/SKILL.md; .agents/skills/wreview/SKILL.md; .agents/skills/wqa/SKILL.md; .claude/skills/; docs/workflow/pack.md; docs/workflow/roadmap.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-w-entry-points/16-frontmatter-assert.txt; docs/qa/evidence/2026-09-03-w-entry-points/70-doc-provenance-table.txt; docs/qa/evidence/2026-09-03-w-entry-points/70-doc-provenance.txt
last_report: docs/qa/reports/2026-09-03-w-entry-points.md
overlaps: QAS-resolve-phase-skill-procedures; DOC-read-explicit-workflow-provenance
---

New promise from `w-entry-points`. The human types `/w` and must see exactly
`wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`, `wreview`, and `wqa`.
Each `description` starts with the phase name and contains `Argument:`.
`docs/workflow/pack.md` lists those seven rows; roadmap slice 2 ends `(done)`.

`QAS-resolve-phase-skill-procedures` still owns procedure pointers on the five
phase skills. This scenario owns only the seven-name menu and the docs that
must match it.
