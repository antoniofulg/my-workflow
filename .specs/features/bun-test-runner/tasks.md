# Bun Test Runner Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `tlc-spec-driven` skill: activate it by name and follow its Execute
flow and Critical Rules. If the skill cannot be activated, stop and report the blocker.

**Design**: `.specs/features/bun-test-runner/design.md`
**Status**: Approved

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`,
> `docs/guidelines/GATES.md`, the existing eight structural suites, and the feature spec.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Bun discovery/runtime config | integration | Canonical files only; ignored evidence excluded; Bun 1.4 required | `tools/shared/tests/*.test.ts` | `bun test` |
| Structural contract suites | integration | Preserve every existing assertion and all 115 tests; native imports only | `tools/**/*.test.ts` | `npm test` |
| npm dependency/package boundary | integration | No Vitest graph; valid npm tree; clean dry-run package | `tools/shared/tests/*.test.ts` | `npm ls --all && npm pack --dry-run --json` |
| Changelog/release contract | integration | Published v0.6.0 exact; v0.7.0 Unreleased complete; package stays 0.6.0 | `tools/shared/tests/qa-skills.test.ts` | `bun test ./tools/shared/tests/qa-skills.test.ts -t "release"` |
| Adoption/QA public workflow | integration | No host mutation; current scenario walked with evidence | `scripts/test_adopt.py`, `docs/qa/` | `python3 scripts/test_adopt.py && npm run test:all` |

## Gate Check Commands

> Generated from `package.json` and repository guidelines; commands become final as tasks migrate the runner.

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Focused structural contract | `bun test ./tools/shared/tests/qa-skills.test.ts -t "<contract-name>"` |
| Full | Runtime, dependency, release, or adoption boundary | `npm test && python3 scripts/test_adopt.py && npm pack --dry-run --json` |
| Build | Phase/feature close | `npm run test:all && python3 tools/test_workflow_config.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check && npm ls --all && npm pack --dry-run --json && git diff --check` |

## Execution Plan

### Phase 1: Native runner

```text
T1 -> T2 -> T3
```

### Phase 2: Release and public contract

```text
T3 -> T4 -> T5
```

## Task Breakdown

### T1: Configure canonical Bun 1.4 discovery

**What**: Add repository-local Bun discovery and TypeScript support while keeping the current runner available for the transition gate.
**Where**: `bunfig.toml`
**Depends on**: None
**Reuses**: Existing `tools` suite boundary and npm lock workflow.
**Requirement**: BTR-01, BTR-03, BTR-17

**Tools**:

- MCP: official Bun 1.4 documentation via Context7, Docs MCP, or official web fallback
- Skill: `tlc-spec-driven`, `ponytail full`

**Done when**:

- [x] `bunfig.toml` sets `test.root` to `./tools`.
- [x] Official Bun types compatible with local Bun 1.4.0 are installed through npm and configured.
- [x] `bun test` discovers exactly eight files and 115 tests, including zero ignored QA evidence copies.
- [x] `npm test` remains green during this transition commit.

**Tests**: BTR-IT-001
**Gate**: full
**Commit**: `build(test): configure Bun 1.4 discovery`

### T2: Switch structural suites to native bun:test

**What**: Replace Vitest imports with Bun-native imports and make `npm test` invoke Bun while preserving every assertion.
**Where**: `tools/**/*.test.ts`
**Depends on**: T1
**Reuses**: Existing test bodies, names, parameter tables, and timeout values.
**Requirement**: BTR-02, BTR-04, BTR-06, BTR-07, BTR-08, BTR-18

**Tools**:

- MCP: official Bun 1.4 test API documentation
- Skill: `tlc-spec-driven`, `ponytail full`

**Done when**:

- [x] All eight tracked suites import from `bun:test`; zero active `vitest` imports remain.
- [x] `npm test` invokes Bun and reports eight files, 115 passes, and zero failures.
- [x] `it.each`, suite/test timeouts, subprocesses, and `-t` filtering preserve contracted results.
- [x] Missing Bun has no wrapper or fallback path to Vitest.

**Tests**: BTR-IT-002, BTR-IT-003, BTR-IT-004, BTR-IT-006
**Gate**: build
**Commit**: `test(tooling): run structural contracts with Bun`

### T3: Remove the Vitest dependency graph

**What**: Remove Vitest and its obsolete TypeScript globals, regenerating the npm lockfile through npm.
**Where**: `package.json`
**Depends on**: T2
**Reuses**: Existing npm package-manager boundary.
**Requirement**: BTR-05, BTR-20

**Tools**:

- MCP: NONE
- Skill: `tlc-spec-driven`, `ponytail full`

**Done when**:

- [x] `package.json`, `package-lock.json`, and `tsconfig.json` contain no active Vitest dependency or type reference.
- [x] `npm ls --all` exits zero with no Vitest package in the tree.
- [x] `npm pack --dry-run --json` contains no Vitest artifact or ignored QA evidence.
- [x] The Build gate passes with the native Bun suite.

**Tests**: BTR-IT-005, BTR-IT-010
**Gate**: build
**Commit**: `build(test): remove Vitest dependency`

### T4: Stage v0.7.0 Unreleased notes

**What**: Restore the published v0.6.0 changelog section and stage both pending changes under v0.7.0 Unreleased.
**Where**: `CHANGELOG.md`
**Depends on**: T3
**Reuses**: Existing host-owned removal rationale, tagged migration guide, and release contract suite.
**Requirement**: BTR-09, BTR-10, BTR-11, BTR-12, BTR-13, BTR-19

**Tools**:

- MCP: NONE
- Skill: `tlc-spec-driven`, `ponytail full`

**Done when**:

- [ ] The v0.6.0 section equals tag `v0.6.0` byte-for-byte.
- [ ] `0.7.0 - Unreleased` has `Changed` Bun migration and `Removed` host-owned continuation notes.
- [ ] The migration note links the v0.5.0 tagged guide and invents no cleanup command.
- [ ] Package/lock versions remain 0.6.0 and no tag or release is created.

**Tests**: BTR-IT-007, BTR-IT-008
**Gate**: build
**Commit**: `docs(release): stage v0.7.0 tooling notes`

### T5: Publish the current Bun QA contract

**What**: Update current testing/release documentation and invalidate the affected release scenario for a fresh CLI QA walk.
**Where**: `docs/qa/`
**Depends on**: T4
**Reuses**: `J-review-workflow-release`, `REL-report-current-workflow-release`, and existing QA profile.
**Requirement**: BTR-14, BTR-15, BTR-16

**Tools**:

- MCP: official Bun 1.4 documentation
- Skill: `tlc-spec-driven`, `ponytail full`, `qa-plan`, `qa-execute`

**Done when**:

- [ ] Current docs name Bun 1.4, `tools` discovery, npm packaging, and the no-install adoption boundary.
- [ ] Current contract tests reject Vitest wording outside immutable historical evidence.
- [ ] The affected release scenario is reset to `untested` for the closing QA session.
- [ ] Adoption and Build gates pass before QA dispatch.

**Tests**: BTR-IT-009, BTR-E2E-001
**Gate**: build
**Commit**: `docs(test): document the Bun structural gate`

## Phase Execution Map

```text
Phase 1 -> Phase 2

Phase 1: T1 -> T2 -> T3
Phase 2: T3 -> T4 -> T5
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | One discovery/type boundary | ✅ Granular |
| T2 | One runner transition across homogeneous test sources | ✅ Granular |
| T3 | One dependency removal through its owning lock command | ✅ Granular |
| T4 | One release-note correction plus its canonical contract | ✅ Granular |
| T5 | One public QA/documentation contract | ✅ Granular |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | None | ✅ Match |
| T2 | T1 | T1 -> T2 | ✅ Match |
| T3 | T2 | T2 -> T3 | ✅ Match |
| T4 | T3 | T3 -> T4 | ✅ Match |
| T5 | T4 | T4 -> T5 | ✅ Match |

## Test Co-location Validation

| Task | Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Bun discovery/runtime config | integration | BTR-IT-001 | ✅ OK |
| T2 | Structural contract suites | integration | BTR-IT-002/003/004/006 | ✅ OK |
| T3 | npm dependency/package boundary | integration | BTR-IT-005/010 | ✅ OK |
| T4 | Changelog/release contract | integration | BTR-IT-007/008 | ✅ OK |
| T5 | Adoption/QA public workflow | integration/e2e | BTR-IT-009, BTR-E2E-001 | ✅ OK |
