# Host-Agnostic Slice Parallelization Tasks

## Execution Protocol

Implement with `tlc-spec-driven`. Tasks remain sequential inside each slice. Each code-changing slice
closes with a fresh Technical Verifier; deep-review uses the frozen grouped cadence; final QA remains
feature-level.

**Design:** `.specs/features/host-agnostic-slice-parallelization/design.md`
**Status:** Draft delta; T1–T5 remain historically complete

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, `SECURITY.md`, and existing executor/adapter tests.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| Adapter selection and CLI | unit + integration | Every selection, disabled, fallback, and preflight case | `tools/test_parallel_executor.py` | `python3 tools/test_parallel_executor.py` |
| Orca compatibility | integration with CLI double | Status, known-bad, canary, cache, cleanup, redaction | `tools/test_orca_adapter.py` | `python3 tools/test_orca_adapter.py` |
| Maestri compatibility | integration with CLI double | Environment and capability failures with zero mutations | `tools/test_maestri_adapter.py` | `python3 tools/test_maestri_adapter.py` |
| Agent workflow contract | contract | No TLC/review/QA regression; adapter policy installed | `tools/shared/tests/autonomous-parallelization.test.ts` | `npm_config_offline=true npm test` |
| Workflow mode resolution | unit | Default `assisted`; all four explicit modes preserved | `tools/test_workflow_config.py` | `python3 tools/test_workflow_config.py` |
| Assisted planning/executor boundary | unit + integration | Full-equivalent DAG/sync plan; disabled and fail-closed serial; no automatic adapter in assisted | `tools/test_parallel_plan.py`, `tools/test_parallel_executor.py` | `python3 tools/test_parallel_plan.py && python3 tools/test_parallel_executor.py` |
| Assisted coordinator probe | integration with fake Orca | Pointer-only, one-shot mutations, same-handle park/resume, exact cleanup, foreign preservation, import inertness | `tools/test_orca_assisted_probe.py` | `python3 tools/test_orca_assisted_probe.py` |
| Adoption | integration | Assisted probe copied to a disposable consumer and import remains inert | `scripts/test_adopt.py` | `python3 scripts/test_adopt.py` |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | One adapter, registry, probe, or adoption task | Owning Python test file, spec/tasks validators, `git diff --check` |
| Full | Integration/docs close | `npm_config_offline=true npm run test:all`; spec/tasks/state validators; `git diff --check` |
| Build | Planning-only mutation | Spec/tasks validators and `git diff --check` |

## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| A | Host selection fails closed before incompatible effects | `python3 tools/test_parallel_executor.py` | yes | It is the standalone adapter boundary. |
| B | Orca compatibility requires a zero-residue canary | `python3 tools/test_orca_adapter.py` | yes | It independently prevents false Orca compatibility. |
| C | Maestri reports unsupported without mutation | `python3 tools/test_maestri_adapter.py` | yes | It independently exposes current host limitations. |
| D | Adopted workflow documents the proven assisted lifecycle | `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts` | yes | It is the historical assisted contract. |
| E | Unconfigured workflows plan assisted work by default without invoking the automatic adapter | `python3 tools/test_workflow_config.py && python3 tools/test_parallel_plan.py && python3 tools/test_parallel_executor.py` | yes | It establishes the new default and preserves every explicit mode. |
| F | Adopted consumers receive one import-safe pointer-only probe | `python3 tools/test_orca_assisted_probe.py && python3 scripts/test_adopt.py` | yes | It makes the proven mechanics executable and distributable. |
| G | Main agents coordinate eligible slices by default and serialize only on declared fail-closed conditions | `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts` | yes | It completes the standard agent behavior using Slices E and F. |

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
T4 -> T5
```

### Phase 2: Default assisted delivery

Slices E and F are independent and may run concurrently under the coordinator. Slice G starts only
after both close. Each slice has one implementer; tasks remain sequential inside that slice.

```text
Slice E: T6 -> T7 ----\
                      -> T10
