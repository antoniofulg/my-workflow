# Host-Agnostic Slice Parallelization Specification

## Problem Statement

The repository already has a provider-neutral slice scheduler and an Orca execution adapter, but
adapter selection treats Orca capability presence as sufficient. The installed Orca can advertise
that capability while still reproducing a worker lifecycle defect, and Maestri cannot yet provide
machine-verifiable lifecycle and cleanup receipts. The workflow needs an explicit compatibility
gate that preserves serial fallback and exposes both hosts honestly.

## Goals

- [ ] Select a host adapter without changing TLC task, review, gate, or QA semantics.
- [ ] Prove an installed Orca runtime through version-aware lifecycle canary evidence.
- [ ] Represent Maestri explicitly and reject unsafe automation without side effects.
- [ ] Keep successful compatibility evidence local, bounded, restart-safe, and version-sensitive.
- [ ] Permit explicitly authorized coordinator-assisted Orca execution without enabling an incompatible automatic adapter.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Rewriting the deterministic scheduler | The scheduler, DAG, checkpoint sync, and serial fallback already exist. |
| Parsing human-readable Maestri output | Text is not a stable lifecycle contract. |
| Manual Git worktrees inside Maestri floors | Floors own isolation in Maestri. |
| UI automation for Maestri floor deletion | It would couple the workflow to one desktop UI and remain non-deterministic. |
| Bypassing the Orca lifecycle defect inside the automatic adapter | The adapter must prove the installed runtime; assisted execution is a separate, explicitly authorized coordinator path. |
| Parallel tasks inside one slice | TLC remains unchanged. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Adapter selection | `auto`, `orca`, or `maestri` at the executor boundary | The host is runtime state, not a delegated model/provider route. | yes |
| Automatic selection | Prefer the current host only; never cross-fallback from Maestri to Orca | Crossing hosts can attach effects to the wrong workspace. | yes |
| Orca compatibility | Known-bad versions stop before mutation; candidate versions require explicit canary PASS | Version or capability alone does not prove the bug is fixed. | yes |
| Canary cadence | Cache PASS by runtime identity and invalidate when identity changes | Avoid repeated workers and worktree pollution. | yes |
| Maestri compatibility | Require structured lifecycle receipts and machine cleanup | Reliability and zero-residue are mandatory. | yes |
| Unsupported host | Return serial fallback with a decisive reason and zero host effects | Parallelism is optional. | yes |
| Assisted Orca fallback | Explicit human authorization; coordinator owns direct worktrees, terminals, checkpoints, follow-up, and cleanup | Captures useful overlap without claiming machine-verifiable orchestration. | yes |

**Open questions:** none.

## User Stories

### P1: Select only a proven execution host

**User Story:** As a workflow operator, I want deterministic adapter selection so that the same
feature never silently changes execution hosts or loses serial safety.

**Acceptance Criteria:**

1. **HST-01:** WHEN `start` or `resume` runs with parallelization mode `disabled` THEN the executor SHALL return serial fallback without probing or constructing any host adapter. An explicitly requested `preflight` remains a read-only diagnostic in this mode. The executor SHALL accept only the current `workflow.json` schema version `2` and SHALL reject obsolete version `1` snapshots.
2. **HST-02:** WHEN `--adapter auto` runs inside a Maestri terminal THEN the executor SHALL evaluate only Maestri and SHALL NOT fall through to Orca.
3. **HST-03:** WHEN an explicit adapter is unavailable or incompatible THEN the executor SHALL return serial fallback with its backend and decisive reason before creating a checkout or worker.
4. **HST-04:** WHEN a compatible adapter is selected THEN the executor SHALL preserve the existing slice scheduler, checkpoint, Technical Verifier, deep-review, gate, and QA contracts unchanged.

**Independent Test:** Drive disabled `start`/`resume`, disabled `preflight`, auto, explicit, compatible,
and incompatible selections through recording adapters and assert exact effects and fallback reasons.

### P1: Prove the installed Orca lifecycle

