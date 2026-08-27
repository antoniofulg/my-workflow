# Merge-Alone Slice Derivation Tasks

## Execution Protocol

Implement with `tlc-spec-driven` and `ponytail` full. Each task updates its tests, passes its named
gate, updates this file, and creates one atomic Conventional Commit. The Implementer executes the
single batch; a fresh Verifier closes the feature.

**Design**: `.specs/features/merge-alone-slices/design.md`
**Status**: In Progress — awaiting final QA

## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| A | Validated tasks declare independently mergeable outcomes; workflow resolution derives their count, preserves frozen resume, and defaults skipped Tasks to one slice. | `npm run test:all` | yes | This is the complete correction requested by issue #71; parser, resolver, resume, template, and QA changes are technical cohorts of the same outcome. |

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `package.json`, and the canonical
> Python/Bun suites. Existing tests are the floor; every MAS case remains assigned exactly once.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| TLC task validator | unit | Every closure field, membership error, remediation exclusion, and valid 1/2-slice contract | `tools/test_tlc_validators.py`, `tools/fixtures/tlc-validator/*.md` | `python3 tools/test_tlc_validators.py` |
| Workflow resolver | integration | Initial, absent Tasks, malformed Tasks, mismatch, resume, and refresh | `tools/test_workflow_config.py` | `python3 tools/test_workflow_config.py` |
| Parallel task planner | integration | Existing `Slice` membership remains identical when closure table is present | `tools/test_parallel_plan.py` | `python3 tools/test_parallel_plan.py` |
| Skill/template/public docs | structural | Published CLI and unit vocabulary match executable behaviour | `tools/shared/tests/*.test.ts`, `scripts/test_adopt.py` | `npm test`; `python3 scripts/test_adopt.py` |
| QA/changelog records | none | Build and scenario execution gates only | `docs/qa/`, `CHANGELOG.md` | `npm run test:all` |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Validator | T1 | `python3 tools/test_tlc_validators.py && python3 tools/test_parallel_plan.py` |
| Resolver | T2-T3 | `python3 tools/test_workflow_config.py` |
| Public contract | T4 | `npm test && python3 scripts/test_adopt.py` |
| Full | T5 and feature close | `npm run test:all` |

## Execution Plan

### Phase 1: Canonical Contract

```text
T1
```

### Phase 2: Resolver Lifecycle

```text
T2 → T3
```

### Phase 3: Published Workflow

```text
T4 → T5
```

## Task Breakdown

### T1: Validate Merge-Alone Slice Closures

**What**: Extend the canonical TLC task validator with exact closure-table parsing, primary-task
slice membership, deterministic JSON output, fixtures, and downstream planner regression coverage.
**Where**: `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py`
**Slice:** A
**Depends on**: None
**Reuses**: Existing task field parser and `parallel_plan.py` `Slice` field.
**Requirement**: MAS-01, MAS-02, MAS-03, MAS-04, MAS-10, MAS-11

**Tools**:

- MCP: NONE
- Skills: `tlc-spec-driven`, `ponytail`

**Done when**:

- [x] Every primary `T\d+` task has exactly one declared slice.
- [x] Every used slice has one complete closure row with exact lowercase `yes`.
- [x] Duplicate, orphan, missing, and inconsistent records fail with task/slice evidence.
- [x] `--slice-contract-json` emits deterministic validated JSON.
- [x] Remediation IDs do not create primary slices.
- [x] Closure tables do not change existing parallel-plan membership.
- [x] Validator gate passes with at least 16 tests; parallel-plan gate passes with at least 19 tests.

**Tests**: MAS-UT-001, MAS-UT-002, MAS-UT-003, MAS-UT-004, MAS-UT-005, MAS-UT-006,
MAS-UT-007, MAS-IT-008
**Gate**: Validator
**Commit**: `fix(tlc): validate merge-alone slice closures`

**Status**: complete — `python3 tools/test_tlc_validators.py` (16 tests) and
`python3 tools/test_parallel_plan.py` (19 tests) passed.

