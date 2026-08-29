# Hybrid Slice Execution Tasks

## Execution Protocol

T1 bootstraps the replacement under the current `tlc-spec-driven` Execute contract. After CP-S1,
activate `workflow-spec-driven` by name for every remaining task. Keep `ponytail` full throughout.
Each vertical slice uses one implementer per writer worktree; its tasks run sequentially. Every task
co-locates its assigned tests, passes its gate, updates this file, and creates one atomic Conventional
Commit. Every code-changing slice closes with a fresh Technical Verifier before a dependent checkpoint
is consumed. Final Deep Review and QA use fresh sessions on the integrated tree.

**Design:** `.specs/features/hybrid-slice-execution/design.md`
**Status:** In Progress — CP-S6 remediation authorized after preserved validation halt

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`,
> `docs/guidelines/GATES.md`, `package.json`, and the existing canonical suites. Test cases are
> enumerated in `tests.md`; existing suites set style/location, not a coverage ceiling.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Skill instructions and packet builder | unit + contract | Every allowed/forbidden packet field, exact byte boundaries, hard-cut name, attribution, conditional loading | `tools/test_workflow_spec_driven.py`, `tools/shared/tests/*.test.ts` | `python3 tools/test_workflow_spec_driven.py` plus full gate for TS contracts |
| Config and frozen snapshot | unit | Every accepted mode/cap/version and every invalid type/version; resolver/planner/executor alignment | `tools/test_workflow_config.py`, `tools/test_parallel_plan.py` | `python3 tools/test_workflow_config.py && python3 tools/test_parallel_plan.py` |
| Scheduler, health, leases, lifecycle | unit + integration + security | All state/admission branches, dependency/path/resource edge cases, failure paths, exact mutation counts, residue | `tools/test_parallel_executor.py`, `tools/test_machine_health.py` | `python3 tools/test_machine_health.py && python3 tools/test_parallel_executor.py` |
| Orca probe and adapter | integration + security | Pointer-only payload, import safety, every logical mutation under transient failure, identity contradictions, cleanup | `tools/test_orca_assisted_probe.py`, `tools/test_orca_adapter.py` | `python3 tools/test_orca_assisted_probe.py && python3 tools/test_orca_adapter.py` |
| Review convergence state | unit + security | Immutable halt generations, explicit authorization, bypass rejection, independent-PASS-only closure | `tools/test_review_convergence.py` | `python3 tools/test_review_convergence.py` |
| Role routing and independent proof | contract + integration | Author identity separation, slice checkpoint order, integrated review/QA tree, handoff-only last implementer | `tools/shared/tests/autonomous-parallelization.test.ts`, `tools/shared/tests/qa-skills.test.ts` | Full gate |
| Adoption and QA registry | integration + security | Byte identity, old path absence, re-adoption preservation, import zero effects, machine-readable truthful statuses | `scripts/test_adopt.py`, canonical TS QA suites | `python3 scripts/test_adopt.py` plus full gate |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | After a Python component and its canonical suite | The task's named `python3 tools/test_*.py` or `python3 scripts/test_adopt.py` command |
| Full | After each vertical slice checkpoint and every TS contract change | `npm_config_offline=true npm run test:all` |
| Build | Before final review and delivery | `python3 -m compileall -q .agents/skills tools scripts && npm_config_offline=true npm run test:all` |

## Execution Plan

Phase numbers are topological labels for validation. Assisted execution uses the checkpoint DAG:
after CP-S1, S2, S4, and S5 are independent; S3 consumes CP-S2 and CP-S4; S6 consumes every prior
checkpoint.

### Phase 1: S1 — Lean context contract

```text
T1 → T2
```

### Phase 2: S2 — Version-3 workflow contract

```text
T3 → T4
```

### Phase 3: S4 — Pointer-only Orca lifecycle

```text
T5 → T6 → T7
```

### Phase 3R: S4 — Authorized halt recovery and physical mutation proof

```text
T7 → T13 → T14
```

### Phase 4: S5 — Independent proof pipeline

```text
T8
```

### Phase 5: S3 — Adaptive hybrid scheduler

```text
T9 → T10 → T11
```

### Phase 6: S6 — Adoption and truthful QA

```text
T12
```

## Task Breakdown

### T1: Replace TLC with the workflow-owned skill

**What:** Create the attributed `workflow-spec-driven` package from maintained TLC planning/validation
behavior, rewrite delegation around vertical slices and fresh per-slice verification, remove the old
skill tree and every old-name/phase-batch reference, and extend the canonical skill contract test.

**Where:** `.agents/skills/workflow-spec-driven/`
**Depends on:** None
**Reuses:** Current TLC validators, lessons, convergence scripts, and reference structure
**Requirements:** HSE-01, HSE-02, HSE-04

**Tools:** local filesystem/shell; skills `ponytail` full and current `tlc-spec-driven` bootstrap

**Done when:**

- [x] `NOTICE.md` carries author/source/license/change attribution and `skills-lock.json` names only the new skill.
- [x] `rg 'tlc-spec-driven|phase batch|Batch complete'` finds only attribution/history explicitly allowed by the contract test.
- [x] Conditional loading, slice task ordering, and fresh Technical Verifier wording are canonical across skill and instruction references.
- [x] Assigned 1 case passes with no existing assertion weakened or deleted.
- [x] Full gate exits 0 before commit.

**Tests:** unit + contract — UT-001
**Gate:** `npm_config_offline=true npm run test:all`
**Commit:** `refactor(skill): own slice-driven workflow contract`

### T2: Enforce slice packet budgets

**What:** Add the stdlib slice-packet builder, strict field allowlist, pointer-addressable output,
3,072/10,240-byte limits, and redacted byte telemetry; extend its owning skill suite.

**Where:** `.agents/skills/workflow-spec-driven/scripts/slice_packet.py`
**Depends on:** T1
**Reuses:** Workflow skill Python CLI/validator conventions
**Requirements:** HSE-03, HSE-05, HSE-06, HSE-42

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Builder accepts exactly the contract fields and rejects transcript/full-state/unrelated-slice fields.
- [x] Boundary byte counts and pre-dispatch failure are exact.
- [x] Telemetry contains no packet or injected sensitive marker.
- [x] Assigned 4 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0; CP-S1 is ready for a fresh Technical Verifier.

**Tests:** unit + security — UT-002, UT-003, UT-004, SEC-011
**Gate:** `npm_config_offline=true npm run test:all`
**Commit:** `feat(context): enforce slice packet budgets`

### T3: Freeze public workflow schema version 3

**What:** Replace config/snapshot v2 and old parallel modes with the exact v3 surface, freeze
`assisted`, `max_workers`, baseline/ceiling, and reject every old active snapshot until `--refresh`;
align all resolver readers and canonical tests.

**Where:** `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on:** T1 (CP-S1)
**Reuses:** Existing config schema, profile/model resolution, snapshot writer, refresh command
**Requirements:** HSE-07, HSE-08, HSE-09, HSE-10, HSE-11, HSE-40

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Config and snapshot share version 3 and exact errors from `dx.md`.
- [x] Defaults are `assisted` and `auto`; old modes and v1/v2 artifacts produce zero dispatch plans.
- [x] Planner and executor accept the newly frozen snapshot without a version mismatch.
- [x] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [x] Quick and full gates exit 0 before commit.

**Tests:** unit + integration + security — UT-005, UT-006, UT-007, IT-001, SEC-002
**Gate:** `python3 tools/test_workflow_config.py && python3 tools/test_parallel_plan.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(config): freeze hybrid workflow schema`

### T4: Plan hybrid writer lanes

**What:** Extend the ready-slice planner to emit serial-integration or concurrent-writer decisions,
dynamic compatibility metadata, exact blockers/conflicts, and zero-effect dirty-baseline rejection.

**Where:** `.agents/skills/workflow-config/scripts/parallel_plan.py`
**Depends on:** T3
**Reuses:** Existing DAG, checkpoint, path-conflict, capability, and serial-fallback analysis
**Requirements:** HSE-12, HSE-13, HSE-14, HSE-15, HSE-19, HSE-20, HSE-44, HSE-46

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Zero/one/two-ready outcomes match the spec and only concurrent writers receive worktree plans.
- [x] Fixed odd/even ownership is impossible; ready compatibility is recomputed from DAG/path/resource data.
- [x] Overlap names exact paths and dirty baseline yields zero effect intents.
- [x] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0; CP-S2 is ready for a fresh Technical Verifier.

**Tests:** unit + security — UT-008, UT-009, UT-010, UT-011, SEC-009
**Gate:** `npm_config_offline=true npm run test:all`
**Commit:** `feat(planner): plan hybrid writer lanes`

### T5: Ship pointer-only assisted Orca probe

**What:** Create the self-contained stdlib probe with guarded `dispatch`, `inspect`, and `cleanup`
subcommands, packet persistence, short-pointer send, injected runners, JSON stdout, and import safety.

**Where:** `tools/orca_assisted_probe.py`
**Depends on:** T1 (CP-S1)
**Reuses:** `tools/qa_parallel_pilot.py` CLI/JSON conventions and existing Orca adapter redaction
**Requirements:** HSE-22, HSE-23, HSE-29

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Probe imports no evidence module and dispatches only under the `__name__` guard.
- [x] Full packet lands on disk; fake Orca receives one short pointer with no body marker.
- [x] JSON output follows `dx.md` and contains no injected sensitive marker.
- [x] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0 before commit; remediation adds the public lifecycle proof.

**Tests:** integration + security — IT-006, IT-011, SEC-005
**Gate:** `python3 tools/test_orca_assisted_probe.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(orca): ship pointer-only assisted probe`

### T6: Reconcile assisted effects exactly once

**What:** Flatten and implement dispatch/settle state so every mutation is issued once, read-only
inspections settle transient outcomes, and full repository/route/operation/commit/lease identity is
persisted and required.

**Where:** `tools/orca_assisted_probe.py`
**Depends on:** T5
**Reuses:** Existing executor operation receipts, bounded inspections, and Orca adapter capability
**Requirements:** HSE-24, HSE-25, HSE-26, HSE-27, HSE-41, HSE-47

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Every fake mutating command count is one in happy and post-effect-timeout paths.
- [x] Only bounded same-handle read operations repeat.
- [x] Malformed, stale, moved, reused, or contradictory identities fail closed before integration/cleanup.
- [x] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0 before commit; remediation adds correlated Git/lease exactly-once proof.

**Tests:** integration + security — IT-007, IT-008, IT-009, SEC-006, SEC-007
**Gate:** `python3 tools/test_orca_assisted_probe.py && npm_config_offline=true npm run test:all`
**Commit:** `fix(orca): reconcile assisted effects exactly once`

### T7: Prove owned cleanup residue

**What:** Complete cleanup with ordered stop/release/integration/clean-tree/worktree/branch/ref proofs,
repository-contained fixed paths, fail-closed foreign-state handling, and normalized residue reporting.

**Where:** `tools/orca_assisted_probe.py`
**Depends on:** T6
**Reuses:** Existing executor cleanup receipts and deterministic Git worktree ownership from AD-013
**Requirements:** HSE-28, HSE-39, HSE-43, HSE-47

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Proven clean integrated run removes only owned effects and reports residue zero.
- [x] Escaping/symlinked paths, reused handles, dirty trees, unmerged commits, running workers, live leases, or extra refs stop before destruction.
- [x] Failure reports exact logical residue without home paths or raw payloads.
- [x] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0; CP-S4 is ready for a fresh Technical Verifier.

**Tests:** integration + security — IT-010, SEC-001, SEC-008
**Gate:** `python3 tools/test_orca_assisted_probe.py && npm_config_offline=true npm run test:all`
**Commit:** `fix(orca): prove owned cleanup residue`

**Checkpoint result:** Fresh Technical Verification halted CP-S4 after the third failure of immutable
fingerprint `a83ca4d68afa5e45916eae7606c22e6dd57444470bea7b13cfb916684e98bbfd`.
T5-T7 and their commits remain completed history; T13-T14 remediate the missing audit-resume and
successful physical-ledger proofs before CP-S4 is presented again.

### T13: Authorize halted audit generations

**What:** Extend convergence state with append-only audit generations and one explicit resume
operation, then use that operation with the durable 2026-08-28 human authorization reference to
open generation 2 under the existing halted CP-S4 fingerprint without changing its first generation.

**Where:** `.agents/skills/workflow-spec-driven/scripts/review_convergence.py`
**Depends on:** T7
**Reuses:** Existing fingerprint normalization, atomic state writer, and independent result recorder
**Requirements:** HSE-49, HSE-50, HSE-51, HSE-52

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Resume accepts only an existing halted fingerprint plus a non-empty exact authorization
  reference and appends generation 2 with local count 0.
- [x] Generation 1 remains halted at 3, cumulative failures remain 3, and its halt event is retained.
- [x] Unknown/non-halted resume, ordinary-record bypass, same-requirement rewording, replacement
  fingerprint, and inconsistent manually reset state fail before write.
- [x] Only a fresh independent PASS with a green gate closes generation 2 and the fingerprint;
  generation 2 halts independently on its third failed remediation.
- [x] The resume command updates `review-fingerprints.json` using authorization reference
  `.specs/features/hybrid-slice-execution/decisions.md#authorized-cp-s4-resume--2026-08-28`;
  no manual JSON edit or new fingerprint is used.
- [x] Assigned 4 cases and full gate exit 0 before commit.

**Tests:** unit + security — UT-017, UT-018, UT-019, SEC-012
**Gate:** `python3 tools/test_review_convergence.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(review): authorize halted audit generations`

### T14: Centralize assisted mutation issuance

**What:** Replace the probe's distributed mutation paths with one `MutationRunner.issue` guard that
atomically persists `in_flight` before one sink call, reconciles existing `in_flight`/`unknown`
effects by bounded reads only, deletes unreachable legacy mutators, and proves actual Git, provider,
and Orca calls with independent physical ledgers.

**Where:** `tools/orca_assisted_probe.py`
**Depends on:** T13
**Reuses:** Existing effect identities, read-only reconciliation, pointer payload, cleanup ownership,
and stdlib atomic writer pattern from review convergence
**Requirements:** HSE-24, HSE-25, HSE-53, HSE-54, HSE-55, HSE-56, HSE-57

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] `MutationRunner.issue` is the sole reachable Orca/Git/provider mutation boundary for public
  `dispatch` and `cleanup`; a structural AST check rejects any alternate sink.
- [x] State is durably `in_flight` with attempt 1 before the sink; injected atomic-write failure
  leaves prior bytes unchanged and all physical ledgers empty.
- [x] Existing `in_flight`/`unknown` entries issue zero mutations and use only bounded same-identity
  reads; absent or contradictory observations fail closed.
- [x] PATH-backed Git, provider, and Orca ledgers record exactly one physical mutation for every
  logical happy, post-effect-timeout, pointer, and cleanup operation.
- [x] Terminal ledger contains the short packet pointer and never the packet body.
- [x] The duplicate-success Git and provider discrimination mutants both fail the focused suite.
- [x] Assigned 5 new cases, all prior S4 cases, focused gate, and full gate exit 0; generation 2 is
  ready for a fresh independent CP-S4 Technical Verifier.

**Tests:** unit + integration + security — UT-020, IT-017, IT-018, IT-019, SEC-013
**Gate:** `python3 tools/test_orca_assisted_probe.py && npm_config_offline=true npm run test:all`
**Commit:** `fix(orca): centralize assisted mutation issuance`

### T8: Route independent slice proof

**What:** Rewrite provider role templates and autonomous/review guidance so one implementer owns one
slice, tasks are sequential, each code slice gets a fresh Technical Verifier, integrated groups get
fresh Deep Review, final QA is fresh, and the last implementer emits only a compact handoff.

**Where:** `templates/agents/`
**Depends on:** T1 (CP-S1)
**Reuses:** Existing planner/verifier packets, review cadence resolver, QA Plan/Execute routing
**Requirements:** HSE-30, HSE-31, HSE-32, HSE-33, HSE-34

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Claude, Codex, and Cursor packets share the same role boundary and skill name.
- [x] Contract trace proves author ≠ verifier/reviewer/QA and the correct private/integrated tree per phase.
- [x] No implementer packet says one implementer globally, batch complete, or final QA.
- [x] Assisted dispatch names `workflow-spec-driven` as slice-native: independent slices may run
  concurrently while tasks inside one slice remain sequential in its worker/worktree.
- [x] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0; CP-S5 is ready for a fresh Technical Verifier.

**Tests:** unit + integration — UT-015, UT-016, IT-012
**Gate:** `npm_config_offline=true npm run test:all`
**Commit:** `feat(agents): route independent slice proof`

### T9: Normalize host admission health

**What:** Add the stdlib machine-health helper with bounded platform reads, normalized/redacted JSON,
freshness validation, deterministic injected probes, and fail-closed lane-3 admission.

**Where:** `.agents/skills/autonomous/scripts/machine_health.py`
**Depends on:** T3 (CP-S2)
**Reuses:** Python stdlib subprocess/time/disk APIs and executor dependency injection patterns
**Requirements:** HSE-16, HSE-17, HSE-18, HSE-42

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Healthy windows permit one admission; missing/malformed/stale/pressured evidence denies it.
- [x] Explicit and automatic caps are inputs, never silently overridden.
- [x] Raw command, process, env, user, and path markers cannot enter output.
- [x] Assigned 4 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0 before commit.

**Tests:** unit + security — UT-012, UT-013, UT-014, SEC-003
**Gate:** `python3 tools/test_machine_health.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(runtime): normalize host admission health`

### T10: Schedule adaptive writer lanes

**What:** Turn the point-in-time executor into a dynamic slot loop that starts two compatible writer
worktrees, refills freed slots, parks dependencies, synchronizes verified checkpoints, and admits one
health-proved writer at a time within the frozen cap.

**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** T4 (CP-S2), T14 (CP-S4), T9
**Reuses:** Existing lane states, effect receipts, checkpoint sync, worktree destinations, adapter fallback
**Requirements:** HSE-16, HSE-17, HSE-18, HSE-19, HSE-20, HSE-45

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Two compatible writers start in isolated worktrees and freed slots receive the next ready slice.
- [x] Lane 3+ appears only one per healthy settle window and never exceeds cap.
- [x] Moved dependency checkpoint remains parked until sync and reverify.
- [x] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0 before commit.

**Tests:** integration — IT-002, IT-003, IT-005
**Gate:** `python3 tools/test_parallel_executor.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(runtime): schedule adaptive writer lanes`

### T11: Lease heavy workflow gates

**What:** Extend the existing resource-provider claims so resource-bearing writers and heavy gates use
the same correlated acquire/release protocol, wait independently, and never start without their lease.

**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** T10
**Reuses:** Existing `ResourceProvider`, lease receipts, idempotency correlation, environment redaction
**Requirements:** HSE-21, HSE-40, HSE-48

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [x] Competing exclusive heavy gates serialize through the existing provider while light work proceeds.
- [x] Foreign/reused/mismatched leases authorize and release nothing.
- [x] No second lock file, daemon, service, or dependency exists.
- [x] Assigned 2 cases pass with no existing assertion weakened or deleted.
- [x] Full gate exits 0; CP-S3 is ready for a fresh Technical Verifier.

**Tests:** integration + security — IT-004, SEC-004
**Gate:** `python3 tools/test_parallel_executor.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(runtime): lease heavy workflow gates`

### T12: Install and prove the complete hybrid workflow

**What:** Replace adoption paths/references/config/templates with the v3 hybrid package, install the
probe, preserve consumer-owned config/profile on re-adoption, update canonical CFG/QAS/ADP contracts,
and prove the disposable installed tree offline while keeping the live host journey `blocked-verify`.

**Where:** `scripts/adopt.py`
**Depends on:** T2 (CP-S1), T3 (CP-S2), T14 (CP-S4), T8 (CP-S5), T11 (CP-S3)
**Reuses:** COPY_PATHS/COPY_MISSING ownership, `scripts/test_adopt.py`, existing QA personas/journeys/scenarios
**Requirements:** HSE-01, HSE-35, HSE-36, HSE-37, HSE-38, HSE-39

**Tools:** local filesystem/shell; skills `ponytail` full, `workflow-spec-driven`, `qa-plan`, `qa-execute`

**Done when:**

- [x] Dry-run installs every owned component byte-identically, imports probe with zero calls, and installs no TLC path.
- [x] Re-adoption preserves edited consumer config and product QA profile.
- [x] Canonical offline gate exercises all fake providers and invokes live Orca zero times.
- [x] Fake/adoption scenarios cite current evidence; live-host scenario remains truthfully `blocked-verify` with upstream limitation.
- [x] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [x] Build gate exits 0; CP-S6 is ready for fresh Technical Verification, final Deep Review, QA Plan, and QA Execute.

**Tests:** integration + security — IT-013, IT-014, IT-015, IT-016, SEC-010
**Gate:** `python3 scripts/test_adopt.py && python3 -m compileall -q .agents/skills tools scripts && npm_config_offline=true npm run test:all`
**Commit:** `feat(adopt): install hybrid slice workflow`

### Final review remediation: close workflow blockers

**What:** Harden the final workflow contract for oversized health evidence, explicit serial
integration, serial-lane technical proof, slice-keyed validation reports, and immutable review
convergence counters.

**Where:** `.agents/skills/autonomous/`, `.agents/skills/workflow-spec-driven/`,
`.agents/skills/workflow-config/`, `tools/`
**Depends on:** T4, T10, T13

**Done when:**

- [x] Invalid numeric evidence and boolean convergence counters fail closed without rewriting state.
- [x] One ready slice uses the clean integration checkout; two or more compatible slices are the
  only worktree case.
- [x] Serial code-changing lanes capture their post-worker head and require a fresh verifier before
  completion or dependent consumption.
- [x] Slice verifier evidence is keyed by slice and the aggregate `validation.md` is final-only.
- [x] Focused gates and the exact full gate exit 0 before commit.

**Gate:** `python3 tools/test_machine_health.py && python3 tools/test_parallel_plan.py && python3 tools/test_parallel_executor.py && python3 tools/test_review_convergence.py && npm_config_offline=true npm run test:all`
**Commit:** `fix(workflow): close final review blockers`

### Final review remediation: close probe safety blockers

**What:** Bind every assisted probe mutation and read reconciliation to immutable targets,
prepared leases, effect-specific postconditions, durable diagnostics, and a process-safe ledger.

**Where:** `tools/orca_assisted_probe.py`, `tools/test_orca_assisted_probe.py`
**Depends on:** T14
**Requirements:** HSE-22, HSE-23, HSE-24, HSE-25, HSE-26, HSE-27, HSE-28, HSE-29, HSE-39, HSE-40, HSE-41, HSE-42, HSE-53, HSE-54, HSE-55, HSE-56, HSE-57

**Done when:**

- [x] Diagnostics redact terminal/provider text, secrets, packet bodies, and raw receipts.
- [x] Foreign mutation targets, destructive observations, malformed/unleased resources, and
  pointer-kind mismatches fail before a physical sink.
- [x] Lease receipts prove acquisition/release state; reconciliation proves the requested
  postcondition and never issues a mutation.
- [x] Concurrent dispatch shares the durable issue lock and preserves one physical mutation.
- [x] Probe check passes 24/24 and the exact full gate exits 0.

**Gate:** `python3 tools/test_orca_assisted_probe.py && npm_config_offline=true npm run test:all`
**Commit:** `fix(orca): close final probe review blockers`

### Final QA Plan: hybrid adoption and assisted execution

**What:** Map every HSE criterion to durable adoption, configuration, offline assisted-execution,
or internal technical evidence; reset changed public promises for a fresh independent walk while
preserving the live Orca limitation.

**Where:** `docs/qa/journeys/`, `docs/qa/scenarios/`, `docs/qa/charters/`
**Depends on:** CP-S6 and final implementation review
**Requirements:** HSE-01 through HSE-57

**Done when:**

- [x] All 57 acceptance criteria have one explicit disposition across the three 2026-08-29 charters.
- [x] Adoption, configuration, offline fake-provider, and convergence scenarios are `untested`; the passing fallback is an adjacent canary.
- [x] Real Orca lifecycle and completed-pilot cleanup remain `blocked-verify`.
- [x] The handoff names the existing CLI/manual adapter, checkout-local fake providers, evidence/report paths, and a fresh QA Execute Verifier.
- [x] No product walk, live Orca action, framework installation, or product/runtime edit occurred in QA Plan.

**Gate:** `npm_config_offline=true npm run test:all`
**Commit:** `test(qa): plan hybrid adoption verification`

### Final QA Execute: hybrid adoption and assisted execution

**What:** Walk adopted workflow through public CLIs with checkout-local fake providers, record fresh
independent readback, and preserve unreachable live-host boundary truthfully.

**Where:** `docs/qa/reports/2026-08-29-hybrid-slice-execution.md`, affected scenario frontmatter,
ignored `docs/qa/evidence/2026-08-29-hybrid-slice-execution/`
**Depends on:** Final QA Plan
**Requirements:** HSE-01 through HSE-57

**Done when:**

- [x] All 3 charters have terminal verdicts: 6 offline/adoption scenarios pass and 2 live-Orca
  scenarios remain `blocked-verify` with external boundary named.
- [x] Adoption proves 65 selected managed files byte-identical, old TLC absent, consumer state
  preserved, package membership present, and probe import makes 0 Orca calls.
- [x] Public planner/executor walks prove serial integration, 2 compatible writers, dependency and
  path blocking, disabled zero-effect fallback, fail-closed health, and provider refusal.
- [x] Pointer delivery contains 0 packet-body occurrences; all 7 transient logical mutation classes
  record exactly 1 physical call; cleanup reconciles to zero owned residue.
- [x] Convergence halts generation 1 at 3, appends authorized generation 2 without history reset,
  rejects missing authorization without a write, and closes only on fresh independent PASS.
- [x] Nine edge probes pass; current scenario evidence and report paths reload independently.
- [x] Live Orca, external skill installation, network publication, and product/runtime edits remain
  absent from this QA session.
- [ ] Closing gate exits 0. The adoption gate assertion now accepts the current `pass` verdict and
  dated evidence/report while preserving the live Orca `blocked-verify` assertion; fresh QA retest
  remains pending before this task can close.

**Gate:** `npm_config_offline=true npm run test:all`
**Commit:** `test(qa): verify hybrid adoption workflow`

## Checkpoint DAG

| Producer | Checkpoint | Consumers | Proof required before release |
| --- | --- | --- | --- |
| S1 / T2 | CP-S1 | S2, S4, S5 | Full gate + fresh Technical Verifier |
| S2 / T4 | CP-S2 | S3 | Resolver/planner v3 tests + fresh Technical Verifier |
| S4 / T14 | CP-S4 | S3, S6 | Authorized generation-2 audit + structural single issuer + physical Git/provider/Orca ledgers + fresh Technical Verifier PASS |
| S5 / T8 | CP-S5 | S6 | Role-route trace + fresh Technical Verifier |
| S3 / T11 | CP-S3 | S6 | Scheduler/health/lease trace + fresh Technical Verifier |
| S6 / T12 | CP-S6 | Final review/QA | Build gate + fresh Technical Verifier |

## Test Assignment Ledger

Each ID appears once below and once in exactly one task `Tests` field.

| Task | Assigned IDs |
| --- | --- |
| T1 | UT-001 |
| T2 | UT-002, UT-003, UT-004, SEC-011 |
| T3 | UT-005, UT-006, UT-007, IT-001, SEC-002 |
| T4 | UT-008, UT-009, UT-010, UT-011, SEC-009 |
| T5 | IT-006, IT-011, SEC-005 |
| T6 | IT-007, IT-008, IT-009, SEC-006, SEC-007 |
| T7 | IT-010, SEC-001, SEC-008 |
| T13 | UT-017, UT-018, UT-019, SEC-012 |
| T14 | UT-020, IT-017, IT-018, IT-019, SEC-013 |
| T8 | UT-015, UT-016, IT-012 |
| T9 | UT-012, UT-013, UT-014, SEC-003 |
| T10 | IT-002, IT-003, IT-005 |
| T11 | IT-004, SEC-004 |
| T12 | IT-013, IT-014, IT-015, IT-016, SEC-010 |

## Task Granularity Check

| Task | Single deliverable | Status |
| --- | --- | --- |
| T1 | Workflow-owned skill package | Granular |
| T2 | Slice packet builder | Granular |
| T3 | Public v3 config/snapshot resolver | Granular |
| T4 | Hybrid ready-slice plan | Granular |
| T5 | Probe pointer/import surface | Granular |
| T6 | Probe effect reconciliation | Granular |
| T7 | Probe cleanup proof | Granular |
| T13 | Authorized convergence generation | Granular |
| T14 | Probe mutation issue guard | Granular |
| T8 | Independent role routing | Granular |
| T9 | Normalized health evidence | Granular |
| T10 | Adaptive writer-slot loop | Granular |
| T11 | Heavy-gate leases | Granular |
| T12 | Adopted end-to-end workflow | Cohesive vertical slice |

## Diagram-Definition Cross-Check

| Task | Depends on | In-phase diagram predecessor | Status |
| --- | --- | --- | --- |
| T1 | None | None | Match |
| T2 | T1 | T1 | Match |
| T3 | T1 (cross-phase) | None | Match |
| T4 | T3 | T3 | Match |
| T5 | T1 (cross-phase) | None | Match |
| T6 | T5 | T5 | Match |
| T7 | T6 | T6 | Match |
| T13 | T7 | T7 | Match |
| T14 | T13 | T13 | Match |
| T8 | T1 (cross-phase) | None | Match |
| T9 | T3 (cross-phase) | None | Match |
| T10 | T4, T14 (cross-phase), T9 | T9 | Match |
| T11 | T10 | T10 | Match |
| T12 | T2, T3, T14, T8, T11 (cross-phase) | None | Match |

## Test Co-location Validation

| Task | Layer | Matrix requires | Task says | Status |
| --- | --- | --- | --- | --- |
| T1 | Skill contract | unit + contract | unit + contract | OK |
| T2 | Packet builder | unit + security | unit + security | OK |
| T3 | Config/snapshot | unit + integration + security | unit + integration + security | OK |
| T4 | Planner | unit + security | unit + security | OK |
| T5 | Orca probe surface | integration + security | integration + security | OK |
| T6 | Orca effect state | integration + security | integration + security | OK |
| T7 | Cleanup state | integration + security | integration + security | OK |
| T13 | Review convergence state | unit + security | unit + security | OK |
| T14 | Mutation issue guard | unit + integration + security | unit + integration + security | OK |
| T8 | Role routing | unit + integration | unit + integration | OK |
| T9 | Health provider | unit + security | unit + security | OK |
| T10 | Adaptive scheduler | integration | integration | OK |
| T11 | Resource leases | integration + security | integration + security | OK |
| T12 | Adoption and QA registry | integration + security | integration + security | OK |
