# Parallel Slice Executor Tasks

## Execution Protocol

Implement these tasks with `tlc-spec-driven`. Keep tasks sequential inside each slice, update this
file before every atomic commit, and close every code-changing slice with a fresh Technical Verifier.
The feature's frozen mode is authoritative; absent a capable executor, use the existing serial path.

**Design:** `.specs/features/parallel-slice-executor/design.md`
**Status:** In Progress

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
| Full | Autonomous integration or feature close | `npm_config_offline=true npm run test:all`; all TLC/state/index validators; `git diff --check` |
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

**Status:** complete
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

**Status:** complete
**Slice:** B
**Resources:** none
**Observable behaviour:** The coordinator creates a validated child Git worktree before resource preparation; the Orca adapter attaches its worker to that existing checkout, validates every receipt, blocks on correlated events, follows up the same terminal, and releases only accepted owned workers.
**Where:** `.agents/skills/autonomous/scripts/orca_adapter.py`
**Depends on:** T2
**Requirement:** EXE-06–EXE-11, SEC-005, SEC-006
**Reuses:** T1 subprocess/path primitives and Orca `orchestration.contract.v1` commands.
**Tools:** Skills `ponytail` and `orca-cli`; live Orca guide is authoritative.
**Done when:**

- [ ] Recording-CLI assertions prove validated Git worktree creation precedes resource preparation and worker attachment.
- [ ] Run/task/dispatch/terminal/worktree/head/idempotency fields are all correlated before state changes.
- [ ] `worker_done`, clean waiter, dependency follow-up, timeout, escalation, failure, mismatch, and duplicate receipts have exact outcomes.
- [ ] Logs/state expose no worker transcript body or environment value.
- [ ] `python3 tools/test_orca_adapter.py` reports all assigned cases passing with zero failures.

**Tests:** IT-002–IT-004, SEC-005, SEC-006 in `tools/test_orca_adapter.py`
**Gate:** Quick. Commit `feat(workflow): adapt orca slice workers`.

### T4: Reconcile Git checkpoints and verified slices

**Status:** complete
**Slice:** C
**Resources:** none
**Observable behaviour:** A clean dependent lane rebases onto one exact producer checkpoint, restores itself on conflict, invalidates changed-head evidence, and merges verified slices deterministically without rewriting their commits.
**Where:** `.agents/skills/autonomous/scripts/git_adapter.py`
**Depends on:** T2
**Requirement:** EXE-12–EXE-17
**Reuses:** T1 subprocess/path primitives and existing branching/evidence rules.
**Tools:** Skill `ponytail`; Git CLI only.
**Done when:**

- [x] Exact-commit sync and ancestor no-op receipts include pre/post HEAD and changed paths.
- [x] Rebase/merge conflicts abort and restore the original clean state; no side is auto-selected.
- [x] Incomparable multiple checkpoints return serial recovery.
- [x] Changed HEAD invalidates affected gate, Technical Verifier, and deep-review receipts.
- [x] Verified slice commits survive deterministic feature-branch integration.
- [x] `python3 tools/test_git_adapter.py` reports all assigned cases passing with zero failures.

**Tests:** UT-004–UT-006 in `tools/test_git_adapter.py` (7 cases)
**Gate:** Quick. Commit `feat(workflow): reconcile slice checkpoints`.

### T5: Freeze the consumer resource provider

**Status:** complete
**Slice:** D
**Resources:** none
**Observable behaviour:** Workflow resolution freezes an optional safe repository-relative provider executable and preserves an existing valid snapshot when provider validation fails.
**Where:** `.agents/skills/workflow-config/scripts/workflow_config.py`
**Depends on:** T2
**Requirement:** EXE-19–EXE-22, SEC-003, SEC-004
**Reuses:** Existing strict TOML parser, atomic snapshot replacement, and resume semantics.
**Tools:** Skill `ponytail`; no documentation lookup.
**Done when:**

- [x] Absent provider freezes as null without changing disabled/default behavior.
- [x] Valid executable freezes as a normalized repository-relative path.
- [x] Absolute, external, directory, non-executable, and unsafe-symlink paths fail before snapshot replacement.
- [x] `python3 tools/test_workflow_config.py` reports all existing and IT-005 cases passing with zero failures.