### T2: Derive Initial Workflow Slice Count

**What**: Make initial workflow resolution derive count from the validated closure contract, default
missing Tasks to one slice, fail closed on malformed Tasks, and treat `--slices` as an optional exact
assertion.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Slice:** A
**Depends on**: T1
**Reuses**: Validator JSON CLI, existing `balanced_groups`, `ConfigError`, and atomic snapshot writer.
**Requirement**: MAS-01, MAS-02, MAS-05, MAS-06, MAS-07

**Tools**:

- MCP: NONE
- Skills: `tlc-spec-driven`, `ponytail`

**Done when**:

- [x] Praxis fixture derives one slice and the independent-capabilities fixture derives two.
- [x] No `tasks.md` derives one slice.
- [x] Present malformed Tasks stops before snapshot write.
- [x] Optional zero, negative, or mismatched `--slices` stops before snapshot write.
- [x] Resolver gate passes with at least 49 tests.

**Tests**: MAS-IT-001, MAS-IT-002, MAS-IT-003, MAS-IT-004, MAS-IT-005
**Gate**: Resolver
**Commit**: `fix(config): derive slice count from task outcomes`

**Status**: complete — `python3 tools/test_workflow_config.py` (49 tests) passed.

### T3: Preserve Resume and Refresh Semantics

**What**: Keep valid snapshot resume ahead of task access and make explicit refresh revalidate and
derive current closures without changing the version-2 snapshot schema.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Slice:** A
**Depends on**: T2
**Reuses**: Existing snapshot validation, refresh branch, and atomic replacement.
**Requirement**: MAS-08

**Tools**:

- MCP: NONE
- Skills: `tlc-spec-driven`, `ponytail`

**Done when**:

- [x] Resume returns the frozen snapshot after Tasks change from one to two slices.
- [x] Resume does not validate changed or malformed Tasks.
- [x] Refresh derives current Tasks and atomically replaces groups.
- [x] Existing snapshot schema remains unchanged.
- [x] Resolver gate passes with at least 51 tests.

**Tests**: MAS-IT-006, MAS-IT-007
**Gate**: Resolver
**Commit**: `fix(config): preserve frozen slice resolution on resume`

**Status**: complete — `python3 tools/test_workflow_config.py` (51 tests) passed.

### T4: Publish the Slice Planning Contract

**What**: Update the TLC task template, workflow-config skill, README CLI examples, and structural
contracts so agents define merge-alone slices before workflow resolution and understand phase/cohort
and batch as separate units.
**Where**: `.agents/skills/tlc-spec-driven/references/tasks.md`
**Slice:** A
**Depends on**: T3
**Reuses**: Existing workflow tour, adoption copy rules, and Bun structural suite.
**Requirement**: MAS-09

**Tools**:

- MCP: NONE
- Skills: `writing-for-agents`, `tlc-spec-driven`, `ponytail`

**Done when**:

- [x] Template requires the closure table and one `Slice` field per primary task.
- [x] Template defines slice, phase/cohort, and batch without overlapping ownership.
- [x] Workflow-config docs run after validated Tasks and show optional assertion only.
- [x] README examples derive count without `--slices` ownership.
- [x] Structural/adoption gates pass with at least 116 Bun tests and `scripts/test_adopt.py` exit 0.

**Tests**: MAS-IT-009
**Gate**: Public contract
**Commit**: `docs(workflow): publish merge-alone slice contract`

**Status**: complete — `npm test` passed with 116 tests and `python3 scripts/test_adopt.py` exited 0.

### T5: Refresh Current QA and Release Promises

**What**: Update the existing workflow-configuration journey/scenarios and the v0.7.0 Unreleased
changelog entry, then reset affected current promises for independent QA.
**Where**: `docs/qa/`
**Slice:** A
**Depends on**: T4
**Reuses**: Existing CFG journey/scenarios and current Unreleased changelog section.
**Requirement**: MAS-01, MAS-02, MAS-03, MAS-05, MAS-08, MAS-09

