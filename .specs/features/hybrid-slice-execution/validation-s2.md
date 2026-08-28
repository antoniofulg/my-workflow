# Hybrid Slice Execution S2 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `d484be1..06f2028`
**Author commits:** `d4fa3fc`, `06f2028`
**Verifier:** independent session, author != verifier

## Scope and diff

`git diff --shortstat d484be1..06f2028` reports 14 files changed, 457 insertions, and
165 deletions. `git diff --check d484be1..06f2028` exits 0.

The frozen route remains coherent and intentionally serial for this feature:
`.specs/features/hybrid-slice-execution/workflow.json:20` stores version 3 policy with
`mode: disabled`, `max_workers: auto`, automatic baseline 2, and automatic ceiling 4.

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| HSE-07 | Config and snapshot both use schema version 3. | `tools/test_workflow_config.py:430` asserts parsed config version 3; `tools/test_workflow_config.py:1028` asserts frozen snapshot version 3. | PASS |
| HSE-08 | Only `assisted` and `disabled`; default `assisted`. | `tools/test_workflow_config.py:107` asserts the default mode is `assisted`; `tools/test_workflow_config.py:124` exercises both accepted modes; `tools/test_workflow_config.py:175` asserts the exact invalid-mode error and unchanged snapshot. | PASS |
| HSE-09 | `max_workers` accepts `auto` or integer >=1; default `auto`. | `tools/test_workflow_config.py:113` asserts `auto`; `tools/test_workflow_config.py:159` rejects 0, -1, float, object, and array with the exact error. | PASS |
| HSE-10 | Frozen v3 stores policy, provider, role routes, and review cadence. | `tools/test_workflow_config.py:113` asserts mode/cap/baseline/ceiling/provider; `tools/test_workflow_config.py:117` asserts review cadence; `tools/test_workflow_config.py:1028` asserts every delegated role route. | PASS |
| HSE-11 | Config or active snapshot v1/v2 fails with explicit `--refresh` instruction and zero dispatch effect. | Resolver evidence passes at `tools/test_workflow_config.py:204`. Planner instead raises generic `invalid workflow snapshot` at `.agents/skills/workflow-config/scripts/parallel_plan.py:44`, and its test requires that weaker message at `tools/test_parallel_plan.py:357`. Executor also collapses stale versions into generic `invalid workflow snapshot` at `.agents/skills/autonomous/scripts/parallel_execute.py:492`. Direct CLI probes for versions 1 and 2 both exited 1 with `parallel plan: invalid workflow snapshot`, not the specified refresh instruction. | FAIL |
| HSE-12 | Disabled mode is serial and creates no concurrent-writer worktree. | `tools/test_parallel_plan.py:95` asserts one `serial-integration` lane with `worktree: False`; `tools/test_parallel_executor.py:1420` forbids planner, Git-state, and adapter calls in disabled execution. | PASS |
| HSE-13 | No ready slice means zero writers plus exact blocking dependency IDs. | No canonical assertion constructs a fully dependency-blocked valid DAG and asserts both `lanes == []` and dependency IDs. Existing dependency tests retain another ready lane, for example `tools/test_parallel_plan.py:246`. Evidence-or-zero applies. | GAP |
| HSE-14 | Exactly one ready slice runs in the integration checkout without a worktree. | `tools/test_parallel_plan.py:429` asserts the complete one-lane result, including `serial-integration` and `worktree: False` at line 441. | PASS |
| HSE-15 | Two or more compatible slices start at most two writer worktrees. | `tools/test_parallel_plan.py:193` asserts exactly T1/T2 selected, T3/T4 capped, and every selected lane has `worktree: True`. | PASS |
| HSE-19 | A free lane selects the next ready compatible slice rather than odd/even ownership. | `tools/test_parallel_plan.py:193` asserts declared-order compatible selection independent of parity; `tools/test_parallel_plan.py:207` proves a conflicting middle task is skipped while the next compatible task is selected. | PASS |
| HSE-20 | Only concurrent implementer writers receive worktrees; read-only roles remain in integration checkout. | `tools/test_parallel_plan.py:193` proves selected writer lanes use worktrees, but no test supplies or observes Planner, coordinator, Explorer, or read-only review roles. The assigned UT-011 outcome is not fully asserted. Evidence-or-zero applies. | GAP |
| HSE-40 | Malformed/untrusted structured input is rejected before the next external mutation. | `tools/test_workflow_config.py:159` rejects cap type/bounds; `tools/test_workflow_config.py:175` preserves the prior snapshot on invalid mode; `tools/test_workflow_config.py:1295` preserves malformed snapshot bytes. | PASS |
| HSE-44 | Overlapping write paths serialize and report exact paths. | `tools/test_parallel_plan.py:179` asserts `serial-integration` and exact `write-conflict:T1:T2:src/shared.py:src/shared.py`. | PASS |
| HSE-46 | Dirty integration checkout causes zero writer/worktree/Orca/Git/provider mutations. | `tools/test_parallel_plan.py:218` asserts blocked decision and empty lanes. It does not run the coordinator with effect-counting fakes, so the specified zero effects across every boundary are not directly asserted. | GAP |

