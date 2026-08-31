# Configurable Test Lock — Final Integrated Validation

**Date**: 2026-08-31
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `origin/main..a5eb535`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | PASS | Command lock, CLI boundary, lifecycle, and security controls verified. |
| T2 | PASS | Parallel adoption installs and tracks the wrapper; core omits it. |
| T3 | PASS | README documents explicit project and machine activation. |
| T4 | PASS | Adopted agent guidance points to the public resource-lock contract. |
| T5 | PASS | Concurrent first creation is serialized and exactly-once. |

## Spec-Anchored Requirements

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize one project resource. | `tools/test_parallel_resource_lock.py:128-133` omits scope and requires `first-start, first-end, second-start, second-end`. | PASS |
| CTL-02 | Unrelated repositories serialize one machine resource. | `tools/test_parallel_resource_lock.py:157-162` supplies `machine` and requires the exact serialized order. | PASS |
| CTL-03 | Different resource names overlap. | `tools/test_parallel_resource_lock.py:135-143` requires `second-start` before `first-end`. | PASS |
| CTL-04 | Omitted scope defaults to project. | `tools/test_parallel_resource_lock.py:128-133` omits `--scope` across linked worktrees and requires serialization. | PASS |
| CTL-05 | Wrapper returns the child status exactly. | `tools/test_parallel_resource_lock.py:336-340` requires child status `17` and the specified unavailable-executable status `127`. | PASS |
| CTL-06 | Acquisition timeout is bounded and starts no command. | `tools/test_parallel_resource_lock.py:243-248` requires status `75`, absent sentinel, and successful holder completion. | PASS |
| CTL-07 | Normal/abnormal holder exit and waiter interruption need no manual cleanup. | `tools/test_parallel_resource_lock.py:250-272` requires inherited-descriptor blocking, interrupted waiter status `130`, undisturbed holder completion, and later acquisition. | PASS |
| CTL-08 | Exact resource/scope/timeout/argv settings apply; invalid input fails before execution. | `tools/test_parallel_resource_lock.py:319-337,353-378` requires invalid status `2`, no side effect, literal `--`, exact child status, and usable help; `tools/test_parallel_resource_lock.py:390-415` requires the configured resource/scope diagnostic and bounded timeout. | PASS |
| CTL-09 | Parallel installs and tracks the dormant wrapper; core omits it. | `scripts/test_adopt.py:610-632` asserts core absence, byte-identical parallel installation, managed manifest ownership, idempotency, and conflict preservation. | PASS |
| SEC-001 | Shell metacharacters remain literal argv. | `tools/test_parallel_resource_lock.py:329-335` requires exact literal arguments and no injected file. | PASS |
| SEC-002 | Unsafe resource paths fail before filesystem or command mutation. | `tools/test_parallel_resource_lock.py:317-323` requires status `2`, absent command sentinel, and unchanged lock-root entries for every unsafe value. | PASS |
| SEC-003 | Private directory, ownership, lock-file symlink, and root replacement fail closed. | `tools/test_parallel_resource_lock.py:418-457` requires symlink referents untouched and foreign ownership rejected; `tools/test_parallel_resource_lock.py:459-493` requires stable-FD operation without writing through the substituted root. | PASS |
| SEC-004 | Metadata and diagnostics omit argv and environment secrets. | `tools/test_parallel_resource_lock.py:390-414` requires secret absence, typed allowlisted holder fields, one diagnostic, and the 2,048-character bound. | PASS |
| CTL-10 | Concurrent first requests for an absent lock execute exactly once in serialized order. | `tools/test_parallel_resource_lock.py:183-185` proves the lock is absent; `tools/test_parallel_resource_lock.py:221-235` starts both requests, requires both status `0`, and accepts only the two valid four-event serialized orders. | PASS |

**Result**: 14/14 requirements match the specified outcomes; 0 spec-precision gaps.

## Test Contract

