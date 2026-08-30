# Configurable Test Lock — Slice S1 Validation R2

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `4c2ca56..62cddd6`
**Verifier**: independent sub-agent (author ≠ verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | ❌ Not done | Build gate and 3/3 discrimination mutations pass, but CTL-08 still exposes the obsolete CLI identity `test_resource_lock.py`. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize the same project resource. | `tools/test_parallel_resource_lock.py:103-108` — both invocations omit scope and the event log must equal `first-start, first-end, second-start, second-end`. | ✅ PASS |
| CTL-02 | Unrelated repositories serialize the same machine resource. | `tools/test_parallel_resource_lock.py:127-132` — both invocations select `machine` and the exact serialized event order is asserted. | ✅ PASS |
| CTL-03 | Different resource names remain concurrent. | `tools/test_parallel_resource_lock.py:111-118` — `second-start` must precede `first-end`. | ✅ PASS |
| CTL-04 | Omitted scope defaults to project scope. | `tools/test_parallel_resource_lock.py:103-108` — `scope=None` omits `--scope` for both linked-worktree invocations and the shared project lock serializes them. | ✅ PASS |
| CTL-05 | Wrapper returns the exact child status. | `tools/test_parallel_resource_lock.py:198` — child status `17` must be returned unchanged. | ✅ PASS |
| CTL-06 | Timeout returns `75` without starting the command. | `tools/test_parallel_resource_lock.py:150-152` — return code is `75` and the command sentinel must not exist. | ✅ PASS |
| CTL-07 | Kernel lifecycle recovers after holder exit and waiter interruption does not disturb the holder. | `tools/test_parallel_resource_lock.py:155-175` — wrapper death leaves the waiter blocked until child end; interrupted waiter returns `130`, holder completes, and only the later waiter runs. | ✅ PASS |
| CTL-08 | Exact CLI settings validate before execution and command argv executes directly. | `tools/test_parallel_resource_lock.py:183-200` discriminates invalid resource/scope/timeout/command, direct argv, status, and missing executable. However `tools/resource_lock.py:55` sets public parser identity to obsolete `test_resource_lock.py`; running the invalid-input path prints that obsolete name instead of the frozen `resource_lock.py` surface. | ❌ FAIL |
| SEC-001 | Shell metacharacters remain literal argv and cannot inject a command. | `tools/test_parallel_resource_lock.py:190-196` — recorder must equal all four literals and injected file must remain absent. | ✅ PASS |
| SEC-002 | Unsafe resource paths fail before filesystem or command mutation. | `tools/test_parallel_resource_lock.py:182-188` — empty, 65-character, absolute, separator, whitespace, and traversal inputs return `2`; command sentinel and lock root remain absent. | ✅ PASS |
| SEC-003 | Symlinked or foreign-owned lock paths fail closed. | `tools/test_parallel_resource_lock.py:238-277` — root symlink leaves referent empty, lock-file symlink leaves referent unchanged, and mocked foreign ownership must raise `ValueError`. | ✅ PASS |
| SEC-004 | Holder metadata and diagnostics omit argv/environment secrets. | `tools/test_parallel_resource_lock.py:202-235` — sentinel must be absent from lock metadata and stderr while required allowlisted holder fields remain present. | ✅ PASS |

**Status**: 11/12 S1 requirements match their complete spec-defined outcome; CTL-08 has one public-surface mismatch.

## Test Contract Coverage

| Cases | Evidence | Result |
| --- | --- | --- |
| UT-001..UT-004 | `tools/test_parallel_resource_lock.py:134-140,178-200` | ✅ 4/4 |
| IT-001..IT-007 | `tools/test_parallel_resource_lock.py:96-175,198,202-235` | ✅ 7/7 |
| SEC-001..SEC-004 | `tools/test_parallel_resource_lock.py:178-277` | ✅ 4/4 |

All 15 T1 cases map to a spec criterion or listed edge. The suite is subprocess-level integration except the deterministic foreign-owner unit seam; this is the cheapest layer that crosses the CLI, process, Git, and filesystem boundaries. CTL-08 remains incomplete because no assertion checks the frozen CLI identity used in parser errors.

## Listed Edge Cases

- ✅ Outside Git fails before the command: `tools/test_parallel_resource_lock.py:248-251` asserts wrapper status `2` instead of the child status `9`.
- ✅ Empty, overlong, absolute, separator, whitespace, and traversal resource names fail before command or lock-root mutation: `tools/test_parallel_resource_lock.py:182-187`.
- ✅ Symlinked root, symlinked lock file, and foreign-owned root fail closed without referent mutation: `tools/test_parallel_resource_lock.py:238-277`.
- ✅ Interrupted waiter returns `130`, does not run, and does not disturb the current holder: `tools/test_parallel_resource_lock.py:165-175`.

## Build Gate

**Command**:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

**Result**: exit `0`.

- Bun: 123 passed, 0 failed, 1,123 assertions across 8 files.
- Python discovery: every tracked suite exited zero; the S1 contract reported `ok (5 tests)`.
- Knowledge: 0 errors, 35 existing gap warnings.
- Diff check: exit 0.

## Discrimination Sensor

All mutations ran in detached scratch worktree `/tmp/my-workflow-lock-verify-r2.BFZVcP/tree` at `62cddd6`; each mutation was reversed before the next.

| Mutation | Production site | Wrong outcome injected | Discriminating assertion | Result |
| --- | --- | --- | --- | --- |
| Project namespace collapsed to literal machine key | `tools/resource_lock.py:206` | Unrelated repositories receive one project key. | `tools/test_parallel_resource_lock.py:140` requires two project lock files. | ✅ Killed; suite exit 1 |
| Timeout fallthrough | `tools/resource_lock.py:212-213` | Timed-out waiter continues toward holder metadata/command instead of returning `75`. | `tools/test_parallel_resource_lock.py:151` requires exact timeout status (with sentinel absence at `:152`). | ✅ Killed; suite exit 1 |
| Removed inherited descriptor | `tools/resource_lock.py:186-190` | Wrapper death releases exclusivity while child remains alive. | `tools/test_parallel_resource_lock.py:160` requires the next waiter to remain blocked. | ✅ Killed; suite exit 1 |

**Sensor depth**: high-risk S1 boundaries.  
**Result**: 3/3 killed. Baseline after reversal: `ok (5 tests)`, exit 0.

## Security Residual

- Applied requirements: SEC-001 through SEC-004 from `.specs/features/configurable-test-lock/tests.md:29-36`.
- Threat model: `.specs/features/configurable-test-lock/threat-model.md`; reviewed S1, S6, and S11 controls against the complete S1 diff.
- SEC-001: PASS — `tools/test_parallel_resource_lock.py:190-196`.
- SEC-002: PASS — `tools/test_parallel_resource_lock.py:182-188`.
- SEC-003: PASS — `tools/test_parallel_resource_lock.py:238-277`.
- SEC-004: PASS — `tools/test_parallel_resource_lock.py:202-235`.
- Open Critical: 0.
- Open High: 0.
- Verdict: PASS for the security residual; the overall slice fails only on CTL-08 public CLI identity.

## Prior Fingerprint Reconciliation

The five findings recorded in `review-fingerprints.json` are behaviorally remediated by the current assertions and green gate: canonical discovery (`tools/shared/tests/qa-skills.test.ts:1098-1118`), default scope (`tools/test_parallel_resource_lock.py:103-108`), lifecycle edges (`:155-175,268-277`), metadata secrecy (`:202-235`), and path validation (`:182-188`). Their durable entries remain `open`; the orchestrator can close those generations using this independent report. The new CTL-08 parser-identity gap is distinct.

## Ranked Gap / Fix Task

1. **Major — CTL-08 public CLI identity is stale.** Premise: `tools/resource_lock.py:55` hardcodes `prog="test_resource_lock.py"` after the shipped file was renamed. Path: any argparse validation failure prints `usage: test_resource_lock.py ...`, contradicting `.specs/features/configurable-test-lock/dx.md:5-8` and retaining an obsolete public path. Verdict: change the parser identity to `resource_lock.py` and extend the existing CLI validation assertion to discriminate the name; rerun Quick and Build gates plus a fresh independent verifier.

## Isolation

- Real-tree porcelain before verification: clean.
- Scratch worktree removed after all mutations were reversed and its baseline suite passed.
- Real-tree porcelain after scratch cleanup: clean before this required report; afterward only `validation-s1-r2.md` is new.
