# Configurable Test Lock — Slice S1 Validation R4

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `4c2ca56..13550e8`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | ✅ Done | All 12 S1 requirements match the contract; Build gate exits zero; 3/3 behavior mutations are killed. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize the same project resource. | `tools/test_parallel_resource_lock.py:103-108` — both commands omit scope and the event log must equal `first-start, first-end, second-start, second-end`. | ✅ PASS |
| CTL-02 | Unrelated repositories serialize the same machine resource. | `tools/test_parallel_resource_lock.py:127-132` — both commands select `machine` and must produce the same serialized order. | ✅ PASS |
| CTL-03 | Different resource names remain concurrent. | `tools/test_parallel_resource_lock.py:111-118` — `second-start` must precede `first-end`. | ✅ PASS |
| CTL-04 | Omitted scope defaults to project scope. | `tools/test_parallel_resource_lock.py:103-108` — `scope=None` omits `--scope`, while linked worktrees still serialize. | ✅ PASS |
| CTL-05 | The wrapper returns the exact child exit status. | `tools/test_parallel_resource_lock.py:201` — child status `17` must be returned unchanged. | ✅ PASS |
| CTL-06 | Timeout exits non-zero without starting the command. | `tools/test_parallel_resource_lock.py:150-152` — exact status `75` and absent command sentinel. | ✅ PASS |
| CTL-07 | Normal/abnormal holder exit recovers without cleanup; interruption leaves the holder undisturbed. | `tools/test_parallel_resource_lock.py:155-175` — inherited lock blocks until child end; interrupted waiter returns `130`; only the later waiter runs. | ✅ PASS |
| CTL-08 | Exact CLI inputs apply; invalid input fails before execution; argv stays direct; diagnostics are bounded, useful, and secret-free. | `tools/test_parallel_resource_lock.py:183-203,215-239` — invalid matrix, literal argv, public identity, exact statuses, required diagnostic fields, one immediate line, and 2,048-character ceiling are asserted. | ✅ PASS |
| SEC-001 | Shell metacharacters remain literal argv and create no injected file. | `tools/test_parallel_resource_lock.py:193-199` — recorder equals all four literals and `injected` remains absent. | ✅ PASS |
| SEC-002 | Traversal, absolute path, separator, whitespace, empty, and overlong resources fail before mutation. | `tools/test_parallel_resource_lock.py:182-187` — every unsafe input returns `2`; command sentinel and lock root remain absent. | ✅ PASS |
| SEC-003 | Symlinked or foreign-owned lock paths fail closed without touching referents. | `tools/test_parallel_resource_lock.py:243-282` — root/file symlink referents remain unchanged and mocked foreign ownership raises `ValueError`. | ✅ PASS |
| SEC-004 | Lock metadata and diagnostics omit argv/environment secrets. | `tools/test_parallel_resource_lock.py:215-239` — sentinel is absent from metadata and stderr while allowlisted holder fields remain typed. | ✅ PASS |

**Status**: 12/12 S1 requirements match their complete spec-defined outcomes; 0 precision gaps.

## Public CLI and Exact Diagnostic Bounds

- Parser identity is `resource_lock.py`: `tools/resource_lock.py:54-61`.
- Invalid-scope stderr must contain `resource_lock.py` and exclude obsolete `test_resource_lock.py`: `tools/test_parallel_resource_lock.py:188-191`.
- Occupied timeout emits exactly one immediate JSON line in the short wait: `tools/test_parallel_resource_lock.py:222-233`.
- Every emitted line is at most 2,048 characters: `tools/test_parallel_resource_lock.py:234`.
- Production emits once on first contention and suppresses repeats: `tools/resource_lock.py:166-182`.
- CLI help probe printed `usage: resource_lock.py [-h] {run} ...`.

## Test Contract and Edge Cases

- UT-001..UT-004: resource validation, project/machine identity, timeout, and command validation are asserted at `tools/test_parallel_resource_lock.py:96-140,178-203`.
- IT-001..IT-007: project/machine serialization, unrelated concurrency, exit status, timeout, inherited-descriptor recovery, and bounded diagnostics are asserted at `tools/test_parallel_resource_lock.py:96-175,201,215-239`.
- SEC-001..SEC-004: all four abuse outcomes are asserted at `tools/test_parallel_resource_lock.py:182-282`.
- Outside Git returns `2` before the child can run: `tools/test_parallel_resource_lock.py:253-256`.
- Interrupted waiter returns `130`, never executes, and does not disturb the current holder: `tools/test_parallel_resource_lock.py:165-175`.
- Linked worktrees share a project identity while unrelated repositories create two project lock files: `tools/test_parallel_resource_lock.py:96-108,134-140`.