- UT-001..UT-004: `tools/test_parallel_resource_lock.py:146-171,312-378` covers resource, project/machine identity, timeout, command, and literal-separator validation.
- IT-001..IT-009: `tools/test_parallel_resource_lock.py:121-309,336-415` covers both scopes, unrelated concurrency, exact status, timeout, lifecycle, diagnostics, and concurrent first creation; `scripts/test_adopt.py:607-632` covers adoption.
- SEC-001..SEC-004: `tools/test_parallel_resource_lock.py:317-493` covers every named abuse case at the subprocess/filesystem boundary.
- All 17 named cases are assigned exactly once in `.specs/features/configurable-test-lock/tasks.md:216-219`; 0 orphaned, duplicated, hollow, or unclaimed.

## Edge Cases

- Project scope outside Git fails before the child: `tools/test_parallel_resource_lock.py:428-431`.
- Traversal, separators, whitespace, empty, and overlong resources fail before mutation: `tools/test_parallel_resource_lock.py:317-323`.
- Static root/file symlinks and foreign ownership fail closed: `tools/test_parallel_resource_lock.py:418-457`.
- Root replacement after directory open remains bound to the stable descriptor: `tools/test_parallel_resource_lock.py:459-493`.
- Interrupted waiter leaves the holder intact and permits later acquisition: `tools/test_parallel_resource_lock.py:260-272`.

## Build Gate

Command:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

Result: exit `0`.

- Bun: 123 passed, 0 failed, 0 skipped; 1,123 assertions across 8 files.
- Python discovery: all 18 tracked suite files exited zero; resource lock reported 7/7 and adoption reported 65/65.
- Knowledge: 0 errors and 36 warnings.
- Diff check: exit `0`.
- Suite inventory: `rtk git ls-tree -r --name-only origin/main | rtk rg '^(scripts|tools)/test_.*\\.py$' | rtk wc -l` returned `17`; `rtk git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | rtk wc -l` returned `18`; delta `+1`, with 0 removed suites.
- Focused post-sensor baseline: `rtk python3 tools/test_parallel_resource_lock.py` returned exit `0`, 7/7 passed.

## Discrimination Sensor

The mutation ran in detached worktree `/tmp/my-workflow-ctl-sensor.8U8ZDJ`; the implementation checkout was not mutated.

| Mutation | Wrong behavior | Detector | Result |
| --- | --- | --- | --- |
| Set `FIRST_CREATION_ATTEMPTS` from `3` to `1` | Removes recovery from the induced transient `ENOENT` during simultaneous first creation. | `tools/test_parallel_resource_lock.py:174-235`; targeted invocation failed at line 224 with `test-resource-lock: lock file is unavailable`. | KILLED, exit 1 |

**Sensor depth**: lightweight, one targeted behavior mutation focused on the changed first-creation path.
**Result**: 1/1 killed, 0 survived. Scratch worktree removed; real-tree porcelain matched the empty baseline before this report was written.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code and no speculative abstraction | PASS |
| Surgical scope and no unrelated improvement | PASS |
| Standard-library and existing repository patterns | PASS |
| Spec-anchored outcomes and per-layer coverage | PASS |
| Every test maps to a requirement, edge case, or done-when criterion | PASS |
| Guidelines followed: `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/REVIEW-ROUNDS.md` | PASS |

## Requirement Traceability

All CTL-01..CTL-10 and SEC-001..SEC-004 remain verified on current HEAD. T1..T5 and both slices are complete.

## Ranked Gaps

None.

## Summary

**Overall**: PASS. The integrated feature meets all 14 requirements on current HEAD.

**Spec-anchored check**: 14/14 requirements matched; 0 precision gaps.
**Test contract**: 17/17 named cases pass.
**Gate**: exit 0; 123 Bun tests and 18/18 Python suites passed.
**Sensor**: 1 injected, 1 killed, 0 survived.
