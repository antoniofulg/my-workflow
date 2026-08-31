# Configurable Test Lock — Final Integrated Validation R1

**Date**: 2026-08-30
**Spec**: `.specs/features/configurable-test-lock/spec.md`
**Diff range**: `origin/main..281cd2a`
**Verifier**: fresh independent Technical Verifier (author != verifier)
**Verdict**: FAIL

## Task Completion

| Task | Status | Notes |
| --- | --- | --- |
| T1 | Needs fix | Lock mechanics pass their canonical suite, but CTL-08 accepts a command without the required `--` delimiter. |
| T2 | PASS | Parallel adoption installs and tracks the wrapper; core omits it. |
| T3 | PASS | README documents explicit project/machine activation. |
| T4 | PASS | Adopted parallel guidance points to the public contract. |

## Spec-Anchored Requirements

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| CTL-01 | Linked worktrees serialize one project resource. | `tools/test_parallel_resource_lock.py:106-118` requires exact first-start/first-end/second-start/second-end order. | PASS |
| CTL-02 | Unrelated repositories serialize one machine resource. | `tools/test_parallel_resource_lock.py:131-142` requires the same exact serialized order under `machine`. | PASS |
| CTL-03 | Different resource names overlap. | `tools/test_parallel_resource_lock.py:120-128` requires `second-start` before `first-end`. | PASS |
| CTL-04 | Omitted scope defaults to project. | `tools/test_parallel_resource_lock.py:113-118` omits scope and requires linked-worktree serialization. | PASS |
| CTL-05 | Wrapper returns exact child status. | `tools/test_parallel_resource_lock.py:213` requires status `17`. | PASS |
| CTL-06 | Timeout is bounded and starts no command. | `tools/test_parallel_resource_lock.py:160-162` requires status `75` and absent sentinel. | PASS |
| CTL-07 | Holder exit and interruption recover without manual cleanup. | `tools/test_parallel_resource_lock.py:165-187` requires inherited-descriptor blocking, waiter status `130`, undisturbed holder, and later acquisition. | PASS |
| CTL-08 | Exact CLI settings apply; invalid input fails before execution; command is argv after required `--`. | Resource/scope/timeout/missing-command/direct-argv assertions exist at `tools/test_parallel_resource_lock.py:190-215`, but `tools/resource_lock.py:196-200` accepts a non-empty remainder without proving or requiring the delimiter. Probe `python3 tools/resource_lock.py run --resource browser python3 -c 'raise SystemExit(17)'` returned `17`, not invalid-input status `2` required by `dx.md:20,26`. | FAIL |
| CTL-09 | Parallel installs and tracks the dormant wrapper; core omits it. | `scripts/test_adopt.py:607-632` asserts core absence, byte-identical parallel install, managed manifest ownership, idempotency, and conflict preservation. | PASS |
| SEC-001 | Shell metacharacters remain literal argv. | `tools/test_parallel_resource_lock.py:205-211` requires exact literal arguments and no injected file. | PASS |
| SEC-002 | Unsafe resource paths fail before mutation. | `tools/test_parallel_resource_lock.py:194-203` requires status `2`, absent command sentinel, and absent lock root for the full invalid matrix. | PASS |
| SEC-003 | Unsafe lock paths fail closed. | `tools/test_parallel_resource_lock.py:255-294` requires symlink referents unchanged and foreign ownership rejected. | PASS for tested static substitution; residual race below. |
| SEC-004 | Metadata and diagnostics omit secrets. | `tools/test_parallel_resource_lock.py:217-251` requires sentinel absence, allowlisted holder fields, one bounded diagnostic line, and typed values. | PASS |

**Result**: 12/13 requirements pass; CTL-08 fails. No spec-precision gaps.

## Test Contract

- UT-001..UT-004: `tools/test_parallel_resource_lock.py:131-150,190-215` — all contracted resource, identity, timeout, and missing-command outcomes pass.
- IT-001..IT-007: `tools/test_parallel_resource_lock.py:106-187,213,227-252` — all seven process/diagnostic cases pass.
- IT-008: `scripts/test_adopt.py:607-632` — parallel install/core omission passes in the canonical adoption suite.
- SEC-001..SEC-004: `tools/test_parallel_resource_lock.py:194-294` — all four named abuse cases pass at the contracted layer.
- All 16 named cases are assigned once in `tasks.md:184-188`; none are orphaned or duplicated. The required-delimiter outcome in `dx.md:20` has no test-contract case.

## Edge Cases

- Outside Git fails before the child: `tools/test_parallel_resource_lock.py:265-268`.
- Unsafe resource matrix fails before mutation: `tools/test_parallel_resource_lock.py:194-203`.
- Static root/file symlinks and foreign ownership fail closed: `tools/test_parallel_resource_lock.py:255-294`.
- Interrupted waiter leaves the holder intact: `tools/test_parallel_resource_lock.py:175-187`.

