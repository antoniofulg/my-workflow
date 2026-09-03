# Specify Impact and Designer Test Contract

Gate (scoped): `python3 tools/test_phase_skills.py && python3 tools/test_tlc_validators.py && python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py && bun test`. Full: `bun run test:all`.

## Unit
| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Large and Complex specs require Impact (SID-01 AC6, EC1) | fixture spec with header `Size: Large` and no `## Impact`; same with `Size: Complex`; same with `Size: Medium`; same with `Size: Small`; Large with `## Impact` body `none` | first two exit 1 naming `Impact`; Medium and Small exit 0; `none` body exits 0 |
| UT-002 | Specify carries the new steps (SID-01 AC1–AC3; SID-02 AC1–AC4) | read `.agents/skills/wspecify/SKILL.md` and `references/gap-hunt.md` | Impact after the dimensions sweep and before User Stories; listing names features, pages, and scenario ids; uiux.md step cites `docs/guidelines/UI-UX.md`; gap-hunt Small-skip / Medium-Large-ask / Complex-recommend in both files; SKILL.md ≤ 200 lines |
| UT-003 | Template and downstream phases wired (SID-01 AC4, AC5, AC7; SID-03 AC5) | read `spec-template.md`, `wdesign/SKILL.md`, `wverify/SKILL.md`, `docs/guidelines/UI-UX.md` | template has `## Impact` between Assumptions and User Stories; wdesign step 1 names `uiux.md` and the designer dispatch; wverify names Impact scenario reruns; UI-UX.md says Specify |
| UT-004 | Designer templates and preload (SID-03 AC2) | parse the three designer templates | Claude `skills: [wdesign, ponytail]`, no `disallowedTools`, body names `uiux.md`, `docs/design/`, `uiux-review.md`; Codex and Cursor bodies name `wdesign` |
| UT-005 | Roles matrix includes designer (SID-03 AC1) | import `workflow_config`; parse `.my-workflow.toml.example` | `designer` in `ROLES` and in the delegated set; three `[models.<provider>.designer]` tables parse with the Assumptions models |
| UT-006 | AGENTS.md and pack.md name the designer (SID-03 AC6) | read both | `designer` present; AGENTS.md ≤ 134 lines; pack.md says five windows |

## Integration
| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Sync renders designer packets (SID-03 AC3) | temp root with the real templates, example config, and skills; `--sync-agents` | `.claude/agents/designer.md`, `.codex/agents/designer.toml`, `.cursor/agents/designer.md` written; Claude packet keeps `skills:` line byte-identical |
| IT-002 | Sync rejects a config missing the designer table (SID-03 AC4, EC3) | temp root whose toml lacks `[models.<provider>.designer]` for each of claude, codex, cursor; then one lacking `templates/agents/claude/designer.md` | each exits non-zero naming that table or template; nothing written |
| IT-003 | Adopt runtime paths include designer (SID-03 AC3) | `adopt.py plan <tmp> --layers core --json` | RUNTIME_PATHS contains the three designer runtime files; plan lists the three templates as managed |

## End-to-end
None.

## Security
None; no runtime, auth, or data surface.
