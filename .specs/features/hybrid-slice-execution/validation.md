# Hybrid Slice Execution Validation

**Date:** 2026-08-29
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `2ab4cecc2d9daede27015c7edec543800e7bd763..552695302db4c45cc6adc1c82eea49d80c8dbbad`
**Verifier:** independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

All 14 numbered task records, both final-review remediation batches, QA Plan, QA Execute, and its
fresh retest are complete. The six slice reports are PASS, the three QA charters have terminal
verdicts, and the integrated tree has no unresolved blocker.

## Spec-Anchored Acceptance Criteria

Evidence-or-zero was re-derived from executable assertions. One row exists for every requirement.

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| HSE-01 | Adoption installs only `workflow-spec-driven` | `scripts/test_adopt.py:405` - byte-identical new authority and old paths absent at lines 422-434 | PASS |
| HSE-02 | Attribution and CC BY 4.0 notice | `tools/shared/tests/qa-skills.test.ts:181` - notice contains author, license, and source | PASS |
| HSE-03 | Slice packet contains only bounded slice context | `tools/test_workflow_spec_driven.py:102` - every allowed section is asserted; unknown fields fail at line 94 | PASS |
| HSE-04 | Conditional loading; no phase batches/final-only Verifier | `tools/shared/tests/qa-skills.test.ts:186` - forbidden wording absent and per-slice validation present through line 197 | PASS |
| HSE-05 | Exact 3,072/10,240-byte limits stop output | `tools/test_workflow_spec_driven.py:115` - boundaries and oversize failures asserted through line 150 | PASS |
| HSE-06 | Telemetry contains counts, not content | `tools/test_workflow_spec_driven.py:152` - marker absent and exact component totals asserted through line 170 | PASS |
| HSE-07 | Config and snapshot schema version 3 | `tools/test_workflow_config.py:1034` - snapshot version equals 3 | PASS |
| HSE-08 | Mode is only assisted/disabled; assisted default | `tools/test_workflow_config.py:149` - default v3 parallelization exact; invalid mode error at line 195 | PASS |
| HSE-09 | Cap is auto or integer >=1; auto default | `tools/test_workflow_config.py:151` - exact default policy; invalid inputs preserve state at lines 606-610 | PASS |
| HSE-10 | Frozen snapshot stores complete policy/routes/cadence | `tools/test_workflow_config.py:113` - parallelization, cadence, and role routes asserted through line 119 | PASS |
| HSE-11 | Old configs/snapshots reject before effects | `tools/test_parallel_plan.py:475` - exact version errors; CLI emits no plan at lines 484-486 | PASS |
| HSE-12 | Disabled mode is serial with no writer worktree | `tools/test_parallel_executor.py:2456` - integration receipt and worker-only effects asserted through line 2486 | PASS |
| HSE-13 | No ready slice means no writer and exact blockers | `tools/test_parallel_plan.py:293` - blocked decision, empty lanes, and dependency reasons asserted through line 311 | PASS |
| HSE-14 | One ready slice uses integration checkout | `tools/test_parallel_plan.py:207` - serial-integration decision; `tools/test_parallel_executor.py:2462` asserts integration path | PASS |
| HSE-15 | Two compatible writers start at cap two | `tools/test_parallel_executor.py:2310` - selected tasks equal T1/T2 and cap equals 2 | PASS |
| HSE-16 | Healthy settle admits one lane up to auto ceiling four | `tools/test_parallel_executor.py:2321` - one extra lane and cap 3; repeated admissions at lines 2368-2375 | PASS |
| HSE-17 | Missing/bad health denies growth and preserves active lanes | `tools/test_machine_health.py:44` - invalid evidence denies; reader failure leaves cap 2 at `tools/test_parallel_executor.py:2392` | PASS |
| HSE-18 | Explicit cap is respected and still health-gated | `tools/test_parallel_executor.py:2349` - explicit cap 5 grows exactly one lane per healthy call; cap 1 re-derived at lines 2552-2554 | PASS |
| HSE-19 | Freed lane takes next compatible ready slice | `tools/test_parallel_executor.py:2396` - conflicting T2 skipped and T3 selected | PASS |
| HSE-20 | Only concurrent implementers receive worktrees | `tools/test_parallel_plan.py:224` - selected writers have worktrees and role map excludes read-only roles; serial path has only worker effect at `tools/test_parallel_executor.py:2485` | PASS |
| HSE-21 | Heavy gates acquire/release correlated provider leases | `tools/test_parallel_executor.py:2444` - invalid claim has zero acquire; valid exclusive claim acquires/releases once through line 2451 | PASS |
| HSE-22 | Complete packet persisted; Orca gets pointer | `tools/test_orca_assisted_probe.py:107` - pointer state and packet path asserted through line 113 | PASS |
| HSE-23 | Terminal text excludes packet body | `tools/test_orca_assisted_probe.py:111` - one send, marker absent, pointer path present | PASS |
| HSE-24 | Every logical mutation is issued at most once | `tools/test_orca_assisted_probe.py:161` - attempts equal 1 and all Orca mutation counts equal 1 through line 176 | PASS |
| HSE-25 | Transient response reconciles with reads, no mutation retry | `tools/test_orca_assisted_probe.py:395` - unknown settles with mutate=1/read=1; restart ledgers remain one at lines 706-733 | PASS |
| HSE-26 | Worker effects require full correlation | `tools/test_orca_assisted_probe.py:403` - each identity-field mutation rejects or the matching state settles through line 426 | PASS |
| HSE-27 | Malformed/reused/contradictory evidence fails closed | `tools/test_orca_assisted_probe.py:431` - public cleanup contradiction table rejects; no destructive call at line 463 | PASS |
| HSE-28 | Cleanup removes only proved ownership and reaches residue zero | `tools/test_orca_assisted_probe.py:308` - cleaned status/residue empty and physical stop/release/Git counts exact through line 324 | PASS |
| HSE-29 | Probe import performs zero effects | `scripts/test_adopt.py:439` - installed import exits 0 and fake Orca call file stays empty through line 460 | PASS |
| HSE-30 | Slice worker runs tasks sequentially with gate/commit | `tools/shared/tests/autonomous-parallelization.test.ts:88` - sequential tasks, scoped gate, and atomic commit asserted through line 95 | PASS |
| HSE-31 | Fresh verifier precedes dependent consumption | `tools/shared/tests/autonomous-parallelization.test.ts:102` - fresh identity/private checkpoint route asserted; stage order at lines 125-161 | PASS |
| HSE-32 | Integrated group routes to fresh Deep Reviewer | `tools/shared/tests/autonomous-parallelization.test.ts:112` - fresh reviewer receives integrated range, never private tree | PASS |
| HSE-33 | Final implementation review is followed by fresh QA Plan and QA Execute | `tools/shared/tests/autonomous-parallelization.test.ts:106` proves routing; `docs/qa/reports/2026-08-29-hybrid-slice-execution.md:3` records the fresh QA Execute and retest after the three dated QA Plan charters | PASS |
| HSE-34 | Last implementer writes handoff only | `tools/shared/tests/autonomous-parallelization.test.ts:161` - handoff route exact; packet excludes final QA at lines 93-95 | PASS |
| HSE-35 | Adoption installs complete workflow byte-identically | `scripts/test_adopt.py:410` - every owned component exists and bytes match through line 434 | PASS |
| HSE-36 | Re-adoption updates owned files, preserves consumer files | `scripts/test_adopt.py:377` - stale owned copies repaired while config/profile bytes remain unchanged through line 400 | PASS |
| HSE-37 | Canonical offline gate covers all fake boundaries without live Orca | `scripts/test_adopt.py:439` - call-counting fake remains empty; full gate result recorded below | PASS |
| HSE-38 | Fake/adoption journeys have current evidence; live Orca stays blocked | `scripts/test_adopt.py:536` - lines 541-546 require current adoption/fallback PASS and live-Orca `blocked-verify`; the scenario registry records 6 PASS and 2 blocked entries | PASS |
| HSE-39 | Paths/executables are owned, contained, non-symlinked, fixed argv | `tools/test_workflow_spec_driven.py:193` - escape/absolute/symlink table rejects before IO through line 224; adoption symlink guard starts at `scripts/test_adopt.py:465` | PASS |
| HSE-40 | Invalid untrusted structured input rejects before next effect | `tools/test_workflow_config.py:658` - invalid config exits 2 with no config/runtime/outside mutations through line 663; forged lease releases zero at `tools/test_parallel_executor.py:2607` | PASS |
| HSE-41 | Persisted state retains immutable reconciliation identities | `tools/test_orca_assisted_probe.py:403` - every identity field is validated; attempt/effect identity persisted at lines 655-659 | PASS |
| HSE-42 | Diagnostics redact secrets, bodies, terminal text, home paths | `tools/test_workflow_spec_driven.py:172` - secret and home markers absent through line 191; `tools/test_orca_assisted_probe.py:748` rejects six terminal/provider/body fields through line 756 | PASS |
| HSE-43 | Incomplete cleanup proof stops before destructive step | `tools/test_orca_assisted_probe.py:466` - unsafe-state table asserts zero stop/rm/branch/switch calls at line 504 | PASS |
| HSE-44 | Overlapping write paths serialize and report conflict | `tools/test_parallel_plan.py:281` - T1/T3 selected and exact T1/T2 path conflict reported at line 283 | PASS |
| HSE-45 | Moved checkpoint stays parked until sync/reverify | `tools/test_parallel_executor.py:1661` - evidence invalidated and worker withheld; resume only after accepted proof through line 1690 | PASS |
| HSE-46 | Dirty integration checkout causes zero dispatch effects | `tools/test_parallel_plan.py:293` - dirty baseline yields blocked decision and empty lanes | PASS |
| HSE-47 | Reused handle/path identity rejects destructive cleanup | `tools/test_orca_assisted_probe.py:403` - identity-field mismatches fail; unsafe cleanup has zero destructive effects at line 504 | PASS |
| HSE-48 | Failed heavy-gate lease does not block unrelated light work | `tools/test_parallel_executor.py:2445` - first lease granted, competing lease returns None, acquire count remains 1 | PASS |
| HSE-49 | Authorized resume appends next generation | `tools/test_review_convergence.py:147` - generation 2 and exact authorization asserted through line 154 | PASS |
| HSE-50 | Resume preserves generation 1/cumulative count | `tools/test_review_convergence.py:148` - cumulative count stays 3 and generation 1 bytes match at line 151 | PASS |
| HSE-51 | Halt bypasses reject before state change | `tools/test_review_convergence.py:179` - rejected attempts preserve original bytes; inconsistent reset preserved at line 190 | PASS |
| HSE-52 | Only fresh independent green PASS closes generation | `tools/test_review_convergence.py:202` - failure/red gate stay open; qualifying PASS closes while generation 1 stays halted through line 209 | PASS |
| HSE-53 | Atomic in-flight ledger precedes each sink | `tools/test_orca_assisted_probe.py:655` - sink observes in-flight attempt 1; persistence failure leaves bytes unchanged at line 675 | PASS |
| HSE-54 | Dispatch/cleanup have one mutation issuer | `tools/test_orca_assisted_probe.py:610` - AST guard accepts `MutationRunner.issue` and rejects alternate Git/private sinks through line 636 | PASS |
| HSE-55 | Existing in-flight/unknown state performs reads only | `tools/test_orca_assisted_probe.py:706` - replay leaves all physical ledgers at one and counts only two observations through line 733 | PASS |
| HSE-56 | Physical ledgers prove one Git/provider/Orca mutation and pointer only | `tools/test_orca_assisted_probe.py:696` - exact physical counts and body absence asserted through line 707 | PASS |
| HSE-57 | Pre-sink persistence failure performs zero mutations | `tools/test_orca_assisted_probe.py:675` - prior durable bytes unchanged; zero-call path is exercised by the same canonical test | PASS |

