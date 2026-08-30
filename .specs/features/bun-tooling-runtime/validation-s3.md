# Bun Tooling Runtime CP-S3 Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/bun-tooling-runtime/spec.md`
**Diff range**: `origin/main..HEAD`
**Verifier**: fresh independent Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1 | PASS | Bun manifest, lock, discovery, runtime guard, and structural suites pass the integrated gate. |
| T2 | PASS | Knowledge CLI and frontmatter parser execute through native Bun. |
| T3 | PASS | Locked security CLI boundary passes 38/38 focused tests. |
| T4 | PASS | Disposable pack and adoption boundaries leave zero checkout residue. |
| T5 | PASS | Active authority includes repository and adopted knowledge instructions; historical evidence remains excluded and unchanged. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| BUN-01 | Bun 1.4.0 package manager; Bun 1.4.x runtime. | `package.json:6-9`; `tools/shared/tests/qa-skills.test.ts:927-930` asserts exact package manager, engine, and Bun test command. | PASS |
| BUN-02 | Committed `bun.lock`; no `package-lock.json`. | `tools/shared/tests/qa-skills.test.ts:930-931` asserts lock content and lockfile absence; frozen install preserved SHA-256 `2017e1f780055f755fa145636d98b8f54a7dfc4fcbc89bf982f0ed42dc22cfb5`. | PASS |
| BUN-03 | Structural discovery is limited to `tools/`. | `bunfig.toml:1-3`; `tools/shared/tests/qa-skills.test.ts:974-982` asserts the root, preload, and exact discovered Python suite list. | PASS |
| BUN-04 | Unsupported Bun fails before test cases. | `tools/shared/src/bun-version.ts:1-3`; `tools/shared/tests/qa-skills.test.ts:1032-1036` runs unsupported and malformed version sensors and requires failure before their marker. | PASS |
| BUN-05 | Every TypeScript suite imports `bun:test`; Vitest is absent. | `tools/shared/tests/qa-skills.test.ts:985-1001` enumerates all suites, requires `bun:test`, and rejects Vitest/tsx/yaml dependencies. | PASS |
| BUN-06 | Knowledge CLI runs its TypeScript entrypoint directly with Bun. | `package.json:10-16`; `tools/knowledge/tests/cli.test.ts:38-46` asserts exact `bun tools/knowledge/src/cli.ts`. | PASS |
| BUN-07 | Frontmatter uses `Bun.YAML.parse` without external `yaml`. | `tools/shared/src/frontmatter.ts:31-43`; `tools/shared/tests/frontmatter.test.ts:13-54` asserts mappings, malformed YAML, non-mappings, empty blocks, and CRLF. | PASS |
| BUN-08 | Full gate runs Bun structural suites, then all Python suites. | `package.json:14-16`; `tools/shared/tests/qa-skills.test.ts:978-982` asserts exact gate composition and suite discovery. | PASS |
| BUN-09 | Locked external CLI uses exact `bunx --bun --no-install` argv. | `scripts/install_security_skills.py:522-536`; `tools/shared/tests/security-skills-installation.test.ts:375-385` asserts all three exact fixed command tails. | PASS |
| BUN-10 | Missing locked executable fails closed with no fallback or target mutation. | `scripts/install_security_skills.py:688-699`; `tools/shared/tests/security-skills-installation.test.ts:409-433` removes `bunx`, requires exit 1, and asserts consumer, lock, and managed tree unchanged. | PASS |
| BUN-11 | Package inspection uses disposable Bun pack and leaves no checkout tarball. | `tools/shared/tests/workflow-config.test.ts:36-52` invokes `bun pm pack` into system temp and asserts checkout porcelain equality; fresh real pack counted 425 files and left zero `*.tgz`. | PASS |
| BUN-12 | Adoption omits repository-only TypeScript suites. | `scripts/adopt.py:43-53` copies runtime paths only; `scripts/test_adopt.py:185-189` asserts both test trees absent; fresh adoption found 0 `*.test.ts`. | PASS |
| BUN-13 | Adopted knowledge runs with Bun without consumer packages. | `scripts/test_adopt.py:185-198` executes adopted CLI with Bun and requires exit 0 plus summary; fresh adoption reproduced exit 0. | PASS |
| BUN-14 | No forbidden active npm/npx/Vitest/tsx/package-lock/direct-yaml authority outside explicit history. | `tools/shared/tests/qa-skills.test.ts:79-97` defines active roots including `knowledge`; `tools/shared/tests/qa-skills.test.ts:1004-1023` requires `knowledge/AGENTS.md` in the scan and zero violations. | PASS |
| BUN-15 | Public JavaScript/TypeScript commands use current Bun commands. | `README.md:264-270`, `docs/qa/README.md:39-48`, `docs/guidelines/KNOWLEDGE-WIKI.md:94-97`, and `knowledge/AGENTS.md:196-200`; the active-authority assertion at `tools/shared/tests/qa-skills.test.ts:1020-1023` covers repository and adopted instructions. | PASS |
| BUN-16 | Historical evidence retains original command text. | `tools/shared/tests/qa-skills.test.ts:93-97` defines the historical allowlist and `tools/shared/tests/qa-skills.test.ts:1025-1029` requires retained historical forbidden-command text; `git diff --name-only origin/main..HEAD -- docs/qa/evidence` returned 0 paths. | PASS |
| BUN-17 | Malformed Bun versions fail with the required 1.4.x range. | `tools/shared/src/bun-version.ts:1-3`; malformed-version sensor at `tools/shared/tests/qa-skills.test.ts:1032-1036`. | PASS |
| BUN-18 | Package/executable state stays inside disposable boundaries. | `tools/shared/tests/workflow-config.test.ts:37-52` creates/removes a temp destination and asserts source porcelain unchanged; focused security cases also preserve targets on failure at `tools/shared/tests/security-skills-installation.test.ts:409-456`. | PASS |

