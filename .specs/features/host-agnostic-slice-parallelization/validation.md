# Host-Agnostic Slice Parallelization Validation

**Verdict**: PASS
**Date**: 2026-08-26
**Spec**: `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Diff range**: `2ab4cecc2d9daede27015c7edec543800e7bd763..HEAD`
**Remediation under review**: `a2e22fb`
**Verifier**: independent Verifier (author != verifier)

## Ranked Gaps

None.

Prior ORC-03 duplicate-checkout gap is resolved. The owning test now records and asserts exactly one
checkout creation, exactly one worker start, and one correlated `worker_done` event. The same
duplicate-checkout mutation that survived round 2 is killed in this round.

## Task Completion

| Task | Recorded status | Verification result |
| --- | --- | --- |
| T1 | complete | PASS: HST-01 through HST-04 and SEC-001/SEC-002 have outcome evidence. |
| T2 | complete | PASS: ORC-01 through ORC-07 and SEC-003/SEC-005 through SEC-007 have outcome evidence. |
| T3 | complete | PASS: MAE-01 through MAE-04 and SEC-003 through SEC-005/SEC-007 have outcome evidence. |
| T4 | complete | PASS: adoption contract and declared full gate are green. |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| HST-01 | Disabled start/resume constructs no adapter or host/Git effect; preflight remains diagnostic; v2 is accepted and v1 rejected. | `tools/test_parallel_executor.py:200` - `result = ...start()`; `:204` - `assert constructed is False`; `:1002` - disabled CLI import/factory guard; `:1016` - v2/v1 schema test; `:285` through `:289` - exact disabled preflight diagnostic. | PASS |
| HST-02 | Auto inside Maestri evaluates only Maestri and never falls through to Orca. | `tools/test_parallel_executor.py:1035` - guarded auto-selection test; its Orca import is forbidden and the result is a Maestri adapter. | PASS |
| HST-03 | Unavailable/incompatible explicit adapter serializes with backend/reason before checkout or worker. | `tools/test_parallel_executor.py:224` through `:228` - exact fallback/reason, empty adapter effects, no worktree; `:1131` - unavailable auto adapter has the same effect-free fallback. | PASS |
| HST-04 | Host selection preserves scheduler, checkpoint, Technical Verifier, review, gate, QA, and TLC contracts. | `tools/test_parallel_executor.py:1582` and `:1929` - same-slice order/cardinality; `:2174` - fresh external Verifier; `tools/shared/tests/autonomous-parallelization.test.ts:93` through `:102` - gate, Verifier, deep-review, QA, and TLC contract assertions. | PASS |
| ORC-01 | Probe requires ready reachable runtime, non-empty app version, and `orchestration.contract.v1`. | `tools/test_orca_adapter.py:231` through `:242` - each missing readiness/version/capability case returns `unsupported` with its exact reason. | PASS |
| ORC-02 | Known-bad `1.4.188` stops after read-only status inspection. | `tools/test_orca_adapter.py:219` through `:226` - exact unsupported reason and sole `orca status --json` call. Read-only installed preflight returned the same result. | PASS |
| ORC-03 | Explicit canary creates exactly one disposable checkout and one worker reaching correlated `worker_done`. | `tools/test_orca_adapter.py:373` through `:375` records all effects; `:427` - `assert len(creator_calls) == 1`; `:428` - `assert worker_starts == ["worker-start"]`; `:429` through `:432` assert one event with matching task/dispatch IDs. | PASS |
| ORC-04 | PASS occurs only after result read, acceptance, ack, release proof, checkout removal, and zero-residue proof. | `tools/test_orca_adapter.py:247` through `:264` kills every failed lifecycle/cleanup stage with no cache; `:424` through `:433` proves only the clean lifecycle writes PASS; `:1618` and `:1807` cover read-before-release and ack. | PASS |
| ORC-05 | Failed canary stage records no PASS and reports failed stage plus retained owned IDs. | `tools/test_orca_adapter.py:247` through `:264` iterates start/completion/read/ack/release/removal/absence, asserts exact stage, dispatch/terminal IDs, and absent cache. | PASS |
| ORC-06 | Matching repository/version/capability/executable receipt is reused without another canary. | `tools/test_orca_adapter.py:340` through `:363` makes canary forbidden, then asserts compatible clean cached proof and only two status calls. | PASS |
| ORC-07 | Any compatibility identity change invalidates PASS and requires explicit canary. | `tools/test_orca_adapter.py:269` through `:293` covers version; `:298` through `:335` covers repository, capabilities, executable path, size, and mtime and asserts `candidate`/`canary-required`. | PASS |
| MAE-01 | Maestri requires terminal/socket/CLI and structured lifecycle/cleanup capabilities, but stays incompatible until host-owned execution exists. | `tools/test_maestri_adapter.py:33` through `:50` asserts exact missing capabilities; `:56` through `:70` asserts a complete-looking manifest remains unsupported with cleanup not run. | PASS |
| MAE-02 | Missing capabilities return unsupported with no floor, agent, or Git-worktree effect. | `tools/test_maestri_adapter.py:17` through `:27` asserts exact unsupported/missing list and empty root; `:77` through `:113` proves executor fallback and no generic worktree. | PASS |
| MAE-03 | Current Maestri stays serial even when all capability names are claimed. | `tools/test_maestri_adapter.py:56` through `:70` - complete manifest remains unsupported; `:77` through `:113` - exact `maestri:host-owned-execution-unimplemented` fallback. | PASS |
| MAE-04 | Human-readable Maestri output is never accepted as ownership/completion/cleanup receipt. | `tools/test_maestri_adapter.py:119` through `:127` - human text is rejected as malformed with every capability missing. | PASS |

## Security Requirements

| Requirement | Evidence | Result |
| --- | --- | --- |
| SEC-001 | `tools/test_parallel_executor.py:190` through `:204`, `:1002`, and `:1561` prove disabled execution never constructs/selects an adapter or invokes planner/Git/runtime effects. | PASS |
| SEC-002 | `tools/test_parallel_executor.py:121` through `:130` locates state in Git common state outside `.specs`; `:135` through `:148` proves atomic replacement; `tools/test_orca_adapter.py:269` through `:335` proves repository/runtime/executable scoping. | PASS |
| SEC-003 | `tools/test_parallel_executor.py:153` through `:169` asserts fixed argv, `shell=False`, bounded timeout, and literal metacharacters; `:172` through `:184` rejects path escape and symlink sinks. | PASS |
| SEC-004 | `tools/test_orca_adapter.py:195` through `:214` asserts structured correlated receipts; `:1857` rejects foreign structured source identity; `tools/test_maestri_adapter.py:56` through `:70` refuses capability claims as execution proof. | PASS |
| SEC-005 | `tools/test_orca_adapter.py:1721` and `:1755` assert recursive credential redaction, including free-form structured failures. | PASS |
| SEC-006 | `tools/test_orca_adapter.py:247` through `:264` proves cleanup failures cannot cache PASS; `:424` through `:433` proves only clean zero-residue cleanup reaches compatible receipt. | PASS |
| SEC-007 | `tools/test_orca_adapter.py:1824` and `:1841` reject ack/release without exact correlated ownership; no revocation occurs. | PASS |

**Coverage status**: 22/22 requirements match precise spec outcomes with file:line assertions.

## Edge Cases

- Maestri socket/current or complete-looking manifest cannot cross to Orca or generic Git execution: PASS.
- New Orca identity with old capability set remains candidate until explicit canary: PASS.
- Release/removal/absence failure leaves runtime unsupported and stores no PASS: PASS.
- Foreign repository or executable cache is ignored: PASS.
- Credential-shaped host fields are redacted: PASS.

## Gate Check

- **Declared full command**: `npm_config_offline=true npm run test:all`
- **Result**: PASS, exit 0. Vitest: 110 passed, 0 failed, 0 skipped. Every Python lane completed with zero failures.
- **Feature Python suites**: Maestri 5 passed; Orca 66 passed; executor 51 passed; parallel plan 18 passed.
- **Python test definitions before feature**: 196 top-level `def test_` definitions.
- **Python test definitions after feature**: 214 top-level `def test_` definitions (+18).
- **Structural gates**: `validate_spec.py` 0 errors/warnings; `validate_tasks.py` 0 errors/warnings; `git diff --check 2ab4cecc2d9daede27015c7edec543800e7bd763..HEAD` passed.
- **Read-only installed Orca preflight**: unsupported, version `1.4.188`, exact reason `known-incompatible-version:1.4.188`, cleanup `not-run`; no canary ran.
- **Skipped tests**: none.

## Discrimination Sensor

Scratch used only temporary file copies under `mktemp`; no Git worktree, stash, Orca canary, or
Maestri mutation was used. Temporary copies were deleted after execution.

| Mutation | Production location | Outcome |
| --- | --- | --- |
| Duplicate the injected checkout-creator call before worker start. | `.agents/skills/autonomous/scripts/orca_adapter.py:624` | KILLED by `tools/test_orca_adapter.py:427`: `assert len(creator_calls) == 1`. |
| Ignore repository/runtime/capability/executable identity mismatch when loading cached PASS. | `.agents/skills/autonomous/scripts/orca_adapter.py:548` | KILLED by `tools/test_orca_adapter.py:334`: expected `candidate`, received stale compatibility. |
| Return `compatible` for a complete Maestri capability manifest despite absent host-owned execution. | `.agents/skills/autonomous/scripts/maestri_adapter.py:107` | KILLED by `tools/test_maestri_adapter.py:68`: expected `unsupported`. |

**Result**: 3/3 killed - PASS.

Real-tree porcelain before and after sensor was byte-for-byte identical:

```text
 M .specs/LESSONS.md
 M .specs/features/host-agnostic-slice-parallelization/spec.md
 M .specs/lessons.json
?? .specs/features/host-agnostic-slice-parallelization/review-fingerprints.json
?? .specs/features/host-agnostic-slice-parallelization/validation.md
```

Existing lessons and `review-fingerprints.json` were preserved.

## Code Quality

Implementation remains scoped to adapter selection, Orca lifecycle proof, Maestri fail-closed
capability reporting, adoption, and their owning tests. It reuses existing scheduler and state
helpers, keeps fixed-argv and fail-closed boundaries, and adds no dependency or compatibility layer.
All in-scope tests map to an acceptance criterion, edge case, security requirement, or task done-when
condition. Validation followed the installed `tlc-spec-driven` `validate.md` contract.

## Requirement Traceability Update

`spec.md` records all 22 requirements as `Verified`; ORC-03 moved from `Needs Fix` to `Verified` after
the cardinality assertion killed the prior surviving mutant.

## Summary

**Overall**: PASS, ready for feature closure.

**Spec-anchored check**: 22/22 requirements matched precise outcomes; 0 spec-precision gaps.

**Sensor**: 3/3 behavior mutations killed.

**Gate**: declared full gate green, with 110 Vitest tests and all Python lanes passing.

**Next step**: commit the verifier-owned validation/traceability artifacts in the normal workflow.
