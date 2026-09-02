# Agent Model Routing Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: **activate it by name and follow its Execute
flow and Critical Rules.** If the skill cannot be activated, stop without implementation.

**Design**: `.specs/features/agent-model-routing/design.md`
**Status**: Done

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

### Phase 3: Local operator state

```text
T15 -> T16 -> T17 -> T18
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
- [x] Validation completes before replacement and generated packets retain template instruction bytes.
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

- [x] Fresh adoption installs the example/templates, initializes local `.my-workflow.toml`, and
  generates matching runtime packets.
- [x] Re-adoption preserves local config and template content while regenerating configured runtime metadata.
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

- [x] Documentation names the local `.my-workflow.toml` as the editable source, tracked templates as
  instruction sources, and native fields/runtime packets as generated.
- [x] Obsolete model-pin ownership language and example-copy steps are removed.
- [x] Contract tests compare every native packet with the central matrix.
- [x] `E2E-001` and `E2E-002` are mapped to the affected public scenarios, which are reset to
  `untested` until a fresh QA plan/execute cycle.
- [x] Build gate passes with zero failures.

**Status:** complete — automated contract/build gates passed; affected QA scenarios remain
`untested` pending a fresh QA plan/execute cycle.

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

### T8: Discriminate frozen agent ownership

**What**: Strengthen the frozen-path regression so a wrong-role packet with matching model and
effort fails specifically on provider-role ownership, while an allowed-but-missing fallback path
fails on existence.
**Where**: `tools/test_workflow_config.py`
**Depends on**: T7
**Requirement**: AMR-06

**Done when**:

- [x] The wrong-role packet carries matching frozen metadata and asserts the exact ownership error.
- [x] The missing allowed candidate asserts the exact missing-file error and both cases preserve
  snapshot bytes.
- [x] The ownership mutant is red in a disposable worktree and the real implementation is green.
- [x] Resolver, adoption, Vitest, task-validator, and diff gates pass.

**Status:** complete — ownership mutant red; real tree 22 resolver tests, adoption suite, and 108 Vitest tests passed.

**Tests**: unit and CLI/manual, `UT-009`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `test(config): discriminate frozen agent ownership`

### T9: Restore configured cadence integration discrimination

**What**: Exercise complete v2 cadence settings through the public resolver CLI and persisted
feature snapshot, preserving direct `balanced_groups()` coverage.
**Where**: `tools/test_workflow_config.py`
**Depends on**: T8
**Requirement**: AMR-01

**Done when**:

- [x] Complete v2 configs using `slice`, `feature`, `grouped.2`, and `grouped.4` produce exact CLI
  JSON and persisted `workflow.json` cadence/groups.
- [x] The `_cadence()` defaulting mutation is red in a disposable worktree while direct grouping
  assertions remain intact.
- [x] Resolver, adoption, Vitest, task-validator, and diff gates pass.

**Status:** complete — cadence mutation red; real tree 23 resolver tests, adoption suite, and 108 Vitest tests passed.

**Tests**: unit and CLI/manual, `UT-001`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `test(config): restore configured cadence integration`

### T10: Harden packet grammar and reset stale QA evidence

**What**: Validate native model round-trips, scope metadata to native headers, preserve template bytes
including CRLF, and remove premature public QA claims. Refresh the always-loaded ownership pointers.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`,
`tools/test_workflow_config.py`, `AGENTS.md`, `docs/workflow/`, `docs/qa/`
**Depends on**: T9
**Requirement**: AMR-01, AMR-03, AMR-04, AMR-08

**Done when**:

- [x] Invalid whitespace model identifiers fail before writes.
- [x] Claude/Cursor frontmatter and Codex native headers are the only metadata sources; body-only,
  duplicate, and missing header fields fail without packet writes.
- [x] CRLF packet bytes and non-model content survive synchronization.
- [x] The changed public scenarios are `untested` and the premature feature QA report is removed.
- [x] Central config ownership is stated compactly in `AGENTS.md` and accurately in optional integration docs.
- [x] Resolver, adoption, Vitest, validator, and diff gates pass.

**Status:** complete — 26 resolver tests, adoption suite, and 108 Vitest tests passed; QA reset for fresh planning/execution.

**Tests**: unit and CLI/manual, `UT-002`, `UT-003`, `UT-006`, `UT-007`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): harden packet grammar and byte preservation`

### T11: Parse Codex metadata at the TOML top level

**What**: Ignore model-like assignments inside multiline TOML strings while synchronizing only
the true top-level Codex model and effort fields.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`,
`tools/test_workflow_config.py`
**Depends on**: T10
**Requirement**: AMR-03

