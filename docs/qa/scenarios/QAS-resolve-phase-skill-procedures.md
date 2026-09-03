---
id: QAS-resolve-phase-skill-procedures
area: QAS
title: Resolve each phase procedure through its own skill
persona: Workflow adopter
journey: J-adopt-workflow
expected: Each of the five phase skills is invocable, carries the procedure for its phase, and every template, reference, and validator path it names exists, while the router names the phase skills and links no retired reference file.
entry_points: .agents/skills/wspecify/SKILL.md; .agents/skills/wdesign/SKILL.md; .agents/skills/wtasks/SKILL.md; .agents/skills/wimplement/SKILL.md; .agents/skills/wverify/SKILL.md; .agents/skills/workflow-spec-driven/SKILL.md; .agents/skills/workflow-spec-driven/references/
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

New promise from the `phase-skills` feature. The five phase procedures moved out of
`workflow-spec-driven/references/{specify,design,tasks,implement,validate}.md` into
`.agents/skills/w<phase>/SKILL.md`, with their artifact templates under each skill's `references/`.
`discuss.md` now lives at `wspecify/references/discuss.md`; `lessons.md`, `memory.md`,
`sub-agents.md`, `code-analysis.md`, and `coding-principles.md` stay with the router.

What breaks silently here is a pointer. An agent that preloads `wimplement` and follows a path that
no longer exists loses the rule at the moment it needs it, and nothing in the gate notices. The walk
therefore follows the paths as written: every relative template reference, every
`.agents/skills/workflow-spec-driven/scripts/<name>.py` citation, and every phase named by the
router.

Frontmatter is part of the promise: each skill's `name` equals its directory, no
`disable-model-invocation` key is present (it would block preload), and the `description` names the
agent that preloads it and its `/w<phase>` entry.