**Status:** 57/57 requirements have spec-anchored `file:line` evidence; no precision gap.

## Discrimination Sensor

Baseline checkout was clean. A detached temporary worktree at inspected HEAD changed the redaction
guard in `tools/orca_assisted_probe.py:179` to `if False and (...)`. Command
`python3 tools/test_orca_assisted_probe.py` exited 1 at
`tools/test_orca_assisted_probe.py:754` because `SECRET_PREVIEW` reached diagnostics. The mutant was
killed. The scratch worktree was removed and pruned; real-checkout porcelain again matched baseline.

**Sensor depth:** lightweight, highest-risk diagnostics trust boundary
**Result:** 1/1 mutation killed; 0 survived - PASS

## Direct Probe and Adoption Evidence

- `python3 tools/test_orca_assisted_probe.py` -> exit 0, `24/24 passed`.
- Four focused fake-provider checks -> exit 0, 4 passed/0 failed: pointer-only transport; one
  Orca/Git/lease mutation under transient failure; restart read-only reconciliation; process-safe
  concurrent claim with one physical mutation.
- Import with `subprocess.run`, `Popen`, and `check_output` replaced by call counters -> exit 0,
  `subprocess_calls: 0`.
- Disposable adoption -> exit 0; installed
  `/var/folders/lc/_v1mn5h560d2tsmz474y7d1c0000gn/T/my-workflow-hybrid-adopt-eo5jgr9x/tools/orca_assisted_probe.py`;
  source bytes identical; new skill present; TLC path absent; installed import made 0 subprocess calls.