**Done when**:

- [x] Codex parsing validates TOML and scans top-level assignments while tracking multiline strings.
- [x] A multiline description containing model-like lines does not become metadata; true top-level
  values are rendered and CRLF/instruction bytes remain unchanged.
- [x] The previous parser fails the regression in a disposable worktree and the corrected parser is
  green on the real tree.
- [x] Resolver, adoption, Vitest, validator, and diff gates pass.

**Status:** complete — previous parser red; corrected tree 27 resolver tests, adoption suite, and 108 Vitest tests passed.

**Tests**: unit and CLI/manual, `UT-003`, `UT-006`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): parse Codex metadata at top level`

### T12: Enforce Codex header boundaries and native round trips

**What**: Stop Codex metadata scanning at the top-level `developer_instructions` assignment and
reject backslash/control identifiers that cannot round-trip through generated TOML strings.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`,
`tools/test_workflow_config.py`
**Depends on**: T11
**Requirement**: AMR-01, AMR-03, AMR-07

**Done when**:

- [x] Top-level Codex model/effort assignments after `developer_instructions` do not satisfy the
  native header; body/multiline bytes remain unchanged and sync fails before writes.
- [x] Codex model IDs containing backslashes fail exact config validation before writes.
- [x] Previous parser regressions are red in disposable worktrees and the corrected tree is green.
- [x] Resolver, adoption, Vitest, validators, and diff gates pass.

**Status:** complete — previous boundary and escaping behavior red; corrected tree 28 resolver tests, adoption suite, and 108 Vitest tests passed.

**Tests**: unit and CLI/manual, `UT-002`, `UT-003`, `UT-006`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): enforce Codex native header boundaries`

### T13: Ignore comment delimiters in the Codex scanner

**What**: Strip TOML comments outside quoted strings before tracking triple-quoted string state,
while preserving inline comments after real assignments.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`,
`tools/test_workflow_config.py`
**Depends on**: T12
**Requirement**: AMR-03

**Done when**:

- [x] Triple-double and triple-single quote text in valid comments does not enter multiline state.
- [x] Inline comments after real top-level model/effort assignments remain byte-preserved and do
  not prevent metadata parsing/rendering.
- [x] The previous scanner is red against the valid-comment regression and the corrected tree is
  green with CRLF/instruction/comment bytes preserved.
- [x] Resolver, adoption, Vitest, validators, and diff gates pass.

**Status:** complete — previous scanner red; corrected tree 28 resolver tests, adoption suite, and 108 Vitest tests passed.

**Tests**: unit and CLI/manual, `UT-003`, `UT-006`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): ignore comment delimiters in Codex scanner`

### T14: Replace the Codex lexer with TOML-backed assignment parsing

**What**: Parse the complete Codex packet with the standard-library TOML parser, identify the
top-level native header boundary, and replace only the quoted metadata value spans while retaining
all surrounding bytes, including inline comments and CRLF newlines.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`,
`tools/test_workflow_config.py`
**Depends on**: T13
**Requirement**: AMR-01, AMR-03, AMR-07

**Done when**:

- [x] Valid quoted TOML data containing `#` and opposite triple-quote tokens does not hide later
  metadata; multiline body assignments and after-boundary keys remain excluded.
- [x] Single-line native assignments are validated and decoded by `tomllib`, including escaped
  strings, while duplicate or ambiguous metadata remains rejected before writes.
- [x] Rendering replaces only the quoted value spans and preserves exact model/effort comments,
  instruction bytes, and CRLF newlines.
- [x] The previous scanner and an inline-suffix mutation are red in disposable worktrees; the
  corrected tree is green through resolver, adoption, Vitest, validators, and diff gates.

**Status:** complete — old scanner rejected valid opposite-triple quoted data and the suffix
mutation deleted an effort comment; corrected tree passes 28 resolver, 17 adoption, and 108 Vitest
tests.

