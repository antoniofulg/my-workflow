# Hybrid Slice Execution Specification

**Status:** Approved
**Decision:** AD-015

## Problem Statement

The adopted workflow teaches vertical slices at the project level but its vendored
`tlc-spec-driven` skill still delegates sequential phase batches and repeats whole-feature context.
The existing parallel executor also lacks adaptive lane admission, coherent snapshot-version reading,
and shipped pointer-only Orca tooling. Consuming projects therefore cannot get the approved hybrid,
assisted-by-default workflow from adoption alone.

## Goals

- [ ] Install one attributed workflow-owned spec-driven skill with no obsolete TLC path.
- [ ] Materialize slice-only packets with executable byte budgets and redacted telemetry.
- [ ] Dispatch ready slices dynamically with zero or more isolated writer lanes, starting at two and
  scaling one lane at a time to four only on healthy hosts.
- [ ] Preserve exactly-once external mutations, deterministic ownership, and residue-zero cleanup
  while using pointer-only Orca delivery.
- [ ] Keep Technical Verification, Deep Review, and QA independent from implementers.
- [ ] Prove the complete adopted workflow with canonical tests, fake providers, and an adoption
  dry-run without a live Orca dependency.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Fixing or modifying Orca | The upstream Orca team owns the transport defect. |
| Live Orca execution in automated gates | The host journey remains external and `blocked-verify`. |
| Shared model memory between workers | This feature minimizes serialized context; it cannot change provider accounting. |
| Automatic admission above four lanes | Four is the approved automatic ceiling; an integer is a human-owned cap. |
| Compatibility with TLC path, config v2, or snapshot v2 | The project requires hard cuts and explicit refresh. |
| Deployment, release, or package publication | Autonomous delivery ends at repository merge. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Public skill name | `workflow-spec-driven` | The workflow owns behavior that now diverges from upstream TLC. | yes |
| Configuration and snapshot version | `3` for both public artifacts | One version removes the existing v2/v1 reader mismatch and makes the hard cut explicit. | yes |
| Automatic lane policy | Baseline 2, one-at-a-time scale, ceiling 4 | This is the approved speed/resource balance. | yes |
| Explicit integer cap | Any integer at least 1; values above 2 still require healthy admission | The user can bound or raise capacity without bypassing machine proof. | yes |
| Missing health evidence | Do not admit lane 3 or later | Unknown capacity is not proof of safety. | yes |
| Context budgets | Role packet at most 3,072 bytes; slice packet at most 10,240 bytes | These preserve the approved small role packet and context-pack targets as executable limits. | yes |
| Live host QA | `blocked-verify` with fake-Orca automation remaining mandatory | Upstream support is outside this repository and automated gates must stay deterministic. | yes |

**Open questions:** none.

## Implicit-Requirement Dimensions

| Dimension | Resolution |
| --- | --- |
| Input validation and bounds | Validate config types, lane caps, snapshot version, packet bytes, paths, provider JSON, and receipt identities before effects. |
| Failure and partial failure | Fail closed, reconcile from read-only evidence, park blocked slices, and preserve owned state for safe cleanup. |
| Idempotency, retry, duplicates | Never retry mutating Orca/Git/provider calls; reconcile the same handle and operation from bounded read-only inspections. |
| Auth boundaries and rate limits | N/A because all interfaces are checkout-local CLIs with no network ingress or user accounts. |
| Concurrency and ordering | Ready-slice DAG, path/resource compatibility, admission slots, settle windows, checkpoint sync, and sequential tasks per slice define order. |
| Data lifecycle and expiry | Packet/state files live in checkout-local feature evidence; cleanup proves stopped workers, released leases, removed owned worktrees, and zero refs. |
| Observability | Machine-only JSON reports decisions, byte counts, effects, receipts, and residue with paths, environment values, and payload bodies redacted. |
| External-dependency failure | Orca and resource-provider failures are exercised by fakes; unavailable or contradictory capability prevents unsafe dispatch or cleanup. |
| State-transition integrity | Persisted operation IDs, handles, commit IDs, lease IDs, and ownership proofs guard every lifecycle transition. |