**User Story:** As an Orca user, I want a version-sensitive compatibility canary so that an advertised
capability cannot enable a broken worker lifecycle.

**Acceptance Criteria:**

1. **ORC-01:** WHEN Orca status is inspected THEN the adapter SHALL require a ready reachable runtime, `orchestration.contract.v1`, and a non-empty `appVersion`.
2. **ORC-02:** IF the installed Orca version is known incompatible THEN the adapter SHALL report `unsupported` without creating a Run, Task, worker, or worktree.
3. **ORC-03:** WHEN the operator requests a canary for a candidate version THEN the adapter SHALL create one disposable checkout and one supervised worker that reaches a correlated `worker_done` result.
4. **ORC-04:** BEFORE the canary reports PASS THEN the adapter SHALL read the worker result, acknowledge its delivery, release the owned terminal, remove the disposable checkout, and prove zero live worker or worktree residue.
5. **ORC-05:** IF any canary stage fails or cleanup is unproven THEN the adapter SHALL record no compatible receipt and SHALL report the exact failed stage and retained resource identifiers.
6. **ORC-06:** WHEN a prior PASS receipt matches the current Orca app version, runtime capability set, executable identity, and repository THEN normal start SHALL reuse it without creating another canary.
7. **ORC-07:** WHEN any compatibility identity field changes THEN the adapter SHALL invalidate the cached PASS and require a new explicit canary.

**Independent Test:** Use a recording Orca CLI double for known-bad, successful, failed, stale-cache,
and cleanup-failure paths; then run the read-only preflight against the installed Orca.

### P1: Expose Maestri without unsafe automation

**User Story:** As a Maestri user, I want an explicit adapter preflight so that the scheduler never
mistakes a visually available floor for a machine-verifiable lifecycle.

**Acceptance Criteria:**

1. **MAE-01:** WHEN Maestri is evaluated THEN the adapter SHALL require the current terminal identity, daemon socket, CLI path, structured floor/agent lifecycle receipts, and machine floor cleanup. Until host-owned execution is implemented, no capability claim SHALL return `compatible`.
2. **MAE-02:** IF any required Maestri capability is absent THEN the adapter SHALL report `unsupported` with the missing capabilities and SHALL NOT create a floor, recruit an agent, or invoke Git worktree commands.
3. **MAE-03:** WHILE Maestri lacks a tracked host-owned execution implementation, safe and full execution SHALL remain serial even when `floor create`, `recruit`, `ask`, `check`, and `dismiss` are otherwise available. Capability claims alone SHALL never authorize generic Git-worktree execution.
4. **MAE-04:** The Maestri adapter SHALL NOT parse human-readable output as an ownership, completion, or cleanup receipt.

**Independent Test:** Evaluate absent environment and documented current capabilities, including a
complete-looking capability manifest, through a recording CLI without any mutating command.

### P1: Coordinate assisted Orca slices while automation is unavailable

**User Story:** As a workflow operator, I want the main agent to supervise directly launched Orca
workers so that eligible slices overlap now without weakening any TLC or readiness stage.

**Acceptance Criteria:**

