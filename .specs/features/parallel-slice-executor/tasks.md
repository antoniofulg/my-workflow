# Parallel Slice Executor Tasks

## Execution Protocol

Implement these tasks with `tlc-spec-driven`. Keep tasks sequential inside each slice, update this
file before every atomic commit, and close every code-changing slice with a fresh Technical Verifier.
The feature's frozen mode is authoritative; absent a capable executor, use the existing serial path.

**Design:** `.specs/features/parallel-slice-executor/design.md`
**Status:** Approved

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `SECURITY.md`, existing Python workflow tests, and the approved spec.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Executor state/coordinator | unit + integration | Every transition, restart, idempotency, fallback, resource, and CLI case in `tests.md` | `tools/test_parallel_executor.py` | `python3 tools/test_parallel_executor.py` |
| Orca adapter | integration with CLI double | Every worktree/worker/event/follow-up/release receipt and failure case | `tools/test_orca_adapter.py` | `python3 tools/test_orca_adapter.py` |
| Git adapter | integration in disposable repositories | Exact checkpoint, ancestor no-op, conflict abort, evidence invalidation, and integration order | `tools/test_git_adapter.py` | `python3 tools/test_git_adapter.py` |
| Workflow config/planner | unit + integration | Provider path validation plus exact/missing/ambiguous resource metadata | `tools/test_workflow_config.py`, `tools/test_parallel_plan.py` | `python3 tools/test_workflow_config.py && python3 tools/test_parallel_plan.py` |
| Agent workflow contract | contract + real QA | Existing stages, executable seam, fail-closed fallback, and real Orca two-worktree pilot | `tools/shared/tests/*.test.ts`, `docs/qa/**` | `npm_config_offline=true npm test` plus declared QA adapter |
| Specs and decisions | structural | Strict spec/tasks/state/index validation and clean diff | `.specs/**` | Validator commands below |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Executor, Orca, Git, config, or planner task | Owning Python test file(s), `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/parallel-slice-executor/tasks.md`, and `git diff --check` |
| Full | Autonomous integration or feature close | `npm_config_offline=true npm test`; every `tools/test_*.py`; all TLC/state/index validators; `git diff --check` |
| Build | Planning/decision-only mutation | Strict spec/tasks/state/index validators and `git diff --check` |

## Execution Plan

Tasks are sequential inside each slice. Cross-slice edges are the only potential inter-slice
dispatch points; this feature itself follows its frozen mode and therefore does not bootstrap from
an executor it has not yet completed.

### Slice A: Resume-safe coordinator

```text
T1 -> T2
```

### Slice B: Orca worker lifecycle

```text
T2 -> T3
```

### Slice C: Checkpoint reconciliation

```text
T2 -> T4
```

### Slice D: Safe workflow adoption

```text
T2 -> T5 -> T6
T3 + T4 + T6 -> T7
```

## Task Breakdown

### T1: Define executor state and safe effect primitives

**Status:** complete
**Slice:** A
**Resources:** none
**Observable behaviour:** Runtime state accepts only declared transitions, persists atomically outside versioned specs, rejects foreign state, and executes validated argv/path effects without shell expansion.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** None
**Requirement:** EXE-01, EXE-02, EXE-05, SEC-001, SEC-002, SEC-003, SEC-004
**Reuses:** `parallel_plan.py`, Git repository identity, standard library dataclasses/json/pathlib/subprocess.
**Tools:** Skill `ponytail`; no documentation lookup.
**Done when:**

- [ ] State schema and legal transitions reject malformed, foreign, duplicate, and out-of-order input before effects.
- [ ] Atomic local-state replacement survives an injected pre-rename failure and stays outside tracked files.
- [ ] Safe subprocess and bounded-path helpers use fixed argv, `shell=False`, timeout, and symlink checks.
- [ ] `python3 tools/test_parallel_executor.py` reports every assigned case passing with zero failures.

**Tests:** UT-001, UT-003, SEC-001–SEC-004 in `tools/test_parallel_executor.py`
**Gate:** Quick. Commit `feat(workflow): define parallel executor state`.

### T2: Drive idempotent lanes and resource leases