## User Stories

### P1: Adopt a lean workflow-owned planning contract

**User Story:** As a workflow adopter, I want one slice-native spec-driven skill so agents receive
only the instructions required for their current role and slice.

**Acceptance Criteria:**

1. WHEN adoption completes THEN the workflow SHALL install `.agents/skills/workflow-spec-driven` and SHALL leave `.agents/skills/tlc-spec-driven` absent. (HSE-01)
2. The installed skill SHALL identify the adapted work, original author and source, CC BY 4.0 license, and material modifications in `NOTICE.md`. (HSE-02)
3. WHEN a slice packet is materialized THEN the workflow SHALL include only that slice's tasks, cited acceptance criteria, assigned test IDs, gate, required design excerpt, and compact memory. (HSE-03)
4. The workflow SHALL load guidelines only when their documented trigger applies and SHALL contain no phase-batch or feature-only-Verifier instruction. (HSE-04)
5. IF a role packet exceeds 3,072 bytes or a slice packet exceeds 10,240 bytes THEN the workflow SHALL report the exact byte count in redacted JSON and SHALL stop before provider dispatch. (HSE-05)
6. WHEN packet telemetry is emitted THEN the workflow SHALL report component and total byte counts without packet bodies, secrets, absolute home paths, or environment values. (HSE-06)

**Independent Test:** Adopt into a temporary project, materialize one slice packet, and run the packet
budget command to prove exact installed paths, bounded bytes, and excluded whole-feature context.

### P1: Configure one coherent assisted workflow contract

**User Story:** As a project owner, I want a small stable configuration so assisted execution is the
default and serial execution remains explicit.

**Acceptance Criteria:**

1. The workflow configuration and frozen feature snapshot SHALL both use public schema version `3`. (HSE-07)
2. The `parallelization.mode` key SHALL accept only `assisted` and `disabled`, with `assisted` as the default. (HSE-08)
3. The `parallelization.max_workers` key SHALL accept `"auto"` or an integer of at least `1`, with `"auto"` as the default. (HSE-09)
4. WHEN a version-3 snapshot is frozen THEN the workflow SHALL store the mode, configured cap, automatic baseline `2`, automatic ceiling `4`, resource-provider path, role routes, and review cadence. (HSE-10)
5. IF configuration or an active feature snapshot uses version `1` or `2` THEN the workflow SHALL reject it with an explicit refresh instruction and SHALL perform no dispatch effect. (HSE-11)
6. WHILE mode is `disabled` the workflow SHALL execute slices serially without creating a concurrent-writer worktree. (HSE-12)

**Independent Test:** Resolve valid and invalid version-3 configs into snapshots and prove old configs
and snapshots fail before planner or executor effects.

### P1: Schedule writers by readiness and host capacity

**User Story:** As a coordinator, I want ready slices assigned dynamically so parallelism shortens the
critical path without saturating the machine or isolating read-only roles.

**Acceptance Criteria:**

1. WHEN no slice is ready THEN the scheduler SHALL dispatch no writer and SHALL report the blocking dependency IDs. (HSE-13)
2. WHEN exactly one slice is ready THEN the scheduler SHALL dispatch it serially in the clean integration checkout without creating an extra worktree. (HSE-14)
3. WHEN at least two compatible slices are ready THEN the scheduler SHALL start at most two concurrent writer worktrees. (HSE-15)
4. WHILE `max_workers` is `"auto"`, WHEN a settle window completes with normalized healthy evidence THEN the scheduler SHALL admit at most one additional lane, up to four active writers. (HSE-16)
5. IF health evidence is missing, malformed, stale, or unhealthy THEN the scheduler SHALL admit no lane above two and SHALL keep already healthy work running. (HSE-17)
6. WHILE `max_workers` is an integer the scheduler SHALL never exceed that cap and SHALL still require healthy evidence for every admission above two. (HSE-18)
7. WHEN a lane becomes free THEN the scheduler SHALL assign the next ready dependency-, path-, and resource-compatible slice instead of using a fixed odd/even allocation. (HSE-19)
8. The scheduler SHALL create persistent worktrees only for concurrent implementer writers; Planner, coordinator, Explorer, and read-only review sessions SHALL use the clean integration checkout. (HSE-20)
9. WHEN a heavy gate needs an exclusive resource THEN the scheduler SHALL acquire and release it through the configured resource-provider lease protocol before running that gate. (HSE-21)