All 15 T1 test-contract cases map to one S1 requirement or listed edge; none are unclaimed. Subprocess integration is the cheapest layer that crosses CLI, process, Git, and filesystem boundaries. The foreign-owner seam is a deterministic unit check.

## Build Gate

**Command**:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

**Result**: exit `0`.

- Bun: 123 passed, 0 failed, 0 skipped; 1,123 assertions across 8 files.
- Python discovery: 18/18 tracked suites exited zero; S1 contract printed `ok (5 tests)`.
- Knowledge: 0 errors, 35 existing gap warnings.
- Diff check: exit 0.
- Python inventory before S1: 17 (`git ls-tree -r --name-only 4c2ca56 | rg '^(scripts|tools)/test_[^/]+\\.py$' | wc -l`).
- Python inventory after S1: 18 (`git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | wc -l`); delta +1 canonical contract suite.
- Existing tests weakened, skipped, or deleted in S1: 0.

## Discrimination Sensor

Detached scratch worktree: `/tmp/my-workflow-test-lock-r4.2k0pOD/tree` at `13550e8`; removed after reversal and green baseline.

| Mutation | Production site | Wrong behavior injected | Discriminating assertion | Result |
| --- | --- | --- | --- | --- |
| Added a second timeout diagnostic | `tools/resource_lock.py:179-181` | Short occupied wait emits two JSON lines. | `tools/test_parallel_resource_lock.py:233` requires exactly one. | ✅ Killed; suite exit 1 |
| Collapsed every project identity | `tools/resource_lock.py:84` | Unrelated repositories share one project lock key. | `tools/test_parallel_resource_lock.py:140` requires two project lock files. | ✅ Killed; suite exit 1 |
| Removed inherited lock descriptor | `tools/resource_lock.py:185-190` | Killing wrapper releases exclusivity while child survives. | `tools/test_parallel_resource_lock.py:160` requires next waiter to remain blocked. | ✅ Killed; suite exit 1 |

**Sensor depth**: lightweight, focused on the highest-risk S1 boundaries.
**Result**: 3/3 killed, 0 survived. After reversal: `rtk python3 tools/test_parallel_resource_lock.py` -> `ok (5 tests)`, exit 0.

## Code Quality

| Principle | Status |
| --- | --- |
| Standard library only; no dependency or daemon | ✅ |
| Minimum component and one canonical contract suite | ✅ |
| Surgical S1 scope; no speculative adoption behavior | ✅ |
| Public CLI exactly matches `dx.md` | ✅ |
| Every assertion matches a spec-defined outcome | ✅ |
| Every T1 test maps to the contract or a listed edge | ✅ |
| Guidelines followed: `TEST-CONTRACT.md`, `SECURITY.md`, `VERIFICATION-EVIDENCE.md` | ✅ |

## Security Residual

- Security basis: `.specs/features/configurable-test-lock/threat-model.md` plus `docs/guidelines/SECURITY.md` review residual; S11 makes the threat model applicable.
- SEC-001 / S6: PASS — direct argv and injection sentinel at `tools/test_parallel_resource_lock.py:193-199`.
- SEC-002 / S6: PASS — full unsafe-resource matrix and pre-mutation assertions at `tools/test_parallel_resource_lock.py:182-187`.
- SEC-003 / S6, S11: PASS — root/file symlink and ownership controls at `tools/test_parallel_resource_lock.py:243-282`; production uses owner/mode checks and `O_NOFOLLOW` at `tools/resource_lock.py:92-123`.
- SEC-004 / S6: PASS — metadata and stderr secrecy at `tools/test_parallel_resource_lock.py:215-239`.
- Open Critical: 0.
- Open High: 0.
- Verdict: PASS.

## Prior Fingerprint Reconciliation

All eight recorded generations are behaviorally resolved on this tree: Python discovery, default scope, holder lifecycle, metadata secrecy, unsafe paths, public CLI identity, report whitespace, and diagnostic boundedness. `review-fingerprints.json` retains their append-only `open` records; status bookkeeping remains orchestrator-owned and does not represent a surviving behavior gap.

## QA Disposition

The diff adds a public CLI. Technical verification passes; QA Plan and QA Execute remain separate fresh Verifier phases after the public adoption/documentation slice integrates the CLI journey.

## Isolation

- Real-tree porcelain before verification: clean.
- All three mutations ran only in the detached scratch worktree.
- Scratch baseline passed, scratch worktree was removed, and its parent temp directory was removed.
- Real-tree porcelain after scratch cleanup: clean before this required report.

## Summary

**Overall**: PASS.

**Spec-anchored check**: 12/12 requirements matched, 0 gaps.
**Gate**: 123 Bun tests plus 18/18 Python suites passed; 0 failures; knowledge 0 errors; diff check clean.
**Sensor**: 3 injected, 3 killed, 0 survived.