**Status:** pending
**Slice:** A
**Resources:** none
**Observable behaviour:** `start`, `resume`, and `status` reconcile one effect per idempotency key, acquire/release declared resources, and emit serial fallback without constructing adapters when capability is absent.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** T1
**Requirement:** EXE-03, EXE-04, EXE-18–EXE-22, SEC-007, SEC-008
**Reuses:** T1 state/effect primitives and frozen planner JSON.
**Tools:** Skill `ponytail`; no documentation lookup.
**Done when:**

- [ ] Restart reconciliation cannot duplicate a worktree, worker, follow-up, acquire, or release action.
- [ ] `Resources: none` bypasses acquisition; resource-bearing lanes require one correlated prepared lease.
- [ ] Provider timeout, malformed output, live-lease reuse, foreign cleanup, and repeated owned cleanup follow the spec.
- [ ] CLI stdout is one JSON object; failures use stderr/non-zero; read-only status produces no effects.
- [ ] `python3 tools/test_parallel_executor.py` reports all executor cases passing with zero failures.

**Tests:** UT-002, UT-007, UT-008, IT-001, SEC-007, SEC-008 in `tools/test_parallel_executor.py`
**Gate:** Quick. Commit `feat(workflow): drive parallel executor lanes`.

### T3: Adapt the Orca worker lifecycle

**Status:** pending
**Slice:** B
**Resources:** none
**Observable behaviour:** The Orca adapter creates a child worktree before its worker, validates every receipt, blocks on correlated events, follows up the same terminal, and releases only accepted owned workers.
**Where:** `.agents/skills/autonomous/scripts/orca_adapter.py`
**Depends on:** T2
**Requirement:** EXE-06–EXE-11, SEC-005, SEC-006
**Reuses:** T1 subprocess/path primitives and Orca `orchestration.contract.v1` commands.
**Tools:** Skills `ponytail` and `orca-cli`; live Orca guide is authoritative.
**Done when:**

- [ ] Recording-CLI assertions prove worktree creation precedes resource preparation and worker start.
- [ ] Run/task/dispatch/terminal/worktree/head/idempotency fields are all correlated before state changes.
- [ ] `worker_done`, clean waiter, dependency follow-up, timeout, escalation, failure, mismatch, and duplicate receipts have exact outcomes.
- [ ] Logs/state expose no worker transcript body or environment value.
- [ ] `python3 tools/test_orca_adapter.py` reports all assigned cases passing with zero failures.

**Tests:** IT-002–IT-004, SEC-005, SEC-006 in `tools/test_orca_adapter.py`
**Gate:** Quick. Commit `feat(workflow): adapt orca slice workers`.

### T4: Reconcile Git checkpoints and verified slices

**Status:** pending
**Slice:** C
**Resources:** none
**Observable behaviour:** A clean dependent lane rebases onto one exact producer checkpoint, restores itself on conflict, invalidates changed-head evidence, and merges verified slices deterministically without rewriting their commits.
**Where:** `.agents/skills/autonomous/scripts/git_adapter.py`
**Depends on:** T2
**Requirement:** EXE-12–EXE-17
**Reuses:** T1 subprocess/path primitives and existing branching/evidence rules.
**Tools:** Skill `ponytail`; Git CLI only.
**Done when:**

- [ ] Exact-commit sync and ancestor no-op receipts include pre/post HEAD and changed paths.
- [ ] Rebase/merge conflicts abort and restore the original clean state; no side is auto-selected.
- [ ] Incomparable multiple checkpoints return serial recovery.
- [ ] Changed HEAD invalidates affected gate, Technical Verifier, and deep-review receipts.
- [ ] Verified slice commits survive deterministic feature-branch integration.
- [ ] `python3 tools/test_git_adapter.py` reports all assigned cases passing with zero failures.

**Tests:** UT-004–UT-006 in `tools/test_git_adapter.py`
**Gate:** Quick. Commit `feat(workflow): reconcile slice checkpoints`.

### T5: Freeze the consumer resource provider