**Independent Test:** Feed a deterministic DAG, health sequence, and fake leases to the scheduler and
observe serial, two-lane, incremental four-lane, parking, reuse, and fail-closed outcomes.

### P1: Coordinate Orca safely through pointer delivery

**User Story:** As an assisted-execution coordinator, I want shipped deterministic Orca tooling so
transport defects and transient responses cannot duplicate work or destroy the wrong checkout.

**Acceptance Criteria:**

1. WHEN a worker packet is ready THEN the coordinator SHALL persist the complete packet and SHALL send Orca only a short pointer naming that packet. (HSE-22)
2. The pointer sent through `orca terminal send --text` SHALL never contain the packet body. (HSE-23)
3. WHEN a logical `create`, `send`, `set`, `stop`, `rm`, Git worktree mutation, or lease mutation begins THEN the coordinator SHALL issue that mutation at most once. (HSE-24)
4. IF a mutation response is missing or transiently fails THEN the coordinator SHALL reconcile the same operation through bounded read-only inspections and SHALL not retry the mutation. (HSE-25)
5. BEFORE accepting a worker effect THEN the coordinator SHALL prove repository identity, worktree ownership, terminal handle, route, task ID, operation ID, and expected commit checkpoint. (HSE-26)
6. IF receipts, provider observations, or Git observations are malformed, stale, reused, or contradictory THEN the coordinator SHALL fail closed and SHALL preserve evidence for cleanup. (HSE-27)
7. WHEN cleanup runs THEN the coordinator SHALL stop only the proven worker, release only correlated leases, remove only the owned clean worktree, remove its branch/ref, and report residue zero. (HSE-28)
8. WHEN `tools/orca_assisted_probe.py` is imported THEN the module SHALL perform zero Orca, Git, filesystem-mutation, or provider calls. (HSE-29)

**Independent Test:** Put fake `orca`, Git, and resource-provider executables on `PATH`, induce
transient and contradictory observations, and assert exact mutation counts, pointer contents, and
cleanup residue.

### P1: Preserve independent proof at every boundary

**User Story:** As a maintainer, I want authors and verifiers separated so faster execution never
turns into self-certification.

**Acceptance Criteria:**

1. WHILE an implementer owns a slice worktree the implementer SHALL execute that slice's tasks sequentially and SHALL finish each task with its scoped gate and atomic Conventional Commit. (HSE-30)
2. WHEN a code-changing slice reaches its checkpoint THEN a fresh Technical Verifier SHALL verify that slice before any dependent slice consumes the checkpoint. (HSE-31)
3. WHEN the frozen review group is integrated THEN a fresh Deep Reviewer SHALL review the integrated commit range rather than either writer's private tree. (HSE-32)
4. WHEN final implementation review is complete THEN fresh QA Plan and QA Execute sessions SHALL verify public configuration and adoption behavior. (HSE-33)
5. WHEN the last implementer finishes THEN it SHALL write only a compact handoff and SHALL not perform Technical Verification, Deep Review, or final QA. (HSE-34)

**Independent Test:** Materialize role packets and a multi-slice execution trace, then prove author
identity differs from verifier/reviewer/QA identities and every phase sees the intended clean tree.

### P1: Adopt and prove the complete workflow without live Orca

**User Story:** As a consuming project, I want adoption to install the whole hybrid workflow and
prove it locally without depending on the current Orca host.

