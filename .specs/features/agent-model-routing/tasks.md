# Agent Model Routing Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute
flow and Critical Rules.** If the skill cannot be activated, stop without implementation.

**Design**: `.specs/features/agent-model-routing/design.md`
**Status**: Approved

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/GATES.md`,
> `package.json`, `tools/test_workflow_config.py`, `scripts/test_adopt.py`, and
> `tools/shared/tests/workflow-config.test.ts`.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Config parser and renderer | unit | Every spec branch and listed invalid input | `tools/test_workflow_config.py` | `python3 tools/test_workflow_config.py` |
| Adoption integration | integration | Empty, existing, repeated, and invalid target paths | `scripts/test_adopt.py` | `python3 scripts/test_adopt.py` |
| Pack contracts | unit | All providers, roles, docs pointers, and generated parity | `tools/shared/tests/*.test.ts` | `npm test -- --run tools/shared/tests/workflow-config.test.ts tools/shared/tests/qa-skills.test.ts` |
| Config and documentation | none | Full build gate and manual contract comparison | repository paths | Build gate only |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Resolver/parser/renderer task | `python3 tools/test_workflow_config.py` |
| Full | Adoption or public contract task | `python3 scripts/test_adopt.py && npm test` |
| Build | Phase and feature close | `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py` |

## Execution Plan

### Phase 1: Central model contract

```text
T1 -> T2 -> T3
```

### Phase 2: Adoption and public contract

```text
T3 -> T4 -> T5
```

## Task Breakdown

### T1: Define and validate the model matrix

**What**: Replace the example config with a strict version 2 central model matrix and parse it.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on**: None
**Reuses**: Existing strict TOML loader and error format.
**Requirement**: AMR-01, AMR-05

**Tools**:

- MCP: OpenAI Docs and indexed official Claude documentation already gathered by the planner
- Skill: `ponytail`

**Done when**:

- [x] Version 2 requires every provider-role model and effort.
- [x] Version 1, missing entries, unknown keys, empty models, and invalid efforts fail with exact paths.
- [x] `UT-001` and `UT-002` pass in the canonical resolver suite.
- [x] Quick gate passes with zero failures.

**Status:** complete — `python3 tools/test_workflow_config.py` (3 passed, 0 failed).

**Tests**: unit, `UT-001`, `UT-002`
**Gate**: Quick, `python3 tools/test_workflow_config.py`
**Commit**: `feat(config): centralize agent model settings`

### T2: Materialize native packet metadata

**What**: Add explicit, idempotent `--sync-agents` rendering for every provider and role.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on**: T1
**Reuses**: Existing agent path conventions and atomic replacement pattern.
**Requirement**: AMR-02, AMR-03, AMR-04

**Tools**:

- MCP: NONE
- Skill: `ponytail`

**Done when**:

- [x] All fifteen packets render their native model syntax from central config.
- [x] Validation completes before replacement and preserves non-model bytes.
- [x] JSON output lists changed and unchanged project-relative paths.
- [x] `UT-003` through `UT-007` and `UT-011` pass.
- [x] Quick gate passes with zero failures.

**Status:** complete — `python3 tools/test_workflow_config.py` (6 passed, 0 failed); CLI sync and idempotent second sync passed.

**Tests**: unit, `UT-003`, `UT-004`, `UT-005`, `UT-006`, `UT-007`, `UT-011`
**Gate**: Quick, `python3 tools/test_workflow_config.py`
**Commit**: `feat(config): synchronize provider agent metadata`

### T3: Freeze delegated model settings

**What**: Store model and effort in feature snapshots and reject resume drift until explicit refresh.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on**: T2
**Reuses**: Existing snapshot validation, frozen resume, and refresh flow.
**Requirement**: AMR-05, AMR-06

**Tools**:

- MCP: NONE
- Skill: `ponytail`

**Done when**:

- [x] New and refreshed delegated role entries include model and effort.
- [x] Resume returns frozen values and rejects packet metadata drift.
- [x] Planner remains outside delegated snapshot roles.
- [x] `UT-008`, `UT-009`, and `UT-010` pass.
- [x] Quick gate passes with zero failures.

**Status:** complete — `python3 tools/test_workflow_config.py` (8 passed, 0 failed); feature snapshot refreshed to schema v2.

**Tests**: unit, `UT-008`, `UT-009`, `UT-010`
**Gate**: Quick, `python3 tools/test_workflow_config.py`
**Commit**: `feat(config): freeze delegated model settings`

### T4: Synchronize adoption targets

**What**: Install missing central config and synchronize model metadata after adopting packets.
**Where**: `scripts/adopt.py`
**Depends on**: T3
**Reuses**: Existing missing-only copy and disposable-target smoke fixtures.
**Requirement**: AMR-07

**Tools**:

- MCP: NONE
- Skill: `ponytail`

**Done when**:

- [x] Fresh adoption installs `.my-workflow.toml` and matching packets.
- [x] Re-adoption preserves config and non-model packet content while applying configured metadata.
- [x] Invalid packet synchronization fails with its path.
- [x] `IT-001`, `IT-002`, and `IT-003` pass.
- [x] Full gate passes with zero failures.

**Status:** complete — `python3 scripts/test_adopt.py && npm test` (adoption checks passed; 108 Vitest tests passed).

**Tests**: integration, `IT-001`, `IT-002`, `IT-003`
**Gate**: Full, `python3 scripts/test_adopt.py && npm test`
**Commit**: `feat(adopt): apply centralized agent settings`

### T5: Publish and walk the central configuration contract

**What**: Update agent instructions, workflow docs, contract tests, and durable QA promises.
**Where**: `README.md`
**Depends on**: T4
**Reuses**: Existing CFG journey/scenarios and provider matrix contract tests.
**Requirement**: AMR-08

**Tools**:

- MCP: NONE
- Skills: `ponytail`, `writing-for-agents`, `qa-plan`, `qa-execute`

**Done when**:

- [x] Documentation names `.my-workflow.toml` as the editable source and native fields as generated.
- [x] Obsolete model-pin ownership language and example-copy steps are removed.
- [x] Contract tests compare every native packet with the central matrix.
- [x] `E2E-001` and `E2E-002` have terminal QA evidence.
- [x] Build gate passes with zero failures.

**Status:** complete — `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py` (108 Vitest tests plus adoption and resolver suites passed); QA scenarios `CFG-centralize-agent-model-routing` and `CFG-freeze-feature-workflow` are terminal `pass`.

**Tests**: unit and CLI/manual, `E2E-001`, `E2E-002`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `docs(config): publish centralized model workflow`

### T6: Remediate independent verification findings

**What**: Restore baseline resolver invariants and add discriminating coverage for CLI contracts,
all-provider synchronization, snapshot drift, checkout isolation, and target-local adoption values.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`,
`tools/test_workflow_config.py`, `scripts/test_adopt.py`
**Depends on**: T5
**Requirement**: AMR-01, AMR-03, AMR-04, AMR-06, AMR-07

**Done when**:

- [x] Public CLI errors use the documented `workflow-config:` prefix, exit 2, and emit no stdout.
- [x] All provider packet bytes, exact path sets, full idempotence, validation-before-write, drift,
  isolation, adoption parity, and baseline resolver invariants are discriminated.
- [x] `python3 tools/test_workflow_config.py`, `python3 scripts/test_adopt.py`, and `npm test` pass.

**Status:** complete — 21 resolver tests, adoption suite, and 108 Vitest tests passed at T6 completion.

**Tests**: unit and integration, `UT-001`, `UT-002`, `UT-003`, `UT-004`, `UT-005`, `UT-006`, `UT-007`, `UT-008`, `UT-009`, `UT-010`, `UT-011`, `IT-001`, `IT-002`, `IT-003`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): restore resolver and adoption verification coverage`

### T7: Restore final baseline resolver contracts

**What**: Restore exhaustive cadence coverage, frozen agent-path validation cases, and the public
`--sync-agents` argument-conflict CLI assertion.
**Where**: `tools/test_workflow_config.py`
**Depends on**: T6
**Requirement**: AMR-01, AMR-05, AMR-06

**Done when**:

- [x] Schema-v2 resume rejects both an agent path belonging to another role and a missing path with
  exit 2, empty stdout, and unchanged snapshot bytes.
- [x] Slice, feature, and grouped cadence matrices plus slice-count bounds are covered.
- [x] `--sync-agents` combined with resolution arguments exits 2 with the exact public diagnostic
  and no writes.
- [x] Resolver, adoption, and Vitest gates pass.

**Status:** complete — 22 resolver tests, adoption suite, and 108 Vitest tests passed.

**Tests**: unit and CLI/manual, `UT-002`, `UT-008`, `UT-009`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): restore final resolver contracts`

## Phase Execution Map

```text
Phase 1 -> Phase 2

Phase 1: T1 -> T2 -> T3
Phase 2: T3 -> T4 -> T5 -> T6 -> T7
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | One config parser contract | PASS |
| T2 | One packet materializer | PASS |
| T3 | One snapshot state transition | PASS |
| T4 | One adoption integration | PASS |
| T5 | One public contract publication | PASS |
| T6 | Verification remediation | PASS |
| T7 | Final resolver contract restoration | PASS |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Start | PASS |
| T2 | T1 | T1 -> T2 | PASS |
| T3 | T2 | T2 -> T3 | PASS |
| T4 | T3 | T3 -> T4 | PASS |
| T5 | T4 | T4 -> T5 | PASS |
| T6 | T5 | T5 -> T6 | PASS |
| T7 | T6 | T6 -> T7 | PASS |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Config parser | unit | unit | PASS |
| T2 | Renderer | unit | unit | PASS |
| T3 | Snapshot resolver | unit | unit | PASS |
| T4 | Adoption integration | integration | integration | PASS |
| T5 | Contract/docs | unit + CLI/manual | unit + CLI/manual | PASS |
| T6 | Resolver/adoption regression coverage | unit + integration | unit + integration | PASS |
| T7 | Resolver contract restoration | unit + CLI/manual | unit + CLI/manual | PASS |
