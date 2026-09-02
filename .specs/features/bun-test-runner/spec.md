# Bun Test Runner Specification

## Problem Statement

The repository's structural TypeScript tests use Vitest even though Bun 1.4 provides the required
test primitives natively. The current release notes also place the unpublished integration removal
inside the already-published v0.6.0 section. The next local release train needs a Bun-native test
gate and an honest v0.7.0 Unreleased changelog without publishing or changing the package version.

## Goals

- [x] Run the canonical structural TypeScript suite with Bun 1.4 and no Vitest dependency.
- [x] Preserve npm and `package-lock.json` for packaging while Bun owns only TypeScript tests.
- [x] Keep ignored QA evidence outside canonical test discovery.
- [x] Restore the published v0.6.0 changelog and stage both pending changes under v0.7.0 Unreleased.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Switching package installation or publishing from npm to Bun | Bun replaces only the test runner. |
| Creating `bun.lock` | npm continues to own dependency resolution and the release lockfile. |
| Changing package version from 0.6.0 | The complete v0.7.0 release train is not assembled yet. |
| Creating a tag, GitHub release, or package publication | The user explicitly withheld release authorization. |
| Installing or upgrading Bun on an operator machine | Tool installation and host mutation remain operator-owned. |
| Implementing `.my-workflow.toml` v3 | That is a separate feature. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Bun documentation baseline | Official Bun 1.4 documentation and local Bun 1.4.0 | The user required Bun 1.4 guidance for the migration. | yes |
| Package manager boundary | Keep npm, `package-lock.json`, `npm pack`, and npm publication | Only the structural test runner is changing. | yes |
| Canonical discovery | Configure `[test] root = "./tools"` in repository-local `bunfig.toml` | Bun positional arguments are substring filters and discovered ignored QA evidence copies. | yes |
| Runner compatibility | Hard-cut imports and contracts to `bun:test`; no Vitest fallback | The repository does not preserve backward compatibility. | yes |
| Release state | Add `0.7.0 - Unreleased`; keep package metadata at 0.6.0 | Another feature will join the release before publication. | yes |

**Open questions:** none - all resolved or logged above.

## Implicit-Requirement Dimensions

| Dimension | Resolution |
| --- | --- |
| Input validation and bounds | N/A because this feature adds no input schema; Bun receives repository-owned test configuration. |
| Failure and partial failure | Missing or incompatible Bun fails the command non-zero; no hidden fallback is provided. |
| Idempotency and retry | Repeated `npm test`, `bun test`, and `npm install` runs preserve tracked state. |
| Auth boundaries and rate limits | N/A because no authenticated or network product surface changes. |
| Concurrency and ordering | Bun's default sequential file execution remains authoritative; the feature adds no concurrency override. |
| Data lifecycle and expiry | N/A because no persistent product data is created. |
| Observability | Existing command exit codes and test summaries remain the observable contract. |
| External-dependency failure | Bun 1.4 is an explicit developer prerequisite; adoption does not install it. |
| State-transition integrity | Published v0.6.0 history remains fixed while v0.7.0 stays explicitly Unreleased. |

## User Stories

### P1: Run structural contracts with Bun 1.4 ⭐ MVP

**User Story**: As a workflow maintainer, I want the TypeScript contract suite to run natively on
Bun 1.4 so that the repository owns one smaller test toolchain without losing coverage.

**Why P1**: This is the requested toolchain change and must preserve every current contract.

**Acceptance Criteria**:

1. The repository SHALL declare Bun 1.4.x as the supported structural TypeScript test runtime. (BTR-01)
2. WHEN `npm test` runs with Bun 1.4 THEN the repository SHALL execute the canonical eight files and 115 tests rooted under `tools` with zero failures. (BTR-02)
3. WHEN `bun test` runs from the repository root THEN the repository SHALL exclude ignored QA evidence and execute the same canonical test set as `npm test`. (BTR-03)
4. The canonical TypeScript test files SHALL import test APIs from `bun:test` and contain no active import from `vitest`. (BTR-04)
5. The package manifest and npm lockfile SHALL contain no Vitest dependency or Vitest-only transitive package. (BTR-05)
6. WHEN `npm run test:all` runs THEN the repository SHALL execute the Bun structural suite followed by every registered Python suite with zero failures. (BTR-06)
7. WHEN a maintainer supplies `-t` to the Bun gate THEN the repository SHALL filter tests by the matching full test name. (BTR-07)
8. IF Bun 1.4 is unavailable THEN the structural test command SHALL fail non-zero without invoking Vitest or another compatibility runner. (BTR-08)