Slice F: T8 -> T9 ----/
```

## Task Breakdown

### T1: Add compatibility-aware adapter selection

**Status:** complete
**Slice:** A
**Resources:** none
**Observable behaviour:** `preflight` reports exact host compatibility even when disabled, disabled start/resume remain effect-free, and incompatible start/resume serialize without cross-host fallback.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Depends on:** None
**Requirement:** HST-01–HST-04, SEC-001, SEC-002
**Reuses:** Existing CLI, serial result, runtime-state path, and atomic JSON helpers.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; no new dependency.
**Done when:**

- [ ] CLI accepts `preflight` and `auto|orca|maestri` with one JSON result.
- [ ] Disabled `start`/`resume` imports or probes no adapter; explicit `preflight` remains diagnostic.
- [x] Executor accepts only workflow snapshot schema v2 and rejects obsolete v1 before host effects.
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

**Status:** complete
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

**Status:** complete
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

### T5: Publish coordinator-assisted Orca execution

**Status:** complete
**Slice:** D
**Resources:** none
**Observable behaviour:** The main agent can overlap eligible Orca slices, park a worker at its next
unmet dependency, resume that same terminal after exact
checkpoint sync, and clean only integrated owned resources while automatic orchestration stays
unsupported.
**Where:** `.agents/skills/autonomous/references/parallelization.md`, host-adapter threat/DX contracts,
and the canonical autonomous contract test.
**Depends on:** T4
**Requirement:** AST-01–AST-07, SEC-008
**Reuses:** Orca `worktree create` startup shell promotion, terminal wait/read/send/list/stop,
worktree comments/removal, existing checkpoint sync, and serial fallback rules.
**Tools:** Skills `ponytail`, `orca-cli`, `writing-for-agents`; current Orca CLI guide is authoritative.
**Done when:**

- [x] Contract distinguishes assisted coordination from automatic adapter compatibility.
- [x] Coordinator starts at most one worker per ready slice and workers stop at the first unmet task dependency.
- [x] Parked checkpoints record exact task/dependency/HEAD state and end the worker turn without polling.
- [x] Dependency completion synchronizes the exact producer commit, reruns the affected gate, and follows up the same terminal.
- [x] Dirty, ambiguous, conflicting, or failed state serializes without automatic resolution or unsafe cleanup.
- [x] Cleanup stops workers and removes only clean integrated coordinator-owned worktrees, with zero owned residue proven.
- [x] Frozen implementer provider/model/effort is expressed explicitly and proven by two consecutive connected `source=screen` reads matching the frozen route before prompt delivery; the exact-handle route loop runs every 250 ms for at most 60000 ms, resets on nonmatch, and remains separate from dependency waiting.
- [x] The explicit base/setup worktree startup shell is proven new and unused, receives `exec <validated-command>`, and remains the sole worker handle; no second terminal is created.
- [x] Worktree creation snapshots before state, issues one unique-name mutating create, and reconciles a missing/late receipt through a 250 ms / 60000 ms SETTLE WINDOW with cumulative inventory difference and final audit, without blind retry or ambiguous adoption.
- [x] Immutable ownership receipt is separated from mutable head/handle state; the worktree is detached when needed, the exact branch is safely deleted and its ref absence proven, and only then is the worktree removed.
- [x] Every logical packet records the exact handle, unique turn ID/phase, pre-head, task/comment/gate state, and one expected marker; each send occurs once with no retry or replacement worker.
- [x] Error, missing, or `agent_prompt_stalled` receipts reconcile only the same handle through a machine-only 250 ms / 300000 ms bounded effect proof; partial, dirty, conflicting, foreign, or ambiguous effects serialize, and commit-only adoption is rejected.
- [x] TLC task order, Verifier, grouped deep-review, QA, and full-gate contracts remain unchanged.
- [x] `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts` passes with zero failures.

**Tests:** IT-005, SEC-006 in `tools/shared/tests/autonomous-parallelization.test.ts`; E2E-001 in final QA.
**Gate:** Full. Commit `docs(workflow): enable coordinator-assisted Orca slices`.

### T6: Default workflow resolution to assisted mode

**Status:** complete
**Slice:** E
**Resources:** none
**Observable behaviour:** A consumer that does not choose a mode receives `assisted`; explicit
`disabled`, `safe`, and `full` remain unchanged.
**Where:** `.agents/skills/workflow-config/scripts/workflow_config.py`
**Files:** `.my-workflow.toml.example`, `tools/test_workflow_config.py`
**Depends on:** T5
**Requirement:** HST-05
**Reuses:** Existing resolver constants, snapshot validation, and table-driven mode tests.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; no new dependency.
**Done when:**

- [x] Missing parallelization configuration freezes `mode: assisted`.
- [x] Explicit `disabled|assisted|safe|full` survives resolution and snapshot validation unchanged.
- [x] Invalid modes still fail before snapshot mutation.
- [x] `python3 tools/test_workflow_config.py` passes with zero failures.

**Tests:** UT-007 in `tools/test_workflow_config.py`
**Gate:** Quick. Commit `feat(workflow): default to assisted parallelization`.

### T7: Route assisted plans outside the automatic adapter

**Status:** complete
**Slice:** E
**Resources:** none
**Observable behaviour:** Assisted mode exposes `full`-equivalent ready/sync planning to the main
coordinator, while explicit disabled and every unsafe or non-parallel plan execute sequentially with
zero automatic-adapter effect.
**Where:** `.agents/skills/workflow-config/scripts/parallel_plan.py`
**Files:** `.agents/skills/autonomous/scripts/parallel_execute.py`, `tools/test_parallel_plan.py`,
`tools/test_parallel_executor.py`
**Depends on:** T6
**Requirement:** HST-06, AST-08
**Reuses:** Existing `full` dependency/sync logic, disabled short-circuit, serial result, and recording adapters.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; no new dependency.
**Done when:**

- [x] Assisted independent and completed-producer plans equal `full` readiness and `sync_after` output.
- [x] Incomplete dependencies remain waiting; write conflicts and malformed metadata serialize.
- [x] Assisted `start`/`resume` returns a coordinator plan before automatic adapter construction.
- [x] Explicit disabled still invokes no planner, adapter, Git, or host call.
- [x] `safe` and `full` keep their automatic-adapter behavior unchanged.
- [x] `python3 tools/test_parallel_plan.py && python3 tools/test_parallel_executor.py` passes with zero failures.

**Tests:** UT-008 in `tools/test_parallel_plan.py`; IT-006 in `tools/test_parallel_executor.py`
**Gate:** Quick. Commit `feat(workflow): route assisted slice execution`.

### T8: Ship the self-contained assisted Orca probe

**Status:** complete
**Slice:** F
**Resources:** none
**Observable behaviour:** A main agent can execute the proven assisted lifecycle through one
import-safe stdlib module, with pointer-only delivery and no retried mutation.
**Where:** `tools/orca_assisted_probe.py`
**Files:** `tools/test_orca_assisted_probe.py`
**Depends on:** T5
**Requirement:** AST-10, AST-11, SEC-009
**Reuses:** The read-only Retest 12→11→6→5 evidence chain in the sibling QA checkout,
`docs/qa/scenarios/QAS-coordinate-assisted-orca-slices.md`, and the Retest 12 report. Do not edit or
import evidence files.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; stdlib only; fake `orca` on `PATH` for tests.
**Done when:**

- [x] Live Retest 12 behavior is flattened into one module with no `importlib` or evidence import.
- [x] Repository/worktree/branch, packet path, provider/model/effort, task/commit expectations, gates,
  markers, timing, and ownership prefix are parameters; no fixture or retest identifier is hardcoded.
- [x] Module dispatch occurs only under `if __name__ == "__main__":`; importing it records zero Orca calls.
- [x] Fake Orca injects transient/error/missing receipts and records exactly one create, send, comment
  set, stop, and rm per logical operation; repeated calls are read-only inspections only.
- [x] Sent payload equals the pointer and never contains the packet body.
- [x] Fake two-slice lifecycle parks, verifies, syncs, reruns the gate, resumes the same handle,
  integrates, cleans owned resources, and preserves foreign resources.
- [x] `python3 tools/test_orca_assisted_probe.py` passes with zero failures.

**Result:** 4/4 fake-Orca contract checks passed; mutations are one-shot, read-only retries are
bounded, pointer delivery excludes the packet body, cleanup preserves foreign worktrees, and import
is inert.

**Tests:** IT-007, IT-008, IT-009, SEC-007 in `tools/test_orca_assisted_probe.py`
**Gate:** Quick. Commit `feat(orca): ship assisted coordinator probe`.

### T9: Install the assisted probe during adoption

**Status:** complete
**Slice:** F
**Resources:** none
**Observable behaviour:** A real adoption into a disposable consumer installs the assisted probe at
`tools/orca_assisted_probe.py`, and importing the installed copy performs no Orca call.
**Where:** `scripts/adopt.py`
**Files:** `scripts/test_adopt.py`
**Depends on:** T8
**Requirement:** AST-12
**Reuses:** Existing `tools/qa_parallel_pilot.py` COPY_PATHS placement and
`BUG-20260825-adoption-omits-parallel-pilot` assertions.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; stdlib only.
**Done when:**

- [x] `COPY_PATHS` installs the probe adjacent to `tools/qa_parallel_pilot.py`.
- [x] Existing adoption suite proves the file lands in a disposable target.
- [x] The installed copy imports with fake Orca on `PATH` and records zero Orca calls.
- [x] `python3 scripts/test_adopt.py` passes with zero failures.

**Result:** Adoption copies the probe beside the parallel pilot, replaces stale managed copies,
preserves consumer configuration, and imports the installed module with zero Orca calls.

**Tests:** IT-011 in `scripts/test_adopt.py`
**Gate:** Quick. Commit `feat(adopt): install assisted coordinator probe`.

### T10: Publish assisted execution as the standard agent contract

**Status:** complete
**Slice:** G
**Resources:** none
**Observable behaviour:** Adopted agents dispatch safe independent slices through the main
coordinator by default, and choose sequential work only for explicit disabled mode or fail-closed
planning/runtime conditions.
**Where:** `AGENTS.md`
**Files:** `.agents/skills/autonomous/references/parallelization.md`,
`tools/shared/tests/autonomous-parallelization.test.ts`
**Depends on:** T7, T9
**Requirement:** AST-01–AST-12, SEC-008, SEC-009
**Reuses:** Existing assisted contract, shipped probe, frozen route, TLC slice ownership, and canonical contract suite.
**Tools:** Skills `ponytail`, `tlc-spec-driven`, `writing-for-agents`; no documentation lookup.
**Done when:**

- [x] AGENTS routes Execute to assisted inter-slice dispatch whenever the frozen plan exposes safe independent slices.
- [x] Main coordinator ownership covers create, pointer delivery, parking, producer verification,
  exact commit sync, affected-gate rerun, same-handle continuation, integration, and cleanup.
- [x] Slice workers cannot spawn or clean sibling workers and tasks remain sequential within a slice.
- [x] Explicit `disabled`, no ready overlap, write/resource/isolation failure, or uncertifiable
  ownership/reconciliation uses sequential execution.
- [x] Pointer-only transport remains mandatory with no body, threshold, retry, or replacement fallback.
- [x] Automatic `safe`/`full` adapter semantics remain unchanged and no compatibility PASS is fabricated.
- [x] `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts` passes with zero failures.
- [x] `npm_config_offline=true npm run test:all` passes with zero failures on the final tree.

**Result:** The adopted agent contract defaults eligible inter-slice work to coordinator-assisted
dispatch, keeps tasks within each slice sequential, and serializes explicit `disabled` or any
fail-closed plan/runtime condition. IT-010 exercises the assisted and disabled executor paths.

**Tests:** IT-005, IT-010 in `tools/shared/tests/autonomous-parallelization.test.ts`
**Gate:** Full. Commit `docs(agents): default to assisted slice execution`.

## Phase Execution Map

```text
Slice A: T1
Slice B: T1 -> T2
Slice C: T1 -> T3
Slice D: T2 -> T4
         T3 -> T4
         T4 -> T5
