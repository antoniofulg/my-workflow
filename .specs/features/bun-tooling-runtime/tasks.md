# Bun Tooling Runtime Tasks

## Execution Protocol (MANDATORY -- do not skip)

Implement these tasks with the `workflow-spec-driven` skill. Each code-changing slice closes with a
fresh Technical Verifier before a dependent slice consumes its checkpoint.

**Design**: `.specs/features/bun-tooling-runtime/design.md`
**Status**: Approved

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, existing TypeScript/Python suites,
> and the feature spec.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Bun manifest/runner | integration | Every BUN-01..08 outcome plus unsupported-version edge | `tools/**/*.test.ts` | `bun test` |
| Knowledge parser | unit | Existing branches plus BUN-06/07 semantic parity | `tools/knowledge/tests/**`, `tools/shared/tests/**` | `bun test` |
| Python command boundary | unit/integration | Exact argv, missing executable, no fallback | `scripts/test_*.py`, `tools/test_*.py` | `python3 scripts/test_adopt.py` and owning Python suite |
| Package/adoption | integration | Membership, idempotency, byte identity, zero residue | `scripts/test_adopt.py`, `tools/shared/tests/**` | `bun run test:all` |
| Documentation | none | Active commands match manifest; historical paths preserved | canonical contract suites | `bun run test:all` |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Bun structural/knowledge changes | `bun test` |
| Scoped | Python command/adoption changes | owning Python suite plus `bun test` |
| Full | Slice checkpoint and feature close | `bun install --frozen-lockfile && bun run test:all` |
| Build | Package boundary | `bun pm pack --dry-run` plus full gate |

## Execution Plan

```text
T1 → T2 → T3 → T5
T2 → T4 → T5
```

S2 and S3 may open together only after CP-S1 passes. Tasks inside each slice remain sequential.

## Task Breakdown

### T1: Migrate the structural toolchain atomically

**What**: Replace npm/Vitest/tsx/package-lock authority with Bun manifest, lock, config, version preload, and `bun:test` suites in one green transition.
**Where**: `package.json`
**Depends on**: None
**Reuses**: local proven Bun discovery and preload pattern
**Requirement**: BUN-01, BUN-02, BUN-03, BUN-04, BUN-05, BUN-08, BUN-17

**Tools**:
- MCP: official Bun docs fallback
- Skill: ponytail

**Done when**:
- [x] `packageManager` pins Bun 1.4.0 and scripts use Bun only.
- [x] `bun.lock` is committed and `package-lock.json` and Vitest are absent; `tsx` remains only for T2's knowledge boundary.
- [x] `bunfig.toml` limits discovery to `tools` and preloads a 1.4.x guard.
- [x] Every structural suite imports `bun:test`.
- [x] `bun install --frozen-lockfile && bun test` exits 0 with the canonical suite count (114 passed).

**Tests**: IT-001, IT-002, UT-001
**Gate**: Full
**Commit**: `build(tooling): make Bun the runtime authority`

### T2: Run knowledge tooling with native Bun capabilities

**What**: Execute the knowledge CLI directly with Bun and replace the external YAML parser with `Bun.YAML` while preserving the parser contract.
**Where**: `tools/shared/src/frontmatter.ts`
**Depends on**: T1
**Reuses**: existing frontmatter and CLI tests
**Requirement**: BUN-06, BUN-07, BUN-13

**Tools**:
- MCP: official Bun docs fallback
- Skill: ponytail

**Done when**:
- [x] Knowledge script executes the TypeScript entrypoint with Bun.
- [x] External `yaml` dependency and import are absent.
- [x] Existing valid/malformed frontmatter outcomes remain exact.
- [x] `bun test tools/knowledge tools/shared` and the existing knowledge CLI contract executed through `bun run knowledge` exit 0.

**Tests**: UT-002, IT-005
**Gate**: Quick
**Commit**: `refactor(knowledge): use native Bun tooling`

### T3: Execute external security skills through locked Bun

**What**: Replace npx execution with fixed `bunx --bun --no-install` argv and fail-closed tests.
**Where**: `scripts/install_security_skills.py`
**Depends on**: T2
**Reuses**: existing command-builder and security installer tests
**Requirement**: BUN-09, BUN-10

**Tools**:
- MCP: official Bun docs fallback
- Skill: ponytail

**Done when**:
- [ ] Every active skills CLI call uses exact locked Bun argv.
- [ ] Missing local executable produces non-zero without install/fetch fallback.
- [ ] Owning Python suite and `bun test` exit 0.

**Tests**: UT-003, IT-007, SEC-001
**Gate**: Scoped
**Commit**: `build(skills): run external installers with Bun`

### T4: Move package and adoption checks to Bun

**What**: Inspect package membership through Bun, stop adopting repository-only TS tests, and prove disposable Bun execution without checkout residue.
**Where**: `scripts/test_adopt.py`
**Depends on**: T2
**Reuses**: current package/adoption byte-identity checks
**Requirement**: BUN-11, BUN-12, BUN-13, BUN-18

**Tools**:
- MCP: official Bun docs fallback
- Skill: ponytail

**Done when**:
- [ ] Package checks use Bun in a disposable boundary and leave no checkout tarball.
- [ ] Adoption omits repository-only TypeScript tests.
- [ ] Adopted knowledge CLI runs with Bun and no external YAML package.
- [ ] Adoption/re-adoption byte identity and consumer preservation remain green.

**Tests**: IT-004, IT-005, SEC-002
**Gate**: Build
**Commit**: `test(adopt): verify Bun package boundaries`

### T5: Publish the Bun-only active command contract

**What**: Replace active npm/Node command authority in public docs and canonical scans while preserving historical evidence verbatim.
**Where**: `README.md`
**Depends on**: T3, T4
**Reuses**: existing documentation and QA contract suites
**Requirement**: BUN-14, BUN-15, BUN-16

**Tools**:
- MCP: none
- Skill: writing-for-agents, ponytail

**Done when**:
- [ ] Active README/workflow/guideline commands match `package.json` Bun scripts.
- [ ] Canonical scan finds no forbidden active authority outside the historical allowlist.
- [ ] Historical reports/specs remain byte-unchanged.
- [ ] `bun install --frozen-lockfile && bun run test:all` and `bun pm pack --dry-run` exit 0.

**Tests**: IT-003, IT-006, E2E-001
**Gate**: Full
**Commit**: `docs(workflow): document the Bun tooling contract`

## Dependency Execution Map

```text
T1 → T2 → T3 ──→ T5
          └→ T4 ──→ T5
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | One indivisible green runner migration | ✅ Atomic transition |
| T2 | One knowledge runtime boundary | ✅ Granular |
| T3 | One external executable boundary | ✅ Granular |
| T4 | One package/adoption boundary | ✅ Granular |
| T5 | One public command contract | ✅ Granular |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | root | ✅ |
| T2 | T1 | T1 → T2 | ✅ |
| T3 | T2 | T2 → T3 | ✅ |
| T4 | T2 | T2 → T4 | ✅ |
| T5 | T3, T4 | T3/T4 → T5 | ✅ |

## Test Co-location Validation

| Task | Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Bun manifest/runner | integration | IT-001/002, UT-001 | ✅ |
| T2 | Knowledge parser | unit/integration | UT-002, IT-005 | ✅ |
| T3 | Python command boundary | unit/integration | UT-003, IT-007, SEC-001 | ✅ |
| T4 | Package/adoption | integration/security | IT-004/005, SEC-002 | ✅ |
| T5 | Documentation contract | full integration | IT-003/006, E2E-001 | ✅ |
