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

## Out of Scope

| Feature | Reason |
| --- | --- |
| Rewriting the deterministic scheduler | The scheduler, DAG, checkpoint sync, and serial fallback already exist. |
| Parsing human-readable Maestri output | Text is not a stable lifecycle contract. |
| Manual Git worktrees inside Maestri floors | Floors own isolation in Maestri. |
| UI automation for Maestri floor deletion | It would couple the workflow to one desktop UI and remain non-deterministic. |
| Bypassing the Orca lifecycle defect | The adapter must prove the installed runtime, not reproduce lifecycle ownership itself. |
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

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Executor CLI and local compatibility state | Strict schema, atomic local receipt, disabled short-circuit | SEC-001, SEC-002 |
| S6 | Executable, Git, and filesystem sinks | Fixed argv, validated checkout path, no shell | SEC-003 |
| S9 | Orca and Maestri runtimes | Correlated machine receipts; no text parsing | SEC-004, SEC-005 |
| S11 | Workers, worktrees, floors, terminals | Cleanup proof before compatibility PASS | SEC-006, SEC-007 |

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
| State-transition integrity | `unknown -> candidate -> compatible|unsupported`; only a clean canary reaches compatible. |

## Edge Cases

- IF `MAESTRI_SOCKET` is present but the CLI path is absent or not executable THEN selection SHALL stop at Maestri and return serial fallback.
- IF Orca reports a new version with the old capability set THEN the version SHALL remain a candidate until the canary passes.
- IF the canary worker completes but release or checkout removal fails THEN the runtime SHALL remain unsupported.
- IF a cached receipt belongs to another repository or executable THEN it SHALL be ignored.
- IF a host response contains credential-shaped fields THEN persisted and emitted diagnostics SHALL redact their values.

## Security Requirements

1. **SEC-001:** Disabled mode performs no adapter probe or mutation.
2. **SEC-002:** Compatibility receipts are atomic, repository-scoped local state outside `.specs/`.
3. **SEC-003:** Every host and Git command uses fixed argv, `shell=False`, bounded timeout, and validated paths.
4. **SEC-004:** Host responses are accepted only as structured machine-readable objects correlated to the current request.
5. **SEC-005:** Credential-shaped response fields are redacted before diagnostics or persistence.
6. **SEC-006:** A compatibility PASS requires a settled worker and zero disposable checkout residue.
7. **SEC-007:** The adapter never removes or dismisses a resource without an exact ownership receipt.

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
| SEC-001 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-002 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-003 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-004 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-005 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-006 | Boundary, probes, and cleanup | A–C | ✅ Verified |
| SEC-007 | Boundary, probes, and cleanup | A–C | ✅ Verified |

**Coverage:** 22 total requirements, 22 mapped, 0 unmapped.

**Post-validation cleanup recheck (`3487c27`):** ORC-04, ORC-05, and SEC-006 remain verified.
Test-only teardown now removes its exact registered fixture worktree and sentinel root; the owning
suite preserves unowned paths through its assertions, and production cleanup remains unchanged.

## Success Criteria

- [ ] Current Orca `1.4.188` reports unsupported with zero mutations.
- [ ] A recording candidate Orca build passes only after full lifecycle and cleanup proof.
- [ ] Current Maestri reports the exact missing machine capabilities with zero mutations.
- [ ] Disabled mode and incompatible adapters create no workers, worktrees, floors, or agents.
- [ ] Existing scheduler, Orca adapter, Git adapter, and full workflow gates remain green.
