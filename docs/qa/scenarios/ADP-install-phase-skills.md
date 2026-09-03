---
id: ADP-install-phase-skills
area: ADP
title: Install the five phase skills with the core layer
persona: Workflow adopter
journey: J-adopt-workflow
expected: A core-layer adoption reports the five phase skill directories as managed and leaves the target holding each `.agents/skills/w<phase>/SKILL.md` plus a `.claude/skills/w<phase>` link that resolves to it, while re-adoption preserves consumer-owned skill trees.
entry_points: README.md#adopt-the-workflow; python3 scripts/adopt.py plan <target> --layers core --json; python3 scripts/adopt.py apply <target> --layers core; python3 scripts/adopt.py status <target>; .agents/skills/wspecify; .agents/skills/wdesign; .agents/skills/wtasks; .agents/skills/wimplement; .agents/skills/wverify; .claude/skills/
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: ADP-adopt-workflow-safely; ADP-layered-workflow-adoption
---

New promise from the `phase-skills` feature. `scripts/adopt.py` `CORE_PATHS` gained
`.agents/skills/wspecify`, `wdesign`, `wtasks`, `wimplement`, and `wverify`, and `_prepare_sync`
now treats `.agents/skills` as a sync input alongside `templates/agents`. The checkout tracks
`.claude/skills/w<phase>` as symlinks to `../../.agents/skills/w<phase>`.

The observable an adopter cares about is the installed result, not the catalog constant: after a
core apply the target must be able to open each phase procedure through both the canonical path and
the Claude link, and a second apply over a target carrying consumer-owned skills must not clobber
them.

`ADP-adopt-workflow-safely` and `ADP-layered-workflow-adoption` remain the canonical owners of the
general adoption safety and layering promises; this scenario owns only the phase-skill membership
and link resolution.