1. **AST-01:** IF the automatic Orca adapter is incompatible AND the human explicitly authorizes assisted execution THEN the coordinator MAY use Orca's direct worktree plus startup-shell promotion and explicit frozen provider/model/effort command after proving one new, uniquely owned, unused startup handle with no agent/default-task activity; it SHALL send the command once and use a bounded machine-only exact-handle probe (`interval_ms=250`, `timeout_ms=60000`) to verify two consecutive connected `source=screen` reads matching that frozen route before sending the task prompt, while the automatic executor remains serial and records no compatibility PASS. This TUI materialization probe is not the event-driven dependency waiter and performs no model turns or task-state polling.
2. **AST-02:** WHEN a declared slice-start dependency reaches its required completed and verified state THEN the coordinator SHALL start at most one worker for that slice, and that worker SHALL execute only sequential tasks through the first unmet dependency.
3. **AST-03:** WHEN the next task depends on an unavailable upstream task THEN the worker SHALL leave a clean committed checkpoint, report its slice, completed-through task, next task, exact dependency, and current HEAD in the Orca worktree comment, then end its turn without polling.
4. **AST-04:** WHEN the declared upstream dependency completes THEN the coordinator SHALL synchronize the exact producer commit into the private dependent worktree, rerun the affected gate, and follow up the same startup worker handle. A stale handle SHALL be refreshed only as that exact handle from the owned worktree; a different terminal SHALL serialize instead of starting another worker. Before every logical packet the coordinator SHALL record the exact handle, unique turn ID/phase, pre-head, task/comment/gate state, exact expected task IDs, expected task-commit count, allowed changed paths including the task-status path, and expected `TURN_DONE <phase> head=<40-hex-sha>` marker, write the complete packet body including that marker to a coordinator-owned packet file outside every slice worktree, issue exactly one send carrying only a short fixed-shape pointer to that file, and never retry or replace the worker after any receipt outcome. A success SHALL use the normal 300-second worker-turn barrier; an error, missing receipt, or `agent_prompt_stalled` SHALL enter only same-handle machine-only effect reconciliation at 250 ms intervals for at most 300000 ms, accepting exactly one complete effect only when the connected handle, unique marker SHA, two fresh non-Working source=screen frames plus tui-idle, Git HEAD, required statuses, atomic commits, gates, exact pre-head ancestry, expected commit count/identities, and packet-declared changed-path allowlist all agree. Only phase `B_PARKED` SHALL require the exact parked-B comment; route, A, and other nonparked phases SHALL not require that comment. Reset, foreign/unrelated/extra commits, out-of-scope paths, or status mismatch SHALL serialize the lane.
5. **AST-05:** IF the checkpoint is dirty, missing, conflicting, fails its affected gate, or cannot be reconciled unambiguously THEN the coordinator SHALL stop that lane and continue through serial recovery without automatic conflict resolution.
6. **AST-06:** WHEN verified slice commits are integrated in deterministic slice order THEN the coordinator SHALL stop the exact startup worker handle, revalidate ownership and integration, detach the worktree if needed, safely delete only its exact owned branch and prove ref absence before removing the clean integrated worktree, then prove zero owned worktree, branch-ref, and terminal residue.
7. **AST-07:** Assisted overlap SHALL preserve one atomic commit and scoped gate per task, Technical Verifier per code-changing slice, frozen grouped deep-review cadence, final QA, and one full gate on the final tree.

**Independent Test:** Run a disposable two-slice Orca pilot where slice B starts after an early slice
A dependency, parks at a later dependency, resumes through the same terminal after exact checkpoint
sync, and leaves zero owned worktree or terminal residue.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Executor CLI and local compatibility state | Strict schema, atomic local receipt, disabled short-circuit | SEC-001, SEC-002 |
| S6 | Executable, Git, and filesystem sinks | Fixed argv, validated checkout path, no shell | SEC-003, SEC-008 |
| S9 | Orca and Maestri runtimes | Correlated machine receipts; no text parsing | SEC-004, SEC-005 |
| S11 | Workers, worktrees, floors, terminals | Cleanup proof before compatibility PASS; exact coordinator ownership for assisted cleanup | SEC-006–SEC-008 |

## Implicit Requirement Dimensions

| Dimension | Resolution |
| --- | --- |
| Input validation & bounds | Adapter names, versions, paths, capabilities, IDs, timeouts, and receipts are validated. |
| Failure / partial-failure states | Every incomplete canary or cleanup result remains incompatible and names retained ownership. |
| Idempotency / retry | PASS receipts are identity-bound; repeated checks are read-only until identity changes. |
| Auth boundaries & rate limits | Adapters inherit local operator authority and grant no new remote authority. |
| Concurrency / ordering | Existing scheduler and sequential task order remain authoritative. |
| Data lifecycle / expiry | Local receipts expire on runtime identity change and contain no transcript or secret. |
| Observability | Preflight emits backend, version, capabilities, cache state, failed stage, and cleanup result. |
| External-dependency failure | Missing CLI/socket/runtime/capability returns serial fallback. |
| State-transition integrity | Automatic: `unknown -> candidate -> compatible|unsupported`; assisted: `ready -> running -> parked -> resumed -> integrated -> cleaned`, with ambiguity returning to serial. |

