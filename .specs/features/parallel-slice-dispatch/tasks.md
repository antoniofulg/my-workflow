# Parallel Slice Dispatch Tasks

**Design:** `.specs/features/parallel-slice-dispatch/design.md`
**Status:** Done

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, existing workflow-config tests, and the approved spec.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Workflow configuration | integration | Default, all enum values, invalid input, atomic preservation, resume | `tools/test_workflow_config.py` | `python3 tools/test_workflow_config.py` |
| Parallel planner | unit + integration | Every graph branch and fallback reason in `tests.md` | `tools/test_parallel_plan.py` | `python3 tools/test_parallel_plan.py` |
| Agent workflow contract | contract | Serial fallback, worker lifecycle, sync, invalidation, existing reviews | `tools/shared/tests/*.test.ts` | `npm_config_offline=true npm test` |
| Specs and decisions | structural | Spec/tasks/AD validators and clean diff | `.specs/**` | validator commands below |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Configuration or planner task | Targeted Python test file plus `git diff --check` |
| Full | Agent contract or final tree | `npm_config_offline=true npm test` plus all Python workflow tests |
| Build | Planning/decision state | TLC validators, `python3 tools/ad-index.py --check`, and `git diff --check` |

## Execution Plan

Phases and tasks stay sequential. Each phase is one observable vertical slice.

### Phase 1: Freeze the mode

```text
T1
```

### Phase 2: Plan ready slices

```text
T2
```

### Phase 3: Consume the plan safely

```text
T3 → T4
```

## Task Breakdown

### T1: Freeze the parallelization mode

**Status:** complete
**Observable behaviour:** Workflow resolution defaults to `disabled`, accepts only `disabled|safe|full`, freezes the selected mode, and preserves existing snapshots on invalid input.
**Where:** `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on:** None
**Requirement:** PAR-01, PAR-02, PAR-03, PAR-04
**Tests:** IT-001, IT-002, IT-003, IT-004 in `tools/test_workflow_config.py`
**Gate:** Run `python3 tools/test_workflow_config.py`, both TLC validators by explicit feature path, `python3 tools/ad-index.py --check`, and `git diff --check`. Commit `feat(config): freeze parallel dispatch mode`.

### T2: Generate deterministic slice plans

**Status:** complete
**Observable behaviour:** A read-only CLI preserves intra-slice order and projects disabled, safe, full, blocked, checkpoint, conflict, and serial-fallback states deterministically.
**Where:** `.agents/skills/workflow-config/scripts/parallel_plan.py`
**Depends on:** T1
**Requirement:** PAR-05, PAR-06, PAR-07, PAR-08, PAR-09, PAR-10, PAR-11
**Tests:** UT-001–UT-007 and IT-005 in `tools/test_parallel_plan.py`
**Gate:** Run `python3 tools/test_parallel_plan.py`, `python3 tools/test_workflow_config.py`, `git diff --check`, and the task validator. Commit `feat(workflow): plan parallel slice dispatch`.

### T3: Define autonomous inter-slice orchestration

**Status:** complete
**Observable behaviour:** Autonomous consumes a safe plan only with an isolated capable orchestrator, ends waiting worker turns, follows up on dependency events, syncs at checkpoints, and falls back serially without changing TLC.
**Where:** `.agents/skills/autonomous/references/parallelization.md`
**Depends on:** T2
**Requirement:** PAR-12, PAR-13, PAR-14, PAR-15, PAR-16
**Tests:** IT-006 in the existing shared workflow contract suite
**Gate:** Run `npm_config_offline=true npm test`, both targeted Python suites, `git diff --check`, and the task validator. Commit `feat(workflow): orchestrate parallel slices safely`.

### T4: Record durable dispatch and spec lifecycle decisions

**Status:** complete
**Observable behaviour:** Future features read the opt-in dispatch policy and versioned spec lifecycle from the decision index without relying on stale `AD-003`.
**Where:** `.specs/STATE.md`
**Depends on:** T3
**Requirement:** PAR-12, PAR-16
**Tests:** Structural AD index and feature state validation
**Gate:** Run `python3 tools/ad-index.py`, `python3 tools/ad-index.py --check`, both TLC validators, `npm_config_offline=true npm test`, and `git diff --check`. Commit `docs(workflow): record parallel dispatch decisions`.

## Review Remediation

| Task | Depends on | Status | Observable behaviour | Tests | Gate | Commit |
| --- | --- | --- | --- | --- | --- | --- |
| T2R1 | T2 | complete | Dependency eligibility precedes write-conflict evaluation; incomplete dependencies remain blocked; `in_progress` is never redispatched; `waiting` becomes `follow_up` only after dependencies complete. | Regression cases in `tools/test_parallel_plan.py` | `python3 tools/test_parallel_plan.py`, `python3 tools/test_workflow_config.py`, `git diff --check`, task validator | `fix(workflow): harden parallel planner readiness` |
| T3R1 | T3 | complete | IT-006 proves exact dependency/head reporting, dirty-worker refusal, gate reruns after checkpoint and invalidation, affected evidence invalidation, and final reconciliation no-op. | Existing `tools/shared/tests/autonomous-parallelization.test.ts` IT-006 | Targeted Vitest, full npm/Python suites, validators, `git diff --check` | `test(workflow): enforce parallel orchestration safety` |
| TDR1 | T3/T4 | complete | Deep-review blockers are closed: unreadable task input fails non-zero, planner validates snapshot identity/schema, checked-in v1 snapshots resume with disabled mode, and IT-006 pins clean checkpoints and sync ordering. | Existing workflow-config and autonomous contract suites | Full npm/Python suites, validators, AD index, `git diff --check` | `fix(workflow): close parallel dispatch review blockers` |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | None | Match |
| T2 | T1 | Phase 1 precedes Phase 2 | Match |
| T3 | T2 | Phase 2 precedes Phase 3 | Match |
| T4 | T3 | `T3 → T4` | Match |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Workflow configuration | integration | IT-001–IT-004 | OK |
| T2 | Parallel planner | unit + integration | UT-001–UT-007, IT-005 | OK |
| T3 | Agent workflow contract | contract | IT-006 | OK |
| T4 | Specs and decisions | structural | structural validators | OK |
