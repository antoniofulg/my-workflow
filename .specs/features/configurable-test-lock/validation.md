# Configurable Test Lock — Final Integrated Validation R2

**Date**: 2026-08-31
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `origin/main..2fef05d`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: PASS

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | PASS | Command lock, CLI boundary, lifecycle, and security controls verified. |
| T2 | PASS | Parallel adoption installs and tracks the wrapper; core omits it. |
| T3 | PASS | README documents explicit project and machine activation. |
| T4 | PASS | Adopted agent guidance points to the public resource-lock contract. |

## Spec-Anchored Requirements

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize one project resource. | `tools/test_parallel_resource_lock.py:113-118` omits scope and requires `first-start, first-end, second-start, second-end`. | PASS |
| CTL-02 | Unrelated repositories serialize one machine resource. | `tools/test_parallel_resource_lock.py:131-142` requires the same exact serialized order under `machine`. | PASS |
| CTL-03 | Different resource names overlap. | `tools/test_parallel_resource_lock.py:120-128` requires `second-start` before `first-end`. | PASS |
| CTL-04 | Omitted scope defaults to project. | `tools/test_parallel_resource_lock.py:113-118` omits `--scope` and requires linked-worktree serialization. | PASS |
| CTL-05 | Wrapper returns the exact child status. | `tools/test_parallel_resource_lock.py:213` requires status `17`; `tools/test_parallel_resource_lock.py:214` requires `127` for a missing executable. | PASS |
| CTL-06 | Timeout is bounded and starts no command. | `tools/test_parallel_resource_lock.py:160-162` requires status `75` and an absent sentinel. | PASS |
| CTL-07 | Holder exit and interruption recover without manual cleanup. | `tools/test_parallel_resource_lock.py:165-187` requires inherited-descriptor blocking, waiter status `130`, an undisturbed holder, and later acquisition. | PASS |
| CTL-08 | Exact settings apply; invalid input fails before execution; command requires literal `--` and executes as argv. | `tools/test_parallel_resource_lock.py:190-227` requires invalid status `2`, exact literals, exact child status, absent mutation, and rejection without `--`. | PASS |
| CTL-09 | Parallel installs and tracks the dormant wrapper; core omits it. | `scripts/test_adopt.py:607-632` asserts core absence, byte-identical parallel install, managed manifest ownership, idempotency, and conflict preservation. | PASS |
| SEC-001 | Shell metacharacters remain literal argv. | `tools/test_parallel_resource_lock.py:205-211` requires exact literal arguments and no injected file. | PASS |
| SEC-002 | Unsafe resource paths fail before mutation. | `tools/test_parallel_resource_lock.py:194-203` requires status `2`, absent command sentinel, and absent lock root for every unsafe input. | PASS |
| SEC-003 | Root and lock-file substitution fail closed, including the root replacement race. | `tools/test_parallel_resource_lock.py:267-338` requires static symlink referents untouched, foreign ownership rejected, and a replacement path unable to receive the lock file after a stable directory FD opens. | PASS |
| SEC-004 | Metadata and diagnostics omit argv and environment secrets. | `tools/test_parallel_resource_lock.py:229-264` requires sentinel absence, allowlisted typed holder fields, one diagnostic, and the 2,048-character bound. | PASS |

**Result**: 13/13 requirements match the specified outcome; 0 spec-precision gaps.

## Test Contract

- UT-001..UT-004: `tools/test_parallel_resource_lock.py:131-150,190-227` covers resource, identity, timeout, missing-command, and literal-separator validation.
- IT-001..IT-007: `tools/test_parallel_resource_lock.py:106-187,213-264` covers both scopes, unrelated concurrency, status, timeout, inherited lifecycle, and diagnostics.
- IT-008: `scripts/test_adopt.py:607-632` covers the parallel install/core omission boundary and manifest ownership.
- SEC-001..SEC-004: `tools/test_parallel_resource_lock.py:194-338` covers every named abuse case at the subprocess/filesystem boundary.
- All 16 named cases are assigned once by `.specs/features/configurable-test-lock/tasks.md:186-190`; 0 orphaned and 0 duplicated.
- The added Python discovery inventory entry at `tools/shared/tests/qa-skills.test.ts:1101` claims the repository gate's tracked-suite boundary; no test or net behavior is unclaimed.

## Edge Cases

- Outside Git fails before the child: `tools/test_parallel_resource_lock.py:277-280`.
- Traversal, separators, whitespace, empty, and overlong resources fail before filesystem or command mutation: `tools/test_parallel_resource_lock.py:194-199`.
- Static root/file symlinks and foreign ownership fail closed: `tools/test_parallel_resource_lock.py:267-306`.
- Root replacement after directory open remains bound to the stable FD and leaves the substituted referent empty: `tools/test_parallel_resource_lock.py:308-338`.
- Interrupted waiter leaves the holder intact and permits later acquisition: `tools/test_parallel_resource_lock.py:175-187`.

