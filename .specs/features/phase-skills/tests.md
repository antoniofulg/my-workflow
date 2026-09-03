# Phase Skills Test Contract

Gate (scoped): `python3 tools/test_phase_skills.py && python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py`. Full: `bun run test:python`.

## Unit
| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Five phase skills exist with scoped frontmatter (PSK-01 AC1) | read `.agents/skills/w{specify,design,tasks,implement,verify}/SKILL.md` | each has frontmatter `name` equal to its directory and `disable-model-invocation: true` |
| UT-002 | Line caps hold (PSK-01 AC2, PSK-02 AC1) | `wc -l` on each phase SKILL.md and the router | each phase SKILL.md ≤ 200; router ≤ 150 |
| UT-003 | Moved references are gone and no phase grew (PSK-01 AC5) | list router `references/`; sum lines per phase skill | `specify.md`, `design.md`, `tasks.md`, `implement.md`, `validate.md`, `discuss.md` absent from router; per-phase totals ≤ 228+159 (specify incl. discuss), 193, 443, 426, 339, each plus 10 |
| UT-004 | Router links skills, not references (PSK-02 AC2–4) | grep router SKILL.md | no `references/<phase>.md` link, no `## Commands`, `## Context Loading Strategy`, or `## Coordinator-assisted` heading; sizing table cells contain `wspecify`, `wdesign`, `wtasks`, `wimplement` |
| UT-005 | Claude templates declare preload and tool scope (PSK-03 AC1–2) | parse frontmatter of the five Claude templates | planner `skills` = `[workflow-spec-driven, wspecify, wtasks, ponytail]`, no `disallowedTools`; implementer `skills` = `[wimplement, ponytail]` and `disallowedTools: Skill`; verifier `skills` = `[wverify]`, no `disallowedTools`; explorer and deep-reviewer `disallowedTools: Skill` with unchanged `tools` |
| UT-006 | Every template load line resolves (PSK-03 AC5–6) | scan `## Load` / `## Do not load` lines in all 15 templates for backticked names | every `Skill \`x\`` resolves to `.agents/skills/x/SKILL.md`; every `docs/...` path exists; codex and cursor planner/implementer/verifier bodies name their phase skill and contain no `implement.md`, `validate.md`, `specify.md`, `tasks.md` reference-file token |
| UT-007 | Claude symlinks resolve (PSK-04 AC1) | `os.readlink` on `.claude/skills/w*` | each is a symlink to `../../.agents/skills/<name>` and `git ls-files` lists it |
| UT-008 | Phase skills cite validator and template paths that exist (PSK-01 AC3–4) | grep each phase SKILL.md for `scripts/*.py` and `references/*.md` tokens | every validator token starts with `.agents/skills/workflow-spec-driven/scripts/` and exists; every `references/` token resolves inside that skill |
| UT-009 | Docs list the skills (PSK-04 AC3–4) | read `docs/workflow/pack.md`, `docs/workflow/roadmap.md`, `AGENTS.md` | pack table rows for all five skills; roadmap contains "under 200 lines"; `AGENTS.md` ≤ 134 lines |

## Integration
| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Sync passes preload keys through (PSK-03 AC3) | copy repo templates, toml example, and skills into a temp root; run `workflow_config.py --root <tmp> --sync-agents` | generated `.claude/agents/implementer.md` equals the template except the `model:` and `effort:` lines; `skills:` and `disallowedTools:` lines byte-identical |
| IT-002 | Sync rejects an unknown preload skill (PSK-03 AC4) | same temp root with implementer template `skills: [wimplement, nope]` | exit ≠ 0; stderr names `templates/agents/claude/implementer.md` and `nope`; no file under `.claude/agents/`, `.codex/agents/`, `.cursor/agents/` written |
| IT-003 | Core layer installs the phase skills (PSK-04 AC2) | `adopt.py plan <tmp-target> --layers core --json` from the repo | managed paths include all five `.agents/skills/w*` directories |

## End-to-end
None. No user journey opens; adoption is covered by IT-003 and the existing `J-adopt-workflow` scenarios.

## Security
None. No runtime, schema, auth, or public behaviour surface; docs and skill text only.