**Tools**:

- MCP: NONE
- Skills: `tlc-spec-driven`, `ponytail`

**Done when**:

- [x] Existing CFG/ADP scenario expectations describe derived count, closure validation, and frozen resume.
- [x] Every changed current scenario is reset to `untested` with pending report fields.
- [x] The v0.7.0 Unreleased changelog records the fix without publishing a release.
- [x] Full gate passes with zero failures.

**Tests**: none — QA documents and changelog are owned by the full gate; fresh `qa-plan` and
`qa-execute` sessions run after implementation review.
**Gate**: Full
**Commit**: `docs(qa): record merge-alone slice validation`

**Status**: complete — current CFG/ADP promises are fresh and `npm run test:all` passed with zero
failures.

### R1: Close Technical Verifier Evidence Gaps

**What**: Strengthen existing regression fixtures and assertions for error identity, refresh
failure atomicity, every named remediation/boundary shape, and direct validator-to-planner
membership equality.

- Where: `tools/test_tlc_validators.py`
- Slice: A
- Depends on: T5
- Reuses: Existing MAS fixtures, resolver snapshot helpers, and parallel-plan parser.
- Requirements: MAS-03, MAS-04, MAS-05, MAS-07, MAS-10, MAS-11

**Tools**:

- MCP: NONE
- Skills: `tlc-spec-driven`, `ponytail`

**Done when**:

- [x] Closure/membership failures assert offending task or slice identity.
- [x] Mismatched and malformed refresh preserve an existing snapshot byte-for-byte.
- [x] Both `T2R1` and `TDR1` remain outside primary slice membership/count.
- [x] Parallel-plan membership is compared directly with validator output from the same document.
- [x] Zero and negative optional count assertions fail explicitly.
- [x] Targeted suites and full gate pass with no weakened, removed, or skipped tests.

- Tests: Strengthen MAS-UT-003, MAS-UT-005, MAS-UT-006, MAS-UT-007, MAS-IT-003, MAS-IT-008,
  and the MAS-05 boundary edge case.
- Gate: Full
- Commit: `test(workflow): strengthen merge-alone contract coverage`
- Status: complete — validator 16, resolver 54, planner 19, and full `npm run test:all` gates passed.

### R2: Pin Exact-Yes Error Identity

**What**: Require every invalid merge-alone decision assertion to name both slice `A` and the exact
lowercase `yes` contract.

- Where: `tools/test_tlc_validators.py`
- Slice: A
- Depends on: R1
- Reuses: Existing MAS-UT-004 parameterized invalid-decision test.
- Requirement: MAS-03

**Done when**:

- [x] `no`, empty, `Yes`, and `true` each assert slice `A` plus exact lowercase `yes`.
- [x] Validator gate passes with no weakened, removed, or skipped tests.

- Tests: Strengthen MAS-UT-004.
- Gate: Validator
- Commit: `test(tlc): pin merge-alone error identity`
- Status: complete — `python3 tools/test_tlc_validators.py` passed with 16 tests and no skips.

### DR1: Align Canonical Slice Task Syntax

**What**: Make validated primary-task headings and Slice fields match the planner's canonical
syntax, normalize closure gates before emptiness checks, and publish/test Slice fields on every task
template example while preserving nested phase outlines.

- Where: `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py`; `.agents/skills/tlc-spec-driven/references/tasks.md`; canonical TLC tests/fixtures and structural contract
- Slice: A
- Depends on: R2
- Reuses: Planner heading/field syntax, existing nested-phase fixture, and published Task Breakdown
  examples.
- Requirements: MAS-03, MAS-09, MAS-11

**Done when**:

- [x] Primary task validation accepts only case-sensitive `### T<number>:` headings with exactly
  `**Slice:**` fields, rejects planner-incompatible shapes, and leaves nested `#### T<number>:` phase
  outlines outside primary duplicate detection.
