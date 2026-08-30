# Bun Tooling Runtime — S1 Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/bun-tooling-runtime/spec.md`
**Diff range**: `ded5c06^..2ff1968`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

---

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | PASS | Bun owns the package, lock, discovery, version guard, test runner, and full gate. |
| T2 | PASS | Bun executes the knowledge CLI directly and native YAML preserves parser outcomes. |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| BUN-01 | Pin `bun@1.4.0` and support exactly Bun 1.4.x. | `tools/shared/tests/deep-review-installation.test.ts:68` — `expect(packageManifest.packageManager).toBe("bun@1.4.0")`; `tools/shared/tests/qa-skills.test.ts:932` — `expect(manifest.engines?.bun).toBe(">=1.4.0 <1.5.0")`. | PASS |
| BUN-02 | Commit `bun.lock`, remove `package-lock.json`, and keep frozen install byte-stable. | `tools/shared/tests/deep-review-installation.test.ts:69-70` — exact presence/absence assertions; frozen install preserved SHA-256 `2017e1f780055f755fa145636d98b8f54a7dfc4fcbc89bf982f0ed42dc22cfb5`. | PASS |
| BUN-03 | Discover structural TypeScript tests only below `tools/`. | `tools/shared/tests/qa-skills.test.ts:933-935` — exact `[test]`, root, and preload assertions. | PASS |
| BUN-04 | Unsupported Bun fails before executing a suite. | `tools/shared/tests/qa-skills.test.ts:962-966` invokes the sensor; `tools/shared/tests/qa-skills.test.ts:71-73` requires non-zero, absent marker, and the 1.4.x error. | PASS |
| BUN-05 | Every TypeScript suite uses `bun:test`; no Vitest runtime remains. | `tools/shared/tests/qa-skills.test.ts:943-957` enumerates all suites, asserts `bun:test`, and rejects the dependency. | PASS |
| BUN-06 | Knowledge runs its TypeScript entrypoint directly with Bun, without `tsx`. | `tools/knowledge/tests/cli.test.ts:43-45` — exact `bun tools/knowledge/src/cli.ts` assertion; `tools/shared/tests/qa-skills.test.ts:957` rejects direct `tsx`. | PASS |
| BUN-07 | Frontmatter uses `Bun.YAML.parse` without direct `yaml`, preserving exact outcomes. | `tools/shared/tests/qa-skills.test.ts:957-959` asserts native authority; `tools/shared/tests/frontmatter.test.ts:6-54` asserts absence, mapping, empty, unclosed, malformed, scalar, and CRLF outcomes. | PASS |
| BUN-08 | `bun run test:all` runs Bun suites followed by `scripts/test_adopt.py` and every canonical Python suite. | `tools/shared/tests/qa-skills.test.ts:936-940` asserts the exact chain, adopter, 15-entrypoint inventory, and sorted execution loop. | PASS |
| BUN-17 | Malformed or unsupported versions fail with the required 1.4.x range. | `tools/shared/tests/qa-skills.test.ts:962-966` runs both injected values; helper assertions at `tools/shared/tests/qa-skills.test.ts:71-73` require fail-closed behavior. | PASS |

**Status**: 9/9 S1 criteria match precise spec outcomes.

## Assigned Test Contract

| Case | Expected | Evidence | Result |
| --- | --- | --- | --- |
| UT-001 | Unsupported and malformed Bun exit non-zero before suites. | Focused contract passed; neutralizing the guard in scratch failed the contract before completion. | PASS |
| UT-002 | Native YAML preserves every frontmatter branch. | `tools/shared/tests/frontmatter.test.ts:6-54`; replacing parse output with `{}` caused 4 failures. | PASS |
| IT-001 | Frozen install succeeds without changing the lock. | Before/after lock SHA-256 matched and install exited 0. | PASS |
| IT-002 | Bun discovers only canonical suites under `tools/`. | Exact root/preload assertions plus `bun test`: 117 passed across 8 files. | PASS |
| IT-003 | Full gate runs Bun and every Python suite. | Full gate exited 0; deleting the Python discovery/execution loop failed the owning contract. | PASS |
| IT-005 | Adoption is byte-stable, omits TS tests, and runs knowledge with Bun. | Assigned to T4/S3 by `tasks.md`; remains open and does not weaken S1 traceability. | OPEN — T4/S3 |

## Gate Evidence

- `bun install --frozen-lockfile` — exit 0; `bun.lock` SHA-256 unchanged at `2017e1f780055f755fa145636d98b8f54a7dfc4fcbc89bf982f0ed42dc22cfb5`.
- `bun test tools/shared/tests/qa-skills.test.ts tools/shared/tests/frontmatter.test.ts tools/knowledge/tests/cli.test.ts` — 37 passed, 0 failed, 544 assertions, 3 files.
- `bun run test:all` — exit 0; Bun phase 117 passed, 0 failed, 1070 assertions, 8 files; adopter plus 15 discovered Python entrypoints exited 0.
- `find tools -type f -name 'test_*.py' | sort | nl -ba` — 15 Python tool-suite entrypoints.
- `find tools -type f -name '*.test.ts' | sort | nl -ba` — 8 TypeScript suites.
- `git worktree list --porcelain | grep '^worktree ' | wc -l` — 2 source worktrees after scratch cleanup and stale-entry prune.
- `git diff --check` — exit 0.

The planned T1 count was 114 Bun tests. Current count is 117: delta +3 contract tests from remediation, with no existing suite removed.

## Discrimination Sensor

| Mutation | Scratch file | Result |
| --- | --- | --- |
| Remove the `find | sort | while | python3` loop from `test:python` | `package.json:15` | KILLED: exact Bun-to-Python contract failed 1/27. |
| Neutralize the Bun 1.4.x guard with `false &&` | `tools/shared/src/bun-version.ts:1` | KILLED: version sensor failed 1/27 because the marker ran. |
| Replace `Bun.YAML.parse(...)` with `{}` | `tools/shared/src/frontmatter.ts:33` | KILLED: parser suite failed 4/7. |

**Sensor depth**: lightweight, three behavior-level mutations in a detached temporary worktree.
**Result**: 3/3 killed — PASS.

## Edge Cases

- PASS — malformed Bun version fails closed before the marker suite.
- PASS — unsupported Bun version fails closed before the marker suite.
- PASS — absent, empty, malformed, scalar, nested, and CRLF frontmatter retain exact outcomes.
- OPEN — package/executable mutations outside disposable boundaries belong to T3/T4 (BUN-18), not S1.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum native implementation | PASS |
| Surgical changes; no unrelated product behavior | PASS |
| No new runtime abstraction or dependency | PASS |
| Tests assert spec outcomes, not implementation success alone | PASS |
| Every S1 test maps to BUN-01..08 or BUN-17 | PASS |
| Guidelines followed: feature `tests.md`, `tasks.md`, and verifier `validate.md` | PASS |

## Validator Evidence

- `validate_spec.py .specs/features/bun-tooling-runtime/spec.md` — 0 errors, 0 warnings.
- `validate_tasks.py .specs/features/bun-tooling-runtime/tasks.md` — 0 errors, 0 warnings.
- `validate_state.py bun-tooling-runtime` — expected non-zero because final `validation.md` is reserved for the incomplete five-task feature; this S1 checkpoint is `validation-s1.md`.

## Requirement Traceability Update

CP-S1 is PASS for T1/T2: BUN-01..08 and BUN-17 are verified. BUN-09..16 and BUN-18 remain assigned to T3..T5. IT-005 remains exclusively assigned to T4/S3 and is not an S1 blocker.