**Tests**: unit and CLI/manual, `UT-003`, `UT-006`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): replace Codex lexer with TOML-backed parsing`

### T15: Move versioned defaults to example and templates

**What**: Restore the tracked example with `profiles.mixed`, move canonical packets to templates, and ignore local config/runtime paths.
**Where**: `templates/agents/`
**Depends on**: T14
**Requirement**: AMR-01, AMR-09

**Done when**:

- [x] The complete v2 matrix and `profiles.mixed` live in tracked `.my-workflow.toml.example`.
- [x] All fifteen canonical instruction bodies moved byte-for-byte to tracked provider templates.
- [x] The local config and all three generated runtime trees are untracked and ignored while the
  current checkout retains usable runtime copies.
- [x] `git ls-files`, `git check-ignore`, and `npm pack --dry-run` prove the ownership and packaging
  boundaries.

**Status:** complete — tracked sources package correctly; local config/runtime paths are ignored;
template hashes match the retained runtime copies; Build gate passed.

**Tests**: none — config/artifact layer; Build gate verifies packaging and Git ownership.
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `refactor(config): separate agent templates from runtime`

### T16: Generate runtime packets from local state

**What**: Make sync initialize local config from the example and render complete canonical runtime packets from templates.
**Where**: `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on**: T15
**Requirement**: AMR-02, AMR-03, AMR-04, AMR-05, AMR-06

**Done when**:

- [x] Fresh sync copies and validates the example into local config, then generates all fifteen
  canonical runtime packets from templates.
- [x] Repeat sync is byte-identical and runtime edits are overwritten from unchanged templates.
- [x] Resolver and snapshots use only canonical generated runtime paths; extension fallback is gone.
- [x] Invalid config/template sources fail before any runtime packet write.

**Status:** complete — 30 resolver tests passed, including fresh initialization, template-driven
regeneration, canonical-path rejection, and validation-before-write coverage.

**Tests**: unit — initialization, generation, idempotence, missing runtime, and snapshot/resume.
**Gate**: Quick, `python3 tools/test_workflow_config.py`
**Commit**: `feat(config): generate local provider runtimes`

### T17: Adopt local configuration safely

**What**: Install tracked example/templates, preserve existing local config, merge ignore rules, and generate runtime packets during adoption.
**Where**: `scripts/adopt.py`
**Depends on**: T16
**Requirement**: AMR-07, AMR-09

**Done when**:

- [x] Fresh adoption installs the example/templates, initializes local config, and generates all
  canonical runtime packets without copying runtime trees as managed sources.
- [x] Re-adoption preserves local config byte-for-byte, merges all four local ignore rules, and
  regenerates runtime packets from templates.
- [x] Runtime edits are disposable; invalid templates fail adoption without changing runtime bytes.
- [x] Fresh and repeated adoption tests pass with the full adoption gate.

**Status:** complete — adoption suite passes, including fresh/repeated/customized/invalid targets,
template-driven regeneration, local-config preservation, and ignore ownership.

**Tests**: integration — fresh, repeated, customized, and invalid targets.
**Gate**: Full, `python3 scripts/test_adopt.py && npm test`
**Commit**: `feat(adopt): generate local agent runtimes`

### T18: Publish and verify local ownership

**What**: Update instructions, docs, contract/package tests, and QA promises for example/template versus local/runtime ownership.
**Where**: `README.md`
**Depends on**: T17
**Requirement**: AMR-08, AMR-09
**Done when**:

- [x] Agent instructions, README, workflow docs, optional integration guidance, and QA profile describe
  example/template versus local/runtime ownership and the one setup/sync flow.
- [x] Contract and package tests prove the mixed profile, canonical paths, tracked sources,
  ignored local state, and package inclusion/exclusion rules.
- [x] Affected public scenarios and journeys are reset to `untested` for a fresh QA plan/execute
  cycle; no stale pass is retained.

**Status:** complete — documentation and contracts updated, package ownership checks pass, and
affected QA scenarios are explicitly untested pending fresh QA.

**Tests**: unit and CLI/manual — contract/package tests plus final QA.
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `docs(config): publish local agent configuration`

### T19: Close revised architecture test gaps

**What**: Prove the shipped `mixed` profile and adoption's malformed-local-config contract in the
canonical configuration and adoption suites.
**Where**: canonical configuration and adoption contract suites
**Depends on**: T18
**Requirement**: AMR-01, AMR-07

**Done when**:

- [x] The tracked example's exact four `profiles.mixed` mappings are asserted and public profile
  resolution returns the exact provider route for every delegated role.
- [x] Adoption with a malformed existing local config exits 1 with the exact actionable diagnostic,
  preserves local config/template/example/runtime bytes, and makes no partial writes.
- [x] Resolver, adoption, Vitest, task/spec/state validators, diff, and commit gates pass.

**Status:** complete — canonical contract and adoption suites pass with 30 resolver, 18 adoption,
and 110 Vitest tests; malformed local-config adoption is byte-preservation covered.