- No live Orca command ran.

## Gate Check

- `python3 -m compileall -q .agents/skills tools scripts` -> exit 0, no output.
- `npm_config_offline=true npm run test:all` -> exit 0. Vitest: 8 files, 114/114 tests passed.
  Python discovery: `find tools -type f -name 'test_*.py' -print | sort | wc -l` -> 15 suites;
  all completed without failure. Probe lane reported 24/24; adoption contains 24 checks.
- Feature diff: `git diff --name-only $(git merge-base HEAD origin/main)..HEAD | wc -l` -> 129 files.
  Deleted-test audit returned no paths.
- Before-feature test count was not re-run; no unsupported delta is claimed.
- Skipped tests: none reported by Vitest or Python suites.
- Warnings: adoption correctly reports external security skills are not bundled; this is not a gate
  failure and no installer was authorized or run.

## Code Quality and Edge Cases

- Contract comparisons used `spec.md`, `tests.md`, `design.md`, and `tasks.md`.
- Canonical suites own each named invariant; no duplicate verification test was added.
- Path overlap, dirty baseline, stale/malformed health, explicit cap, checkpoint movement, foreign
  lease, contradictory effect identity, unsafe cleanup, atomic-write failure, restart, and concurrent
  issue cases all have discriminating assertions cited above.