**Spec result:** 10 PASS, 1 FAIL, 3 evidence gaps across 14 scoped requirements.

## Gates

- `python3 tools/test_workflow_config.py && python3 tools/test_parallel_plan.py && python3 tools/test_parallel_executor.py && python3 tools/test_qa_parallel_pilot.py` exited 0: config 45, planner 21, executor 45, QA pilot 13; total 124 passed, 0 failed.
- `npm_config_offline=true npm run test:all` exited 0. Vitest: 8 files, 111 tests passed, 0 failed. Every Python test command exited 0.
- Focused test-function inventory from `rg -c '^def test_'` versus `git show d484be1:<file>`: 120 before, 124 after, delta +4. No focused test was removed.

Green gates do not override HSE-11 or evidence-or-zero gaps.

## Discrimination sensor

All mutations ran only in detached `/tmp/hse-s2-sensor.NMZkSp/tree`, then the worktree and parent
directory were removed.

| Mutation | Focused command | Result |
| --- | --- | --- |
| Bypass stale v1/v2 refresh branch in `workflow_config.py`. | `python3 tools/test_workflow_config.py` | KILLED: exact stale-snapshot error assertion failed. |
| Change default mode `assisted` to `disabled`. | `python3 tools/test_workflow_config.py` | KILLED: default snapshot assertion failed. |
| Bypass dirty-baseline branch in `parallel_plan.py`. | `python3 tools/test_parallel_plan.py` | KILLED: blocked-decision assertion failed. |

**Sensor result:** 3 injected, 3 killed, 0 survived.

Before sensor work, real checkout porcelain was empty. After scratch cleanup and fingerprint
recording, `git diff --name-only` lists only
`.specs/features/hybrid-slice-execution/review-fingerprints.json`; source files have no real-tree
diff. `git worktree list --porcelain | rg -c '^worktree '` reports 14 both before and after sensor
cleanup.

## Code quality

The implementation is localized and reuses the existing resolver, planner, executor, and tests.
No dependency or compatibility layer was added. The public stale-version error is nevertheless
inconsistent across readers, and three assigned outcomes lack exact canonical assertions.

## Ranked gaps and fix tasks

1. **HSE-11, Major:** make planner and executor distinguish snapshot versions 1/2 and return the
   exact refresh instruction before planning/effects. Extend both canonical suites to assert the
   exact message and zero adapter/worktree/provider effects for v1 and v2. Fingerprint
   `81a3b9dd92021d7a716e9690a3e4862827a0a710749364e8a7ec7a3854b882a1`.
2. **HSE-46, Major test gap:** exercise dirty assisted execution through `Coordinator` with
   effect-counting Git, worktree, Orca, and provider fakes; assert every count is zero. Fingerprint
   `3b758f0615f29c07278568858fe492951453c2a432f5fc52364c58dd64465ae9`.
3. **HSE-13, Minor test gap:** add a valid fully dependency-blocked planner case and assert no lanes
   plus exact dependency blocker IDs. Fingerprint
   `d52c885e44a136c64f3f832a7457b252818baf7c4a53901f4e5b303d5b1b7cff`.
4. **HSE-20, Minor test gap:** extend the owning role/planner contract so read-only roles are present
   and explicitly receive no worktree while two implementer writers do. Fingerprint
   `2983a344cc820c21d390af298ce7bd179a543dd6c9bec800b4829472e5191bf4`.

## Summary

**Overall:** FAIL. CP-S2 must not release to S3. The v3 resolver/default/disabled/hybrid planning
mechanics pass their gates and all three mutants die, but HSE-11 is observably wrong and HSE-13,
HSE-20, and HSE-46 remain evidence gaps.