Slice E: T5 -> T6 -> T7
Slice F: T5 -> T8 -> T9
Slice G: T7 -> T10
         T9 -> T10
```

## Phase 3: Resumed verifier remediation

The first independent verification round found three proof gaps. T11 closes them without changing
the assisted lifecycle contract or the historical evidence record.

```text
T10 -> T11

T11 -> T12
```

### T11: Enforce assisted effect and cleanup proofs

**Status:** complete
**Slice:** G
**Resources:** none
**Observable behaviour:** Effect reconciliation rejects zero or mismatched commit expectations and
pending canonical tasks; cleanup rejects either surviving linked-worktree registration or surviving
admin Git metadata after the owned path is removed.
**Where:** `tools/orca_assisted_probe.py`
**Files:** `tools/test_orca_assisted_probe.py`
**Depends on:** T10
**Requirement:** AST-04, AST-06, SEC-008
**Reuses:** Existing effect reconciliation, canonical task parser, cleanup ownership receipt, and
temporary Git worktree test helpers.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; stdlib only.
**Done when:**

- [x] `effect()` requires a positive expected commit count and a nonempty subject list whose length
  matches that count, so a zero-commit effect cannot pass.
- [x] A pending expected task raises `ProbeError`, and the canonical test fails if task completion
  is replaced by an unconditional truthy predicate.
- [x] Cleanup raises when the linked-worktree registration survives path removal.
- [x] Cleanup raises when the admin linked-worktree Git directory survives registration/path removal.
- [x] `python3 tools/test_orca_assisted_probe.py` passes with zero failures.

**Result:** Effect checks reject invalid commit expectations and pending canonical tasks; independent
temporary-Git cases reject surviving registration and admin Git directory residue. The probe check
passes 20/20.

**Tests:** IT-012, SEC-010 in `tools/test_orca_assisted_probe.py`
**Gate:** Quick. Commit `fix(orca): enforce assisted effect and cleanup proofs`.

### T12: Close assisted capability, route, receipt, and cleanup review gaps

**Status:** complete
**Slice:** G
**Resources:** none
**Observable behaviour:** Assisted execution fails closed when direct Orca capability, resource,
route, receipt, handle, timing, or immutable cleanup proof is unavailable or ambiguous; every
mutating operation remains exactly once and only correlated same-handle read-only reconciliation
may continue.
**Where:** `tools/orca_assisted_probe.py`
**Files:** `tools/test_parallel_executor.py`, `tools/test_orca_assisted_probe.py`,
`tools/shared/tests/autonomous-parallelization.test.ts`
**Depends on:** T11
**Requirement:** AST-01, AST-04, AST-06, AST-08, SEC-007, SEC-008
**Reuses:** Existing fixed-argv probe, canonical task reconciliation, resource-provider boundary,
and fake-Orca lifecycle tests.
**Tools:** Skills `ponytail`, `tlc-spec-driven`; stdlib only.
**Done when:**

- [x] Assisted capability/isolation and resource-provider proofs fail closed before host effects.
- [x] Pointer paths, repository receipts, Git checkout identity, route tuples, terminal handles,
  tui-idle receipts, commit identities, and cleanup identity are exact and correlated.
- [x] Ambiguous create effects and moved handles fail closed before destructive cleanup.
- [x] Route timing is finite and bounded to the contract's 60-second window.
- [x] `python3 tools/test_orca_assisted_probe.py`, executor tests, and canonical Vitest pass.

**Result:** Review remediation closes all 19 canonical defects with 22 fake-Orca checks and
58 executor checks; no live Orca run was used.

**Tests:** IT-013, SEC-011 in `tools/test_orca_assisted_probe.py` and executor suites
**Gate:** Quick. Commit `fix(orca): close assisted probe review gaps`.

## Task Granularity Check

| Task | Scope | Status |
| --- | --- | --- |
| T1 | One executor selection boundary | PASS |
| T2 | One Orca compatibility capability | PASS |
| T3 | One Maestri compatibility capability | PASS |
| T4 | One canonical adoption contract | PASS |
| T5 | One assisted coordinator contract | PASS |
| T6 | One workflow-mode default | PASS |
| T7 | One assisted planner/executor boundary | PASS |
| T8 | One self-contained coordinator probe plus its canonical fake-host check | PASS |
| T9 | One adoption COPY_PATHS invariant plus its owning test | PASS |
| T10 | One adopted agent dispatch contract plus its canonical contract test | PASS |
| T11 | One resumed assisted effect and cleanup proof remediation plus its canonical fake-host checks | PASS |
| T12 | Assisted capability, route, receipt, and cleanup fail-closed review remediation | PASS |

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | None | PASS |
| T2 | T1 | T1 -> T2 | PASS |
| T3 | T1 | T1 -> T3 | PASS |
| T4 | T2, T3 | T2 + T3 -> T4 | PASS |
| T5 | T4 | T4 -> T5 | PASS |
| T6 | T5 | T5 -> T6 | PASS |
| T7 | T6 | T6 -> T7 | PASS |
| T8 | T5 | T5 -> T8 | PASS |
| T9 | T8 | T8 -> T9 | PASS |
| T10 | T7, T9 | T7 + T9 -> T10 | PASS |
| T11 | T10 | T10 -> T11 | PASS |
| T12 | T11 | T11 -> T12 | PASS |

## Test Co-location Validation

| Task | Code Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | Adapter selection/CLI | unit + integration | UT/IT in executor suite | PASS |
| T2 | Orca compatibility | integration double | UT/IT in Orca suite | PASS |
| T3 | Maestri compatibility | integration double | UT/IT in Maestri suite | PASS |
| T4 | Agent workflow contract | contract | shared/adoption suites | PASS |
| T5 | Agent workflow contract | contract + QA pilot | shared contract test + E2E-001 | PASS |
| T6 | Workflow mode resolution | unit | UT-007 in resolver suite | PASS |
| T7 | Assisted plan/executor boundary | unit + integration | UT-008 + IT-006 in canonical planner/executor suites | PASS |
| T8 | Assisted coordinator probe | fake-host integration | IT-007–IT-009 + SEC-007 in one runnable stdlib check | PASS |
| T9 | Adoption | integration | IT-011 in existing adoption suite | PASS |
| T10 | Agent workflow contract | contract | IT-005 + IT-010 in canonical autonomous suite | PASS |
| T11 | Assisted coordinator probe | fake-host integration | IT-012 + SEC-010 in the owning probe suite | PASS |
| T12 | Assisted coordinator and probe boundaries | unit + fake-host integration | IT-013 + SEC-011 in canonical executor/probe suites | PASS |

## Implementation Batch Recommendation

Phase 2 contains five tasks, within one task-budgeted batch. The coordinator should dispatch one
implementer for Slice E and one implementer for Slice F concurrently, then dispatch one implementer
for Slice G after T7 and T9 are green and committed. No phase split or front/back split is needed.

Phase 3 contains two resumed remediation tasks: T11 follows T10 after the independent Verifier
reported proof gaps, and T12 closes the final Deep Review defects. They own the probe, assisted
executor boundary, and their runnable checks, and each closes with the Quick gate.