**Acceptance Criteria:**

1. WHEN adoption runs THEN the installed copy SHALL include the workflow-owned skill, assisted probe, autonomous scheduler, workflow resolver, role templates, config example, and canonical guidance at byte-identical destinations. (HSE-35)
2. WHEN adoption is repeated THEN the workflow SHALL update owned files and SHALL preserve the consumer's `.my-workflow.toml` and product-owned QA profile. (HSE-36)
3. WHEN the canonical gate runs THEN the workflow SHALL exercise schema, packets, scheduler, health, leases, fake Orca lifecycle, adoption, and import safety without invoking live Orca. (HSE-37)
4. WHILE upstream Orca transport support remains externally unverified the live-host QA scenario SHALL remain `blocked-verify` with the limitation named, while fake-provider and adoption journeys SHALL carry current evidence. (HSE-38)

**Independent Test:** Run the complete offline gate and an adoption dry-run into a disposable project,
then import the installed probe with a call-counting fake Orca.

## Security Acceptance Criteria

1. BEFORE a configured executable, packet path, state path, worktree path, or cleanup target is used, the workflow SHALL prove it is repository-owned, non-symlinked where required, and representable as fixed argv without shell interpolation. (HSE-39)
2. IF untrusted config, snapshot, provider JSON, health JSON, receipt JSON, or state JSON violates its schema or correlation identity THEN the workflow SHALL reject it before the next external mutation. (HSE-40)
3. WHILE operation state is persisted the workflow SHALL retain immutable operation, repository, slice, handle, commit, worktree, and lease identities required to reconcile the same effect. (HSE-41)
4. WHEN diagnostics or telemetry are emitted THEN the workflow SHALL redact secrets, environment values, packet bodies, terminal text, and absolute home-directory prefixes. (HSE-42)
5. IF ownership, integration, clean-tree, process-stop, lease-release, branch-removal, or ref-removal proof is incomplete THEN cleanup SHALL stop before the destructive step and SHALL report the unresolved residue. (HSE-43)

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Public config, snapshot schema, role behavior, adoption, and scheduler runtime | Version-3 hard cut, typed bounds, executable contract tests | HSE-07, HSE-08, HSE-09, HSE-10, HSE-11, HSE-35 |
| S6 | Config/JSON inputs, packet and worktree paths, subprocess argv, diagnostics | Schema validation, repository containment, fixed argv, redaction | HSE-05, HSE-06, HSE-39, HSE-40, HSE-42 |
| S9 | Orca and consumer resource-provider processes | Capability proof, pointer-only delivery, correlated receipts, bounded read-only reconciliation | HSE-22, HSE-23, HSE-24, HSE-25, HSE-26, HSE-27 |
| S10 | Frozen snapshots and persisted operation/lease/cleanup state | Immutable identities, version checks, same-handle reconciliation | HSE-10, HSE-11, HSE-26, HSE-28, HSE-41 |
| S11 | Concurrent processes, isolated worktrees, gates, terminals, cleanup | Writer-only isolation, health admission, leases, ownership proof, fail-closed cleanup | HSE-15, HSE-16, HSE-17, HSE-20, HSE-21, HSE-28, HSE-43 |

## Edge Cases

- IF two ready slices claim overlapping write paths THEN the scheduler SHALL serialize them and SHALL report the conflicting paths. (HSE-44)
- IF a dependency checkpoint moves after verification THEN the consumer slice SHALL remain parked until the new commit is synchronized and reverified. (HSE-45)
- IF the integration checkout is dirty before serial or concurrent dispatch THEN the coordinator SHALL perform no writer, worktree, Orca, Git, or provider mutation. (HSE-46)
- IF a worker handle or worktree path is reused for a different repository, slice, or operation THEN the coordinator SHALL reject the observation and SHALL not perform destructive cleanup. (HSE-47)
- IF a heavy-gate lease cannot be acquired THEN the gate SHALL wait or fail closed while unrelated light work remains eligible. (HSE-48)

