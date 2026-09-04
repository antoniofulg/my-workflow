---
id: QAS-offer-gap-hunt-at-plan-approval
area: QAS
title: Offer a sized gap hunt at plan approval
persona: Workflow adopter
journey: J-adopt-workflow
expected: At plan approval the installed Specify procedure skips a gap hunt for Small, asks for Medium and Large, recommends it for Complex, runs it only for Complex under autonomous while recording the skip in decisions.md, and records settled findings as acceptance criteria or context.md decisions.
entry_points: .agents/skills/wspecify/SKILL.md; .agents/skills/wspecify/references/gap-hunt.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-specify-impact-designer/16-wspecify-impact.txt; docs/qa/evidence/2026-09-03-specify-impact-designer/21-gap-hunt.txt
last_report: docs/qa/reports/2026-09-03-specify-impact-designer.md
overlaps: QAS-write-specify-impact-and-uiux; QAS-resolve-phase-skill-procedures
---

New promise from `specify-impact-designer`. The gap hunt is a question at plan approval, not a
hidden extra phase. What breaks silently is a Small or autonomous Medium run that still launches
explorers, or a settled finding left as a note.

`QAS-write-specify-impact-and-uiux` owns Impact and uiux.md. This scenario owns only the
sized gap-hunt question, frontier rounds, and settlement rule.
