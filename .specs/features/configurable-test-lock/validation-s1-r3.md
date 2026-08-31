# Configurable Test Lock — Slice S1 Validation R3

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `4c2ca56..0b6216d`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | ❌ Not done | The mandatory Build gate exits `2`; IT-007 also lacks a bounded-diagnostic assertion. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize the same project resource. | `tools/test_parallel_resource_lock.py:103-108` — both commands omit scope and the event list must equal `first-start, first-end, second-start, second-end`. | ✅ PASS |
| CTL-02 | Unrelated repositories serialize the same machine resource. | `tools/test_parallel_resource_lock.py:127-132` — both commands select `machine` and the same exact serialized event order is required. | ✅ PASS |
| CTL-03 | Different resource names remain concurrent. | `tools/test_parallel_resource_lock.py:111-118` — `events.index("second-start") < events.index("first-end")`. | ✅ PASS |
| CTL-04 | Omitted scope defaults to project scope. | `tools/test_parallel_resource_lock.py:103-108` — `scope=None` omits the flag and linked worktrees still serialize. | ✅ PASS |
| CTL-05 | Wrapper returns the exact child status. | `tools/test_parallel_resource_lock.py:201` — wrapped status `17` must be returned unchanged. | ✅ PASS |
| CTL-06 | Timeout returns non-zero without starting the command. | `tools/test_parallel_resource_lock.py:150-152` — exact status `75` and absent sentinel. | ✅ PASS |
| CTL-07 | Abnormal holder exit preserves the inherited lock; interruption leaves the holder undisturbed; later acquisition needs no cleanup. | `tools/test_parallel_resource_lock.py:155-175` — waiter remains blocked through child lifetime, interrupted waiter returns `130`, holder exits `0`, and only the later waiter runs. | ✅ PASS |
| CTL-08 | Exact CLI inputs validate before execution, argv is direct, public identity is `resource_lock.py`, and wait diagnostics are bounded and useful. | `tools/test_parallel_resource_lock.py:183-203,230-237` covers invalid inputs, literal argv, statuses, identity, required diagnostic fields, and secrecy. No assertion limits diagnostic line count or line size. | ❌ GAP |
| SEC-001 | Shell metacharacters remain literal argv and create no injected file. | `tools/test_parallel_resource_lock.py:193-199` — recorder equals all four literals and `injected` is absent. | ✅ PASS |
| SEC-002 | Unsafe resource paths fail before filesystem or command mutation. | `tools/test_parallel_resource_lock.py:182-187` — empty, overlong, absolute, separator, whitespace, and traversal inputs return `2`; command and lock-root sentinels stay absent. | ✅ PASS |
| SEC-003 | Symlinked and foreign-owned lock paths fail closed without touching referents. | `tools/test_parallel_resource_lock.py:241-280` — root/link referents remain unchanged and mocked foreign ownership raises `ValueError`. | ✅ PASS |
| SEC-004 | Metadata and diagnostics omit command/environment secrets. | `tools/test_parallel_resource_lock.py:215-237` — sentinel is absent from metadata and stderr while allowlisted holder fields remain typed. | ✅ PASS |

**Status**: 11/12 S1 requirements have complete discriminating evidence. CTL-08 remains incomplete.

## Public CLI Identity

- ✅ Parser declares `prog="resource_lock.py"` at `tools/resource_lock.py:55`.
- ✅ Invalid-scope stderr must contain `resource_lock.py` at `tools/test_parallel_resource_lock.py:190`.
- ✅ The obsolete `test_resource_lock.py` identity must be absent at `tools/test_parallel_resource_lock.py:191`.
- ✅ The shipped path and invocation match `.specs/features/configurable-test-lock/dx.md:5-12`.

## Test Contract and Edge Cases

- ✅ UT-001..UT-004: resource, project/machine identity, timeout, and command validation are asserted at `tools/test_parallel_resource_lock.py:103-140,182-203`.
- ✅ IT-001..IT-006: serialization, unrelated concurrency, exit status, timeout, and inherited-descriptor recovery are asserted at `tools/test_parallel_resource_lock.py:96-175,201`.
- ❌ IT-007: field presence and secrecy pass at `tools/test_parallel_resource_lock.py:230-237`, but “bounded diagnostics” has no assertion for maximum lines or bytes.
- ✅ SEC-001..SEC-004: all four named abuse outcomes are asserted at `tools/test_parallel_resource_lock.py:182-280`.
- ✅ Outside Git returns `2` before the child can return `9`: `tools/test_parallel_resource_lock.py:251-254`.
- ✅ Empty, 65-character, absolute, separator, whitespace, and traversal resources fail before mutation: `tools/test_parallel_resource_lock.py:182-187`.
- ✅ Symlinked root/file and foreign ownership fail closed: `tools/test_parallel_resource_lock.py:241-280`.
- ✅ Interrupted waiter returns `130` without disturbing the holder: `tools/test_parallel_resource_lock.py:165-175`.