## Requirement Traceability

| Requirement ID | Story | Design slice | Status |
| --- | --- | --- | --- |
| HSE-01 | Lean skill | S1 | Implemented in T1 |
| HSE-02 | Lean skill | S1 | Implemented in T1 |
| HSE-03 | Lean skill | S1 | Implemented in T2 |
| HSE-04 | Lean skill | S1 | Implemented in T1 |
| HSE-05 | Lean skill | S1 | Implemented in T2 |
| HSE-06 | Lean skill | S1 | Implemented in T2 |
| HSE-07 | Config contract | S2 | In Design |
| HSE-08 | Config contract | S2 | In Design |
| HSE-09 | Config contract | S2 | In Design |
| HSE-10 | Config contract | S2 | In Design |
| HSE-11 | Config contract | S2 | In Design |
| HSE-12 | Config contract | S2 | In Design |
| HSE-13 | Hybrid scheduler | S3 | In Design |
| HSE-14 | Hybrid scheduler | S3 | In Design |
| HSE-15 | Hybrid scheduler | S3 | In Design |
| HSE-16 | Hybrid scheduler | S3 | In Design |
| HSE-17 | Hybrid scheduler | S3 | In Design |
| HSE-18 | Hybrid scheduler | S3 | In Design |
| HSE-19 | Hybrid scheduler | S3 | In Design |
| HSE-20 | Hybrid scheduler | S3 | In Design |
| HSE-21 | Hybrid scheduler | S3 | In Design |
| HSE-22 | Orca lifecycle | S4 | In Design |
| HSE-23 | Orca lifecycle | S4 | In Design |
| HSE-24 | Orca lifecycle | S4 | In Design |
| HSE-25 | Orca lifecycle | S4 | In Design |
| HSE-26 | Orca lifecycle | S4 | In Design |
| HSE-27 | Orca lifecycle | S4 | In Design |
| HSE-28 | Orca lifecycle | S4 | In Design |
| HSE-29 | Orca lifecycle | S4 | In Design |
| HSE-30 | Independent proof | S5 | In Design |
| HSE-31 | Independent proof | S5 | In Design |
| HSE-32 | Independent proof | S5 | In Design |
| HSE-33 | Independent proof | S5 | In Design |
| HSE-34 | Independent proof | S5 | In Design |
| HSE-35 | Adoption | S6 | In Design |
| HSE-36 | Adoption | S6 | In Design |
| HSE-37 | Adoption | S6 | In Design |
| HSE-38 | Adoption | S6 | In Design |
| HSE-39 | Security | S1, S2, S4, S6 | In Design |
| HSE-40 | Security | S2, S3, S4 | In Design |
| HSE-41 | Security | S4 | In Design |
| HSE-42 | Security | S1, S3, S4 | In Design |
| HSE-43 | Security | S4 | In Design |
| HSE-44 | Edge case | S3 | In Design |
| HSE-45 | Edge case | S3 | In Design |
| HSE-46 | Edge case | S3, S4 | In Design |
| HSE-47 | Edge case | S4 | In Design |
| HSE-48 | Edge case | S3 | In Design |

**Coverage:** 48 total, 48 mapped to design slices, 0 unmapped.

## Success Criteria

- [ ] Adoption installs `workflow-spec-driven` and `orca_assisted_probe.py` byte-identically and
  installs no `tlc-spec-driven` path.
- [ ] Role packets are at most 3,072 bytes and slice packets are at most 10,240 bytes under the
  canonical materialization check.
- [ ] Deterministic tests prove serial, two-lane, and incremental four-lane scheduling, including
  health and lease failures.
- [ ] Fake-Orca tests prove one mutation per logical operation, pointer-only payloads, import-time
  zero calls, and residue-zero cleanup.
- [ ] `npm_config_offline=true npm run test:all` exits `0` on the final adopted tree without live Orca.
