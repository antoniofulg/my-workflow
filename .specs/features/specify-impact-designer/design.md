# Specify Impact and Designer Design

**Spec**: `.specs/features/specify-impact-designer/spec.md`
**Status**: Approved

## Architecture Overview

Two independent slices. S1 changes procedure text plus one validator rule. S2 adds one role to the matrix, which touches config, templates, sync, adopt, and their tests.

```
wspecify/SKILL.md      + Impact step (two explorers) + uiux.md step + gap-hunt question
wspecify/references/   + gap-hunt.md (rounds format)      spec-template.md + ## Impact
wdesign/SKILL.md       step 1 loads uiux.md; dispatch designer when uiux.md exists
wverify/SKILL.md       rerun Impact scenario ids
validate_spec.py       parse `Size:` from the header line; require ## Impact for Large|Complex
workflow_config.py     ROLES += designer (delegated); schema/sync/snapshot loops unchanged
templates/agents/*/designer.*   three new packets
adopt.py RUNTIME_PATHS += designer×3; .my-workflow.toml.example += 3 tables
```

## Code Reuse Analysis

- `validate_spec.py` `section_bounds` already detects sections; the size parse is one regex on the first ten lines.
- `workflow_config.py` iterates `ROLES`; adding the name propagates to schema validation, sync, and snapshots. `DELEGATED_ROLES` (planner excluded) gains designer.
- Designer template body reuses the planner template shape; Codex TOML shape from `templates/agents/codex/planner.toml`.
- `tools/test_workflow_config.py` fixtures build packets per role from `ROLES`; extend the fixture role list.

## Components

### Impact step and gap hunt (wspecify)
- Location: `.agents/skills/wspecify/SKILL.md`, `references/gap-hunt.md`.
- Interfaces: `## Impact` section (affected features, pages, scenario ids, or `none`); gap-hunt question wording and round format.

### Size-aware validator
- Location: `validate_spec.py`. Parse `^Size:\s*(Small|Medium|Large|Complex)` within the first ten lines; require `Impact` when Large or Complex. Missing `Size:` line: no requirement (older specs).

### Designer role
- Config: `ROLES` and delegated roles; example tables: claude `inherit`/`high`, codex `gpt-5.6-sol`/`high`, cursor `claude-fable-5-1-thinking-high`/`high`.
- Templates: Claude frontmatter `model`, `effort`, `skills: [wdesign, ponytail]`; body: role, load list, deliverables (`docs/design/<feature>/*.html`, `uiux-review.md`), do-not-load, report shape.

## Risks & Concerns

- The TS suites enumerate template paths; adding a role changes counts in three files. Mitigation: IT-003 and `bun test` in the scoped gate.
- Existing local tomls in six worktrees break sync until they gain designer tables. Mitigation: error names the table; this checkout's toml is updated in S2.

## Tech Decisions

- AD-029: `designer` is a delegated matrix role that owns mockups and `uiux-review.md`; Claude runs it on `inherit`.