**Independent Test**: Run `npm test`, `bun test`, a targeted `bun test -t` command, and
`npm run test:all`; compare discovered files and tests with the pre-migration baseline.

### P1: Stage honest v0.7.0 release notes ⭐ MVP

**User Story**: As a release operator, I want pending changes recorded under v0.7.0 Unreleased so
that published v0.6.0 history remains truthful while the next release continues to accumulate work.

**Why P1**: The current changelog attributes unpublished behavior to an immutable published version.

**Acceptance Criteria**:

1. The v0.6.0 changelog section SHALL remain byte-for-byte equal to the published v0.6.0 tag. (BTR-09)
2. The changelog SHALL contain a `0.7.0 - Unreleased` section that records the Bun 1.4 test-runner migration under `Changed`. (BTR-10)
3. The `0.7.0 - Unreleased` section SHALL record removal of the retired integration, host-owned continuation, durable repository context, and the external-state rule under `Removed`. (BTR-11)
4. The v0.7.0 migration note SHALL link to the tagged v0.5.0 lifecycle guide for the retired integration without inventing or executing cleanup commands. (BTR-12)
5. WHILE v0.7.0 remains Unreleased, package and lockfile version fields SHALL remain 0.6.0 and no tag or publication SHALL be created. (BTR-13)

**Independent Test**: Compare the v0.6.0 section with the tag, inspect the v0.7.0 section, verify
version parity remains 0.6.0, and confirm no tag points at the feature HEAD.

### P2: Keep the public QA contract current

**User Story**: As a repository adopter, I want test and release documentation to name the actual
runner and canonical discovery boundary so that local verification matches the supported workflow.

**Why P2**: `npm test` and release certification are public developer interfaces.

**Acceptance Criteria**:

1. WHEN current testing documentation describes the structural gate THEN it SHALL name Bun 1.4 and the `tools` discovery root. (BTR-14)
2. WHEN the release QA scenario is invalidated by this migration THEN it SHALL be reset and walked through the declared CLI adapter before feature completion. (BTR-15)
3. The adoption workflow SHALL NOT install Bun, edit host settings, or create a Bun lockfile. (BTR-16)

**Independent Test**: Adopt into a disposable fixture, inspect current QA documentation, execute
the release scenario, and verify host/project sentinels and tracked lockfiles remain unchanged.

## Edge Cases

- IF ignored QA evidence contains copied `*.test.ts` files THEN canonical discovery SHALL execute none of those copies. (BTR-17)
- IF a tracked test still imports `vitest` THEN the migration contract SHALL fail. (BTR-18)
- IF the v0.6.0 changelog differs from its published tag THEN the release-history contract SHALL fail. (BTR-19)
- WHEN `npm pack --dry-run --json` runs THEN the package SHALL exclude ignored QA evidence and include no Vitest runtime artifact. (BTR-20)

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| BTR-01 | Run structural contracts | Tasks | Verified |
| BTR-02 | Run structural contracts | Tasks | Verified |
| BTR-03 | Run structural contracts | Tasks | Verified |
| BTR-04 | Run structural contracts | Tasks | Verified |
| BTR-05 | Run structural contracts | Tasks | Verified |
| BTR-06 | Run structural contracts | Tasks | Verified |
| BTR-07 | Run structural contracts | Tasks | Verified |
| BTR-08 | Run structural contracts | Tasks | Verified |
| BTR-09 | Stage v0.7.0 notes | Tasks | Verified |
| BTR-10 | Stage v0.7.0 notes | Tasks | Verified |
| BTR-11 | Stage v0.7.0 notes | Tasks | Verified |
| BTR-12 | Stage v0.7.0 notes | Tasks | Verified |
| BTR-13 | Stage v0.7.0 notes | Tasks | Verified |
| BTR-14 | Keep QA current | Tasks | Verified |
| BTR-15 | Keep QA current | Tasks | Verified |
| BTR-16 | Keep QA current | Tasks | Verified |
| BTR-17 | Edge cases | Tasks | Verified |
| BTR-18 | Edge cases | Tasks | Verified |
| BTR-19 | Edge cases | Tasks | Verified |
| BTR-20 | Edge cases | Tasks | Verified |

**Coverage:** 20 total, 20 mapped to tasks, 0 unmapped.

## Success Criteria

- [x] Bun 1.4 executes exactly the canonical pre-migration TypeScript suite with zero failures.
- [x] Vitest and its orphaned lockfile graph are absent.
- [x] npm packaging and every Python suite remain green.
- [x] Published v0.6.0 changelog history is unchanged and v0.7.0 is explicitly Unreleased.
- [x] QA and independent verification pass without remote or operator-state mutation.