## Build Gate

Command:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

Result: exit `0`.

- Bun: 123 passed, 0 failed, 0 skipped; 1,123 assertions across 8 files.
- Python discovery: 18/18 tracked suites exited zero; resource lock reported 5/5 and adoption reported 65/65.
- Knowledge: 0 errors and 36 gap warnings, including this newly verified feature awaiting later knowledge harvesting.
- Diff check: exit 0.
- Suite inventory: 17 Python suites at `origin/main`, 18 at HEAD, delta +1; 8 Bun suites at both refs; existing suites removed: 0.

Focused post-sensor baseline:

```text
rtk python3 tools/test_parallel_resource_lock.py
```

Result: exit `0`, 5/5 tests.

## Discrimination Sensor

All mutations ran in detached temporary worktrees at `2fef05d`; the real product tree was never mutated.

| Mutation | Wrong behavior | Detector | Result |
| --- | --- | --- | --- |
| Disable literal-separator guard | Commands without `--` execute. | `tools/test_parallel_resource_lock.py:216-227` requires status `2` and absent sentinel. | KILLED, exit 1 |
| Reopen lock path by name instead of relative to stable directory FD | Root substitution redirects lock creation into the referent. | `tools/test_parallel_resource_lock.py:308-338` requires the substituted directory remain empty. | KILLED, exit 1 |
| Remove inherited lock FD from the child | Killing the wrapper releases exclusivity before the child exits. | `tools/test_parallel_resource_lock.py:165-173` requires child end before waiter start. | KILLED, exit 1 |

**Result**: 3/3 killed, 0 survived. All scratch worktrees were removed.

## Code Quality and Net Diff

- Standard-library `argparse`, `fcntl`, filesystem descriptors, and `subprocess` implement the requested boundary without a daemon or dependency.
- The lock is one resource per invocation; unrelated gates remain concurrent.
- Adoption is inert and reuses the existing `parallel` layer; consumer commands are not rewritten.
- Product changes are limited to the tool, canonical tests, adoption inventory, public contract, agent pointer, QA entry point, and feature artifacts.
- `docs/qa/scenarios/QAS-serialize-heavy-test-resources.md:8-9` now names the shipped CLI and remains `untested` for separate QA phases.
- No live Orca, network operation, QA execution, push, PR, merge, or release occurred.

## Fingerprints

- `.specs/features/configurable-test-lock/review-fingerprints.json`: 12 total, 12 closed, 0 open.
- Final-R1 fingerprint `cb2f065...` is closed by `tools/resource_lock.py:198-209` plus `tools/test_parallel_resource_lock.py:216-227`.
- Final-R1 fingerprint `fb7575b...` is closed by `tools/resource_lock.py:92-126,213-230` plus `tools/test_parallel_resource_lock.py:308-338`.
- No older fingerprint remains open.

## Security Residual

- Security skills applied in this verifier session: none; the assigned review used `.specs/features/configurable-test-lock/threat-model.md` and `docs/guidelines/SECURITY.md`.
- Threat model: `.specs/features/configurable-test-lock/threat-model.md`.
- SEC-001 / S6: PASS — `tools/test_parallel_resource_lock.py:205-211`.
- SEC-002 / S6: PASS — `tools/test_parallel_resource_lock.py:194-203`.
- SEC-003 / S6, S11: PASS — `tools/test_parallel_resource_lock.py:267-338`.
- SEC-004 / S6: PASS — `tools/test_parallel_resource_lock.py:229-264`.
- Open Critical: 0.
- Open High: 0.
- Residual risk remains only the specified same-user denial and consumer opt-in/granularity choices in `.specs/features/configurable-test-lock/threat-model.md:43-46`.
- Security verdict: PASS.

## Isolation and QA Disposition

- Real-tree porcelain baseline before gate/sensors: clean.
- Real-tree product code remained untouched; only this canonical report and allowed traceability/status evidence were written.
- All three scratch worktrees were removed. Generated disposable residue was moved recoverably to `/tmp/my-workflow-test-lock-r2-residue.12q9g1`.
- Public CLI/adoption behavior requires separate fresh QA Plan and QA Execute. This technical session performed neither.

## Requirement Traceability Update

All CTL-01..CTL-09 and SEC-001..SEC-004 move from task evidence to `Verified by final R2` in `spec.md`; T1..T4 and both slices are complete in `tasks.md`.

## Summary

**Overall**: PASS — technically ready for the separately routed QA phases.

**Spec-anchored check**: 13/13 requirements matched; 0 precision gaps.
**Test contract**: 16/16 named cases pass; 0 orphaned, duplicated, hollow, or unclaimed cases.
**Gate**: exit 0; 123 Bun tests and 18/18 Python suites passed.
**Sensor**: 3 injected, 3 killed, 0 survived.
**Security**: 0 Critical, 0 High; verdict PASS.
