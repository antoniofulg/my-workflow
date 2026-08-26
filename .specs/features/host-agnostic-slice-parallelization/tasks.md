# Host-Agnostic Slice Parallelization Tasks

## Execution Protocol

Implement with `tlc-spec-driven`. Tasks remain sequential inside each slice. Each code-changing slice
closes with a fresh Technical Verifier; deep-review uses the frozen grouped cadence; final QA remains
feature-level.

**Design:** `.specs/features/host-agnostic-slice-parallelization/design.md`
**Status:** Approved

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `SECURITY.md`, and existing executor/adapter tests.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Adapter selection and CLI | unit + integration | Every selection, disabled, fallback, and preflight case | `tools/test_parallel_executor.py` | `python3 tools/test_parallel_executor.py` |
| Orca compatibility | integration with CLI double | Status, known-bad, canary, cache, cleanup, redaction | `tools/test_orca_adapter.py` | `python3 tools/test_orca_adapter.py` |
| Maestri compatibility | integration with CLI double | Environment and capability failures with zero mutations | `tools/test_maestri_adapter.py` | `python3 tools/test_maestri_adapter.py` |
| Agent workflow contract | contract | No TLC/review/QA regression; adapter policy installed | `tools/shared/tests/autonomous-parallelization.test.ts` | `npm_config_offline=true npm test` |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | One adapter or registry task | Owning Python test file, spec/tasks validators, `git diff --check` |
| Full | Integration/docs close | `npm_config_offline=true npm run test:all`; spec/tasks/state validators; `git diff --check` |
| Build | Planning-only mutation | Spec/tasks validators and `git diff --check` |

## Execution Plan

### Slice A: Compatibility boundary

```text
T1
```

### Slice B: Orca proof

```text
T2
```

### Slice C: Maestri proof

```text
T3
```

### Slice D: Adoption contract

```text
T4
```

## Task Breakdown

### T1: Add compatibility-aware adapter selection

**Status:** complete
**Slice:** A
**Resources:** none
**Observable behaviour:** `preflight` reports exact host compatibility, disabled remains effect-free, and incompatible start/resume serialize without cross-host fallback.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** None
**Requirement:** HST-01–HST-04, SEC-001, SEC-002
**Reuses:** Existing CLI, serial result, runtime-state path, and atomic JSON helpers.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; no new dependency.
**Done when:**

- [ ] CLI accepts `preflight` and `auto|orca|maestri` with one JSON result.
- [ ] Disabled mode imports or probes no adapter.
- [ ] Auto detects Maestri without falling through to Orca.
- [ ] Start/resume require a compatible adapter result and preserve existing scheduler behavior.
- [ ] `python3 tools/test_parallel_executor.py` passes with zero failures.

**Tests:** UT-001, UT-002, IT-003, SEC-001 in `tools/test_parallel_executor.py`
**Gate:** Quick. Commit `feat(workflow): gate parallel host adapters`.

### T2: Prove Orca compatibility with a lifecycle canary

**Status:** complete
**Slice:** B
**Resources:** none
**Observable behaviour:** Known-bad Orca stops read-only; a candidate runtime becomes compatible only after correlated completion and zero-residue cleanup, with PASS cached by identity.
**Where:** `.agents/skills/autonomous/scripts/orca_adapter.py`
**Depends on:** T1
**Requirement:** ORC-01–ORC-07, SEC-003, SEC-005–SEC-007
**Reuses:** Existing Orca JSON calls, worker receipt validation, release logic, redaction, Git worktree helpers.
**Tools:** Skills `ponytail`, `orca-cli`; current CLI help/source is authoritative.
**Done when:**

- [ ] `1.4.188` returns unsupported without mutation.
- [ ] Candidate canary proves worker_done, read, ack, release, worktree removal, and absence.
- [ ] Any failed stage records no PASS and reports exact retained IDs.
- [ ] Matching cache avoids a second canary; changed identity invalidates it.
- [ ] `python3 tools/test_orca_adapter.py` passes with zero failures.

**Tests:** UT-003, UT-004, IT-001, IT-002, SEC-002, SEC-003, SEC-005 in `tools/test_orca_adapter.py`
**Gate:** Quick. Commit `feat(workflow): verify Orca adapter compatibility`.

### T3: Add the fail-closed Maestri capability adapter

**Status:** pending
**Slice:** C
**Resources:** none
**Observable behaviour:** Current Maestri reports its missing machine lifecycle and cleanup capabilities without creating floors, agents, or Git worktrees.
**Where:** `.agents/skills/autonomous/scripts/maestri_adapter.py`
**Depends on:** T1
**Requirement:** MAE-01–MAE-04, SEC-003–SEC-005, SEC-007
**Reuses:** Fixed-argv runner and adapter compatibility result shape.
**Tools:** Skills `ponytail`, `maestri`, `maestri-manager`, `maestri-workspace`.
**Done when:**

- [ ] Missing terminal/socket/CLI identity reports exact unsupported reason.
- [ ] Documented current CLI reports missing structured lifecycle and floor deletion.
- [ ] Probe runs no mutating command and never parses human output as a receipt.
- [ ] `python3 tools/test_maestri_adapter.py` passes with zero failures.

**Tests:** UT-005, IT-004, SEC-004 in `tools/test_maestri_adapter.py`
**Gate:** Quick. Commit `feat(workflow): probe Maestri adapter capabilities`.

### T4: Publish the multi-host execution contract

**Status:** pending
**Slice:** D
**Resources:** none
**Observable behaviour:** Adopted workflows explain adapter selection, Orca update verification, Maestri limitations, cleanup, and unchanged TLC stages from one canonical contract.
**Where:** `.agents/skills/autonomous/references/parallelization.md`
**Depends on:** T2, T3
**Requirement:** HST-04, ORC-01–ORC-07, MAE-01–MAE-04
**Reuses:** Existing autonomous parallelization and adoption tests.
**Tools:** Skills `ponytail`, `writing-for-agents`; no documentation lookup.
**Done when:**

- [ ] Canonical contract names preflight/canary, cache invalidation, and serial reasons once.
- [ ] Adoption installs the Maestri adapter and tests its presence.
- [ ] Full test gate passes with zero failures.

**Tests:** IT-003, IT-004 in `tools/shared/tests/autonomous-parallelization.test.ts` and adoption suites
**Gate:** Full. Commit `docs(workflow): publish host adapter contract`.

## Phase Execution Map

```text
Slice A: T1
Slice B: T1 -> T2
Slice C: T1 -> T3
Slice D: T2 -> T4
         T3 -> T4
```

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | One executor selection boundary | PASS |
| T2 | One Orca compatibility capability | PASS |
| T3 | One Maestri compatibility capability | PASS |
| T4 | One canonical adoption contract | PASS |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | None | PASS |
| T2 | T1 | T1 -> T2 | PASS |
| T3 | T1 | T1 -> T3 | PASS |
| T4 | T2, T3 | T2 + T3 -> T4 | PASS |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Adapter selection/CLI | unit + integration | UT/IT in executor suite | PASS |
| T2 | Orca compatibility | integration double | UT/IT in Orca suite | PASS |
| T3 | Maestri compatibility | integration double | UT/IT in Maestri suite | PASS |
| T4 | Agent workflow contract | contract | shared/adoption suites | PASS |
