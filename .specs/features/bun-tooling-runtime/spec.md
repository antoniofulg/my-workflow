# Bun Tooling Runtime Specification

## Problem Statement

The workflow repository and its adopted TypeScript tools still name npm, npx, Vitest, `tsx`, an npm
lockfile, and an external YAML parser as active authorities. Every consuming project already runs
Bun, so the duplicated Node/npm toolchain adds files, dependencies, and commands without providing a
runtime capability the workflow needs.

## Goals

- [ ] Make Bun 1.4.x the only JavaScript/TypeScript package, runtime, test, pack, and executable authority.
- [ ] Keep the Python workflow, adoption, parallelization, and release gates green without Node/npm fallbacks.
- [ ] Preserve historical evidence while removing active npm/Vitest/tsx/yaml authority.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Layered workflow adoption | Separate dependent feature after Bun establishes the tooling baseline. |
| Rewriting historical QA/spec evidence | Historical commands must remain faithful to the runs that produced them. |
| Publishing this private package | Packaging is inspected only; no registry publication is part of this feature. |
| Changing Python workflow behavior | Scheduler, probe, adoption, and verification semantics stay unchanged. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Bun compatibility line | Require Bun 1.4.x and pin `packageManager` to 1.4.0. | The available fleet and verification runtime use Bun 1.4.0; failing closed prevents silent runner drift. | yes |
| Test framework | Replace Vitest imports with `bun:test`. | Bun provides the required Jest-compatible APIs and TypeScript execution natively. | yes |
| YAML parser | Use `Bun.YAML.parse`. | Native Bun functionality removes the only knowledge-runtime package dependency. | yes |
| External package runner | Use locked local packages through `bunx --bun --no-install`. | The workflow must not fall back to npm/npx or silently fetch an unpinned executable. | yes |
| Historical references | Allow npm/Vitest text only in dated evidence and superseded feature artifacts. | Editing history would make past verification claims false. | yes |

**Open questions:** none - all resolved or logged above.

---

## User Stories

### P1: Run workflow tooling through Bun only ⭐ MVP

**User Story**: As a workflow maintainer, I want one Bun-native toolchain so that local and adopted
projects execute the same commands without Node/npm runner ambiguity.

**Why P1**: Every maintained project already provides Bun; a second package/runtime authority is pure drift.

**Acceptance Criteria**:

1. The repository SHALL declare Bun 1.4.0 as its package manager and Bun 1.4.x as its supported runtime. <!-- BUN-01 -->
2. WHEN dependencies are installed THEN Bun SHALL use a committed `bun.lock` and no `package-lock.json` SHALL exist. <!-- BUN-02 -->
3. WHEN the structural TypeScript gate runs THEN Bun SHALL discover only test files under `tools/`. <!-- BUN-03 -->
4. IF the Bun runtime is outside 1.4.x THEN the structural gate SHALL fail before executing test cases. <!-- BUN-04 -->
5. WHEN TypeScript tests execute THEN every suite SHALL import its test API from `bun:test` and no Vitest runtime SHALL be installed. <!-- BUN-05 -->
6. WHEN the knowledge command executes THEN Bun SHALL run the TypeScript entrypoint directly without `tsx`. <!-- BUN-06 -->
7. WHEN knowledge frontmatter is parsed THEN the workflow SHALL use `Bun.YAML.parse` without the external `yaml` package. <!-- BUN-07 -->
8. WHEN the full gate executes THEN `bun run test:all` SHALL run the Bun structural suites followed by every Python suite. <!-- BUN-08 -->

**Independent Test**: A frozen Bun install followed by `bun run test:all` passes with no Node/npm executable in the command path.

### P1: Use Bun at package and executable boundaries

**User Story**: As an adopter, I want package inspection and external skill execution to use Bun so
that the workflow never silently reintroduces npm or npx.

**Why P1**: Python entrypoints currently invoke npm-family commands even when their host project is Bun-only.

**Acceptance Criteria**:

1. WHEN the security-skill installer invokes its locked CLI THEN it SHALL execute `bunx --bun --no-install` with fixed arguments. <!-- BUN-09 -->
2. IF the locked external executable is absent THEN the installer SHALL fail closed without invoking npm, npx, or a network fallback. <!-- BUN-10 -->
3. WHEN package membership is inspected THEN the workflow SHALL use `bun pm pack` in a disposable destination or dry-run mode and SHALL leave no tarball in the checkout. <!-- BUN-11 -->
4. WHEN adoption installs workflow runtime files THEN it SHALL omit repository-only TypeScript test suites. <!-- BUN-12 -->
5. WHEN the adopted knowledge CLI runs THEN it SHALL execute with Bun and parse frontmatter without consumer Node packages. <!-- BUN-13 -->
6. The active workflow authority SHALL contain no npm, npx, Vitest, `tsx`, `package-lock.json`, or external `yaml` dependency outside an explicit historical allowlist. <!-- BUN-14 -->
7. WHEN public workflow instructions name JavaScript/TypeScript commands THEN they SHALL name Bun commands from the current manifest. <!-- BUN-15 -->
8. WHILE historical evidence is retained, the workflow SHALL preserve its original command text unchanged. <!-- BUN-16 -->

**Independent Test**: Package, adoption, knowledge, and security-skill checks pass with npm/npx unavailable and leave zero checkout residue.

## Edge Cases

- IF Bun reports a malformed or unsupported version THEN the structural gate SHALL fail with the required 1.4.x range. <!-- BUN-17 -->
- IF a package inspection or external executable command would create state outside its declared disposable boundary THEN the workflow SHALL fail before mutating the checkout. <!-- BUN-18 -->

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| BUN-01 | P1: Bun-only tooling | Tasks | Verified by T1 |
| BUN-02 | P1: Bun-only tooling | Tasks | Verified by T1 |
| BUN-03 | P1: Bun-only tooling | Tasks | Verified by T1 |
| BUN-04 | P1: Bun-only tooling | Tasks | Verified by T1 |
| BUN-05 | P1: Bun-only tooling | Tasks | Verified by T1 |
| BUN-06 | P1: Bun-only tooling | Tasks | In Tasks |
| BUN-07 | P1: Bun-only tooling | Tasks | In Tasks |
| BUN-08 | P1: Bun-only tooling | Tasks | Verified by T1 |
| BUN-09 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-10 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-11 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-12 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-13 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-14 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-15 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-16 | P1: Bun package boundaries | Tasks | In Tasks |
| BUN-17 | Edge case | Tasks | Verified by T1 |
| BUN-18 | Edge case | Tasks | In Tasks |

**Coverage:** 18 total, 18 mapped to tasks, 0 unmapped.

---

## Success Criteria

- [ ] `bun install --frozen-lockfile` and `bun run test:all` exit 0 on the final tree.
- [ ] Active authority scan finds zero forbidden npm/Vitest/tsx/yaml paths outside the historical allowlist.
- [ ] Bun package/adoption checks leave zero tracked or ignored residue in the checkout.