## Edge Cases

- IF `MAESTRI_SOCKET` is present but the CLI path is absent or not executable THEN selection SHALL stop at Maestri and return serial fallback.
- IF Orca reports a new version with the old capability set THEN the version SHALL remain a candidate until the canary passes.
- IF the canary worker completes but release or checkout removal fails THEN the runtime SHALL remain unsupported.
- IF a cached receipt belongs to another repository or executable THEN it SHALL be ignored.
- IF a host response contains credential-shaped fields THEN persisted and emitted diagnostics SHALL redact their values.
- IF an assisted worker terminal handle becomes stale THEN the coordinator SHALL reacquire the sole handle from the owned worktree and SHALL NOT dual-send or launch a replacement worker.
- IF an assisted worktree contains unintegrated or dirty changes THEN cleanup SHALL stop and report the exact retained path.
- IF the rendered terminal screen is unavailable, omits the provider, mismatches the frozen provider/model/effort tuple, or is ambiguous THEN assisted execution SHALL serialize before prompt or task edits (AST-01).
- IF the route appears in fewer than two consecutive connected `source=screen` reads, the bounded materialization timeout expires, or the exact handle disconnects THEN assisted execution SHALL serialize before prompt or task edits (AST-01).
- IF a route probe uses a pre-send `tui-idle` result, static screen reads instead of a repeated loop, an unbounded interval, a model turn, or dependency polling THEN it SHALL be rejected as insufficient route proof (AST-01, AST-03).
- IF a worktree create returns no receipt or times out THEN the coordinator SHALL never retry or issue a second create; it SHALL re-list exact worktree and terminal inventories every 250 ms for at most 60000 ms, compute the cumulative difference from `before_inventory`, perform a final inventory/audit at the deadline, and adopt exactly one candidate only after complete immutable receipt and ownership proof, otherwise serializing and exact-cleaning every provably owned late effect (AST-01, SEC-008).
- IF the startup terminal is not a new unused shell, has default/agent activity, or more than one owned handle exists THEN assisted execution SHALL serialize before `exec`, prompt, or task edits (AST-01).
- IF the exact startup handle cannot be kept continuously identified THEN assisted execution SHALL serialize and SHALL NOT create a second terminal (AST-04).
- IF a logical packet returns success, an error, no receipt, or `agent_prompt_stalled` THEN the coordinator SHALL issue no second send or replacement worker; the single send SHALL carry only the short fixed-shape pointer to the coordinator-owned packet file, so a truncated send SHALL fail closed on the absent unique marker instead of half-executing; error/no-receipt/stalled outcomes SHALL reconcile only the same exact handle with machine-only probes every 250 ms for at most 300000 ms and no model turns (AST-04).
- IF the bounded effect reconciliation does not prove exactly one expected turn end-to-end with one unique phase marker SHA, two fresh non-Working source=screen frames plus tui-idle, matching HEAD, statuses, atomic commits, gates, exact pre-head ancestry, expected task commit count/identities, and packet-declared changed-path allowlist THEN the lane SHALL serialize and retain exact recovery; a commit alone SHALL never be accepted as success or used to clean/adopt an effect (AST-04, SEC-008).
- IF the immutable ownership receipt mismatches Orca or Git, the current branch tip does not equal `current_head`, or the slice head is not integrated THEN cleanup SHALL stop before deletion (AST-06, SEC-008).
- IF the exact owned branch cannot be safely deleted or its ref absence cannot be proven before worktree removal THEN cleanup SHALL stop and retain the exact path for serial recovery; if removal already succeeded, cleanup SHALL retain the receipt and identifiers without claiming that the removed path remains (AST-06, SEC-008).

## Security Requirements