## Build Gate

Command:

```text
npm_config_offline=true rtk bun run test:all && rtk bun run knowledge && rtk git diff --check origin/main...HEAD
```

Result: exit `0`.

- Bun: 123 passed, 0 failed, 0 skipped; 1,123 assertions across 8 files.
- Python discovery: 18/18 tracked suites exited zero; adoption reported 65/65 and resource lock 5/5.
- Knowledge: 0 errors, 35 existing gap warnings.
- Diff check: exit 0.
- Python suite inventory: 17 at `origin/main`, 18 at HEAD; delta +1. Existing suites removed: 0.

## Discrimination Sensor

Detached scratch worktree at `281cd2a`; removed after restoration and green focused baseline.

| Mutation | Wrong behavior | Detector | Result |
| --- | --- | --- | --- |
| Collapse every project namespace to `machine` | Unrelated repositories share a project key. | `tools/test_parallel_resource_lock.py:150` requires two project identity lock files. | KILLED, exit 1 |
| Remove `pass_fds=(fd,)` | Wrapper death releases the lock while child survives. | `tools/test_parallel_resource_lock.py:170` requires the next waiter to remain blocked. | KILLED, exit 1 |
| Remove `tools/resource_lock.py` from `PARALLEL_PATHS` | Parallel adoption omits the wrapper. | `scripts/test_adopt.py:456` fixed inventory assertion. | KILLED, exit 1 |

Result: 3/3 killed, 0 survived. Restored scratch passed resource-lock 5/5 and adoption 65/65.

## Fingerprints and Net Diff

- `.specs/features/configurable-test-lock/review-fingerprints.json`: 10 fingerprints, 10 closed, 0 open.
- The unclaimed parse-time `KeyboardInterrupt` catch from `b81276d` is absent at `tools/resource_lock.py:195-200`; runtime interruption handling remains at `tools/resource_lock.py:191,215-216` and is claimed by CTL-07.
- No existing test was weakened or deleted.
- Public QA scenario remains `untested`, as required for the later fresh QA phases, but its entry point is stale: `docs/qa/scenarios/QAS-serialize-heavy-test-resources.md:8` names removed `tools/test_resource_lock.py` instead of `tools/resource_lock.py`.

## Security Residual

- Security skills evidenced in this verifier packet: none. Review used `.specs/features/configurable-test-lock/threat-model.md` and `docs/guidelines/SECURITY.md`.
- SEC-001 / S6: PASS — `tools/test_parallel_resource_lock.py:205-211`.
- SEC-002 / S6: PASS — `tools/test_parallel_resource_lock.py:194-203`.
- SEC-003 / S6, S11: PASS for static substitution — `tools/test_parallel_resource_lock.py:255-294`.
- SEC-004 / S6: PASS — `tools/test_parallel_resource_lock.py:217-251`.
- Residual: `tools/resource_lock.py:92-111` validates the root with `lstat` and later opens the child path by name. A same-user process covered by `threat-model.md:25` can replace the root between those operations; `O_NOFOLLOW` protects only the final lock-file component. This race is not asserted by SEC-003.
- Open Critical: 0.
- Open High: 0.
- Security verdict: PASS for named SEC requirements; one non-High residual needs design/remediation before final PASS.

## Ranked Gaps

1. **Major — CTL-08 CLI delimiter is not enforced or tested.** Require the literal `--` before command argv, add the missing contract case, and prove omission exits `2` before command/lock mutation.
2. **Major — SEC-003 does not close the committed path-replacement race assumption.** Open the verified directory by descriptor and resolve/open the lock relative to it, or narrow the threat model with explicit rationale; add a discriminating race/substitution seam.
3. **Minor — QA scenario points to the removed executable.** Change `docs/qa/scenarios/QAS-serialize-heavy-test-resources.md:8` to `python3 tools/resource_lock.py run` before QA Execute.

## Isolation and QA Disposition

- Real-tree porcelain before gate/sensor: clean.
- Scratch worktree removed; generated external sentinel residue moved recoverably to `/tmp/my-workflow-test-lock-final-residue.AFKNpX`.
- Real-tree porcelain after cleanup was clean before this report.
- Public CLI/adoption behavior requires separate fresh QA Plan and QA Execute after technical remediation. No QA was performed here.

## Summary

**Overall**: FAIL.

**Spec-anchored check**: 12/13 requirements matched; CTL-08 failed.
**Test contract**: 16/16 named cases pass, but one public DX outcome is missing from the contract.
**Gate**: exit 0; 123 Bun tests and 18/18 Python suites passed.
**Sensor**: 3 injected, 3 killed, 0 survived.
**Security**: 0 Critical, 0 High; one unclosed path-race residual.
