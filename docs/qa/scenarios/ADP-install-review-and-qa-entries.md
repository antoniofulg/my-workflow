---
id: ADP-install-review-and-qa-entries
area: ADP
title: Install the review and QA entry skills with the core layer
persona: Workflow adopter
journey: J-adopt-workflow
expected: A core-layer adoption reports the review and QA entry skills as managed and leaves each SKILL.md plus a .claude/skills link that opens the same file.
entry_points: README.md#adopt-the-workflow; python3 scripts/adopt.py plan <target> --layers core --json; python3 scripts/adopt.py apply <target> --layers core; python3 scripts/adopt.py status <target>; .agents/skills/wreview; .agents/skills/wqa; .claude/skills/
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-w-entry-points/11-plan-core.json; docs/qa/evidence/2026-09-03-w-entry-points/12-target-after-plan.txt; docs/qa/evidence/2026-09-03-w-entry-points/13-apply-core.log; docs/qa/evidence/2026-09-03-w-entry-points/14-status.log; docs/qa/evidence/2026-09-03-w-entry-points/15-skill-links.txt; docs/qa/evidence/2026-09-03-w-entry-points/17-body-lines.txt
last_report: docs/qa/reports/2026-09-03-w-entry-points.md
overlaps: ADP-install-phase-skills; ADP-adopt-workflow-safely; ADP-layered-workflow-adoption
---

New promise from `w-entry-points`. `scripts/adopt.py` `CORE_PATHS` gained
`.agents/skills/wreview` and `.agents/skills/wqa`. The checkout tracks
`.claude/skills/wreview` and `.claude/skills/wqa` as symlinks to
`../../.agents/skills/<name>`. A core `plan --json` lists those four paths;
after `apply`, both read paths open one file.

Each installed entry stays under 40 lines. The `wreview` body names
`.agents/skills/deep-review/SKILL.md` and refuses `--publish`. The `wqa` body
runs exactly one QA phase (`qa-plan` when the first argument is `plan`, else
`qa-execute`) and stops when no journey carries the flow tag.

`ADP-install-phase-skills` still owns the original five phase-skill
directories. This scenario owns only the two entry skills and their wrap
instructions.