1. **SEC-001:** Disabled mode performs no adapter probe or mutation.
2. **SEC-002:** Compatibility receipts are atomic, repository-scoped local state outside `.specs/`.
3. **SEC-003:** Every host and Git command uses fixed argv, `shell=False`, bounded timeout, and validated paths.
4. **SEC-004:** Host responses are accepted only as structured machine-readable objects correlated to the current request.
5. **SEC-005:** Credential-shaped response fields are redacted before diagnostics or persistence.
6. **SEC-006:** A compatibility PASS requires a settled worker and zero disposable checkout residue.
7. **SEC-007:** The adapter never removes or dismisses a resource without an exact ownership receipt.
8. **SEC-008:** Assisted cleanup targets only coordinator-owned worktrees whose commits are integrated and whose Git state is clean; missing ownership or residue proof stops deletion.

## Requirement Traceability

| Requirement ID | Design component | Planned slice | Status |
| --- | --- | --- | --- |
| HST-01 | Adapter registry and executor boundary | A | ✅ Verified |
| HST-02 | Adapter registry and executor boundary | A | ✅ Verified |
| HST-03 | Adapter registry and executor boundary | A | ✅ Verified |
| HST-04 | Adapter registry and executor boundary | A | ✅ Verified |
| ORC-01 | Orca compatibility probe and canary | B | ✅ Verified |
| ORC-02 | Orca compatibility probe and canary | B | ✅ Verified |
| ORC-03 | Orca compatibility probe and canary | B | ✅ Verified |
| ORC-04 | Orca compatibility probe and canary | B | ✅ Verified |
| ORC-05 | Orca compatibility probe and canary | B | ✅ Verified |
| ORC-06 | Orca compatibility probe and canary | B | ✅ Verified |
| ORC-07 | Orca compatibility probe and canary | B | ✅ Verified |
| MAE-01 | Maestri capability probe | C | ✅ Verified |
| MAE-02 | Maestri capability probe | C | ✅ Verified |
| MAE-03 | Maestri capability probe | C | ✅ Verified |
| MAE-04 | Maestri capability probe | C | ✅ Verified |
| AST-01 | Coordinator-assisted Orca contract | D | ✅ Contract and two-worker route proof verified |
| AST-02 | Coordinator-assisted Orca contract | D | ✅ Contract; early start/park verified |
| AST-03 | Coordinator-assisted Orca contract | D | ✅ Contract; clean exact B checkpoint verified |
| AST-04 | Coordinator-assisted Orca contract | D | ✅ Contract; exact producer sync, affected gate, and same-handle continuation verified |
| AST-05 | Coordinator-assisted Orca contract | D | ✅ Contract verified; E2E pending |
| AST-06 | Coordinator-assisted Orca contract | D | ✅ Contract verified; E2E pending |
| AST-07 | Coordinator-assisted Orca contract | D | ❌ Tasks, Verifiers, and integration passed; grouped review found one Major before final QA |
| SEC-001 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-002 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-003 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-004 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-005 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-006 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-007 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-008 | Assisted coordinator ownership and cleanup | D | ✅ Contract and full exact Retest 8 cleanup verified |

**Coverage:** 30 total requirements, 30 mapped, 0 unmapped.

**Post-validation cleanup recheck (`3487c27`):** ORC-04, ORC-05, and SEC-006 remain verified.
Test-only teardown now removes its exact registered fixture worktree and sentinel root; the owning
suite preserves unowned paths through its assertions, and production cleanup remains unchanged.

## Success Criteria

- [ ] Current Orca `1.4.188` reports unsupported with zero mutations.
- [ ] A recording candidate Orca build passes only after full lifecycle and cleanup proof.
- [ ] Current Maestri reports the exact missing machine capabilities with zero mutations.
- [ ] Disabled mode and incompatible adapters create no workers, worktrees, floors, or agents.
- [ ] Existing scheduler, Orca adapter, Git adapter, and full workflow gates remain green.
- [ ] An explicitly authorized two-slice Orca pilot parks and resumes the same worker at a later dependency, then leaves zero owned residue.
