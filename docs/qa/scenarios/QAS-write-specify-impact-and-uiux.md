---
id: QAS-write-specify-impact-and-uiux
area: QAS
title: Write Specify Impact and uiux.md before design
persona: Workflow adopter
journey: J-adopt-workflow
expected: The installed Specify procedure writes an Impact section after the dimensions sweep and, when a screen is added or changed, a uiux.md before the closure gate; Design loads that uiux.md and dispatches designer; Verify reruns the named scenario ids or reports no reruns when Impact is none; the spec template carries Impact between Assumptions and User Stories.
entry_points: .agents/skills/wspecify/SKILL.md; .agents/skills/wspecify/references/spec-template.md; .agents/skills/wdesign/SKILL.md; .agents/skills/wverify/SKILL.md; docs/guidelines/UI-UX.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-specify-impact-designer/15-installed-tree.txt; docs/qa/evidence/2026-09-03-specify-impact-designer/16-wspecify-impact.txt; docs/qa/evidence/2026-09-03-specify-impact-designer/17-spec-template.txt; docs/qa/evidence/2026-09-03-specify-impact-designer/18-uiux-guideline.txt; docs/qa/evidence/2026-09-03-specify-impact-designer/19-wdesign.txt; docs/qa/evidence/2026-09-03-specify-impact-designer/20-wverify.txt
last_report: docs/qa/reports/2026-09-03-specify-impact-designer.md
overlaps: QAS-resolve-phase-skill-procedures
---

New promise from `specify-impact-designer`. Specify now maps blast radius and screens before
stories freeze. What breaks silently is a spec that ships with no Impact list and a uiux.md
written after design.

`QAS-resolve-phase-skill-procedures` still owns path resolution on the five phase skills.
This scenario owns the Impact, uiux.md, designer-dispatch, and Impact-rerun steps.