**Status**: 18/18 requirements match the spec-defined outcome; 0 precision gaps.

## Discrimination Sensor

Both mutations ran only in detached temporary worktree
`/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/tmp.2xqPhlDQIh/authority-sensor`.
The worktree was removed afterward; real checkout porcelain returned to its baseline and worktree
count returned to 4.

| Mutation | Focused command | Result |
| --- | --- | --- |
| Added active `npm run forbidden-sensor` to `README.md:270`. | `bun test tools/shared/tests/qa-skills.test.ts -t "IT-006 keeps Bun as the active command authority"` | KILLED — exit 1; violation named `README.md:270`; 0 pass, 1 fail. |
| Added active `npx forbidden-sensor` to adopted `knowledge/AGENTS.md:198`. | Same focused command. | KILLED — exit 1; violation named `knowledge/AGENTS.md:198`; 0 pass, 1 fail. |

**Sensor depth**: lightweight, two boundary mutations.
**Result**: 2/2 killed — PASS.

## Gate Evidence

| Command | Result |
| --- | --- |
| `bun install --frozen-lockfile` | Exit 0; 49 installs checked across 50 packages; no changes; `bun.lock` SHA-256 unchanged. |
| `bun run test:all` | Exit 0; Bun 1.4.0 reported 118 pass, 0 fail, 1,077 assertions across 8 TypeScript suites; every registered Python suite completed successfully. |
| `bun test tools/shared/tests/security-skills-installation.test.ts` | Exit 0; 38 pass, 0 fail, 177 assertions. |
| `python3 tools/test_orca_assisted_probe.py` | Exit 0; 24/24 passed. |
| `bun run knowledge` | Exit 0; 0 errors, 32 non-gating gap warnings. |
| Fresh disposable adoption check | 0 adopted `*.test.ts`; adopted knowledge exit 0 with summary; adopted probe import exit 0 and 0 Orca calls. |
| `bun pm pack --dry-run --ignore-scripts` | Exit 0; 425 files; no checkout archive. |
| Real `bun pm pack --filename <system-temp>/workflow.tgz --ignore-scripts` | Exit 0; 425 archive members; temp archive removed; checkout porcelain unchanged; 0 checkout `*.tgz`. |
| `python3 .agents/skills/workflow-spec-driven/scripts/validate_spec.py .specs/features/bun-tooling-runtime/spec.md` | Exit 0; 0 errors, 0 warnings. |
| `python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py .specs/features/bun-tooling-runtime/tasks.md` | Exit 0; 0 errors, 0 warnings. |
| `git diff --check origin/main..HEAD` | Exit 0. |
| `git diff --name-only origin/main..HEAD -- docs/qa/evidence` | 0 changed paths. |

## Code Quality and Edge Cases

| Check | Result |
| --- | --- |
| Minimum/surgical change; no unrelated feature | PASS |
| Native Bun/std-library facilities before dependencies | PASS |
| Tests assert contracted outcomes, not implementation presence alone | PASS |
| IT-006 includes and requires the adopted `knowledge/AGENTS.md` boundary | PASS |
| Unsupported/malformed Bun, missing executable, pack residue, and consumer preservation edges | PASS |
| Historical evidence preserved | PASS |
| Guidelines | PASS — `docs/guidelines/TEST-CONTRACT.md` rules 5-6 and `docs/guidelines/VERIFICATION-EVIDENCE.md` applied. |

## Summary

**Overall**: PASS — CP-S3/T5 is safe to consume.

The prior hollow authority scan is closed: `knowledge/` is an active root, the canonical test
requires `knowledge/AGENTS.md`, and independent README plus adopted-knowledge mutations both fail
with the exact offending path. Integrated runtime, package, security, adoption, knowledge, probe,
validator, diff, and residue gates are green. No historical evidence changed.