**Tests**: unit and integration, `UT-001`, `IT-003`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `test(config): close revised architecture contract gaps`

### T20: Preflight local ownership and clean-clone contracts

**What**: Preflight every local config/runtime destination before writing, make contract tests
independent of ignored checkout state, and remove stale terminal QA claims.
**Where**: canonical synchronization, contract, adoption, and QA task artifacts
**Depends on**: T19
**Requirement**: AMR-02, AMR-07, AMR-08, AMR-09

**Done when**:

- [x] Fresh and late runtime destination collisions, plus parent-type collisions, fail with
  actionable paths before local config initialization or any runtime replacement.
- [x] The contract suite reads tracked templates or disposable generated outputs and passes in a
  detached clean worktree with no ignored runtime/config files.
- [x] T5 no longer claims terminal QA; affected scenarios remain `untested` pending fresh QA.
- [x] Resolver, adoption, Vitest, clean-clone, packaging, ownership, validator, and diff gates pass.

**Status:** complete — 31 resolver, 18 adoption, and 110 Vitest tests pass; clean-clone contract
execution and collision preflight are covered.

**Tests**: unit and integration, `UT-002`, `IT-003`, `E2E-001`, `E2E-002`
**Gate**: Build, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): preflight local runtime ownership`

### T21: Run customized local config adoption contract

**What**: Include the existing-config adoption integration contract in the canonical test runner.
**Where**: canonical adoption integration suite
**Depends on**: T20
**Requirement**: AMR-07

**Done when**:

- [x] The customized local config test runs from `scripts/test_adopt.py`'s canonical `__main__`
  runner in logical adoption order.
- [x] The adoption suite counts and executes all 18 integration tests with the full Build gate.
- [x] Task, diff, and commit validators pass without changing the validation certificate.

**Status:** complete — the canonical runner executes 18 adoption tests and preserves customized
local config, native values, and non-model bytes.

**Tests**: integration, `IT-002`
**Gate**: Build, `python3 scripts/test_adopt.py && npm test && python3 tools/test_workflow_config.py`
**Commit**: `test(adopt): run customized local config contract`

### T22: Enforce complete adoption smoke registry

**What**: Replace manual adoption test calls with a deterministic registry that rejects missing,
duplicate, or unknown test registrations before execution.
**Where**: canonical adoption integration runner
**Depends on**: T21
**Requirement**: AMR-07

**Done when**:

- [x] The registry names every module-global callable `test_*` exactly once and preserves the
  existing deterministic execution order and `ok` output.
- [x] Removing the customized-config registration makes the canonical runner fail non-zero with
  the missing function name; the real registry executes all 18 tests successfully.
- [x] Full Build, validators, diff, and commit checks pass without modifying `validation.md`.

**Status:** complete — registry completeness is enforced and the removal mutant is red.

**Tests**: integration, `IT-002`
**Gate**: Build, `python3 scripts/test_adopt.py && npm test && python3 tools/test_workflow_config.py`
**Commit**: `test(adopt): enforce complete smoke registry`

### T23: Contain generated runtimes within the checkout

**What**: Reject symlinked runtime parents and destinations, including dangling links, before
configuration initialization or any generated-file write.
**Where**: workflow-config sync preflight and canonical resolver contract suite
**Depends on**: T22
**Requirement**: AMR-07

**Done when**:

- [x] Every runtime parent and destination is checked for symlinks from the checkout root, with
  actionable `workflow-config:` diagnostics and exit 2 before writes.
- [x] Symlinked local config, example, and template sources are rejected under the same ownership
  invariant.
- [x] Canonical disposable tests prove local config, runtime packets, and outside sentinels remain
  unchanged for existing and dangling symlink cases.
- [x] Full Build, clean-worktree/package/Git checks, validators, diff, and commit checks pass
  without modifying `validation.md`.

**Status:** complete — runtime and source symlink escapes are rejected before any write.

**Tests**: unit and CLI, `UT-002`, `IT-003`
**Gate**: Build, clean-worktree/package/Git ownership checks, `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
**Commit**: `fix(config): contain generated runtimes in checkout`

### T24: Discriminate root symlink containment

**What**: Add the canonical CLI contract for rejecting existing and dangling `--root` symlinks
before any generated local state can be created through the link.
**Where**: canonical resolver CLI contract suite
**Depends on**: T23
**Requirement**: AMR-07

**Done when**:

- [x] Existing and dangling root symlinks return exit 2, empty stdout, and the exact
  `workflow-config:` root diagnostic.