- [x] Closure gate validation rejects backtick-only gates with the offending slice identity.
- [x] Every primary task example in the TLC template carries exactly one `**Slice:** [id]` field.
- [x] Canonical validator, planner, structural, adoption, and full gates pass with no weakened,
  removed, or skipped tests.

- Tests: Extend nested-phase, syntax rejection, gate normalization, and template Slice assertions.
- Gate: Targeted TLC/planner/structural/adoption checks plus full `npm run test:all`
- Commit: `fix(workflow): align canonical slice task syntax`
- Status: complete — targeted and full gates passed; ready for final Deep Review.

### DR2: Reject Malformed and Leaking Task Headings

**What**: Reset primary parsing context at canonical remediation headings and reject a primary-looking
heading without its required colon, even when later valid tasks remain.

- Where: `.agents/skills/tlc-spec-driven/scripts/validate_tasks.py`; canonical TLC validator fixture/test
- Slice: A
- Depends on: DR1
- Reuses: Existing remediation fixture and canonical Task Breakdown syntax checks.
- Requirements: MAS-03, MAS-10, MAS-11

**Done when**:

- [x] Canonical `T2R1` and `TDR1` remediation headings reset primary context, and their fields remain
  outside primary membership/count.
- [x] A `### T1` heading without a colon produces an explicit syntax error despite later valid tasks.
- [x] Targeted validator/planner/resolver and full gates pass with no weakened, removed, or skipped
  tests.

- Tests: Extend the canonical remediation fixture and TLC validator syntax assertions.
- Gate: Targeted validator/planner/resolver suites plus full `npm run test:all`
- Commit: `fix(tlc): reject malformed and leaking task headings`
- Status: complete — targeted and full gates passed; ready for final QA.

## Phase Execution Map

```text
Phase 1 → Phase 2 → Phase 3

T1 → T2 → T3 → T4 → T5 → R1 → R2 → DR1 → DR2
```

## Task Granularity Check

| Task | Deliverable | Status |
| --- | --- | --- |
| T1 | One validated closure contract | Pass |
| T2 | One initial-resolution policy | Pass |
| T3 | One resume/refresh lifecycle policy | Pass |
| T4 | One published planning contract | Pass |
| T5 | One current QA/release record set | Pass |
| R1 | One Technical Verifier remediation batch | Pass |
| R2 | One exact error-identity assertion | Pass |
| DR1 | One canonical task-syntax contract | Pass |
| DR2 | One remediation/heading-boundary contract | Pass |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Start | Pass |
| T2 | T1 | T1 → T2 | Pass |
| T3 | T2 | T2 → T3 | Pass |
| T4 | T3 | T3 → T4 | Pass |
| T5 | T4 | T4 → T5 | Pass |
| R1 | T5 | T5 → R1 | Pass |
| R2 | R1 | R1 → R2 | Pass |
| DR1 | R2 | R2 → DR1 | Pass |
| DR2 | DR1 | DR1 → DR2 | Pass |

## Test Co-location Validation

| Task | Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | TLC validator + planner | unit + integration | MAS unit cases + MAS-IT-008 | Pass |
| T2 | Workflow resolver initial | integration | MAS-IT-001..005 | Pass |
| T3 | Workflow resolver lifecycle | integration | MAS-IT-006..007 | Pass |
| T4 | Agent/public contract | structural + adoption | MAS-IT-009 | Pass |
| T5 | QA/changelog records | none | none; full/QA gates | Pass |
| R1 | Existing validator/resolver/planner contracts | unit + integration | Strengthened MAS assertions | Pass |
| R2 | TLC validator error contract | unit | Strengthened MAS-UT-004 | Pass |
| DR1 | Validator/template/planner contract | unit + structural | Strengthened MAS-03/MAS-09/MAS-11 | Pass |
| DR2 | Validator heading-boundary contract | unit | Strengthened MAS-03/MAS-10/MAS-11 | Pass |
