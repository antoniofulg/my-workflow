# Hybrid Slice Execution S2 Validation

**Verdict:** PASS
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `d484be1..89ddb3f`
**Verifier:** independent session, author != verifier

## Scope and isolation

`git diff --shortstat d484be1..89ddb3f` reports 17 files changed, 764 insertions, and
167 deletions. `git diff --check d484be1..89ddb3f` exits 0.

The real checkout porcelain was empty before gates and mutations. The repository had exactly
2 legitimate worktrees. After scratch cleanup, porcelain remained empty and
`git worktree list --porcelain | rg -c '^worktree '` still reported 2.

## Task completion

| Task | Recorded state | Verification result |
| --- | --- | --- |
| T3 | Complete | PASS: HSE-07 through HSE-11 and HSE-40 match specified outcomes |
| T4 | Complete | PASS: HSE-12 through HSE-15, HSE-19, HSE-20, HSE-44, and HSE-46 match specified outcomes |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | `file:line` + assertion evidence | Result |
| --- | --- | --- | --- |
| HSE-07 | Config and snapshot both use schema version 3. | `tools/test_workflow_config.py:435` — `assert config["version"] == 3`; `tools/test_workflow_config.py:1034` — `assert snapshot["version"] == 3`. | PASS |
| HSE-08 | Only `assisted` and `disabled`; default `assisted`. | `tools/test_workflow_config.py:113` asserts exact default policy; `tools/test_workflow_config.py:128` iterates both accepted modes; `tools/test_workflow_config.py:195` asserts exact invalid-mode error and line 198 asserts snapshot bytes unchanged. | PASS |
| HSE-09 | `max_workers` accepts `auto` or integer >=1; default `auto`. | `tools/test_workflow_config.py:113` asserts `max_workers: auto`; `tools/test_workflow_config.py:159` exercises zero, negative, float, object, and array; lines 165-168 assert exact rejection. | PASS |
| HSE-10 | Frozen v3 stores mode, cap, baseline, ceiling, provider, routes, and review cadence. | `tools/test_workflow_config.py:113` asserts exact parallelization object; line 117 asserts cadence; lines 1034-1042 assert version and each delegated role route. | PASS |
| HSE-11 | Config or active snapshot v1/v2 fails with refresh instruction and zero dispatch effects. | `tools/test_workflow_config.py:216` asserts resolver refresh text; `tools/test_parallel_plan.py:443` and lines 452-456 assert API/CLI text; `tools/test_parallel_executor.py:253` asserts executor text and line 256 asserts zero adapter/Git/provider/worktree calls. | PASS |
| HSE-12 | Disabled mode is serial and creates no concurrent writer worktree. | `tools/test_parallel_plan.py:105` asserts exact serial lane with `worktree: False`; `tools/test_parallel_executor.py:205`-209 assert disabled result and adapter factory untouched. | PASS |
| HSE-13 | No ready slice dispatches no writer and reports blocking dependency IDs. | `tools/test_parallel_plan.py:276` — `assert plan["lanes"] == []`; lines 277-279 assert empty ready set and exact blockers `dependency-incomplete:T2` and `in-progress:T2`. | PASS |
| HSE-14 | Exactly one ready slice uses integration checkout without an extra worktree. | `tools/test_parallel_plan.py:507`-540 asserts exact one-lane CLI payload, including `execution: serial-integration`, `worktree: False`, and every read-only role false. | PASS |
| HSE-15 | Two or more compatible slices initially start at most two writer worktrees, even when explicit cap is 3 or 4. | `tools/test_parallel_plan.py:224` exercises `auto,1,2,3,4`; lines 228-230 assert one lane only for cap 1 and exactly two otherwise; lines 239-240 assert remaining tasks blocked by effective baseline. | PASS |
| HSE-19 | A free lane selects next compatible ready slice instead of odd/even ownership. | `tools/test_parallel_plan.py:203`-204 assert declared-order selection; lines 245-251 prove a resource-conflicting middle task is skipped for compatible T3. | PASS |
| HSE-20 | Only concurrent implementers get worktrees; read-only roles remain in clean checkout. | `tools/test_parallel_plan.py:205` asserts selected writer worktrees; lines 206-215 assert implementer true and Planner/coordinator/Explorer/Verifier/Deep Reviewer/QA roles false. | PASS |
| HSE-40 | Malformed structured input is rejected before next external mutation. | `tools/test_workflow_config.py:159`-168 reject invalid cap schemas; lines 175-199 reject invalid mode without replacement; lines 1295-1308 preserve malformed snapshot bytes. | PASS |
| HSE-44 | Overlapping write paths serialize and report exact paths. | `tools/test_parallel_plan.py:189` asserts `serial-integration`; lines 191-193 assert exact `write-conflict:T1:T2:src/shared.py:src/shared.py`. | PASS |
| HSE-46 | Dirty integration checkout performs no writer/worktree/Orca/Git/provider mutation. | `tools/test_parallel_plan.py:261`-264 assert blocked plan and zero lanes; `tools/test_parallel_executor.py:305`-310 assert blocked result, empty actions, and zero adapter/Git/provider/worktree calls. | PASS |

