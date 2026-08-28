# Hybrid Slice Execution S2 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `d484be1..97f6076`
**Author commits:** `d4fa3fc`, `06f2028`, `97f6076`
**Verifier:** independent session, author != verifier

## Scope and isolation

`git diff --shortstat d484be1..97f6076` reports 17 files changed, 737 insertions, and
167 deletions. `git diff --check d484be1..97f6076` exits 0.

The real checkout porcelain was empty before the gate and mutations. The repository had exactly
2 legitimate worktrees. After all scratch cleanup, porcelain remained empty and
`git worktree list --porcelain | rg -c '^worktree '` still reported 2.

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | Evidence | Result |
| --- | --- | --- | --- |
| HSE-07 | Config and snapshot both use schema version 3. | `tools/test_workflow_config.py:435` asserts parsed config version 3; `tools/test_workflow_config.py:1034` asserts frozen snapshot version 3. | PASS |
| HSE-08 | Only `assisted` and `disabled`; default `assisted`. | `tools/test_workflow_config.py:113` asserts the default; `tools/test_workflow_config.py:128` exercises both accepted values; `tools/test_workflow_config.py:195` asserts the exact invalid-mode error and line 198 proves no replacement. | PASS |
| HSE-09 | `max_workers` accepts `auto` or integer >=1; default `auto`. | `tools/test_workflow_config.py:113` asserts `auto`; `tools/test_workflow_config.py:159` rejects zero, negative, float, object, and array with the exact error at lines 165-168. | PASS |
| HSE-10 | Frozen v3 stores mode, cap, baseline, ceiling, provider, routes, and review cadence. | `tools/test_workflow_config.py:113` asserts the complete parallelization policy, line 117 asserts cadence, and lines 1034-1042 assert version and every delegated role route. | PASS |
| HSE-11 | Config or active snapshot v1/v2 fails with the refresh instruction and zero dispatch effects. | `tools/test_workflow_config.py:204` preserves the stale snapshot and asserts the exact resolver message; `tools/test_parallel_plan.py:397` covers v1/v2 API and CLI messages; `tools/test_parallel_executor.py:214` asserts both versions, exact CLI/API text, and zero adapter/Git/provider/worktree factory calls at line 256. | PASS |
| HSE-12 | Disabled mode is serial and creates no concurrent-writer worktree. | `tools/test_parallel_plan.py:95` asserts one `serial-integration` lane with `worktree: False`; `tools/test_parallel_executor.py:195` proves the coordinator returns before constructing the adapter. | PASS |
| HSE-13 | No ready slice dispatches no writer and reports blocking dependency IDs. | `tools/test_parallel_plan.py:241` builds a valid fully blocked DAG; lines 248-251 assert zero lanes, zero ready IDs, and exact blockers `dependency-incomplete:T2` and `in-progress:T2`. | PASS |
| HSE-14 | Exactly one ready slice uses the integration checkout without an extra worktree. | `tools/test_parallel_plan.py:462` constructs one ready consumer; lines 479-497 assert the complete `serial-integration` lane with `worktree: False`. | PASS |
| HSE-15 | At least two compatible slices start at most two concurrent writer worktrees. | `tools/test_parallel_plan.py:193` proves the `auto` path selects two. A direct valid v3 probe with `max_workers: 4` returned `lane_count: 4` and tasks `T1,T2,T3,T4`; `.agents/skills/workflow-config/scripts/parallel_plan.py:427` uses the integer as the initial cap. This bypasses the required baseline of two. | FAIL |
| HSE-19 | A free lane selects the next compatible ready slice rather than odd/even ownership. | `tools/test_parallel_plan.py:193` asserts declared-order selection independent of parity; `tools/test_parallel_plan.py:217` proves a resource-conflicting middle task is skipped for the next compatible task. | PASS |
| HSE-20 | Only concurrent implementers receive worktrees; read-only roles remain in the clean checkout. | `tools/test_parallel_plan.py:193` asserts both selected implementers have worktrees and lines 201-210 assert Planner, coordinator, Explorer, Verifier, Deep Reviewer, QA Plan, and QA Execute have none. | PASS |
| HSE-40 | Malformed structured input is rejected before the next external mutation. | `tools/test_workflow_config.py:159` rejects invalid cap types/bounds; lines 175-199 reject invalid modes without replacing the snapshot; `tools/test_workflow_config.py:1295` preserves malformed snapshot bytes. | PASS |
| HSE-44 | Overlapping write paths serialize and report exact paths. | `tools/test_parallel_plan.py:179` asserts `serial-integration` and exact `write-conflict:T1:T2:src/shared.py:src/shared.py`. | PASS |
| HSE-46 | Dirty integration checkout performs no writer/worktree/Orca/Git/provider mutation. | `tools/test_parallel_plan.py:228` asserts the blocked plan and zero lanes; `tools/test_parallel_executor.py:275` runs the coordinator with effect-counting factories and lines 305-310 assert empty actions and zero adapter, Git, provider, and worktree calls. | PASS |

**Spec result:** 13 PASS, 1 FAIL across 14 scoped requirements. The four gaps from the prior S2
report now have direct evidence, but their stored fingerprints remain open because this checkpoint
did not reach PASS.

## Gates

- `python3 tools/test_workflow_config.py`: 45 passed, 0 failed.
- `python3 tools/test_parallel_plan.py`: 22 passed, 0 failed.
- `python3 tools/test_parallel_executor.py`: 47 passed, 0 failed.
- `python3 tools/test_qa_parallel_pilot.py`: 13 passed, 0 failed.
- `npm_config_offline=true npm run test:all`: exit 0. Vitest reported 8 files and 111 tests passed;
  every Python suite completed with zero failures.
- Focused inventory from `rg -c '^def test_'` and `git show d484be1:<file>`: 127 current versus
  120 at the base, delta +7. No focused test was removed.

Green gates do not override the HSE-15 outcome failure.

## Discrimination sensor

Each mutation ran in a detached temporary worktree at `97f6076`. Every worktree and temporary parent
was removed before the next mutation.

| Mutation | Focused command | Result |
| --- | --- | --- |
| Replace the planner's v1/v2 refresh error with generic `invalid workflow snapshot`. | `python3 tools/test_parallel_plan.py` | KILLED: exact stale-version assertion failed. |
| Make a fully blocked plan create a read-only Verifier worktree lane. | `python3 tools/test_parallel_plan.py` | KILLED: zero-lane/read-only policy assertion failed. |
| Disable the coordinator's dirty-plan short-circuit. | `python3 tools/test_parallel_executor.py` | KILLED: zero-effect counter assertion failed. |

**Sensor result:** 3 injected, 3 killed, 0 survived.

## Code quality

The remediation is localized and reuses the resolver, planner, executor, and canonical suites. It
adds no dependency or compatibility reader. The initial-cap branch is the only scoped outcome gap:
the configured ceiling is incorrectly treated as permission to skip health-gated admission.

## Ranked gap and fix task

1. **HSE-15, Major:** cap initial assisted writer selection at `min(2, max_workers)` for integer
   caps, retaining one serial lane for cap 1. Add a canonical planner assertion that explicit caps
   3 and 4 still select exactly two initial writers and block the remainder until later health
   admission. Fingerprint
   `a8d8977c8dfd6c896ca9968c85e588a5db0601bb3a050789ba5ca496b7fecb93`.

## Summary

**Overall:** FAIL. CP-S2 must not release to S3. The four previously reported gaps are now covered,
the full gate passes, and all required mutants die. Explicit `max_workers` values above two still
start more than two writers before health evidence, violating HSE-15 and the approved admission
contract.