- [x] The existing-target test proves no local config, runtime packet, or external sentinel is
  created or changed through the symlink.
- [x] Removing only the root-symlink guard makes the canonical test red; the real suite is green.
- [x] Full Build, validators, diff, and commit checks pass without modifying `validation.md`.

**Status:** complete — root symlink mutant red and canonical root containment tests green.

**Tests**: unit and CLI, `UT-002`, `IT-003`
**Gate**: Build, `python3 tools/test_workflow_config.py && npm test && python3 scripts/test_adopt.py`
**Commit**: `test(config): discriminate root symlink containment`

## Phase Execution Map

```text
Phase 1 -> Phase 2 -> Phase 3

Phase 1: T1 -> T2 -> T3
Phase 2: T3 -> T4 -> T5 -> T6 -> T7 -> T8 -> T9 -> T10 -> T11 -> T12 -> T13 -> T14
Phase 3 handoff: T14 -> T15 -> T16 -> T17 -> T18 -> T19 -> T20 -> T21 -> T22 -> T23 -> T24
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
| T8 | Frozen agent ownership discrimination | PASS |
| T9 | Configured cadence integration | PASS |
| T10 | Packet grammar, bytes, and QA evidence | PASS |
| T11 | Codex top-level metadata parsing | PASS |
| T12 | Codex header boundary and native round trip | PASS |
| T13 | Codex comment-aware scanning | PASS |
| T14 | TOML-backed Codex assignment parsing | PASS |
| T15 | Repository ownership migration | PASS |
| T16 | Runtime generator | PASS |
| T17 | Adoption integration | PASS |
| T18 | Public contract publication | PASS |
| T19 | Revised architecture contract coverage | PASS |
| T20 | Local write preflight and clean-clone contract | PASS |
| T21 | Customized adoption runner contract | PASS |
| T22 | Complete adoption smoke registry | PASS |
| T23 | Symlink-contained runtime ownership | PASS |
| T24 | Root symlink containment contract | PASS |

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
| T8 | T7 | T7 -> T8 | PASS |
| T9 | T8 | T8 -> T9 | PASS |
| T10 | T9 | T9 -> T10 | PASS |
| T11 | T10 | T10 -> T11 | PASS |
| T12 | T11 | T11 -> T12 | PASS |
| T13 | T12 | T12 -> T13 | PASS |
| T14 | T13 | T13 -> T14 | PASS |
| T15 | T14 | Earlier phase -> T15 | PASS |
| T16 | T15 | T15 -> T16 | PASS |
| T17 | T16 | T16 -> T17 | PASS |
| T18 | T17 | T17 -> T18 | PASS |
| T19 | T18 | T18 -> T19 | PASS |
| T20 | T19 | T19 -> T20 | PASS |
| T21 | T20 | T20 -> T21 | PASS |
| T22 | T21 | T21 -> T22 | PASS |
| T23 | T22 | T22 -> T23 | PASS |
| T24 | T23 | T23 -> T24 | PASS |

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
| T8 | Frozen path ownership | unit + CLI/manual | unit + CLI/manual | PASS |
| T9 | Configured cadence integration | unit + CLI/manual | unit + CLI/manual | PASS |
| T10 | Packet grammar and public QA reset | unit + CLI/manual | unit + CLI/manual | PASS |
| T11 | Codex top-level metadata | unit + CLI/manual | unit + CLI/manual | PASS |
| T12 | Codex native boundary and round trip | unit + CLI/manual | unit + CLI/manual | PASS |
| T13 | Codex comment-aware scanner | unit + CLI/manual | unit + CLI/manual | PASS |
| T14 | Codex TOML assignment parser and byte-preserving renderer | unit + CLI/manual | unit + CLI/manual | PASS |
| T15 | Config/artifact | none | none | PASS |
| T16 | Resolver/generator | unit | unit | PASS |
| T17 | Adoption integration | integration | integration | PASS |
| T18 | Contract/docs | unit + CLI/manual | unit + CLI/manual | PASS |
| T19 | Mixed profile and malformed adoption config | unit + integration | unit + integration | PASS |
| T20 | Local collision and clean-clone ownership | unit + integration | unit + integration | PASS |
| T21 | Customized local config adoption | integration | integration | PASS |
| T22 | Complete adoption runner registry | integration | integration | PASS |
| T23 | Symlink-contained runtime ownership | unit + CLI/manual | unit + CLI/manual | PASS |
| T24 | Root symlink containment contract | unit + CLI/manual | unit + CLI/manual | PASS |
