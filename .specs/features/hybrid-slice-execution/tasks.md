# Hybrid Slice Execution Tasks

## Execution Protocol

T1 bootstraps the replacement under the current `tlc-spec-driven` Execute contract. After CP-S1,
activate `workflow-spec-driven` by name for every remaining task. Keep `ponytail` full throughout.
Each vertical slice uses one implementer per writer worktree; its tasks run sequentially. Every task
co-locates its assigned tests, passes its gate, updates this file, and creates one atomic Conventional
Commit. Every code-changing slice closes with a fresh Technical Verifier before a dependent checkpoint
is consumed. Final Deep Review and QA use fresh sessions on the integrated tree.

**Design:** `.specs/features/hybrid-slice-execution/design.md`
**Status:** Approved

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

- [ ] Builder accepts exactly the contract fields and rejects transcript/full-state/unrelated-slice fields.
- [ ] Boundary byte counts and pre-dispatch failure are exact.
- [ ] Telemetry contains no packet or injected sensitive marker.
- [ ] Assigned 4 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0; CP-S1 is ready for a fresh Technical Verifier.

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

- [ ] Config and snapshot share version 3 and exact errors from `dx.md`.
- [ ] Defaults are `assisted` and `auto`; old modes and v1/v2 artifacts produce zero dispatch plans.
- [ ] Planner and executor accept the newly frozen snapshot without a version mismatch.
- [ ] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [ ] Quick and full gates exit 0 before commit.

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

- [ ] Zero/one/two-ready outcomes match the spec and only concurrent writers receive worktree plans.
- [ ] Fixed odd/even ownership is impossible; ready compatibility is recomputed from DAG/path/resource data.
- [ ] Overlap names exact paths and dirty baseline yields zero effect intents.
- [ ] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0; CP-S2 is ready for a fresh Technical Verifier.

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

- [ ] Probe imports no evidence module and dispatches only under the `__name__` guard.
- [ ] Full packet lands on disk; fake Orca receives one short pointer with no body marker.
- [ ] JSON output follows `dx.md` and contains no injected sensitive marker.
- [ ] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0 before commit.

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

- [ ] Every fake mutating command count is one in happy and post-effect-timeout paths.
- [ ] Only bounded same-handle read operations repeat.
- [ ] Malformed, stale, moved, reused, or contradictory identities fail closed before integration/cleanup.
- [ ] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0 before commit.

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

- [ ] Proven clean integrated run removes only owned effects and reports residue zero.
- [ ] Escaping/symlinked paths, reused handles, dirty trees, unmerged commits, running workers, live leases, or extra refs stop before destruction.
- [ ] Failure reports exact logical residue without home paths or raw payloads.
- [ ] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0; CP-S4 is ready for a fresh Technical Verifier.

**Tests:** integration + security — IT-010, SEC-001, SEC-008
**Gate:** `python3 tools/test_orca_assisted_probe.py && npm_config_offline=true npm run test:all`
**Commit:** `fix(orca): prove owned cleanup residue`

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

- [ ] Claude, Codex, and Cursor packets share the same role boundary and skill name.
- [ ] Contract trace proves author ≠ verifier/reviewer/QA and the correct private/integrated tree per phase.
- [ ] No implementer packet says one implementer globally, batch complete, or final QA.
- [ ] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0; CP-S5 is ready for a fresh Technical Verifier.

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

- [ ] Healthy windows permit one admission; missing/malformed/stale/pressured evidence denies it.
- [ ] Explicit and automatic caps are inputs, never silently overridden.
- [ ] Raw command, process, env, user, and path markers cannot enter output.
- [ ] Assigned 4 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0 before commit.

**Tests:** unit + security — UT-012, UT-013, UT-014, SEC-003
**Gate:** `python3 tools/test_machine_health.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(runtime): normalize host admission health`

### T10: Schedule adaptive writer lanes

**What:** Turn the point-in-time executor into a dynamic slot loop that starts two compatible writer
worktrees, refills freed slots, parks dependencies, synchronizes verified checkpoints, and admits one
health-proved writer at a time within the frozen cap.

