# Phase Skills Design

**Spec**: `.specs/features/phase-skills/spec.md`
**Status**: Approved

---

## Architecture Overview

Text moves; one check is added. The router stays at `.agents/skills/workflow-spec-driven/` and
keeps `scripts/` and the shared references. Five sibling skills receive the phase procedures.
Claude agent templates gain frontmatter that preloads them.

```
.agents/skills/
  workflow-spec-driven/   router: SKILL.md ≤150 (rules, sizing→skill map, .specs, resume, chain)
    references/           lessons.md memory.md sub-agents.md code-analysis.md coding-principles.md
    scripts/              unchanged (validate_spec, validate_tasks, check_commit, validate_state, lessons, slice_packet, review_convergence)
  wspecify/   SKILL.md ≤200 + references/{spec-template.md, discuss.md}
  wdesign/    SKILL.md ≤200 + references/design-template.md
  wtasks/     SKILL.md ≤200 + references/tasks-template.md (template, execution map, checks)
  wimplement/ SKILL.md ≤200 + references/execution-template.md (post-gate review detail, pause)
  wverify/    SKILL.md ≤200 + references/validation-template.md
.claude/skills/w*  →  ../../.agents/skills/w*
templates/agents/claude/*.md   skills: [...]  disallowedTools: Skill (narrow roles)
```

Approaches considered: (a) thin SKILL.md pointing at the old reference, chosen against because
preload injects only SKILL.md; (b) move `scripts/` with each phase, chosen against because adopted
gate paths and four suites cite the router path; (c) this: procedure in SKILL.md, templates in
`references/`, scripts stay.

## Code Reuse Analysis

### Existing Components to Leverage

- `workflow_config.py` `render_agent_packet` copies template bytes and replaces only model and
  effort, so `skills:` and `disallowedTools:` pass through with no renderer change.
- `sync_agents` already validates every template before writing; the new skill-name check hooks
  there so a failure writes nothing.
- `scripts/adopt.py` `CORE_PATHS` is the only catalog; adding five entries installs the skills.
- `tools/test_deep_review_token_metrics.py` already reads skill files as a contract; the new
  `tools/test_phase_skills.py` follows that precedent and the repo's `def test_*` plus `__main__`
  runner style from `tools/test_workflow_config.py`.

### Integration Points

- `autonomous`, `deep-review`, `qa-*` skills cite `workflow-spec-driven` by name; unchanged.
- Template bodies (15 files) cite skills by prose; renamed lines only.

## Components

### Phase skill (×5)

- **Purpose**: one phase's procedure, preloadable alone.
- **Location**: `.agents/skills/w<phase>/SKILL.md`, `references/`.
- **Interfaces**: frontmatter `name`, `description`, `disable-model-invocation: true`; body cites
  validators as `.agents/skills/workflow-spec-driven/scripts/<x>.py` and templates by relative path.
- **Reuses**: the current reference text, split at its `## Template` heading.

### Router

- **Purpose**: sizing, phase→skill map, `.specs` layout, critical rules, resume.
- **Location**: `.agents/skills/workflow-spec-driven/SKILL.md`.
- **Change**: sizing table cells name `wspecify` etc.; Commands, Context Loading, and
  Coordinator sections removed; coordinator text folded into `references/sub-agents.md`.

### Preload check in sync

- **Purpose**: fail sync when a Claude template preloads a skill that does not exist.
- **Location**: `workflow_config.py`, inside the pre-write validation of `sync_agents`.
- **Interface**: parse `skills:` (inline list or block list) from the Claude frontmatter; each
  name must satisfy `root/.agents/skills/<name>/SKILL.md` exists; raise `ConfigError` naming
  template path and skill.

### Contract test

- **Location**: `tools/test_phase_skills.py`; `PHASES` tuple grows one entry per skill task.
- **Covers**: UT-001..UT-009 from `tests.md`.

## Data Models

None.

## Error Handling Strategy

Sync: unknown preload skill raises before any write, same path as an invalid model. Contract
tests name the file and the offending token.

## Risks & Concerns

- `implement.md` is 426 lines; reaching 200 in SKILL.md needs the post-gate review detail and the
  execution template moved to `references/`. Mitigation: UT-003 caps total growth at +10 lines so
  nothing is padded, and the edge case forbids deleting a rule.
- Cursor and Codex may ignore or reject unknown frontmatter keys. Mitigation: keys are added to
  Claude templates only.
- A `Skill \`x\`` prose token regex in UT-006 may miss a load line phrased differently.
  Mitigation: the test scans every line under `## Load` and `## Do not load` for backticked
  tokens and requires each to resolve as a skill, a file, or a heading anchor.

## Tech Decisions

- Recorded as AD-028: phase procedures live in preloadable skills; the router only dispatches.