**Tests:** IT-005 in `tools/test_workflow_config.py` (18 cases)
**Gate:** Quick. Commit `feat(config): freeze parallel resource provider`.

### T6: Plan explicit lane resources

**Status:** complete
**Slice:** D
**Resources:** none
**Observable behaviour:** The deterministic plan carries normalized resource names, permits explicit `none`, and serializes missing or ambiguous resource metadata before the executor can act.
**Where:** `.agents/skills/workflow-config/scripts/parallel_plan.py`
**Depends on:** T5
**Requirement:** EXE-18–EXE-21
**Reuses:** Existing task parser, fallback reasons, and byte-deterministic JSON projection.
**Tools:** Skill `ponytail`; no documentation lookup.
**Done when:**

- [x] Each lane contains a stable `resources` array; `none` becomes an empty array.
- [x] Missing, mixed-`none`, duplicated, or malformed resource names produce exact serial reasons.
- [x] Existing mode, dependency, waiting, and conflict behavior remains green.
- [x] `python3 tools/test_parallel_plan.py` reports all existing and IT-006 cases passing with zero failures.

**Tests:** IT-006 in `tools/test_parallel_plan.py` (16 cases)
**Gate:** Quick. Commit `feat(workflow): plan isolated lane resources`.

### T7: Bind autonomous execution and prove Orca concurrency

**Status:** complete (implementation); E2E-001 is owned by the feature-closing fresh-QA step.
**Slice:** D
**Resources:** none
**Observable behaviour:** Autonomous invokes the deterministic executor when its frozen mode and capabilities allow, otherwise runs serially; a real disposable Orca run proves two isolated worktrees active concurrently and cleans only owned workers.
**Where:** `.agents/skills/autonomous/references/parallelization.md`
**Depends on:** T3, T4, T6
**Requirement:** EXE-01–EXE-22
**Reuses:** Existing autonomous entry gate, review stages, executor CLI, and Orca QA adapter.
**Tools:** Skills `ponytail`, `writing-skills`, `orca-cli`, `qa-plan`, and `qa-execute` as their stages fire.
**Done when:**

- [x] Policy names the exact executor commands, capability gate, event lifecycle, checkpoint/merge split, evidence invalidation, resource provider, and serial recovery.
- [x] Shared contract tests prove TLC tasks, gates, Verifier, grouped deep-review, final QA, and full gate are unchanged.
- [x] Writing-skills audit records every checklist item Pass.
- [x] T7 hands E2E-001 to the feature-closing fresh-QA step outside this implementation task; the real Orca journey remains untested until that step.
- [x] Full gate and strict feature/state/index validators pass for authored implementation; feature-level state remains incomplete until E2E-001 QA.

**Tests:** IT-007 in `tools/shared/tests/autonomous-parallelization.test.ts` and executor capability tests; E2E-001 handoff in `qa-pilot.md` (untested)
**Gate:** Full. Commit `feat(workflow): execute parallel slices autonomously`.

### T7R1: Make the parallel pilot executable

**Remediation status:** complete
**Slice:** D
**Remediation resources:** none
**Observable behaviour:** The E2E-001 handoff creates a disposable safe-mode fixture with two explicit `Resources: none` lanes, proves both lanes through the public planner before Orca mutation, and provides exact cleanup.
**Where:** `tools/qa_parallel_pilot.py`
**Remediation depends on:** T7
**Remediation requirements:** E2E-001, EXE-06, EXE-18
**Remediation done when:**

- [x] Setup creates a temporary Git source HEAD, frozen `safe` snapshot, and two pending independent lanes without touching product files.
- [x] Dry-run asserts exactly two ready resource-free lanes and rejects disabled/completed feature targets.
- [x] Handoff runs public planner/executor against `parallel-pilot` and defines explicit cleanup; the real Orca start remains fresh-QA-only.
- [x] Canonical QA contract test covers setup, dry-run, cleanup, and handoff target identity.

