# Specify Impact and Designer Specification

Size: Large. Ticket: none (roadmap slice 3, `docs/workflow/roadmap.md`). Delegated roles run on Cursor.

## Problem Statement

A feature that touches a shared entity silently changes other screens (a Publications feature touched People and Agenda; nobody tracked it). `uiux.md` is written in Design, after the spec froze, so user actions and blockers are mapped too late. Nobody asks whether the plan has gaps before execution. And the only agent that produces mockups is the planner, on whatever model the planner runs.

## Goals

- [ ] Specify writes `uiux.md` and an `## Impact` section, and the verifier reruns the impacted scenarios.
- [ ] Specify offers a gap hunt at plan approval, sized by scope.
- [ ] A `designer` role exists in the matrix, preloads `wdesign`, and is dispatched for UI-bearing Design.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Mockup fidelity gate, reuse lint, token extraction | Roadmap slice 4 |
| Qualifier role | Roadmap slice 6 |
| Changing how mockups are stored (`docs/design/`) | FRONTEND.md already owns it |
| A dependency graph tool for Impact | Two explorer traces are enough; add tooling when traces miss |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Impact gathering | Two explorer traces: data and model dependencies; pages, journeys, jobs, events, and QA scenarios that read them | Explorer is the read-only search role | y |
| Impact enforcement | `validate_spec.py` requires `## Impact` when the spec's header line says `Size: Large` or `Size: Complex`; Medium and Small may omit it | Deterministic gate, sized like Design and Tasks | y |
| No-regression criteria | Each affected feature listed in Impact gets one ubiquitous AC in the spec; wverify reruns the QA scenarios Impact names | Makes the map testable | y |
| `uiux.md` timing | Written in Specify, after ACs, before the closure gate, only when a screen is added or changed; UI-UX.md guideline updated to say so; wdesign step 1 loads it | Human decision from shaping | y |
| Gap hunt | A question at plan approval: skipped for Small, asked for Medium and Large, recommended for Complex; two subagents (unhappy paths against current behaviour and QA scenarios; domain and data gaps), then numbered question rounds with a recommended answer each; findings become ACs or `context.md` decisions; under `autonomous`, run it only for Complex | Human decision from shaping; frontier-round format from the installed `grilling` skill | y |
| Designer role | New matrix role `designer` for all three providers; Claude `model = "inherit"` so it follows the session model (Fable here); Codex `gpt-5.6-sol` high; Cursor `claude-fable-5-1-thinking-high` | Human wants Fable on design; `inherit` passes the id check and Claude Code accepts it | y |
| Designer ownership | Mockups under `docs/design/` from `uiux.md` and `spec.md`, plus `uiux-review.md`; the planner keeps the architecture half of `design.md` | UI-UX.md flow already names a design agent | y |
| Dispatch rule | wdesign: when the feature has `uiux.md`, dispatch `designer` before internal design | One rule, one trigger | y |
| Existing local tomls | Sync fails naming the missing `[models.<provider>.designer]` table; the example gains the three tables | Complete matrix is AD-010; no silent fallback | y |

**Open questions:** none - all resolved or logged above.

---

## Impact

- `wspecify`, `wdesign`, `wverify` SKILL.md text and line caps (UT-002); `spec-template.md`.
- `validate_spec.py` and `tools/test_tlc_validators.py`; every existing spec without `## Impact` that says `Size: Large` — only this feature's own specs, both of which carry the section.
- `workflow_config.py` ROLES, schema, sync, snapshot; `tools/test_workflow_config.py` role fixtures; `tools/shared/tests/workflow-config.test.ts`, `qa-skills.test.ts`, `autonomous-parallelization.test.ts` role enumerations; `scripts/adopt.py` RUNTIME_PATHS; `.my-workflow.toml.example`; `templates/agents/*`.
- `docs/guidelines/UI-UX.md`, `docs/workflow/pack.md`, `AGENTS.md` role line, `docs/workflow/roadmap.md`.
- QA scenarios `CFG-centralize-agent-model-routing`, `ADP-adopt-workflow-safely`, `QAS-resolve-phase-skill-procedures` cover changed promises.

---

## User Stories

### P1: Specify maps impact and screens ⭐ MVP

**User Story**: As the planner, I want Specify to record which features a change touches and which screens it adds, so that regressions are named before design starts.

**Why P1**: The Publications regression is the motivating failure.

**Acceptance Criteria**:

1. The `wspecify` procedure SHALL contain an Impact step after the dimensions sweep and before user stories that dispatches two explorers (data and model dependencies; pages, journeys, jobs, events, and QA scenarios) and writes an `## Impact` section listing affected features, pages, and scenario ids.
2. WHEN Impact lists an affected feature THEN the spec SHALL carry one ubiquitous acceptance criterion stating that feature's behaviour is unchanged.
3. The `wspecify` procedure SHALL contain a `uiux.md` step, after acceptance criteria and before the closure gate, that applies only when a screen is added or changed and follows `docs/guidelines/UI-UX.md`.
4. The guideline `docs/guidelines/UI-UX.md` SHALL state that `uiux.md` is written in Specify, and `wdesign` step 1 SHALL load `uiux.md` when present.
5. The `wverify` procedure SHALL rerun the QA scenario ids named in `## Impact` and report each as pass, fail, or untested.
6. IF a spec whose header says `Size: Large` or `Size: Complex` lacks an `## Impact` section THEN `validate_spec.py` SHALL exit non-zero naming the section; WHEN the header says `Size: Medium` or `Size: Small` THEN it SHALL not require the section.
7. The spec template `references/spec-template.md` SHALL contain the `## Impact` section between Assumptions and User Stories.

**Independent Test**: `validate_spec.py` on a Large fixture without Impact exits 1; on a Medium fixture without Impact exits 0.

---

### P1: Gap hunt at plan approval

**User Story**: As the human approving a plan, I want the planner to offer a gap hunt, so that unhappy paths and domain gaps surface before execution.

**Why P1**: The human had to remind the agent about multi-publication cases.

**Acceptance Criteria**:

1. The `wspecify` procedure SHALL contain a gap-hunt step at plan approval that is skipped for Small, asked for Medium and Large, and recommended for Complex, and SHALL cite `references/gap-hunt.md` for the procedure.
2. WHEN the human accepts THEN the planner SHALL dispatch two explorers (unhappy paths against current behaviour and QA scenarios; domain and data gaps) and SHALL then ask numbered questions in frontier rounds, each with a recommended answer.
3. WHEN a round settles a finding THEN it SHALL become an acceptance criterion or a `context.md` decision, never a note.
4. WHILE running under `autonomous` the planner SHALL run the gap hunt only for Complex and SHALL record the skip in `decisions.md`.

**Independent Test**: `grep -c 'gap-hunt' .agents/skills/wspecify/SKILL.md` is at least 1 and the reference file exists.

---

### P1: A designer role in the matrix

**User Story**: As the planner, I want a `designer` agent on the model I choose, so that mockups come from a design-strong model while planning stays where it is.

**Why P1**: Fable produces the mockups the human wants; the planner should not have to be Fable for that.

**Acceptance Criteria**:

1. The `workflow_config.py` ROLES SHALL include `designer` as a delegated role for every provider, and `.my-workflow.toml.example` SHALL carry `[models.<provider>.designer]` tables with the models in the Assumptions table.
2. The repository SHALL contain `templates/agents/{claude,codex,cursor}/designer.{md,md,toml}`; the Claude template SHALL declare `skills: [wdesign, ponytail]`, no `disallowedTools`, and a body that loads `uiux.md`, `spec.md`, `docs/guidelines/UI-UX.md`, and `docs/guidelines/FRONTEND.md`, writes mockups under `docs/design/` and `uiux-review.md`, and never writes product code.
3. WHEN `--sync-agents` runs THEN it SHALL generate `.claude/agents/designer.md`, `.codex/agents/designer.toml`, and `.cursor/agents/designer.md`, and `scripts/adopt.py` RUNTIME_PATHS SHALL list them.
4. IF a local `.my-workflow.toml` lacks a `[models.<provider>.designer]` table THEN `--sync-agents` SHALL exit non-zero naming that table.
5. The `wdesign` procedure SHALL dispatch `designer` before internal design whenever `uiux.md` exists, and SHALL keep the architecture half of `design.md` with the planner.
6. The file `AGENTS.md` SHALL name the designer among the roles and SHALL stay at or below 134 lines; `docs/workflow/pack.md` SHALL name five windows.

**Independent Test**: `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --sync-agents` reports the three designer packets changed; a Claude spawn of `designer` has `# Design` in context.

---

## Edge Cases

- IF `## Impact` says "none" THEN `validate_spec.py` SHALL accept it and wverify SHALL report no reruns.
- IF the gap hunt finds nothing THEN the planner SHALL say so in one line and proceed.
- IF a provider template for designer is missing THEN `--sync-agents` SHALL fail naming the template path, as it does for other roles.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| SID-01 | P1: Specify maps impact and screens | Design | Pending |
| SID-02 | P1: Gap hunt at plan approval | Design | Pending |
| SID-03 | P1: A designer role in the matrix | Design | Pending |

**Coverage:** 3 total, 0 mapped to tasks, 3 unmapped ⚠️

---

## Success Criteria

- [ ] A Large spec without `## Impact` fails the validator; this feature's own spec passes.
- [ ] A spawned `designer` reports `# Design` present and `wdesign` in its preload.
