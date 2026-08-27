# Host-Agnostic Slice Parallelization Validation

**Verdict**: PASS
**Date**: 2026-08-26
**Spec**: `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Diff range**: `9d97092..4385b25` (AST-01 remediation); full feature range `2ab4cec..4385b25` rechecked
**Verifier**: independent Technical Verifier (author != verifier)

## Ranked Gaps

None. Fingerprint `3de2a98253b74e85b59213bcab3eb5ad8e109c78b4bea90778012f56f6e88bca`
is technically resolved: all five shell-promotion mutants are killed. Its accounting file is
preserved unchanged for the orchestrator to close.

E2E-001 and live Orca execution did not run in this technical phase. Existing QA evidence remains
unchanged; the affected assisted-Orca journey is ready for a fresh QA retest.

## Task Completion

| Task | Recorded status | Verification result |
| --- | --- | --- |
| T1 | complete | PASS: HST-01 through HST-04 and SEC-001/SEC-002 rechecked by the full gate. |
| T2 | complete | PASS: ORC-01 through ORC-07 and SEC-003/SEC-005 through SEC-007 rechecked by the full gate. |
| T3 | complete | PASS: MAE-01 through MAE-04 and SEC-003 through SEC-005/SEC-007 rechecked by the full gate. |
| T4 | complete | PASS: canonical adoption contract remains green. |
| T5 | complete | PASS: AST-01 through AST-07 and SEC-008 remain contract-covered; AST-01 ordering now discriminates. |

## Spec-Anchored Acceptance Criteria

| Requirement | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| HST-01 | Disabled start/resume constructs no adapter or host effect; diagnostic preflight remains available; v2 accepted and v1 rejected. | `tools/test_parallel_executor.py:200-204` asserts serial fallback and no construction; `:1020-1048` asserts no resolution, v2 acceptance, and exact v1 rejection. | PASS |
| HST-02 | Auto inside Maestri evaluates Maestri only. | `tools/test_parallel_executor.py:1066-1087` makes Orca import raise and asserts Maestri selection. | PASS |
| HST-03 | Incompatible adapter serializes with backend/reason before checkout or worker. | `tools/test_parallel_executor.py:224-228` asserts fallback, exact reason, empty effects, and no worktree. | PASS |
| HST-04 | Scheduler, checkpoint, Verifier, review, gate, and QA contracts remain unchanged. | `tools/test_parallel_executor.py:1613-1651,1960-2004,2208-2290` asserts order and fresh Technical Verifier; `tools/shared/tests/autonomous-parallelization.test.ts:97-102` asserts preserved readiness stages. | PASS |
| ORC-01 | Probe requires ready runtime, non-empty app version, and `orchestration.contract.v1`. | `tools/test_orca_adapter.py:237-253` asserts exact unsupported results for each missing field. | PASS |
| ORC-02 | Known-incompatible Orca reports unsupported without mutation. | `tools/test_orca_adapter.py:225-232` asserts exact reason and sole read-only status call. | PASS |
| ORC-03 | Explicit canary creates one checkout and one correlated worker. | `tools/test_orca_adapter.py:443-455` counts one creator, one worker start, and exact correlated result. | PASS |
| ORC-04 | PASS follows read, accept, ack, release, removal, and zero-residue proof. | `tools/test_orca_adapter.py:383-456` asserts the clean ordered lifecycle and compatible cache. | PASS |
| ORC-05 | Failed stage or unproven cleanup stores no PASS and reports stage plus retained IDs. | `tools/test_orca_adapter.py:258-275` asserts exact failure, retained ownership, and absent cache. | PASS |
| ORC-06 | Matching repository/runtime/executable receipt is reused without a canary. | `tools/test_orca_adapter.py:355-378` forbids canary execution and asserts cached compatible proof. | PASS |
| ORC-07 | Any identity change invalidates PASS and requires explicit canary. | `tools/test_orca_adapter.py:282-350` mutates every identity dimension and asserts candidate/canary-required. | PASS |
| MAE-01 | Maestri requires machine lifecycle capabilities and remains incompatible until host-owned execution exists. | `tools/test_maestri_adapter.py:33-71` asserts missing capabilities and rejects a complete-looking manifest. | PASS |
| MAE-02 | Missing capabilities cause unsupported with no floor, agent, or Git effect. | `tools/test_maestri_adapter.py:17-27,77-113` asserts missing list, fallback, and no worktree. | PASS |
| MAE-03 | Capability names alone never authorize generic Git-worktree execution. | `tools/test_maestri_adapter.py:56-71,103-113` asserts host-owned execution remains unimplemented and forbids worktree creation. | PASS |
| MAE-04 | Human-readable output is not a lifecycle receipt. | `tools/test_maestri_adapter.py:119-127` asserts malformed text remains unsupported. | PASS |
| AST-01 | Explicit authorization; one new, uniquely owned, unused startup shell proven before shell-quoted promotion; exact frozen screen tuple proven before prompt; automatic path stays serial and records no PASS. | Policy order is `.agents/skills/autonomous/references/parallelization.md:103-138`; `tools/shared/tests/autonomous-parallelization.test.ts:131-184` rejects generic `--agent`, asserts exact conjunctive proof and quoted commands, and compares ordered lifecycle positions. | PASS (contract only) |
| AST-02 | Start at most one worker after verified dependency and run sequentially to first unmet dependency. | `tools/shared/tests/autonomous-parallelization.test.ts:185-187` asserts both outcomes. | PASS (contract only) |
| AST-03 | Park clean checkpoint with complete identity and end without polling. | `tools/shared/tests/autonomous-parallelization.test.ts:188-192` asserts exact payload and no polling. | PASS (contract only) |
| AST-04 | Sync exact producer, rerun affected gate, and follow up only same startup handle. | `tools/shared/tests/autonomous-parallelization.test.ts:193-196` asserts sync, gate, same-handle follow-up, and no replacement. | PASS (contract only) |
| AST-05 | Dirty, missing, conflicting, failed, or ambiguous checkpoints serialize without auto-resolution. | `tools/shared/tests/autonomous-parallelization.test.ts:197-200` asserts failure set, serial recovery, and no auto-resolution. | PASS (contract only) |
| AST-06 | Deterministic integration precedes cleanup of only clean integrated owned resources, with zero-residue proof. | `tools/shared/tests/autonomous-parallelization.test.ts:201-241` asserts identity, same-handle cleanup, ordered deletion/absence, and zero residue. | PASS (contract only) |
| AST-07 | Preserve atomic commits/gates, Technical Verifier, frozen review, final QA, full gate, and TLC order. | `tools/shared/tests/autonomous-parallelization.test.ts:242-247` asserts every preserved stage. | PASS (contract only) |
| SEC-001 | Disabled mode performs no adapter probe or mutation. | `tools/test_parallel_executor.py:190-204,1020-1028` asserts construction and resolution never occur. | PASS |
| SEC-002 | Compatibility state is atomic, repository-scoped, and outside `.specs/`. | `tools/test_parallel_executor.py:121-148` asserts location and atomic preservation; `tools/test_orca_adapter.py:282-350` asserts identity binding. | PASS |
| SEC-003 | Host/Git commands use fixed argv, no shell, bounded timeout, and bounded paths. | `tools/test_parallel_executor.py:153-184` asserts argv, `shell is False`, timeout, escape rejection, and symlink rejection. | PASS |
| SEC-004 | Host responses are structured and request-correlated. | `tools/test_orca_adapter.py:201-220` asserts receipt identities; `tools/test_parallel_executor.py:1905-1918` rejects a foreign structured source identity. | PASS |
| SEC-005 | Credential-shaped fields are redacted before diagnostics or persistence. | `tools/test_orca_adapter.py:1769-1794,1803-1833` asserts nested and free-form redaction. | PASS |
| SEC-006 | Compatibility PASS requires settled worker and zero checkout residue. | `tools/test_orca_adapter.py:258-275,443-456` asserts failed cleanup cannot cache PASS and clean removal can. | PASS |
| SEC-007 | Cleanup never revokes a resource without exact ownership. | `tools/test_orca_adapter.py:1586-1605` asserts missing/foreign identity blocks revocation. | PASS |
| SEC-008 | Assisted cleanup targets only clean integrated coordinator-owned resources; missing proof stops deletion. | `tools/shared/tests/autonomous-parallelization.test.ts:201-241` asserts exact-id cleanup, ownership controls, ordered absence proof, and fail-closed deletion. | PASS (contract only) |

**Coverage status**: 30/30 requirements match precise spec outcomes with file:line assertions. No
spec-precision gaps. Contract-only results do not claim E2E-001 execution.

## Discrimination Sensor

Sensor used detached temporary worktree `/tmp/ast01-sensor.I3ozAU/tree` at `4385b25`, with existing
dependencies linked. Scratch was removed. Real-tree binary diff hash before and after was identical:
`2971fec5eaa997c1104fdcede446ba1151db3b57fae55716feadd69df41e42ff`.

| Mutation | Production target | Focused result |
| --- | --- | --- |
| Sent `exec` before unused/unique ownership proof. | `parallelization.md:114-130` | KILLED: IT-005 order assertion failed; 1 failed, 3 passed. |
| Added generic `worktree create --agent`. | `parallelization.md:107` | KILLED: IT-005 negative assertion failed; 1 failed, 3 passed. |
| Weakened unused/unique/activity conjunction from `and` to `or`. | `parallelization.md:120-122` | KILLED: IT-005 exact conjunction assertion failed; 1 failed, 3 passed. |
| Removed shell quoting from Codex model interpolation. | `parallelization.md:89` | KILLED: IT-005 provider command pattern failed; 1 failed, 3 passed. |
| Moved prompt send before rendered-screen read. | `parallelization.md:131-133` | KILLED: IT-005 order assertion failed; 1 failed, 3 passed. |

**Sensor depth**: lightweight, five AST-01 shell-promotion contract mutations.
**Result**: 5/5 killed - PASS.

## Gate Check

- **Focused command**: `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts`
- **Focused result**: 4 passed, 0 failed, 0 skipped.
- **Declared full command**: `npm_config_offline=true npm run test:all`
- **Full result**: exit 0; Vitest 112 passed, 0 failed, 0 skipped; all 13 Python test files exited 0.
- **Structural validators**: `validate_spec.py` and `validate_tasks.py` reported 0 errors, 0 warnings.
- **Diff checks**: `git diff --check` passed before report update; final checks are recorded below.
- **Live execution**: no Orca pilot, canary, worker, terminal, or product QA launched.

## Edge Cases and Quality

- `docs/guidelines/TEST-CONTRACT.md` permits contract-layer prose assertions when the artifact is the
  product contract. IT-005 now asserts exact values and their required order rather than token presence.
- Generic agent-coupled worktree creation, partial ownership guards, unquoted tuple values, early
  promotion, and early prompt delivery all fail the owning suite.
- Remediation is limited to policy, DX, and the canonical contract test; no adapter or executor code changed.

## Requirement Traceability Update

`spec.md` marks AST-01 `Contract verified; E2E pending`. AST-02 through AST-07 and SEC-008 remain
contract-verified with E2E pending.

## Summary

**Overall**: PASS. No technical gaps.

**Spec-anchored check**: 30/30 requirements matched; 0 spec-precision gaps.

**Sensor**: 5/5 mutations killed, including every prior AST-01 survivor class.

**Gate**: focused 4/4; full Vitest 112/112 plus all 13 Python lanes; validators green.

**Next step**: close the AST-01 fingerprint, then dispatch fresh QA Execute for the affected assisted-Orca journey.