**Remediation tests:** `tools/test_qa_parallel_pilot.py`, shared IT-007, full Python discovery.
**Remediation gate:** Directed QA fixture, `npm run test:all`, strict validators/index, compile, diff check, adequacy review.
**Remediation commit:** `fix(workflow): make parallel pilot executable`.

### T7R2: Harden parallel pilot source and cleanup lifecycle

**Remediation status:** complete
**Slice:** D
**Remediation resources:** none
**Observable behaviour:** The pilot dry-run correlates frozen source HEAD to the disposable repository and cleanup is idempotent only for the attested fixture root.
**Where:** `tools/qa_parallel_pilot.py`
**Remediation depends on:** T7R1
**Remediation requirements:** E2E-001, EXE-06, SEC-008
**Remediation done when:**

- [x] Dry-run rejects nonexistent or mismatched frozen `git_head` before any executor/Orca effect and returns the exact repository/source head for two lanes.
- [x] First cleanup records a bounded attestation; repeated cleanup of the same root returns an explicit idempotent success.
- [x] Unmarked/arbitrary roots are rejected and never removed; production workflow remains untouched.
- [x] Canonical QA tests kill both verifier mutants.

**Remediation tests:** `tools/test_qa_parallel_pilot.py`, full Python discovery, shared IT-007.
**Remediation gate:** Harness/directed suites, `npm run test:all`, strict validators/index, compile, diff check, adequacy review.
**Remediation commit:** `fix(workflow): harden parallel pilot lifecycle`.

### T7R3: Attest parallel pilot cleanup ownership

**Remediation status:** complete
**Slice:** D
**Remediation resources:** none
**Observable behaviour:** Pilot cleanup removes only the exact attested worktree paths and preserves unowned sibling contents with an honest residual result.
**Where:** `tools/qa_parallel_pilot.py`
**Remediation depends on:** T7R2
**Remediation requirements:** E2E-001, SEC-008
**Remediation done when:**

- [x] Setup persists an ownership attestation binding fixture root, source HEAD, feature, and exact worktree paths.
- [x] Cleanup removes only legitimate owned Git worktrees, never recursively discovers/deletes sibling paths, and reports residual unowned content.
- [x] Sentinel-survival and legitimate-owned-removal tests pass; prior HEAD/retry behavior remains intact.

**Remediation tests:** `tools/test_qa_parallel_pilot.py`, full discovery and directed regressions.
**Remediation gate:** Harness/full gate, strict validators/index, compile, diff check, adequacy review.
**Remediation commit:** `fix(workflow): attest parallel pilot cleanup`.

### T7R4: Bind parallel pilot cleanup receipts

**Remediation status:** complete
**Slice:** D
**Remediation resources:** none
**Observable behaviour:** Pilot cleanup independently correlates the fixture repository HEAD and frozen workflow before destructive effects, and restart retries preserve and re-evaluate exact residual evidence until the bounded sibling is empty.
**Where:** `tools/qa_parallel_pilot.py`
**Remediation depends on:** T7R3
**Remediation requirements:** E2E-001, SEC-008
**Remediation done when:**

- [x] Source-head-only manifest tampering is rejected before any worktree or fixture deletion.
- [x] Cleanup persists an external tombstone with source/workflow correlation, exact residual paths, and a residual status before removing the fixture root.
- [x] Restarted cleanup remains `cleaned: false` while an unowned sentinel remains, then returns idempotent success only after all bounded residuals are gone.
- [x] Exact-path ownership, frozen-head dry-run correlation, and production disabled workflow remain intact.

**Remediation tests:** `tools/test_qa_parallel_pilot.py`, full Python discovery, shared IT-007, and directed executor regressions.
**Remediation gate:** Harness/full gate, strict validators/index, compile, diff check, adequacy review.
**Remediation commit:** `fix(workflow): bind parallel pilot cleanup`.

### T7R5: Prove parallel pilot ownership rejection

