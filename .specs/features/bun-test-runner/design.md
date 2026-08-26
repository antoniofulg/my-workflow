# Bun Test Runner Design

**Spec**: `.specs/features/bun-test-runner/spec.md`
**Status**: Approved

## Architecture Overview

Use Bun 1.4 only as the structural TypeScript test runtime. Keep npm as dependency, packing, and
publishing owner. A repository-local `bunfig.toml` sets the discovery root to `tools`, avoiding
substring-filter discovery and ignored QA evidence. Test sources import `bun:test` directly.

```text
npm test ──────────────┐
                      ├─> Bun 1.4 test runner ─> tools/**/*.test.ts
bun test ──────────────┘          │
                                  └─> bunfig.toml: test.root = "./tools"

npm install / npm pack / publish ─> package-lock.json and npm remain authoritative
```

## Considered Approaches

| Approach | Result | Trade-off |
| --- | --- | --- |
| Bun runner, npm package manager | Chosen | Removes Vitest while preserving published npm workflow and lockfile. |
| Full Bun package-manager migration | Rejected | Expands scope into install, lock, pack, publication, and adoption behavior. |
| Keep Vitest behind a Bun wrapper/fallback | Rejected | Preserves the dependency and creates forbidden compatibility behavior. |

The user confirmed the chosen approach and required official Bun 1.4 documentation.

## Code Reuse Analysis

| Component | Location | How to Use |
| --- | --- | --- |
| Canonical structural suites | `tools/**/*.test.ts` | Keep every test body and assertion; change only runner imports where possible. |
| Existing npm scripts | `package.json` | Preserve `npm test` and `test:all` public entry points. |
| Existing release contract | `tools/shared/tests/qa-skills.test.ts` | Retarget runner and changelog assertions without weakening coverage. |
| Existing adoption gate | `scripts/test_adopt.py` | Prove no host tooling or lockfile mutation. |
| Published tag comparison | `v0.6.0` | Restore immutable changelog history exactly. |

## Components

### Bun discovery configuration

- **Purpose**: Restrict native test discovery to canonical structural tests.
- **Location**: `bunfig.toml`.
- **Interface**: `[test] root = "./tools"`.
- **Dependencies**: Bun 1.4.x.
- **Reuses**: Existing `tools` suite boundary.

### Native structural suites

- **Purpose**: Execute existing behavioural contracts without Vitest.
- **Location**: `tools/**/*.test.ts`.
- **Interface**: named imports from `bun:test`; existing `describe`, `it`, `it.each`, `expect`, and timeouts.
- **Dependencies**: Bun 1.4.x and `@types/bun` for editor/TypeScript resolution.
- **Reuses**: Existing test bodies unchanged except runner-specific syntax proven incompatible.

### npm release boundary

- **Purpose**: Keep installation, lock generation, dry-run packing, and eventual publication stable.
- **Location**: `package.json`, `package-lock.json`.
- **Interface**: `npm test`, `npm run test:all`, `npm pack --dry-run --json`.
- **Dependencies**: npm; Bun only for the test script.
- **Reuses**: Existing package metadata and publication workflow.

### v0.7.0 Unreleased notes

- **Purpose**: Stage pending changes without rewriting published v0.6.0 history.
- **Location**: `CHANGELOG.md`.
- **Interface**: Keep a Changelog sections `Changed`, `Removed`, and migration note.
- **Dependencies**: published `v0.6.0` and tagged v0.5.0 lifecycle guide.
- **Reuses**: Existing removal rationale and migration link.

## Error Handling Strategy

| Error Scenario | Handling | User Impact |
| --- | --- | --- |
| Bun missing or outside supported 1.4 line | Let `npm test` fail non-zero with the native command error. | Clear prerequisite failure; no fallback hides the mismatch. |
| Ignored evidence contains test copies | `test.root` prevents traversal outside `tools`. | Stable canonical count and no historical evidence execution. |
| Bun API differs from Vitest | Change only the incompatible call site and retain its exact assertion outcome. | No contract weakening or skipped test. |
| npm lock becomes inconsistent | Regenerate through npm and require `npm ls --all` exit zero. | Packaging remains reproducible. |
| Published changelog drifts | Contract compares the v0.6.0 section with the tag. | Gate fails before release preparation continues. |

## Risks & Concerns

| Concern | Location | Impact | Mitigation |
| --- | --- | --- | --- |
| Bun positional filters are substring matches | Bun 1.4 test discovery | Historical evidence copies execute unexpectedly. | Use repository-local `test.root = "./tools"`, not a positional directory filter. |
| Suite uses `it.each` and timeout options | `tools/shared/tests/*.test.ts` | Native API differences could change execution. | Run all 115 tests plus targeted parameterized and timeout cases before removing Vitest. |
| TypeScript currently loads Vitest globals | `tsconfig.json` | Editor/type resolution can drift from runtime. | Install `@types/bun`, use Bun types, then remove Vitest globals. |
| Vitest owns a large transitive graph | `package-lock.json` | Hand edits can leave orphaned packages. | Remove through npm's owning command and verify `npm ls --all`. |
| Release note is in published version section | `CHANGELOG.md` | History falsely claims v0.6.0 shipped removal. | Restore tagged section and create v0.7.0 Unreleased. |

## Tech Decisions

| Decision | Choice | Rationale |
| --- | --- | --- |
| Supported documentation/runtime line | Bun 1.4.x | Explicit user requirement; local verification uses 1.4.0. |
| Discovery | `bunfig.toml` `test.root` | Native boundary; avoids stale broad exclusions and substring filters. |
| Package manager | npm | Toolchain change stays limited to tests. |
| Compatibility | Hard cut to `bun:test` | No backward-compatibility layer or dual runner. |
| Version timing | v0.7.0 Unreleased notes, package stays 0.6.0 | Release awaits other features and explicit authorization. |

Official sources used: https://bun.com/docs/test/configuration,
https://bun.com/docs/test/discovery, https://bun.com/docs/typescript, and https://bun.com/.
