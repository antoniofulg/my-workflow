# Bun Tooling Runtime — S3/T4 Technical Validation

**Date**: 2026-08-29
**Spec**: `.specs/features/bun-tooling-runtime/spec.md`
**Diff range**: `1438b7d..a1b9e42`
**Verifier**: independent sub-agent (author != verifier)
**Verdict**: PASS

## Scope

T4 only: BUN-11, BUN-12, BUN-13, BUN-18; IT-004, IT-005, SEC-002. T5 and
BUN-14..16 remain pending and do not affect this checkpoint verdict.

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| BUN-11 | Package inspection uses `bun pm pack` in a disposable destination and leaves no checkout tarball. | `tools/shared/tests/workflow-config.test.ts:37` creates a system-temp destination; `tools/shared/tests/workflow-config.test.ts:41` invokes exact Bun pack argv; `tools/shared/tests/workflow-config.test.ts:51` removes the destination; `tools/shared/tests/workflow-config.test.ts:52` asserts source porcelain is byte-equal to its baseline. | PASS |
| BUN-12 | Adoption installs zero repository-only TypeScript suites. | `scripts/adopt.py:49` copies only knowledge `src`; `scripts/adopt.py:52` copies only shared frontmatter runtime; `scripts/test_adopt.py:188` asserts the knowledge tests are absent; `scripts/test_adopt.py:189` asserts shared tests are absent. | PASS |
| BUN-13 | Adopted knowledge CLI runs with Bun and native YAML, without consumer packages. | `scripts/test_adopt.py:190` invokes `bun` on installed `cli.ts`; `scripts/test_adopt.py:197` requires exit 0; `scripts/test_adopt.py:198` requires the knowledge marker. | PASS |
| BUN-18 | Package inspection cannot create state outside its disposable boundary or mutate the checkout. | `tools/shared/tests/workflow-config.test.ts:39` captures the checkout baseline and `tools/shared/tests/workflow-config.test.ts:52` requires exact equality in `finally`; redirecting the tarball into the checkout failed the owning suite with the new untracked path in the assertion diff. | PASS |

**Spec-anchored status**: 4/4 outcomes matched exactly; 0 precision gaps.

## Assigned Evidence

- `bun pm pack --dry-run --ignore-scripts`: exit 0.
- Real `bun pm pack --filename <temp>/workflow.tgz --ignore-scripts`: exit 0, 421
  tar members, temp directory removed, source porcelain unchanged.
- Disposable adoption: 139 installed files; second adoption byte-identical; 0
  `*.test.ts`; 0 `docs/qa/evidence/` paths.
- Adopted knowledge CLI: exit 0 and emitted `knowledge:`.
- Adopted probe import with fake `orca` first on `PATH`: exit 0, 0 Orca calls.
- No live Orca, npm, npx, network, or registry publication used.

## Discrimination Sensor

Mutation ran in detached temporary worktree `/tmp/my-workflow-bun-t4-mutant-a1b9e42`, which was
removed after the run.

| Mutation | File:line | Result |
| --- | --- | --- |
| Redirect package tarball from the temporary destination to repository root. | `tools/shared/tests/workflow-config.test.ts:38` | Killed: owning suite reported 4 pass, 1 fail; `expect(checkoutPorcelain()).toBe(before)` exposed `?? workflow-verifier-mutant.tgz`. |

**Sensor depth**: lightweight, focused re-test of the previously surviving highest-risk mutant.
**Result**: 1/1 killed — PASS. Real checkout porcelain after cleanup exactly matched its pre-sensor
baseline: only this untracked report.

## Gates

- `bun test tools/shared/tests/workflow-config.test.ts`: 5 passed, 0 failed, 84
  expectations.
- `python3 scripts/test_adopt.py`: 24 registered checks passed (`ok`).
- `bun install --frozen-lockfile`: exit 0; 49 installs across 50 packages, no changes;
  `bun.lock` SHA-256 remained
  `2017e1f780055f755fa145636d98b8f54a7dfc4fcbc89bf982f0ed42dc22cfb5`.
- `bun run test:all`: exit 0; Bun layer 117 passed, 0 failed, 1071 expectations
  across 8 files; `scripts/test_adopt.py` plus all 15 `tools/**/test_*.py` entrypoints
  exited 0.
- `.agents/skills/workflow-spec-driven/scripts/validate_spec.py`: 0 errors, 0 warnings.
- `.agents/skills/workflow-spec-driven/scripts/validate_tasks.py`: 0 errors, 0 warnings.
- `.agents/skills/workflow-spec-driven/scripts/check_commit.py --message "test(adopt): verify Bun package checkpoint"`: OK.
- `git diff --check 1438b7d..HEAD`: exit 0.
- `validate_state.py bun-tooling-runtime`: expected non-zero because final
  `validation.md` belongs after pending T5; this checkpoint is intentionally
  `validation-s3-t4.md`.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum native implementation | PASS |
| Surgical task scope | PASS |
| No product behavior beyond T4 | PASS |
| Assertions target spec outcomes | PASS |
| Package/adoption coverage is discriminating | PASS |
| Every T4 test maps to IT-004, IT-005, or SEC-002 | PASS |
| Project-local validation contract followed | PASS |

## Summary

**Overall**: PASS — T4 package/adoption checkpoint is safe to consume.

Package inspection uses Bun inside a disposable boundary and now has a durable assertion that
kills checkout-residue regressions. Adoption installs runtime-only TypeScript, remains byte-stable,
runs knowledge through Bun without consumer packages, and imports the assisted probe without an
Orca call. T5 remains pending for the public Bun command contract.
