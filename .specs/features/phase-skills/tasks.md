# Phase Skills Tasks

## Execution Protocol

Implement these tasks with the `workflow-spec-driven` skill: activate it by name and follow its Execute flow and Critical Rules. Do not search for skill files by filesystem path. The skill is the source of truth for the full flow (per-task cycle, sub-agent delegation, adequacy review, Verifier, discrimination sensor). If the skill cannot be activated, stop and tell the user.

---

**Design**: `.specs/features/phase-skills/design.md`
**Status**: Approved

---

## Test Coverage Matrix

> Generated from codebase, project guidelines, and spec - confirm before Execute. Guidelines found: `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `package.json` (`test:python`).

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| ---------- | ------------------ | -------------------- | ---------------- | ----------- |
| Skill and template text (product contract) | unit | 1:1 to spec ACs; every listed edge case | `tools/test_phase_skills.py` | `python3 tools/test_phase_skills.py` |
| Config materializer (`workflow_config.py`) | integration | Every new branch: pass-through and reject paths | `tools/test_workflow_config.py` | `python3 tools/test_workflow_config.py` |
| Adopt catalog (`scripts/adopt.py`) | integration | Plan lists the new managed paths | `scripts/test_adopt.py` | `python3 scripts/test_adopt.py` |
| Docs (`docs/workflow/*.md`, `AGENTS.md`, `README.md`) | none | build gate only | - | build gate only |

## Gate Check Commands

> Generated from codebase - confirm before Execute.

| Gate Level | When to Use | Command |
| ---------- | ----------- | ------- |
| Quick | After skill and template text tasks | `python3 tools/test_phase_skills.py` |
| Full | After materializer or adopt tasks | `python3 tools/test_phase_skills.py && python3 tools/test_workflow_config.py && python3 scripts/test_adopt.py` |
| Build | After phase completion | `bun run test:python && git diff --check` |

---

## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| S1 | The five phase skills exist, the router dispatches to them, and the core adopt layer installs them; existing prose-loaded agents keep working | `python3 tools/test_phase_skills.py && python3 scripts/test_adopt.py` | yes | The router keeps its name, so every current template and consumer still resolves |
| S2 | Claude agents preload their phase skill, narrow roles lose the Skill tool, and sync rejects an unknown preload | `python3 tools/test_phase_skills.py && python3 tools/test_workflow_config.py` | yes | Templates are the only change; a consumer without the skills fails sync loudly instead of silently |

## Execution Plan

### Phase 1: Skills and router (S1)

```
T1 → T2 → T3 → T4 → T5 → T6 → T7
```

### Phase 2: Preload (S2)

Every task here depends on T5 from Phase 1.

```
T8 → T11
T9
T10
```

---

## Task Breakdown

### T1: Create the wspecify skill and the contract test

**Slice:** S1
**What**: `.agents/skills/wspecify/` with SKILL.md (procedure from `specify.md`, ≤200 lines), `references/spec-template.md`, `references/discuss.md` (moved), the `.claude/skills/wspecify` symlink, and `tools/test_phase_skills.py` with `PHASES = ("wspecify",)`; delete `workflow-spec-driven/references/specify.md` and `discuss.md`.
**Where**: `.agents/skills/wspecify/`
**Depends on**: None
**Reuses**: `.agents/skills/workflow-spec-driven/references/specify.md`, `tools/test_workflow_config.py` runner style
**Requirement**: PSK-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-001, UT-002, UT-003, UT-007, UT-008 pass for `wspecify`
- [x] `wc -l .agents/skills/wspecify/SKILL.md` ≤ 200
- [x] Quick gate passes

**Tests**: unit (UT-001, UT-002, UT-003, UT-007, UT-008)
**Gate**: quick

---

### T2: Create the wdesign skill

**Slice:** S1
**What**: `.agents/skills/wdesign/` with SKILL.md from `design.md`, `references/design-template.md`, symlink; add `wdesign` to `PHASES`; delete the old reference.
**Where**: `.agents/skills/wdesign/`
**Depends on**: T1
**Reuses**: `.agents/skills/workflow-spec-driven/references/design.md`
**Requirement**: PSK-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Contract tests pass with `wdesign` in `PHASES`
- [x] Quick gate passes

**Tests**: unit (UT-001, UT-002, UT-003, UT-007, UT-008)
**Gate**: quick

---

### T3: Create the wtasks skill

**Slice:** S1
**What**: `.agents/skills/wtasks/` with SKILL.md from `tasks.md` (process, matrix rules, checks), `references/tasks-template.md` (template, execution map, check tables), symlink; add to `PHASES`; delete the old reference.
**Where**: `.agents/skills/wtasks/`
**Depends on**: T2
**Reuses**: `.agents/skills/workflow-spec-driven/references/tasks.md`
**Requirement**: PSK-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Contract tests pass with `wtasks` in `PHASES`
- [x] Quick gate passes

**Tests**: unit (UT-001, UT-002, UT-003, UT-007, UT-008)
**Gate**: quick

---

### T4: Create the wimplement skill

**Slice:** S1
**What**: `.agents/skills/wimplement/` with SKILL.md from `implement.md` (per-task cycle, gate, commit, scope guardrail, slice validation), `references/execution-template.md` (post-gate review detail, execution template, pause), symlink; add to `PHASES`; delete the old reference.
**Where**: `.agents/skills/wimplement/`
**Depends on**: T3
**Reuses**: `.agents/skills/workflow-spec-driven/references/implement.md`
**Requirement**: PSK-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Contract tests pass with `wimplement` in `PHASES`
- [x] Quick gate passes

**Tests**: unit (UT-001, UT-002, UT-003, UT-007, UT-008)
**Gate**: quick

---

### T5: Create the wverify skill

**Slice:** S1
**What**: `.agents/skills/wverify/` with SKILL.md from `validate.md` (process, sensor, UAT, fix plans, lessons hook), `references/validation-template.md` (report template, chat summary), symlink; add to `PHASES`; delete the old reference.
**Where**: `.agents/skills/wverify/`
**Depends on**: T4
**Reuses**: `.agents/skills/workflow-spec-driven/references/validate.md`
**Requirement**: PSK-01

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] Contract tests pass with all five in `PHASES`
- [x] `ls .agents/skills/workflow-spec-driven/references/` lists exactly the five shared files
- [x] Quick gate passes

**Tests**: unit (UT-001, UT-002, UT-003, UT-007, UT-008)
**Gate**: quick

---

### T6: Shrink the router to dispatch

**Slice:** S1
**What**: Rewrite `workflow-spec-driven/SKILL.md` ≤150 lines: sizing table names `wspecify`, `wdesign`, `wtasks`, `wimplement`; remove Commands, Context Loading Strategy, and Coordinator-assisted sections; fold coordinator text into `references/sub-agents.md`; remove every `references/<phase>.md` link.
**Where**: `.agents/skills/workflow-spec-driven/SKILL.md`
**Depends on**: T5
**Reuses**: `.agents/skills/workflow-spec-driven/references/sub-agents.md`
**Requirement**: PSK-02

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-002 (router ≤150) and UT-004 pass
- [x] Quick gate passes

**Tests**: unit (UT-002, UT-004)
**Gate**: quick

---

### T7: Register the skills in adopt and docs

**Slice:** S1
**What**: Add the five directories to `CORE_PATHS` in `scripts/adopt.py`; add rows to the `docs/workflow/pack.md` skill table; correct `docs/workflow/roadmap.md` (SKILL.md carries the procedure under 200 lines); touch `README.md` skill mentions; keep `AGENTS.md` ≤134 lines; extend `scripts/test_adopt.py` with IT-003.
**Where**: `scripts/adopt.py`
**Depends on**: T6
**Reuses**: `scripts/test_adopt.py` plan fixtures
**Requirement**: PSK-04

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-009 and IT-003 pass
- [x] Full gate passes

**Tests**: unit (UT-009), integration (IT-003)
**Gate**: full

---

### T8: Preload skills in the Claude templates

**Slice:** S2
**What**: Add `skills:` and, for implementer, explorer, deep-reviewer, `disallowedTools: Skill` to the five Claude templates per PSK-03 AC1–2; update their `## Load` prose to name the phase skill instead of a reference file; add UT-005 and UT-006 (Claude scope) to the contract test.
**Where**: `templates/agents/claude/`
**Depends on**: T5
**Reuses**: existing template bodies
**Requirement**: PSK-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [x] UT-005 and UT-006 pass for `templates/agents/claude/`
- [x] Quick gate passes

**Tests**: unit (UT-005, UT-006)
**Gate**: quick

---

### T9: Rename load lines in the Codex templates

**Slice:** S2
**What**: Update `## Load` / `## Do not load` prose in the Codex planner, implementer, verifier packets to name the phase skills and no reference file; extend UT-006 to `templates/agents/codex/`.
**Where**: `templates/agents/codex/`
**Depends on**: T5
**Reuses**: existing template bodies
**Requirement**: PSK-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] UT-006 passes for `templates/agents/codex/`
- [ ] Quick gate passes

**Tests**: unit (UT-006)
**Gate**: quick

---

### T10: Rename load lines in the Cursor templates

**Slice:** S2
**What**: Same as T9 for `templates/agents/cursor/`; extend UT-006 to it.
**Where**: `templates/agents/cursor/`
**Depends on**: T5
**Reuses**: existing template bodies
**Requirement**: PSK-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] UT-006 passes for `templates/agents/cursor/`
- [ ] Quick gate passes

**Tests**: unit (UT-006)
**Gate**: quick

---

### T11: Reject unknown preload skills in sync

**Slice:** S2
**What**: In `sync_agents` pre-write validation, parse `skills:` from each Claude template and raise `ConfigError` naming the template and the missing skill when `.agents/skills/<name>/SKILL.md` is absent; add IT-001 and IT-002 to `tools/test_workflow_config.py`.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on**: T8
**Reuses**: `_error`, `_header`, `FRONTMATTER_RE`, existing temp-root fixtures in `tools/test_workflow_config.py`
**Requirement**: PSK-03

**Tools**:

- MCP: NONE
- Skill: NONE

**Done when**:

- [ ] IT-001 and IT-002 pass
- [ ] Full gate passes; `bun run test:python` passes

**Tests**: integration (IT-001, IT-002)
**Gate**: full

---

## Dependency Execution Map

```
Phase 1:  T1 → T2 → T3 → T4 → T5 → T6 → T7
Phase 2:  T8 → T11        (T8, T9, T10 depend on T5)
          T9
          T10
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1–T5 | 1 skill directory each | ✅ Granular |
| T6 | 1 file | ✅ Granular |
| T7 | 1 catalog tuple + doc rows | ✅ Granular |
| T8–T10 | 1 provider template directory each | ✅ Granular |
| T11 | 1 check in 1 function | ✅ Granular |

## Diagram-Definition Cross-Check

| Task | Depends On (task body) | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | none | ✅ Match |
| T2 | T1 | T1 | ✅ Match |
| T3 | T2 | T2 | ✅ Match |
| T4 | T3 | T3 | ✅ Match |
| T5 | T4 | T4 | ✅ Match |
| T6 | T5 | T5 | ✅ Match |
| T7 | T6 | T6 | ✅ Match |
| T8 | T5 | T5 | ✅ Match |
| T9 | T5 | T5 | ✅ Match |
| T10 | T5 | T5 | ✅ Match |
| T11 | T8 | T8 | ✅ Match |

## Test Co-location Validation

| Task | Code Layer Created/Modified | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1–T6, T8–T10 | Skill and template text | unit | unit | ✅ OK |
| T7 | Adopt catalog + docs | integration | unit + integration | ✅ OK |
| T11 | Config materializer | integration | integration | ✅ OK |