**Status:** pending
**Slice:** D
**Resources:** none
**Observable behaviour:** Workflow resolution freezes an optional safe repository-relative provider executable and preserves an existing valid snapshot when provider validation fails.
**Where:** `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on:** T2
**Requirement:** EXE-19–EXE-22, SEC-003, SEC-004
**Reuses:** Existing strict TOML parser, atomic snapshot replacement, and resume semantics.
**Tools:** Skill `ponytail`; no documentation lookup.
**Done when:**

- [ ] Absent provider freezes as null without changing disabled/default behavior.
- [ ] Valid executable freezes as a normalized repository-relative path.
- [ ] Absolute, external, directory, non-executable, and unsafe-symlink paths fail before snapshot replacement.
- [ ] `python3 tools/test_workflow_config.py` reports all existing and IT-005 cases passing with zero failures.

**Tests:** IT-005 in `tools/test_workflow_config.py`
**Gate:** Quick. Commit `feat(config): freeze parallel resource provider`.

### T6: Plan explicit lane resources

**Status:** pending
**Slice:** D
**Resources:** none
**Observable behaviour:** The deterministic plan carries normalized resource names, permits explicit `none`, and serializes missing or ambiguous resource metadata before the executor can act.
**Where:** `.agents/skills/workflow-config/scripts/parallel_plan.py`
**Depends on:** T5
**Requirement:** EXE-18–EXE-21
**Reuses:** Existing task parser, fallback reasons, and byte-deterministic JSON projection.
**Tools:** Skill `ponytail`; no documentation lookup.
**Done when:**

- [ ] Each lane contains a stable `resources` array; `none` becomes an empty array.
- [ ] Missing, mixed-`none`, duplicated, or malformed resource names produce exact serial reasons.
- [ ] Existing mode, dependency, waiting, and conflict behavior remains green.
- [ ] `python3 tools/test_parallel_plan.py` reports all existing and IT-006 cases passing with zero failures.

**Tests:** IT-006 in `tools/test_parallel_plan.py`
**Gate:** Quick. Commit `feat(workflow): plan isolated lane resources`.

### T7: Bind autonomous execution and prove Orca concurrency

**Status:** pending
**Slice:** D
**Resources:** none
**Observable behaviour:** Autonomous invokes the deterministic executor when its frozen mode and capabilities allow, otherwise runs serially; a real disposable Orca run proves two isolated worktrees active concurrently and cleans only owned workers.
**Where:** `.agents/skills/autonomous/references/parallelization.md`
**Depends on:** T3, T4, T6
**Requirement:** EXE-01–EXE-22
**Reuses:** Existing autonomous entry gate, review stages, executor CLI, and Orca QA adapter.
**Tools:** Skills `ponytail`, `writing-skills`, `orca-cli`, `qa-plan`, and `qa-execute` as their stages fire.
**Done when:**

- [ ] Policy names the exact executor commands, capability gate, event lifecycle, checkpoint/merge split, evidence invalidation, resource provider, and serial recovery.
- [ ] Shared contract tests prove TLC tasks, gates, Verifier, grouped deep-review, final QA, and full gate are unchanged.
- [ ] Writing-skills audit records every checklist item Pass.
- [ ] E2E-001 records two distinct Orca worktree/branch/dispatch/terminal receipts active in one run, correlated completion events, clean status, and owned cleanup.
- [ ] Full gate and strict feature/state/index validators pass with zero failures.

**Tests:** IT-007 in `tools/shared/tests/autonomous-parallelization.test.ts`; E2E-001 in the feature QA report
**Gate:** Full. Commit `feat(workflow): execute parallel slices autonomously`.

## Phase Execution Map

```text
T1 -> T2
T2 -> T3
T2 -> T4
T2 -> T5
T5 -> T6
T3 -> T7
T4 -> T7
T6 -> T7
```

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Root | Match |
| T2 | T1 | `T1 -> T2` | Match |
| T3 | T2 | `T2 -> T3` | Match |
| T4 | T2 | `T2 -> T4` | Match |
| T5 | T2 | `T2 -> T5` | Match |
| T6 | T5 | `T5 -> T6` | Match |
| T7 | T3, T4, T6 | `T3 + T4 + T6 -> T7` | Match |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Executor state/primitives | unit + security | UT-001, UT-003, SEC-001–SEC-004 | OK |
| T2 | Coordinator/resource protocol | unit + integration | UT-002, UT-007, UT-008, IT-001, SEC-007, SEC-008 | OK |
| T3 | Orca adapter | integration + security | IT-002–IT-004, SEC-005, SEC-006 | OK |
| T4 | Git adapter | integration | UT-004–UT-006 | OK |
| T5 | Workflow config | integration | IT-005 | OK |
| T6 | Planner | unit + integration | IT-006 plus existing planner suite | OK |
| T7 | Agent contract/real workflow | contract + e2e | IT-007, E2E-001 | OK |