- Exactly two intended worktrees remain: main and `feat/hybrid-slice-execution`.

## Deep Review Round 2 Closure

All 15 Major findings were independently checked against executable assertions and current source:

| # | Round-2 finding | Closure evidence | Result |
| --- | --- | --- | --- |
| 1 | Unbounded health integer could raise | `tools/test_machine_health.py:48` - `10**10000` denies admission at line 56 | PASS |
| 2 | Serial integration lane could bypass fresh Verifier | `tools/test_parallel_executor.py:2456` - worker remains pending until distinct verifier receipt, lines 2483-2497 | PASS |
| 3 | Concurrent slice Verifiers overwrote one report | `tools/shared/tests/autonomous-parallelization.test.ts:358` - slice-keyed report and final-only aggregate asserted | PASS |
| 4 | Closed convergence generation accepted three failures | `tools/test_review_convergence.py:225` - closed/3 rejects without rewriting bytes through line 254 | PASS |
| 5 | Autonomous docs contradicted one-ready serial dispatch | `tools/shared/tests/autonomous-parallelization.test.ts:348` - exact serial guidance required and old contradiction forbidden through line 356 | PASS |
| 6 | Arbitrary terminal/provider fields leaked diagnostics | `tools/test_orca_assisted_probe.py:748` - six sensitive fields absent through line 756 | PASS |
| 7 | Git read reconciliation admitted destructive subcommands | `tools/test_orca_assisted_probe.py:758` - worktree removal and symbolic-ref deletion reject before issue | PASS |
| 8 | Resource claims were not bound to a prepared lease | `tools/test_orca_assisted_probe.py:775` - unleased resource effect never reaches sink through line 787 | PASS |
| 9 | Caller-supplied effects could target foreign terminal/worktree | `tools/test_orca_assisted_probe.py:775` - both foreign targets reject before sink | PASS |
| 10 | Provider `observe_operation` could mutate | `tools/test_orca_assisted_probe.py:771` - provider release observation rejects | PASS |
| 11 | Pointer flag could disagree with physical operation | `tools/test_orca_assisted_probe.py:779` - pointer/worktree-rm mismatch rejects before sink | PASS |
| 12 | Read syntax alone could falsely settle an effect | `tools/test_orca_assisted_probe.py:794` - mismatched Git postcondition remains incomplete | PASS |
| 13 | Lease reconciliation could route release as a read | `tools/test_orca_assisted_probe.py:771` - mutating provider observation rejects | PASS |
| 14 | Concurrent dispatch could overwrite in-flight claim | `tools/test_orca_assisted_probe.py:797` - two processes produce exactly one physical pointer send | PASS |
| 15 | `{released: false}` could settle a release | `tools/test_orca_assisted_probe.py:789` - contradictory release receipt rejects through line 793 | PASS |

**Status:** 15/15 closed. No Critical or Major blocker remains. The serial-guidance contradiction is
absent from the current autonomous contract and guarded by a negative assertion.

## QA Closure

- Three dated charters have terminal verdicts in
  `docs/qa/reports/2026-08-29-hybrid-slice-execution.md:18`.
- Six offline fake/adoption scenarios are `qa_status: pass`; command:
  `rg -l '^qa_status: pass$' docs/qa/scenarios/{ADP-adopt-workflow-safely,CFG-freeze-feature-workflow,CFG-plan-parallel-slice-dispatch,CFG-fallback-unproven-parallel-execution,QAS-coordinate-assisted-slices-offline,QAS-bound-verifier-remediation-per-blocker}.md | wc -l` -> `6`.
- Two real-Orca scenarios remain `qa_status: blocked-verify`; the same report explicitly records
  that live Orca was not invoked.
- Fresh retest at `8257d37` closed `BUG-20260829-final-qa-pass-conflicts-with-adoption-gate` with
  65 byte-identical adopted files, zero import calls, 24 adoption checks, and a green full gate.

## Summary

**Overall:** PASS - ready for feature closure.

All 57 requirements, 15 round-2 Major remediations, offline fake-provider lifecycle, adoption,
import safety, cleanup, concurrency, QA, and discrimination sensor are green. The two live Orca
journeys remain truthfully `blocked-verify`; they are an explicit external limitation, not a hidden
PASS claim. No lesson was distilled because this final validation found no gap or surviving mutant.