**Remediation status:** complete
**Slice:** D
**Remediation resources:** none
**Observable behaviour:** Public cleanup rejects every non-HEAD ownership attestation tamper before changing the fixture, Git worktree, sentinel, or cleanup tombstone.
**Where:** `tools/test_qa_parallel_pilot.py`
**Remediation depends on:** T7R4
**Remediation requirements:** E2E-001, SEC-008
**Remediation done when:**

- [x] Root and feature tampering are rejected before any effect.
- [x] Missing, extra, duplicate, outside, and reordered worktree lists are rejected through the cleanup CLI/process boundary.
- [x] Every adverse case proves the legitimate worktree and unowned sentinel survive and no cleanup tombstone is written.
- [x] Existing source-head, residual retry, exact cleanup, dry-run, and arbitrary-root coverage remains green.

**Remediation tests:** `tools/test_qa_parallel_pilot.py` ownership tamper matrix and full Python discovery.
**Remediation gate:** Harness/full gate, strict validators/index, compile, diff check, adequacy review.
**Remediation commit:** `test(workflow): prove parallel pilot ownership`.

## Review Remediation

The human rejected a slice-global cap because the prior rounds closed different blockers. T2R4
corrects the durable convergence rule before T2R5 resumes the remaining IT-001 fingerprint. T3-T7
remain blocked only until Slice A passes its Technical Verifier.

### Grouped C-D round 1: close parallel executor review blockers

