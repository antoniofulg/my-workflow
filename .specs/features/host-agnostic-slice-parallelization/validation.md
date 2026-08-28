# Host-Agnostic Slice Parallelization Validation

**Verdict**: PASS
**Date:** 2026-08-28
**Spec:** `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Integrated diff range:** `836f9d3..3d3e9982859884326ce885e1febfcc86fb971d07`
**Round-2 remediation:** `3a11f11..3d3e9982859884326ce885e1febfcc86fb971d07`
**Verified HEAD:** `3d3e9982859884326ce885e1febfcc86fb971d07`
**Verifier:** independent Verifier; author != verifier

## Result

PASS. All seven canonical Round-2 defects are closed. Four implementation faults were independently
injected and killed: contradictory readiness aliases, malformed receipt `before` state, adoption
after failed final inventory, and destructive cleanup of a candidate with a reused pre-existing
terminal handle. Handoff is current at T15. This report supplies individual file:line evidence for
all 38 requirements and records validators from this exact checkout.

No Deep Review round 3 was started or requested. No live Orca run was performed. `validation.md` is
the only file written by this verifier.

## Task Completion

| Task | Status | Evidence |
| --- | --- | --- |
| T1-T14 | PASS | Prior verified feature and remediation scope retained |
| T15 | PASS | `.specs/features/host-agnostic-slice-parallelization/tasks.md:506` records the five Round-2 fail-closed outcomes complete |

Handoff names T15 and the T6–T15 delta at `.specs/STATE.md:6` and `.specs/STATE.md:7`.

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | File:line assertion evidence | Result |
| --- | --- | --- | --- |
| HST-01 | Disabled start/resume creates no adapter; diagnostic preflight remains read-only; schema v1 is rejected | `tools/test_parallel_executor.py:196`, `tools/test_parallel_executor.py:484`, `tools/test_parallel_executor.py:1224`, `tools/test_parallel_executor.py:1238` | PASS |
| HST-02 | Auto inside Maestri evaluates only Maestri and never falls through to Orca | `tools/test_parallel_executor.py:1270` asserts selected adapter calls exclude Orca | PASS |
| HST-03 | Explicit unavailable/incompatible adapter serializes before checkout or worker effects | `tools/test_parallel_executor.py:413` and `tools/test_parallel_executor.py:438` assert fallback and zero worktree effects | PASS |
| HST-04 | Existing scheduler, checkpoint, verifier, review, gate, and QA contracts remain intact | `tools/shared/tests/autonomous-parallelization.test.ts:468` asserts atomic gates, Technical Verifier, grouped review, final QA, full gate, and unchanged TLC order | PASS |
| HST-05 | Missing mode freezes `assisted`; explicit supported modes remain unchanged | `tools/test_workflow_config.py:107` and `tools/test_workflow_config.py:121` assert default and explicit values | PASS |
| HST-06 | Assisted planning uses full readiness/sync while executor bypasses automatic adapter | `tools/test_parallel_plan.py:131` and `tools/test_parallel_executor.py:215` assert equal readiness and no automatic adapter construction | PASS |
| ORC-01 | Orca requires ready reachable runtime, contract capability, and nonempty version | `tools/test_orca_adapter.py:237` asserts rejection for each missing field | PASS |
| ORC-02 | Known-bad Orca reports unsupported before Run, Task, worker, or worktree mutation | `tools/test_orca_adapter.py:225` asserts zero lifecycle effects | PASS |
| ORC-03 | Candidate canary creates one correlated checkout and supervised worker reaching worker_done | `tools/test_orca_adapter.py:383` asserts exact lifecycle effects and correlated completion | PASS |
| ORC-04 | Result read, ack, release, removal, and zero residue precede PASS | `tools/test_orca_adapter.py:383` asserts ordered clean removal before cache write | PASS |
| ORC-05 | Failed canary/cleanup records no PASS and reports retained IDs | `tools/test_orca_adapter.py:258` iterates each failure stage and asserts no compatible receipt | PASS |
| ORC-06 | Matching runtime/executable/repository PASS receipt is reused without a new canary | `tools/test_orca_adapter.py:280` and `tools/test_orca_adapter.py:355` assert reuse and zero new lifecycle effects | PASS |
| ORC-07 | Any compatibility identity change invalidates cache reuse | `tools/test_orca_adapter.py:313` asserts new canary requirement for every identity field | PASS |
| MAE-01 | Maestri requires complete structured lifecycle/cleanup capability and remains incompatible without host implementation | `tools/test_maestri_adapter.py:33` and `tools/test_maestri_adapter.py:56` assert unsupported despite complete-looking claims | PASS |
| MAE-02 | Missing Maestri capability reports exact unsupported fields with zero floor/agent/Git mutation | `tools/test_maestri_adapter.py:17` asserts missing fields and empty mutation log | PASS |
| MAE-03 | Current Maestri capability claims cannot reach generic Git-worktree execution | `tools/test_maestri_adapter.py:77` asserts compatible-looking manifest remains serial and Git-free | PASS |
| MAE-04 | Human-readable output is never parsed as a lifecycle receipt | `tools/test_maestri_adapter.py:119` asserts malformed/text output rejection | PASS |
| AST-01 | One exact owned unused startup handle, one create, exact route at 250 ms/60 s, and final inventory proof precede delivery | `tools/test_orca_assisted_probe.py:126`, `tools/test_orca_assisted_probe.py:186`, `tools/test_orca_assisted_probe.py:286`, and `tools/test_orca_assisted_probe.py:416` assert one create, failed-final-audit rejection, route frames, and inactive shell | PASS |
| AST-02 | At most one worker starts per ready slice and tasks remain sequential through first unmet dependency | `tools/test_parallel_executor.py:1817` and `tools/shared/tests/autonomous-parallelization.test.ts:318` assert single active task/worker and sequential stop boundary | PASS |
| AST-03 | Unmet dependency parks a clean exact checkpoint/comment and ends without polling | `tools/shared/tests/autonomous-parallelization.test.ts:321` asserts exact parked comment and no polling; `tools/test_orca_assisted_probe.py:1003` exercises park/resume lifecycle | PASS |
| AST-04 | Exact producer sync, same handle, marker, tasks, commit IDs, paths, gate, clean state, and bounded reconciliation must all agree | `tools/test_orca_assisted_probe.py:799`, `tools/test_orca_assisted_probe.py:821`, `tools/test_orca_assisted_probe.py:869`, `tools/test_orca_assisted_probe.py:935`, and `tools/test_orca_assisted_probe.py:979` assert task parsing, exact commit identity, pending-task rejection, handle rejection, and exact sync | PASS |
| AST-05 | Dirty, conflicting, failed, or ambiguous checkpoint serializes without automatic conflict resolution | `tools/test_parallel_executor.py:1869`, `tools/test_parallel_executor.py:1898`, and `tools/shared/tests/autonomous-parallelization.test.ts:330` assert serial recovery | PASS |
| AST-06 | Deterministic integration and cleanup revalidate exact receipt/handle/Git identity before ordered destructive operations and prove absence | `tools/test_orca_assisted_probe.py:432`, `tools/test_orca_assisted_probe.py:480`, `tools/test_orca_assisted_probe.py:661`, `tools/test_orca_assisted_probe.py:687`, `tools/test_orca_assisted_probe.py:695`, `tools/test_orca_assisted_probe.py:703`, `tools/test_orca_assisted_probe.py:711`, and `tools/test_orca_assisted_probe.py:791` assert ref, foreign-resource, moved-handle, immutable instance/pre-head, registration, and gitdir guards | PASS |
| AST-07 | Atomic task commits/gates, per-slice Technical Verifier, grouped review, final QA, and final full gate remain mandatory | `tools/shared/tests/autonomous-parallelization.test.ts:468` asserts every retained stage; full gate evidence appears below | PASS |
| AST-08 | Disabled, insufficient overlap, conflict, unavailable capability/isolation, or resource ambiguity serializes before host effects | `tools/test_parallel_plan.py:151`, `tools/test_parallel_executor.py:252`, `tools/test_parallel_executor.py:297`, `tools/test_parallel_executor.py:336`, and `tools/test_parallel_executor.py:359` assert each fail-closed branch including contradictory readiness | PASS |
| AST-09 | Main coordinator owns cross-slice lifecycle; workers cannot coordinate or clean siblings | `tools/shared/tests/autonomous-parallelization.test.ts:318` through `tools/shared/tests/autonomous-parallelization.test.ts:359` assert coordinator start/integration/cleanup ordering; `tools/test_orca_assisted_probe.py:1003` exercises two owned lanes | PASS |
| AST-10 | Create/send/set/stop/rm mutations execute exactly once; only bounded reads reconcile uncertain receipts | `tools/test_orca_assisted_probe.py:24`, `tools/test_orca_assisted_probe.py:126`, `tools/test_orca_assisted_probe.py:221`, and `tools/test_orca_assisted_probe.py:248` count mutations and exercise failed-receipt reconciliation | PASS |
| AST-11 | Complete packet stays outside slice worktree; only fixed quoted pointer crosses terminal send; body never crosses | `tools/test_orca_assisted_probe.py:62` asserts exact pointer, absent body, and inert import; `tools/shared/tests/autonomous-parallelization.test.ts:178` asserts adopted contract | PASS |
| AST-12 | Adoption installs one self-contained import-safe probe with no evidence imports or import-time Orca effects | `scripts/test_adopt.py:362` asserts byte identity and zero fake-Orca calls; disposable adoption evidence below repeats it | PASS |
| SEC-001 | Disabled mode performs no adapter probe or mutation | `tools/test_parallel_executor.py:196`, `tools/test_parallel_executor.py:1224`, and `tools/test_parallel_executor.py:1796` assert empty adapter/Git/host effects | PASS |
| SEC-002 | Compatibility/runtime receipts are atomic, repository-scoped local state | `tools/test_parallel_executor.py:127`, `tools/test_parallel_executor.py:141`, and `tools/test_orca_adapter.py:280` assert Git-common state path, atomic replacement, and repository identity binding | PASS |
| SEC-003 | Host/Git commands use fixed argv, `shell=False`, bounded timeouts, and validated paths | `tools/test_parallel_executor.py:159`, `tools/test_parallel_executor.py:178`, and `tools/test_orca_adapter.py:2049` assert argv/no-shell, symlink/path bounds, timeout, and secret-free errors | PASS |
| SEC-004 | Only structured machine objects correlated to the request are accepted | `tools/test_maestri_adapter.py:119`, `tools/test_orca_adapter.py:486`, `tools/test_orca_adapter.py:510`, and `tools/test_orca_assisted_probe.py:388` assert malformed/foreign receipt rejection and controlled `ProbeError` for malformed `before` state | PASS |
| SEC-005 | Credential-shaped response data is redacted before persistence or diagnostics | `tools/test_orca_adapter.py:1666`, `tools/test_orca_adapter.py:1769`, and `tools/test_orca_adapter.py:1803` assert nested/free-text redaction | PASS |
| SEC-006 | Compatibility PASS requires settled worker and zero disposable checkout residue | `tools/test_orca_adapter.py:383` asserts worker completion, release, removal, and absence before cache PASS | PASS |
| SEC-007 | No resource is removed without an exact ownership receipt | `tools/test_orca_assisted_probe.py:265`, `tools/test_orca_assisted_probe.py:480`, `tools/test_orca_assisted_probe.py:687`, and `tools/shared/tests/autonomous-parallelization.test.ts:619` assert reused/foreign/moved handles cause zero destructive mutation | PASS |
| SEC-008 | Assisted cleanup removes only clean integrated coordinator-owned resources; any ownership/residue ambiguity stops deletion | `tools/test_orca_assisted_probe.py:186`, `tools/test_orca_assisted_probe.py:265`, `tools/test_orca_assisted_probe.py:661`, `tools/test_orca_assisted_probe.py:695`, `tools/test_orca_assisted_probe.py:703`, `tools/test_orca_assisted_probe.py:711`, `tools/test_orca_assisted_probe.py:791`, and `tools/test_orca_assisted_probe.py:795` assert failed final audit, reused handle, owned residue, immutable identity, pre-head, registration, and admin-gitdir failures | PASS |
| SEC-009 | Assisted Orca mutations are never retried; missing/transient receipts reconcile only through bounded reads of same resource | `tools/test_orca_assisted_probe.py:24`, `tools/test_orca_assisted_probe.py:221`, `tools/test_orca_assisted_probe.py:248`, and `tools/test_orca_assisted_probe.py:265` assert one-shot call counts, bounded effect proof, retained candidate, and zero calls on reused handle | PASS |

**Requirement count:** 38 total; 38 individually evidenced and PASS.
**Spec-precision gaps:** 0.

## Round-2 Canonical Defects

`.deep-review/assisted-default-final/findings.json` reports seven canonical defects for Round 2.

| Fingerprint | Defect | Closure evidence | Result |
| --- | --- | --- | --- |
| `3a6c2f1f384472e0` | Contradictory readiness aliases | `tools/test_parallel_executor.py:359`; readiness mutant killed | PASS |
| `46143499e539202c` | Handoff stops before current task | `.specs/STATE.md:6` and `.specs/STATE.md:7` name T15/T6–T15 | PASS |
| `44ba1d31b7308f5b` | 38/38 claim lacks security evidence | This report contains separate rows for SEC-001 through SEC-009 with file:line assertions | PASS |
| `743034b1da19ffef` | Validator ran from sibling checkout | Gate section records `.agents/skills/...` commands executed inside this exact checkout | PASS |
| `3b2d3aefb1efb694` | Malformed receipt `before` dereferences uncontrolled shape | `tools/test_orca_assisted_probe.py:388`; shape mutant killed with controlled failure assertion | PASS |
| `03e3566a2d77674f` | Failed final inventory can still adopt cumulative candidate | `tools/test_orca_assisted_probe.py:186`; stale-adoption mutant killed, exactly one create call and no receipt | PASS |
| `5bcbb778d9061005` | Reused pre-existing terminal handle permits destructive late cleanup | `tools/test_orca_assisted_probe.py:265`; reused-handle mutant killed and `calls == []` | PASS |

## Discrimination Sensor

Each mutation ran independently in a detached temporary worktree at exact implementation HEAD.
Scratch was recreated between faults and removed afterward. Real-tree porcelain returned clean.

| Mutation | Focused command | Decisive result | Result |
| --- | --- | --- | --- |
| Restore first-present readiness alias behavior | `python3 tools/test_parallel_executor.py` | exit 1 at contradictory readiness assertion | KILLED |
| Remove receipt `before` object/map shape validation | `python3 tools/test_orca_assisted_probe.py` | exit 1: malformed before inventory accepted | KILLED |
| Fall back to stale cumulative candidates after failed final inventory | `python3 tools/test_orca_assisted_probe.py` | exit 1: required final-inventory controlled error absent | KILLED |
| Skip reused pre-existing handle without marking cleanup ambiguous | `python3 tools/test_orca_assisted_probe.py` | exit 1: destructive calls list was nonempty | KILLED |

**Sensor result:** 4/4 killed; 0 survived — PASS.

## Baseline and Adoption Evidence

- `python3 tools/test_orca_assisted_probe.py`: exit 0, 34/34.
- `python3 tools/test_parallel_executor.py`: exit 0, 59 passed, 0 failed.
- `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts`:
  exit 0, one file and 5/5 tests.
- Disposable adoption installed
  `/tmp/my-workflow-r2-verify.eLzPh8/tools/orca_assisted_probe.py`.
- Source and installed probe were byte-identical at 65,325 bytes each.
- Import with `ORCA=/bin/false`: `IMPORT_OK ORCA_CALLS=0`.
- Disposable target removed: `ADOPTION_TEMP_REMOVED=yes`.

## Gate and Validators

- `npm_config_offline=true rtk npm run test:all`: exit 0; Vitest 8/8 files and 113/113 tests;
  every Python lane green, including probe 34/34, executor 59/59, and Orca adapter 28/28. No skips
  or failures reported.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/host-agnostic-slice-parallelization/spec.md`:
  exit 0, 0 errors, 0 warnings.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/host-agnostic-slice-parallelization/tasks.md`:
  exit 0, 0 errors, 0 warnings.
- `git diff --check`: exit 0 before this report.

## QA and Limitations

`docs/qa/scenarios/QAS-coordinate-assisted-orca-slices.md:9` remains truthfully
`qa_status: untested`. AD-018 at `.specs/STATE.md:289` is scoped to this feature merge, explicitly
defers live Orca QA, preserves pointer-only/fake-host evidence, and claims no false live PASS.
This verifier ran no live Orca and does not upgrade that status.

## Summary

**Overall:** PASS. All seven Round-2 defects are closed; all 38 requirements have explicit
file:line evidence; 4/4 focused mutants were killed; full gate, adoption, import safety, and exact
checkout validators are green. Ready for the round-two validation commit.
