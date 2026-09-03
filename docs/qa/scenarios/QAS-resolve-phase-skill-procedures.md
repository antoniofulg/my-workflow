---
id: QAS-resolve-phase-skill-procedures
area: QAS
title: Resolve each phase procedure through its own skill
persona: Workflow adopter
journey: J-adopt-workflow
expected: Each of the five phase skills is invocable, carries the procedure for its phase, and every template, reference, and validator path it names exists, while the router names the phase skills and links no retired reference file.
entry_points: .agents/skills/wspecify/SKILL.md; .agents/skills/wdesign/SKILL.md; .agents/skills/wtasks/SKILL.md; .agents/skills/wimplement/SKILL.md; .agents/skills/wverify/SKILL.md; .agents/skills/workflow-spec-driven/SKILL.md; .agents/skills/workflow-spec-driven/references/
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-03-w-entry-points/16-frontmatter-assert.txt; docs/qa/evidence/2026-09-03-w-entry-points/20-pointer-resolution.txt; docs/qa/evidence/2026-09-03-w-entry-points/20-pointer-fragment-note.txt
last_report: docs/qa/reports/2026-09-03-w-entry-points.md
overlaps: QAS-fork-w-skills; QAS-list-seven-w-entries
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

The `w-entry-points` feature rewrites those five frontmatters (fork keys, `Argument:` in
`description`, slash-scoped empty-arg line). Procedure and pointer resolution must be reconfirmed
against the new files, so this row is reset to `untested`. Fork keys and the seven-name menu are
owned by `QAS-fork-w-skills` and `QAS-list-seven-w-entries`. Prior evidence remains historical.
