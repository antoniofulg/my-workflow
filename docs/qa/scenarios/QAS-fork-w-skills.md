---
id: QAS-fork-w-skills
area: QAS
title: Fork each w skill into a fresh agent
persona: Workflow adopter
journey: J-adopt-workflow
expected: Each of the seven w skills is marked to run in a fresh agent with the documented role and argument, the five phase skills and wqa bind the slash argument and stop when it is missing, and a spawned implementer still receives wimplement and ponytail without a Skill tool.
entry_points: .agents/skills/wspecify/SKILL.md; .agents/skills/wdesign/SKILL.md; .agents/skills/wtasks/SKILL.md; .agents/skills/wimplement/SKILL.md; .agents/skills/wverify/SKILL.md; .agents/skills/wreview/SKILL.md; .agents/skills/wqa/SKILL.md; templates/agents/claude/implementer.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: QAS-resolve-phase-skill-procedures; CFG-preload-agent-skills-in-packets
---

New promise from `w-entry-points`. Every `w*` skill carries `context: fork`,
`background: false`, an `argument-hint`, and `agent:` planner / planner /
planner / implementer / verifier / planner / verifier. The five phase skills
and `wqa` bind `$ARGUMENTS` on the first body line and stop on a slash-empty
argument; `wreview` takes optional flags. The Claude implementer template still
preloads `wimplement` and `ponytail` with `disallowedTools: Skill`.

The live host return — a `/wspecify a` then `/wspecify b` pair that leaves only
two summaries in the main chat — is the same promise's runtime half. The
CLI/manual adapter inspects the keys that request it; a missing slash session
leaves that leg `untested`, not `blocked-verify`.

`CFG-preload-agent-skills-in-packets` remains the canonical owner of sync
preload and refusal. This scenario owns only the fork keys and the implementer
preload canary.