**Remediation status:** complete
**Slice:** C-D review group
**Remediation resources:** none
**Observable behaviour:** Git, checkpoint, integration, planner, pilot, and handoff boundaries fail closed, persist exact recovery receipts, and leave the real Orca journey to feature-closing fresh QA.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`, `.agents/skills/autonomous/scripts/git_adapter.py`, `.agents/skills/workflow-config/scripts/parallel_plan.py`
**Remediation requirements:** EXE-06–EXE-17, SEC-003, SEC-004, E2E-001
**Remediation done when:**

- [x] External Git worktrees, malformed checkpoints, undeclared paths, and rejected checkpoint worktrees serialize before cross-root effects.
- [x] Accepted worker completion persists the owned producer HEAD; complete verified lanes integrate once in deterministic order.
- [x] The pilot freezes committed task metadata and documents bounded status/resume/ack/release cleanup owned by fresh QA.
- [x] STATE Handoff, T7 ownership, design/DX, memory, validation handoff, and writing audit reflect the post-review boundary.

**Remediation tests:** Git adapter, planner, executor, QA pilot, IT-007, and full repository discovery.
**Remediation gate:** Directed suites, `npm run test:all`, strict spec/tasks, AD index, compile, diff, and check_commit.
**Remediation commit:** `fix(workflow): close parallel executor review blockers`.

### T2R4: Count verification attempts per blocker fingerprint

**Remediation status:** complete
**Slice:** A
**Remediation resources:** none
**Observable behaviour:** Technical Verifier remediation counts are keyed by requirement, root cause, and failure path; distinct blockers start at one and the same blocker halts only after its third failed remediation.
**Where:** `docs/guidelines/REVIEW-ROUNDS.md`
**Remediation depends on:** T2R3
**Remediation requirements:** EXE-23, EXE-24, EXE-25
**Remediation tests:** IT-008 in `tools/shared/tests/qa-skills.test.ts` plus existing shared workflow tests.
**Remediation gate:** Targeted Vitest, full `npm_config_offline=true npm run test:all`, strict spec/tasks validators, AD index, writing-skills audit, and `git diff --check`.
**Remediation commit:** `fix(workflow): count repeated verification blockers`.

### T2R5: Prove safe-mode CLI resume

**Remediation status:** complete
**Slice:** A
**Remediation resources:** none
**Observable behaviour:** Public CLI `resume` loads persisted pending safe-mode state, constructs the selected adapter, reconciles the receipt without a duplicate effect, and emits its own correlated JSON result.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Remediation depends on:** T2R4
**Remediation requirements:** EXE-03, EXE-04, EXE-05
**Remediation tests:** IT-001 safe-mode resume in `tools/test_parallel_executor.py`; the adapter-removal mutant must die.
**Remediation gate:** Executor tests, strict spec/tasks validators, AD index, `git diff --check`, and fresh Technical Verifier.
**Remediation commit:** `fix(workflow): prove safe resume reconciliation`.

### T3R1: Consume live Orca deliveries and close coordinator lifecycle gaps

**Remediation status:** complete
**Slice:** B
**Remediation resources:** none
**Observable behaviour:** Public resume consumes Run-scoped Delivery records, reads and validates the separate worker output receipt before release, preserves exact timeout/waiting/escalation states, and rejects incomplete or uncorrelated worker receipts before any destructive cleanup.
**Where:** `.agents/skills/autonomous/scripts/orca_adapter.py`
**Remediation depends on:** T3
**Remediation requirements:** EXE-07–EXE-11, SEC-005, SEC-006
**Remediation tests:** IT-002–IT-004 and SEC-005–SEC-006 in `tools/test_orca_adapter.py`; public resume lifecycle coverage in `tools/test_parallel_executor.py`.
**Remediation gate:** Adapter and executor suites, strict spec/tasks validators, AD index, `git diff --check`, compile, and fresh Technical Verifier.
**Remediation commit:** `fix(workflow): consume live orca deliveries`.

### T3R2: Harden Orca waiter boundaries and strict receipt recovery

**Remediation status:** complete
**Slice:** B
**Remediation resources:** none
**Observable behaviour:** Run Delivery payloads are redacted before persistence, clean waiters end and survive restart before same-terminal dependency follow-up, sparse worker receipts serialize before running, and missing or duplicate deliveries never release or replace workers.
**Where:** `.agents/skills/autonomous/scripts/orca_adapter.py`
**Remediation depends on:** T3R1
**Remediation requirements:** EXE-07–EXE-11, SEC-005, SEC-006
**Remediation tests:** IT-002–IT-004 and SEC-005–SEC-006 in `tools/test_orca_adapter.py`; public waiter/receipt/recovery coverage in `tools/test_parallel_executor.py`.
**Remediation gate:** Adapter and executor suites, strict spec/tasks validators, AD index, `git diff --check`, compile, and fresh Technical Verifier.
**Remediation commit:** `fix(workflow): harden orca waiter boundaries`.

### T2R1: Harden resume, disabled-mode, isolation, and lease recovery

**Remediation status:** complete
**Slice:** A
**Remediation resources:** none
**Observable behaviour:** Slice A rejects unsafe or unreconcilable effects before dispatch, reconciles crash-window receipts, preserves task order, and performs fail-closed exactly-once resource cleanup.
**Remediation depends on:** T2
**Remediation requirements:** EXE-01–EXE-05, EXE-18–EXE-22, SEC-001, SEC-004, SEC-007, SEC-008
**Remediation done when:**

- [x] Regression tests discriminate every blocking gap in `validation.md`, including pending receipt recovery and pre-effect persistence.
- [x] Disabled mode avoids planner, Git, resource, and adapter effects; duplicate same-slice tasks serialize before dispatch.
- [x] Resource requests and receipts are correlated, resource failures fall back serially, and terminal/halted/abandoned workers release exactly once.
- [x] Scoped threat model exists for the S11 isolation surface.

**Remediation tests:** `python3 tools/test_parallel_executor.py` (21 cases), including T2R1 recovery/resource/path/order cases.
**Remediation gate:** Quick — owning test suite, `validate_tasks.py`, and `git diff --check`.
**Remediation commit:** `fix(workflow): harden parallel executor recovery`.

### T2R2: Close executor crash windows and pre-effect worktree isolation

**Remediation status:** complete
**Slice:** A
**Remediation resources:** none
**Observable behaviour:** Every external action observes a persisted pending receipt; pending acquire, worker, and release receipts reconcile without duplicate effects; same-slice tasks advance in declared order; and the core creates a validated Git worktree before adapter worker attachment.
**Remediation depends on:** T2R1
**Remediation requirements:** EXE-02–EXE-04, EXE-06, EXE-07, EXE-19, SEC-004
**Remediation done when:**

- [x] Acquire, worker, and release effects assert persisted pending intent and pending crash receipts reconcile without repeating the effect.
- [x] Same-slice lanes expose one active task, then advance the next task only after the prior checkpoint completes; acquire precedes worker attachment.
- [x] A deterministic destination is bounded before any writer, Git creates the checkout, and adapters attach workers to an existing worktree.
- [x] The provider-neutral contract is updated in spec/design/DX/tasks; `validation.md` FAIL and generated lessons remain included as evidence.

**Remediation tests:** `python3 tools/test_parallel_executor.py` (25 cases), including T2R2 crash/order/destination cases.
**Remediation gate:** Quick plus strict spec/tasks/index/diff gates.
**Remediation commit:** `fix(workflow): close executor crash windows`.

### T2R3: Close executor verification gaps

**Remediation status:** complete
**Slice:** A
**Remediation resources:** none
**Observable behaviour:** Pending worker receipts reconcile without a second worker effect; recovered leases use the same strict correlation/redaction validator as fresh leases; the core owns all Git worktree creation; and the public `resume` verb emits an observable transition result.
**Remediation depends on:** T2R2
**Remediation requirements:** EXE-04, EXE-05, EXE-20, IT-001, SEC-001
**Remediation done when:**

- [x] A real pending worker action is reconciled and no new `start_worker` effect occurs.
- [x] Recovered acquire receipts require the current idempotency key, resource names, prepared-worktree flag, unique lease ID, and redacted environment before acceptance; nested state receipts are rejected before effects.
- [x] The adapter worktree-creator compatibility path is removed; only the core Git creator and existing-worktree worker attachment remain.
- [x] CLI `resume` is exercised end-to-end and emits its own command/transition result rather than status output.

**Remediation tests:** `python3 tools/test_parallel_executor.py` (26 cases), including T2R3 pending-worker, nested-receipt, contract, and CLI-resume cases.
**Remediation gate:** Executor tests, strict spec/tasks, AD index check, diff check, and compile.
**Remediation commit:** `fix(workflow): close executor verification gaps`.

### TDR1: Close grouped deep-review blockers for Slices A-B

**Remediation status:** complete
**Slice:** A-B review group
**Remediation resources:** none
**Observable behaviour:** Executor and Orca boundaries reject uncorrelated or secret-bearing receipts, lifecycle delivery/release effects survive restart exactly once, public wait controls work, blocker convergence persists deterministically, and durable contracts report only completed slice scope.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Remediation depends on:** T3R2
**Remediation requirements:** EXE-01–EXE-11, EXE-23–EXE-25, SEC-001–SEC-006
**Remediation done when:**

- [x] Worker, worktree, and follow-up receipts use complete provider-neutral correlation; Orca run/task ambiguity and unknown/missing fields fail closed.
- [x] Credential-shaped keys are redacted recursively before any receipt, delivery, output, log, or state persistence.
- [x] Delivery acceptance, acknowledgement, worker release, and resource release persist/reconcile exactly once across restart.
- [x] `resume --wait-seconds` enforces `1..3600`, reaches Orca `--timeout-ms`, and adapter selection/non-default timeout are discriminated.
- [x] A disposable repository test executes the unpatched `git worktree add` path and cleans it through Git.
- [x] A stdlib convergence CLI persists blocker fingerprints/counts, preserves reopened identity, and halts only on the third failed remediation of that fingerprint.
- [x] EXE-18–EXE-22 remain Planned until Slice D; design/DX distinguish current A-B state from future C/D fields and provider-prepared environment.
- [x] Validation records the grouped-review invalidation, review-count wording counts Verifier failure regardless of green gate, and one repository full-gate command includes Vitest plus every Python suite.

**Remediation tests:** Adapter/executor suites, real Git fixture, convergence script suite, shared workflow contracts, and full repository gate.
**Remediation gate:** `npm run test:all`; strict spec/tasks/state/index validators; Python compile; `git diff --check`; deep-review incremental round 2.
**Remediation commit:** `fix(workflow): close executor group review blockers`.

### TDR2: Close final grouped deep-review defects

**Remediation status:** complete
**Slice:** A-B review group
**Remediation resources:** none
**Observable behaviour:** Final-round remediation accepts the supported nested Orca envelope, redacts the whole persisted delivery, persists and reconciles delivery acknowledgement/release correctly, rejects unsafe convergence paths/aliases, and makes the declared full gate run every Python suite.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Remediation depends on:** TDR1
**Remediation requirements:** EXE-03, EXE-04, EXE-07–EXE-11, EXE-23–EXE-25, SEC-001, SEC-005, SEC-006
**Remediation done when:**

- [x] Nested worker envelopes normalize into the strict schema without retaining the envelope; whole Delivery projection/redaction leaves no top-level or nested credential value.
- [x] Ack requires a positively correlated receipt, has a persisted pending action before the call, and restart consumes the persisted completion/delivery/ack shape without replay.
- [x] Worker release requires a correlated receipt before completing the lane.
- [x] Convergence state rejects traversal-capable feature names and accepts `previous_fingerprint` only when that stored fingerprint exists and belongs to the same requirement.
- [x] Design/threat-model fields match persisted lifecycle state and all final-round negative paths have failing-capable tests.
- [x] `npm run test:python` discovers and executes every `tools/test_*.py`; `npm run test:all` remains the declared full gate.

**Remediation tests:** 20 adapter, 32 executor, 6 convergence, every discovered Python suite, shared contracts, and every final-round reproduction.
**Remediation gate:** `npm run test:all`; strict spec/tasks/state/index validators; Python compile; `git diff --check`; no deep-review round 3.
**Remediation commit:** `fix(workflow): close final executor review defects`.

### T4R1: Enforce checkpoint revalidation at the coordinator boundary

**Remediation status:** complete
**Slice:** C
**Remediation resources:** none
**Observable behaviour:** A changed checkpoint receipt is persisted and consumed by the coordinator before worker or follow-up effects; the lane remains gate-required until a passing gate receipt matches its exact current head and identity.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Remediation depends on:** T4
**Remediation requirements:** EXE-15
**Remediation done when:**

- [x] `sync_after` resolves exact producer `current_head` receipts and persists the sync action before the Git effect.
- [x] Changed sync receipts persist `current_head`, paths, and all three evidence invalidations, then block start/follow-up at `gate_required`.
- [x] Restart reuses the accepted sync receipt without resync; invalidated lanes cannot advance without a gate receipt.
- [x] Gate acceptance requires `passed=true`, exact `current_head`, lane, and gate identity and removes only `gate` invalidation.
- [x] Executor integration tests kill the mutator that ignores coordinator invalidation.

**Remediation tests:** `tools/test_parallel_executor.py` (34 cases) plus Git/Orca regressions.
**Remediation gate:** Git adapter, executor, and Orca suites; strict spec/tasks/index; compile; diff check; adequacy review.
**Remediation commit:** `fix(workflow): enforce checkpoint revalidation`.

### T4R2: Gate waiting-lane checkpoint follow-up

**Remediation status:** complete
**Slice:** C
**Remediation resources:** none
**Observable behaviour:** A persisted waiting lane consumes its changed checkpoint before dependency follow-up, remains gate-required across restart, and sends exactly one same-terminal follow-up only after a correlated gate receipt.
**Where:** `.agents/skills/autonomous/scripts/parallel_execute.py`
**Remediation depends on:** T4R1
**Remediation requirements:** EXE-15
**Remediation done when:**

- [x] Waiting/dependency resume consumes `sync_after` before `wait_events` or `follow_up`.
- [x] Changed checkpoint persists `gate_required`, `current_head`, and all evidence invalidations; no adapter follow-up/start occurs before gate acceptance.
- [x] Gate acceptance restores the persisted waiting state and exact terminal identity; follow-up occurs once and restart does not duplicate it.
- [x] The surviving waiting-lane invalidation mutant is killed by the canonical executor test.

**Remediation tests:** `tools/test_parallel_executor.py` (35 cases), Git 7, Orca 20.
**Remediation gate:** Git/executor/Orca regressions; strict spec/tasks/index; compile; diff check; adequacy review.
**Remediation commit:** `fix(workflow): gate waiting checkpoint follow-up`.

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
