# Host-Agnostic Slice Parallelization Validation

**Verdict**: PASS
**Date:** 2026-08-28
**Spec:** `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Integrated diff range:** `836f9d3..35f0c23`
**T11 remediation diff:** `c508c4e..35f0c23`
**Verified HEAD:** `35f0c23`
**Verifier:** independent Verifier, author != verifier

## Result

All 38 requirements have spec-anchored evidence. T11 closes the three prior gaps: effect
reconciliation rejects zero and mismatched commit expectations, a pending canonical task cannot
reconcile, and cleanup independently rejects linked-worktree registration and admin-gitdir residue.
Five scratch mutations were killed. The historical halted fingerprint and lessons remain recorded;
this report does not erase or reset them.

## Task Completion

`tools/orca_assisted_probe.py:552-568` parses canonical task headings and status records. T11 is
complete in `.specs/features/host-agnostic-slice-parallelization/tasks.md:379`.

| Task | Status |
| --- | --- |
| T1-T11 | complete |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome and assertion evidence | Result |
| --- | --- | --- |
| HST-01 | Disabled start/resume constructs no adapter and v1 snapshots fail: `tools/test_parallel_executor.py:190-207`, `tools/test_parallel_executor.py:435-462`, `tools/test_parallel_executor.py:1189-1203` | PASS |
| HST-02 | Auto in Maestri does not fall through to Orca: `tools/test_parallel_executor.py:1221-1245` | PASS |
| HST-03 | Incompatible explicit adapters serialize before effects: `tools/test_parallel_executor.py:364-402`, `tools/test_parallel_executor.py:1317-1335` | PASS |
| HST-04 | Scheduler, readiness, review, gate, and QA stages remain pinned: `tools/shared/tests/autonomous-parallelization.test.ts:55-105` | PASS |
| HST-05 | Default is `assisted`; explicit modes are preserved: `tools/test_workflow_config.py:107-152` | PASS |
| HST-06 | Assisted planning matches full readiness/sync and bypasses automatic adapters: `tools/test_parallel_plan.py:131-176`, `tools/test_parallel_executor.py:209-362` | PASS |
| ORC-01 | Ready runtime, contract capability, and nonempty version are required: `tools/test_orca_adapter.py:237-255` | PASS |
| ORC-02 | Known-bad Orca stops before mutation: `tools/test_orca_adapter.py:225-234` | PASS |
| ORC-03 | Candidate canary creates one correlated supervised lifecycle: `tools/test_orca_adapter.py:383-459` | PASS |
| ORC-04 | Result, acknowledgement, release, removal, and zero residue precede PASS: `tools/test_orca_adapter.py:383-459` | PASS |
| ORC-05 | Every failed stage records no PASS and retains identifiers: `tools/test_orca_adapter.py:258-277` | PASS |
| ORC-06 | Matching repository/runtime/executable receipts are reused: `tools/test_orca_adapter.py:280-310`, `tools/test_orca_adapter.py:355-380` | PASS |
| ORC-07 | Any identity change invalidates cache reuse: `tools/test_orca_adapter.py:313-352` | PASS |
| MAE-01 | Structured lifecycle capabilities are required and no current claim becomes compatible: `tools/test_maestri_adapter.py:33-74` | PASS |
| MAE-02 | Missing Maestri capability returns unsupported with zero effects: `tools/test_maestri_adapter.py:17-30` | PASS |
| MAE-03 | Complete-looking capabilities still cannot reach generic Git execution: `tools/test_maestri_adapter.py:77-116` | PASS |
| MAE-04 | Human-readable output is rejected as a receipt: `tools/test_maestri_adapter.py:119-129` | PASS |
| AST-01 | Unique startup ownership and two consecutive exact screen frames are asserted: `tools/orca_assisted_probe.py:302-519`; `tools/test_orca_assisted_probe.py:125-223` | PASS |
| AST-02 | One ready worker per slice and sequential task ownership are exercised by the two-slice lifecycle: `tools/test_orca_assisted_probe.py:748-926` | PASS |
| AST-03 | B parks with exact checkpoint/comment and resumes without polling: `tools/test_orca_assisted_probe.py:748-926`, `tools/shared/tests/autonomous-parallelization.test.ts:318-325` | PASS |
| AST-04 | Exact commit count/subjects, canonical tasks, same handle, ancestry, paths, gate, clean state, and packet marker must agree: `tools/orca_assisted_probe.py:585-639`; positive, pending-task, and foreign-handle cases: `tools/test_orca_assisted_probe.py:573-722` | PASS |
| AST-05 | Dirty, conflicting, or unproved checkpoints serialize: `tools/shared/tests/autonomous-parallelization.test.ts:330-333` | PASS |
| AST-06 | Cleanup proves exact ownership, integration, branch-ref absence, registration absence, and admin-gitdir absence: `tools/orca_assisted_probe.py:734-868`; independent residue cases: `tools/test_orca_assisted_probe.py:471-548`; real linked-worktree lifecycle: `tools/test_orca_assisted_probe.py:748-926` | PASS |
| AST-07 | Atomic task gates, Verifier, review, QA, and final gate remain explicit: `tools/shared/tests/autonomous-parallelization.test.ts:468-472` | PASS |
| AST-08 | Disabled, insufficient-ready, conflicts, missing isolation, and missing resource proof serialize: `tools/test_parallel_plan.py:151-225`, `tools/test_parallel_executor.py:246-402` | PASS |
| AST-09 | Main coordinator owns cross-slice lifecycle and workers cannot spawn siblings: `tools/shared/tests/autonomous-parallelization.test.ts:318-350`, `tools/shared/tests/autonomous-parallelization.test.ts:500-615` | PASS |
| AST-10 | Create/send/set/stop/rm are one-shot under transient receipts: `tools/test_orca_assisted_probe.py:23-59`, `tools/test_orca_assisted_probe.py:125-163`, `tools/test_orca_assisted_probe.py:274-353` | PASS |
| AST-11 | Only the fixed pointer crosses `terminal send`; body and import dispatch do not: `tools/test_orca_assisted_probe.py:61-123`, `tools/test_orca_assisted_probe.py:879-924` | PASS |
| AST-12 | Adoption copies the self-contained import-inert probe: `scripts/test_adopt.py:362-388` | PASS |
| SEC-001 | Disabled execution has zero adapter construction or mutation: `tools/test_parallel_executor.py:190-207`, `tools/test_parallel_executor.py:435-462` | PASS |
| SEC-002 | Runtime state and receipts are repository/identity scoped: `tools/test_parallel_executor.py:121-152`, `tools/test_orca_adapter.py:280-352` | PASS |
| SEC-003 | Host/Git calls use fixed argv, no shell, timeouts, and bounded paths: `tools/test_parallel_executor.py:153-188`, `tools/test_orca_adapter.py:2049-2075` | PASS |
| SEC-004 | Only correlated structured machine responses are accepted: `tools/test_maestri_adapter.py:119-129`, `tools/test_orca_adapter.py:486-781` | PASS |
| SEC-005 | Credential-shaped diagnostics are redacted: `tools/test_orca_adapter.py:1666-1800` | PASS |
| SEC-006 | PASS requires settled worker and zero disposable canary residue: `tools/test_orca_adapter.py:383-459` | PASS |
| SEC-007 | Cleanup requires exact ownership and preserves foreign worktree, terminal, ref, registration, and admin-gitdir state: `tools/orca_assisted_probe.py:734-868`, `tools/test_orca_assisted_probe.py:274-468` | PASS |
| SEC-008 | Missing ownership or any owned path/ref/registration/admin-gitdir residue stops deletion: `tools/orca_assisted_probe.py:734-868`; both independent Git residue assertions: `tools/test_orca_assisted_probe.py:471-548` | PASS |
| SEC-009 | Mutating Orca calls are one-shot; only reads reconcile: `tools/orca_assisted_probe.py:61-80`, `tools/orca_assisted_probe.py:201-270`; `tools/test_orca_assisted_probe.py:23-59` | PASS |

**Status:** 38/38 matched with discriminating evidence; 0 spec-precision gaps.

## Discrimination Sensor

Scratch checkout: detached worktree at exact `35f0c23`. Each mutation changed only the scratch,
the canonical 20-check probe suite killed it, and the scratch was removed. Real-tree porcelain
before and after retained exactly the same four historical Verifier artifacts.

| Mutation | Requirement | Decisive failure | Result |
| --- | --- | --- | --- |
| Change `expected_count <= 0` to `< 0` | AST-04 | `test_effect_requires_positive_count_and_matching_subjects` assertion failed | KILLED |
| Remove subject-count equality from the guard | AST-04 | invalid mismatch reached reconciliation and raised `AttributeError` instead of required `ProbeError` | KILLED |
| Replace canonical task predicate with `True` | AST-04 | `pending expected task must fail reconciliation` | KILLED |
| Remove only `path in registrations_after` | AST-06, SEC-008 | `cleanup unexpectedly accepted Git residue` in registration case | KILLED |
| Remove only `worktree_gitdir.exists()` | AST-06, SEC-008 | `cleanup unexpectedly accepted Git residue` in admin-gitdir case | KILLED |

**Sensor depth:** focused high-risk remediation, 5 behavior mutations.
**Result:** 5/5 killed, PASS.

## Integration, Pointer, and Adoption Evidence

- Real two-slice fake-host lifecycle parks, syncs, resumes same handle, integrates, and cleans:
  `tools/test_orca_assisted_probe.py:748-926`.
- Exactly-once assertions require one send, stop, and rm per lane while preserving foreign resources:
  `tools/test_orca_assisted_probe.py:920-926`; mutation checks: `tools/test_orca_assisted_probe.py:23-59`.
- Real adoption installed `/tmp/my-workflow-t11-adopt.AZrZ4p/tools/orca_assisted_probe.py`
  byte-identically at 54,676 bytes. Import with `ORCA=/bin/echo` returned
  `IMPORT_OK ORCA_CALLS=0`. Disposable directory removed.
- No live Orca run was performed.

## Gate Check

- `npm_config_offline=true rtk npm run test:all`: exit 0. Vitest 8/8 files and 113/113 tests;
  every package-discovered Python suite passed; probe lane reported 20/20.
- `rtk python3 tools/test_orca_assisted_probe.py`: exit 0, 20/20 passed.
- `rtk python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/host-agnostic-slice-parallelization/spec.md`: exit 0, 0 errors, 0 warnings.
- `rtk python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/host-agnostic-slice-parallelization/tasks.md`: exit 0, 0 errors, 0 warnings.
- `rtk git diff --check`: exit 0 before this report.
- Baseline at `c508c4e`: Vitest 113 and probe 16. Current: Vitest 113 and probe 20; T11 adds four
  canonical probe checks and removes none. Skipped tests: none observed. Failures: none.

## Code Quality and Edge Cases

- Minimum/surgical change: PASS. No new dependency, abstraction, compatibility layer, live-host
  requirement, or scope expansion.
- Zero/mismatched commit expectations fail before reconciliation; pending canonical tasks fail at
  normal reconciliation boundary.
- Cleanup tests distinguish registration residue from admin-gitdir residue.
- Default assisted selection, explicit disabled fallback, pointer-only transport, import safety,
  exactly-once mutations, foreign-resource preservation, and same-handle continuation remain green.
- Guidelines followed: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/GATES.md`,
  `docs/guidelines/VERIFICATION-EVIDENCE.md`, `docs/guidelines/REVIEW-ROUNDS.md`.

## Historical Convergence and Lessons

`review-fingerprints.json` retains historical `fa97ec...` halted record and earlier fingerprints.
`.specs/lessons.json` and `.specs/LESSONS.md` retain L-026 through L-030. Clean PASS adds no lesson
and resets no historical counter.

## QA Disposition

This packet is technical-only. Integrated feature changes public adoption, configuration, CLI, and
docs-as-interface, so its existing QA Plan/QA Execute records remain separate from this verdict.
T11 strengthens fail-closed internals and tests without changing the public contract.

## Summary

**Overall:** PASS; technical requirements ready.
**Spec-anchored check:** 38/38 requirements passed; 0 spec-precision gaps.
**Gate:** full gate green.
**Sensor:** 5/5 mutations killed.
**Ranked gaps:** none.