**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** T4 (CP-S2), T6 (S4 effect checkpoint), T9
**Reuses:** Existing lane states, effect receipts, checkpoint sync, worktree destinations, adapter fallback
**Requirements:** HSE-16, HSE-17, HSE-18, HSE-19, HSE-20, HSE-45

**Tools:** local filesystem/shell; skills `ponytail` full and `workflow-spec-driven`

**Done when:**

- [ ] Two compatible writers start in isolated worktrees and freed slots receive the next ready slice.
- [ ] Lane 3+ appears only one per healthy settle window and never exceeds cap.
- [ ] Moved dependency checkpoint remains parked until sync and reverify.
- [ ] Assigned 3 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0 before commit.

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

- [ ] Competing exclusive heavy gates serialize through the existing provider while light work proceeds.
- [ ] Foreign/reused/mismatched leases authorize and release nothing.
- [ ] No second lock file, daemon, service, or dependency exists.
- [ ] Assigned 2 cases pass with no existing assertion weakened or deleted.
- [ ] Full gate exits 0; CP-S3 is ready for a fresh Technical Verifier.

**Tests:** integration + security — IT-004, SEC-004
**Gate:** `python3 tools/test_parallel_executor.py && npm_config_offline=true npm run test:all`
**Commit:** `feat(runtime): lease heavy workflow gates`

### T12: Install and prove the complete hybrid workflow

**What:** Replace adoption paths/references/config/templates with the v3 hybrid package, install the
probe, preserve consumer-owned config/profile on re-adoption, update canonical CFG/QAS/ADP contracts,
and prove the disposable installed tree offline while keeping the live host journey `blocked-verify`.

**Where:** `scripts/adopt.py`
**Depends on:** T2 (CP-S1), T3 (CP-S2), T7 (CP-S4), T8 (CP-S5), T11 (CP-S3)
**Reuses:** COPY_PATHS/COPY_MISSING ownership, `scripts/test_adopt.py`, existing QA personas/journeys/scenarios
**Requirements:** HSE-01, HSE-35, HSE-36, HSE-37, HSE-38, HSE-39

**Tools:** local filesystem/shell; skills `ponytail` full, `workflow-spec-driven`, `qa-plan`, `qa-execute`

**Done when:**

- [ ] Dry-run installs every owned component byte-identically, imports probe with zero calls, and installs no TLC path.
- [ ] Re-adoption preserves edited consumer config and product QA profile.
- [ ] Canonical offline gate exercises all fake providers and invokes live Orca zero times.
- [ ] Fake/adoption scenarios cite current evidence; live-host scenario remains truthfully `blocked-verify` with upstream limitation.
- [ ] Assigned 5 cases pass with no existing assertion weakened or deleted.
- [ ] Build gate exits 0; CP-S6 is ready for fresh Technical Verification, final Deep Review, QA Plan, and QA Execute.

**Tests:** integration + security — IT-013, IT-014, IT-015, IT-016, SEC-010
**Gate:** `python3 scripts/test_adopt.py && python3 -m compileall -q .agents/skills tools scripts && npm_config_offline=true npm run test:all`
**Commit:** `feat(adopt): install hybrid slice workflow`

## Checkpoint DAG

| Producer | Checkpoint | Consumers | Proof required before release |
| --- | --- | --- | --- |
| S1 / T2 | CP-S1 | S2, S4, S5 | Full gate + fresh Technical Verifier |
| S2 / T4 | CP-S2 | S3 | Resolver/planner v3 tests + fresh Technical Verifier |
| S4 / T7 | CP-S4 | S3, S6 | Fake-Orca exact-effects/cleanup tests + fresh Technical Verifier |
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
| T8 | T1 (cross-phase) | None | Match |
| T9 | T3 (cross-phase) | None | Match |
| T10 | T4, T6 (cross-phase), T9 | T9 | Match |
| T11 | T10 | T10 | Match |
| T12 | T2, T3, T7, T8, T11 (cross-phase) | None | Match |

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
| T8 | Role routing | unit + integration | unit + integration | OK |
| T9 | Health provider | unit + security | unit + security | OK |
| T10 | Adaptive scheduler | integration | integration | OK |
| T11 | Resource leases | integration + security | integration + security | OK |
| T12 | Adoption and QA registry | integration + security | integration + security | OK |
