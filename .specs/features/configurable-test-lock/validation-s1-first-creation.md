# Configurable Test Lock S1 First-Creation Validation

**Verdict**: PASS
**Date**: 2026-08-31
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `1b38676..898b53e7b22c518589dbdbde77084aa7779de6c4`
**Verifier**: independent sub-agent (author != verifier)

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T5 / CTL-10 | PASS | Concurrent first creation recovers without duplicate or overlapping execution. |

## Spec-Anchored Acceptance Criterion

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-10: two invocations concurrently request an absent lock file | Both wrapped commands execute exactly once in serialized order. | `tools/test_parallel_resource_lock.py:185` asserts the lock is absent; `tools/test_parallel_resource_lock.py:221-225` starts two synchronized wrappers and asserts both exit `0`; `tools/test_parallel_resource_lock.py:231-235` requires exactly four events in one of the two serialized orders. | PASS |

**Status**: 1/1 criterion matched the exact spec outcome. No spec-precision gap.

## Retry Boundary Evidence

- `tools/resource_lock.py:32` bounds first-creation recovery to three attempts.
- `tools/resource_lock.py:113-120` retries only `errno.ENOENT` and sleeps `0.01` seconds between remaining attempts.
- `tools/resource_lock.py:115` passes the same validated `directory_fd` to every attempt.
- `tools/resource_lock.py:121-123` maps `ELOOP` separately and fails every other error closed.
- Isolated direct assertion result: `ENOENT=3` opens and `2` sleeps through `directory_fd=71`; `EACCES=1` open and `0` sleeps; `ELOOP=1` open and `0` sleeps.

## Discrimination Sensor

All mutations ran in detached temporary worktrees. The implementation checkout was not mutated.

| Mutation | Changed behavior | Check | Result |
| --- | --- | --- | --- |
| M1 | Disabled the `ENOENT` retry. | Ran `test_concurrent_first_creation_recovers_from_transient_enoent`; it failed at `tools/test_parallel_resource_lock.py:224` with `lock file is unavailable`. | Killed |
| M2 | Replaced the validated directory descriptor with `-1` on a retry. | Ran the same CTL-10 test; it failed at `tools/test_parallel_resource_lock.py:224` with `lock file is unavailable`. | Killed |
| M3 | Retried every filesystem error instead of only `ENOENT`. | Isolated assertion required one `EACCES` open and zero sleeps; mutant performed three opens. | Killed |

**Sensor depth**: lightweight, three targeted behavior mutations.
**Result**: 3/3 killed, 0 survived.

## Gate Check

- **Build command**: `npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD`
- **Result**: exit `0`.
- **Bun tests**: 123 passed, 0 failed, 1,123 assertions.
- **Python suites**: 18/18 suite files passed; the lock contract reported 7 passed, 0 failed.
- **Knowledge**: 0 errors, 36 warnings.
- **Test count delta**: `git show 1b38676:tools/test_parallel_resource_lock.py | rg -c '^def test_'` returned `6`; `rg -c '^def test_' tools/test_parallel_resource_lock.py` returned `7`; delta `+1` for IT-009.
- **Skipped tests**: none reported.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code and no speculative abstraction | PASS |
| Surgical scope | PASS |
| Existing style and stdlib-only implementation | PASS |
| Spec-anchored outcome assertion | PASS |
| IT-009 maps once to CTL-10 | PASS |
| Documented guidelines followed: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/REVIEW-ROUNDS.md` | PASS |

## Ranked Gaps

None.

## Summary

**Overall**: PASS. CTL-10 is ready for integration. The canonical test proves absent-file setup,
two successful executions, exactly-once event cardinality, and serialized order. The implementation
keeps recovery bounded to `ENOENT`, reuses the validated directory descriptor, and fails other
filesystem errors closed.