## Build Gate

**Command**:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

**Result**: exit `2`.

- Bun: 123 passed, 0 failed, 1,123 assertions across 8 files; 0 skipped.
- Python discovery: 18/18 tracked suite executables exited `0`; the S1 contract printed `ok (5 tests)`.
- Knowledge: 0 errors, 35 existing gap warnings.
- Diff check: exit `2` on `.specs/features/configurable-test-lock/validation-s1-r2.md:76` because the committed line `**Sensor depth**: high-risk S1 boundaries.` has trailing whitespace.
- Python suite inventory: 17 at `4c2ca56`, 18 at `0b6216d`, delta +1. Commands: `git ls-tree -r --name-only 4c2ca56 | rg '^(scripts|tools)/test_[^/]+\\.py$' | wc -l`; `git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | wc -l`.
- No existing test was deleted or weakened in the S1 diff.

## Discrimination Sensor

Not run. `.agents/skills/workflow-spec-driven/references/validate.md` requires an immediate stop when the mandatory Build gate is non-zero. Therefore this R3 verifier injected 0 mutations; no scratch worktree was created.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum standard-library implementation | ✅ |
| Surgical S1 production scope | ✅ |
| No speculative abstraction or dependency | ✅ |
| Public CLI matches `dx.md` | ✅ |
| Spec-anchored assertions | ❌ IT-007 boundedness missing |
| Every T1 test maps to contract or edge | ✅ |
| Guidelines followed: `TEST-CONTRACT.md`, `SECURITY.md`, `VERIFICATION-EVIDENCE.md`, `GATES.md` | ✅ |

## Security Residual

- Security skills recorded by the feature: no installed language-specific skill was named in the verifier packet; the verifier applied the committed threat model and `docs/guidelines/SECURITY.md` residual review.
- Threat model: `.specs/features/configurable-test-lock/threat-model.md` (required because S11 applies).
- SEC-001 / S6: PASS — `tools/test_parallel_resource_lock.py:193-199`.
- SEC-002 / S6: PASS — `tools/test_parallel_resource_lock.py:182-187`.
- SEC-003 / S6, S11: PASS for the specified static substitution and ownership outcomes — `tools/test_parallel_resource_lock.py:241-280`.
- SEC-004 / S6: PASS — `tools/test_parallel_resource_lock.py:215-237`.
- Open Critical: 0.
- Open High: 0.
- Verdict: PASS for SEC-001..004; overall slice remains FAIL for CTL-08 and the Build gate.

## Prior Fingerprint Reconciliation

- `3a4f9c...` public CLI identity: behaviorally resolved by `tools/resource_lock.py:55` and discriminated at `tools/test_parallel_resource_lock.py:188-191`.
- Earlier default-scope, lifecycle, metadata-secrecy, path-validation, and discovery findings remain behaviorally resolved by the cited assertions and successful test stages.
- Durable fingerprint statuses remain orchestrator-owned; this verifier changed no fingerprint state.

## Ranked Gaps / Fix Tasks

1. **Blocker — mandatory Build gate is red.** Remove the trailing whitespace at `.specs/features/configurable-test-lock/validation-s1-r2.md:76`, commit the remediation without amending, then rerun Quick and Build gates and dispatch a fresh verifier.
2. **Major — CTL-08 / IT-007 does not discriminate bounded diagnostics.** Extend the canonical subprocess test to assert the occupied-timeout path emits at most the contracted bounded number of JSON lines and each line is no more than the implementation's 2,048-character ceiling; rerun Quick and Build gates and a fresh verifier.

## Isolation

- Real-tree porcelain before verification: clean.
- No scratch mutation was allowed after the red gate.
- Before this report, real-tree porcelain remained clean; this report is the only verifier-authored path.

## Summary

**Overall**: ❌ Not ready.

**Spec-anchored check**: 11/12 S1 requirements matched; 1 evidence gap.
**Gate**: FAIL — tests and knowledge passed, final diff check exited `2`.
**Sensor**: 0 injected, 0 killed, 0 survived; correctly skipped after the red gate.
**Next**: remediate the two ranked gaps, then use a fresh Technical Verifier.