**Spec result:** 14/14 scoped requirements matched; 0 precision gaps.

## Gates

- `python3 tools/test_workflow_config.py`: exit 0; 45 passed, 0 failed.
- `python3 tools/test_parallel_plan.py`: exit 0; 23 passed, 0 failed.
- `python3 tools/test_parallel_executor.py`: exit 0; 47 passed, 0 failed.
- `python3 tools/test_qa_parallel_pilot.py`: exit 0; 13 passed, 0 failed.
- `npm_config_offline=true npm run test:all`: exit 0. Vitest reported 8 files and 111 tests passed; every Python suite exited 0.
- `rg -n '^def test_' tools/test_workflow_config.py tools/test_parallel_plan.py tools/test_parallel_executor.py tools/test_qa_parallel_pilot.py | wc -l`: 128 current focused definitions.
- `git grep -n '^def test_' d484be1 -- tools/test_workflow_config.py tools/test_parallel_plan.py tools/test_parallel_executor.py tools/test_qa_parallel_pilot.py | wc -l`: 120 base definitions; delta +8.
- `git diff --diff-filter=D --name-only d484be1..89ddb3f -- 'tools/test*' | wc -l`: 0 deleted focused test files.

## Discrimination sensor

Each valid mutation ran in its own detached temporary worktree at `89ddb3f`; each owning suite
failed, then `git worktree remove --force` removed the scratch tree.

| Mutation | Fault | Focused command | Result |
| --- | --- | --- | --- |
| M1 | Use automatic ceiling instead of baseline for explicit `max_workers`, so cap 4 admits four initial writers. | `python3 tools/test_parallel_plan.py` | KILLED: `test_initial_admission_uses_baseline_before_explicit_ceiling` failed; exit 1. |
| M2 | Give a fully blocked plan a concurrent Verifier worktree lane. | `python3 tools/test_parallel_plan.py` | KILLED: `test_fully_dependency_blocked_dag_selects_no_lane_and_names_blockers` failed; exit 1. |
| M3 | Bypass dirty-baseline planner short-circuit before coordinator dispatch. | `python3 tools/test_parallel_executor.py` | KILLED: `test_dirty_assisted_coordinator_has_zero_external_effects` failed; exit 1. |

**Sensor result:** 3/3 valid mutations killed, 0 survived. One earlier no-op injection matched no
source branch and was discarded before M3; it did not constitute a mutant.

## Convergence state

The verifier invoked `review_convergence.py` once for each of the five open S2 entries using stored
requirement, root cause, failure path, exact `--previous-fingerprint`, `--gate-passed`, and no
`--verifier-failed`. Every call returned `status: closed` with its count unchanged at 1.

- Closed fingerprints: `2983a344...`, `3b758f06...`, `81a3b9dd...`, `a8d8977c...`, `d52c885e...`.
- `python3 -c 'import json; from collections import Counter; p=json.load(open(".specs/features/hybrid-slice-execution/review-fingerprints.json")); print(len(p["fingerprints"]), Counter(v["status"] for v in p["fingerprints"].values()))'`: 12 total, 12 closed, 0 open, 0 halted.

## Code quality and isolation

The fix is localized to existing stdlib resolver/planner/executor paths and canonical suites. No
compatibility reader, dependency, unrelated abstraction, weakened assertion, deleted test, live
Orca call, or persistent scratch worktree was introduced. Tests remain bounded by assigned S2
requirements in `tests.md`.

No lesson was recorded: all remediations passed; no mutant, uncovered criterion, precision gap, or
spec deviation survived.

## Summary

**Overall:** PASS. CP-S2 may release to S3. No ranked gap remains.
