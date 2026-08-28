# Host-Agnostic Slice Parallelization Validation

**Verdict**: PASS
**Date**: 2026-08-27
**Spec**: `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Diff range**: `851d9b5..ec072a9`
**Verifier**: independent Technical Verifier (author != verifier)

## Ranked Gaps

None. Fingerprint `6cbd12e1ef928d5f0ec328c230da0ea6213f577dafe314885c3d562539b35bc0`
is technically resolved: all 12 packet/reconciliation mutants are killed. Real Orca E2E remains
pending and is not claimed by this technical verdict.

## Spec-Anchored Outcomes

| Outcome | Spec-defined result | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| Frozen implementer route | Assisted implementer is exactly `codex` / `gpt-5.6-luna` / `low`; all other routes, cadence, mode, and overrides stay frozen. | `.specs/features/host-agnostic-slice-parallelization/workflow.json:2`-`:49`; `tools/shared/tests/autonomous-parallelization.test.ts:153`-`:164` assert the exact current tuple and current charter/scenario. Resolver read returned the same v2 snapshot. | PASS |
| One send per logical packet | Route, initial task, and follow-up each send once; no blind retry or replacement after any receipt outcome. | `.agents/skills/autonomous/references/parallelization.md:107`-`:112`; packet-scoped assertions at `tools/shared/tests/autonomous-parallelization.test.ts:341`-`:357`. | PASS |
| Bounded same-handle reconciliation | Error, missing receipt, or `agent_prompt_stalled` reconciles only the same connected startup/current handle every 250 ms for at most 300000 ms, with no model turns. | `.agents/skills/autonomous/references/parallelization.md:114`-`:122`; packet-scoped assertions at `tools/shared/tests/autonomous-parallelization.test.ts:355`-`:364`. | PASS |
| Complete effect proof | One exact marker and complete screen/Git/status/commit/gate/comment agreement are required; every partial, dirty, conflicting, wrong-handle, failed, timeout, or ambiguous state serializes. | `.agents/skills/autonomous/references/parallelization.md:118`-`:126`; packet-scoped assertions at `tools/shared/tests/autonomous-parallelization.test.ts:365`-`:378`. | PASS |
| Dependency wait | Waiting remains event-driven and uses no model-turn polling. | `.agents/skills/autonomous/references/parallelization.md:127`-`:128`; exact packet assertion at `tools/shared/tests/autonomous-parallelization.test.ts:379`-`:381`. | PASS |

Historical reports remain historical: `docs/qa/reports/2026-08-26-assisted-orca-slices.md` and
`docs/qa/reports/2026-08-27-assisted-orca-slices.md` still record their executed `high` route. The
current charter/scenario alone moved to `low`; no historical report was rewritten.

## Focused Gates

- `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts`:
  1 file passed; 4/4 tests passed; 0 failed; 0 skipped.
- `npm_config_offline=true npm test -- --run tools/shared/tests/qa-skills.test.ts`:
  1 file passed; 23/23 tests passed; 0 failed; 0 skipped.
- Workflow resolver read with `--feature host-agnostic-slice-parallelization --slices 4
  --native-provider codex`: exit 0; snapshot v2; implementer `codex` / `gpt-5.6-luna` / `low`;
  `grouped.3`, `disabled`, other roles, and overrides unchanged.
- `validate_spec.py`: 0 errors, 0 warnings.
- `validate_tasks.py`: 0 errors, 0 warnings.
- `git diff --check 851d9b5..ec072a9`: PASS.
- Full gate: not run; packet explicitly required focused gates only.

## Discrimination Sensor

Sensor used temporary file copies in disposable directories. No Git worktree, stash, live Orca,
worker, terminal, or QA mutation was created. A temporary standalone Git repository was used only
to give `qa-skills.test.ts` its normal tracked-file semantics. The real checkout porcelain had only
the two pre-existing validation/fingerprint paths before sensor work and had the identical two
entries afterward.

| Mutation | Focused result |
| --- | --- |
| Permit blind resend after ambiguous receipt. | KILLED — autonomous suite 1 failed, 3 passed. |
| Permit replacement worker for the logical packet. | KILLED — autonomous suite 1 failed, 3 passed. |
| Accept a commit alone as success. | KILLED — autonomous suite 1 failed, 3 passed. |
| Change expected phase marker form. | KILLED — autonomous suite 1 failed, 3 passed. |
| Remove multiple-marker rejection. | KILLED — autonomous suite 1 failed, 3 passed. |
| Remove the 300000 ms bound. | KILLED — autonomous suite 1 failed, 3 passed. |
| Change packet reconciliation interval from 250 ms to 251 ms. | KILLED — autonomous suite 1 failed, 3 passed. |
| Permit model turns during effect reconciliation. | KILLED — autonomous suite 1 failed, 3 passed. |
| Replace event-driven dependency waiting with polling. | KILLED — autonomous suite 1 failed, 3 passed. |
| Drift current frozen implementer effort from `low` to `high`. | KILLED — autonomous suite 1 failed, 3 passed. Baseline QA 23/23 still accepts historical reports that record executed `high` routes. |
| Reconcile against a different connected handle. | KILLED — autonomous suite 1 failed, 3 passed. |
| Continue after dirty/gate-failed/wrong-handle/ambiguous state. | KILLED — autonomous suite 1 failed, 3 passed. |

**Sensor result**: 12/12 killed; 0 survived — PASS.

## Quality and Scope

- Diff changes policy/spec/DX/tasks/threat/QA metadata, one frozen snapshot, and the canonical
  contract test; it changes no TypeScript/Python product implementation.
- Current declarative values are internally consistent and historical QA evidence remains intact.
- Packet assertions are scoped to the canonical packet section and discriminate exact route,
  handle, timing, no-model-turn, event-driven, and fail-closed outcomes.
- Real Orca E2E remains pending after technical remediation. This report makes no E2E success claim.

## Summary

**Overall**: PASS. Focused gates green and discrimination is 12/12.

**Next step**: close the technical fingerprint, then run fresh QA Execute for the mini two-slice
Orca E2E. This report does not close the external Orca lifecycle defect.

## Prior validation record (preserved)

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

## QA Execute Retest — 2026-08-27

**Verdict**: FAIL at AST-01 rendered-route proof.

The fresh QA verifier created and seed-gated the disposable integration ground, proved one new,
unique, unused A startup handle, and sent the exact frozen Codex route. Orca returned
`tui-idle: satisfied`, but the immediate `source=screen` read still showed only the startup shell.
No prompt, task edit, task commit, B slice, overlap, verifier, or grouped review followed. Exact
cleanup proved zero `qa-assisted-20260827` worktree, path, branch-ref, or terminal residue.

Durable evidence: `docs/qa/reports/2026-08-27-assisted-orca-slices.md` and
`docs/qa/bugs/BUG-20260827-assisted-orca-tui-idle-before-route-proof.md`.

## Technical Re-verification — 2026-08-27 (`4858934`)

**Scope:** `d0f18e2..4858934`; independent Verifier, author != verifier.

**Technical contract verdict:** PASS. **Real Orca E2E:** pending a fresh QA Execute retest; this
verdict does not claim that the prior QA failure is closed.

### Remediation outcomes

| Spec-anchored outcome | Independent assertion evidence | Result |
| --- | --- | --- |
| Exactly one create; no blind retry; bounded inventory reconciliation adopts only one unambiguous owned candidate. | `tools/shared/tests/autonomous-parallelization.test.ts:174-183` asserts inventory snapshot/difference, exact create count, no blind retry, ambiguity serialization, and complete ownership proof. | PASS |
| Route probe uses exact handle with `timeout_ms=60000`, `interval_ms=250`, and no model turns. | `tools/shared/tests/autonomous-parallelization.test.ts:184-196` asserts exact-handle screen command, timeout, interval, connected handle, probe/dependency separation, and no model turns. | PASS |
| `tui-idle` alone cannot authorize a prompt. | `tools/shared/tests/autonomous-parallelization.test.ts:194-231` rejects pre-send idle sufficiency and orders the first screen before idle, the second screen after idle, and task payload last. | PASS |
| Frozen provider/model/effort appears in two consecutive connected `source=screen` frames before prompt/task edit. | `.agents/skills/autonomous/references/parallelization.md:102-108,158-170` defines exact tuple, two frames, connected handle, prompt ordering, and fail-closed behavior; `tools/shared/tests/autonomous-parallelization.test.ts:186-229` asserts values and lifecycle order. | PASS |
| Dependency waiting remains event-driven, with no polling or model turns. | `.agents/skills/autonomous/references/parallelization.md:185-190,270-275`; `tools/shared/tests/autonomous-parallelization.test.ts:239-240` assert the completion-event waiter and no polling/model turns. | PASS |

### Focused gate and structural checks

- `npm_config_offline=true npm test -- --run tools/shared/tests/autonomous-parallelization.test.ts`:
  1 file passed; 4 tests passed; 0 failed; 0 skipped.
- `validate_spec.py`: 0 errors, 0 warnings.
- `validate_tasks.py`: 0 errors, 0 warnings.
- `git diff --check d0f18e2..4858934`: PASS.

### Discrimination sensor

Temporary file copies only; no Git/Orca worktree and no live Orca effect. Each mutant made IT-005
fail with 1 failed and 3 passed tests:

| Mutation | Result |
| --- | --- |
| Accept one screen instead of two consecutive screens. | KILLED |
| Accept pre-send `tui-idle` alone. | KILLED |
| Remove explicit `timeout_ms=60000`. | KILLED |
| Permit model-turn polling in the materialization probe. | KILLED |
| Permit blind create retry after missing receipt. | KILLED |
| Permit ambiguous candidate adoption. | KILLED |
| Permit two creates instead of exactly one. | KILLED |

**Sensor result:** 7/7 killed; 0 survived. Real-tree `git status --porcelain=v1` was empty before
sensor work and empty after scratch cleanup.

### Ranked gaps

No technical contract gaps. Fresh QA Execute remains required to prove E2E-001 on real Orca and
close `BUG-20260827-assisted-orca-tui-idle-before-route-proof`.

## QA Execute Retest 1 — Invalid / Not Exercised

Retest 1 on 2026-08-27 produced no scenario verdict. Both startup handles reached two consecutive
connected `source=screen` frames with Codex / `gpt-5.6-luna` / `high`, but the coordinator queued
B's follow-up while the prior parked turn still rendered `Working`. This violates the required
end-turn-before-follow-up boundary and cannot close E2E-001 or the route bug. No new product bug was
filed. Exact cleanup removed A, B, and ground; a 60-second late-effect audit ended with zero matching
Orca worktree, terminal, path, branch ref, or Git worktree residue. Fresh QA Execute remains required.

## QA Execute Retest 2 — Invalid / Not Exercised

Retest 2 on 2026-08-27 proved A's two consecutive rendered route frames and completed A:T1 at clean
commit `d931de7` with gate 3/3. Its machine-only helper stopped at a 60-second QA-harness deadline;
the valid `TURN_DONE A_T1` marker arrived later at the worker's reported 1m14s boundary. No B slice,
overlap, checkpoint, sync, Verifier, grouped review, or final QA ran. This is not a product defect or
an E2E verdict. Exact cleanup plus a 60-second late audit returned to the two-worktree baseline with
zero owned residue. Fresh QA Execute remains required.

## QA Execute Retest 3 — Invalid / Not Exercised

Retest 3 on 2026-08-27 used the corrected 300-second turn window. A's exact route rendered twice,
and A:T1 completed cleanly at `78aab41` with gate 3/3. The cursor adapter retained the unique marker
only as escaped/nested rendered TUI data, so its standalone-line predicate timed out even though an
immediate exact-handle screen showed the marker and ready worker. This QA adapter mismatch is not a
product defect or worker-timeout result. No B lane or follow-up ran. Exact cleanup plus a 60-second
audit returned to the two-worktree baseline with zero owned residue. Fresh QA Execute remains
required.

## QA Execute Retest 4 — Invalid / Not Exercised

Retest 4 on 2026-08-27 proved A's two rendered route frames and completed A:T1 cleanly at `155b4fe`
with gate 3/3. The causal cursor response omitted `result.terminal.text` and returned the stream as
a structured `result.terminal.tail` array. The helper read only the missing field and expired its
300-second deadline despite the exact marker in that post-cursor array. This QA adapter mismatch is
not a product defect or E2E verdict. No B lane or follow-up ran. Exact cleanup plus a 60-second
78-sample audit returned to the two-worktree baseline with zero owned residue. Fresh QA Execute
remains required.

## QA Execute Retest 5 — FAIL

Retest 5 on 2026-08-27 passed corrected startup-route proof for A and B, completed and integrated
A:T1 at `94e6056`, and parked B:T9 cleanly at `87ab805` with the exact dependency comment plus full
rendered-screen barrier. A_FINAL's exact same-handle send then returned `agent_prompt_stalled`, while
that handle silently executed A:T7/A:T8 and created commits `976dbc5` and `4e07291`. Because the
machine receipt contradicted the observed terminal/Git effects, exact A:T7 sync and B continuation
could not proceed safely. The coordinator did not retry or create a replacement. The result is a
product/external-interface FAIL deduplicated to
`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree`; Technical Verifiers, grouped
Deep Review, final persona QA, and normal deterministic integration were not reached. Exact cleanup
removed A/B/ground and their branches, paths, and terminals; a 60-second 85-sample audit returned to
the exact two-worktree baseline with zero owned residue.

## QA Execute Retest 8 — FAIL at grouped review

Luna-medium workers produced six green-gated atomic task commits with no corrective commit. The
assisted flow proved 60.694 seconds of A/B overlap, exact B parking, exact A:T7 sync, affected gate,
same-handle continuation, fresh Sol-medium Technical Verifiers, and conflict-free deterministic
A-then-B integration at `2051517` with fixture gate 9/9.

Grouped Deep Review covered 216/216 selected hunk lines in both lanes and returned
`FIX_BEFORE_SHIP`: 0 Critical, 1 Major. The integrated mini CLI removes a terminal newline, so final
persona QA did not run. Exact cleanup removed all three owned worktrees, branches, refs, paths, and
terminals; the 60-second 63-sample audit found zero residue and restored the exact two-worktree
baseline. Durable bug: `BUG-20260827-assisted-pilot-batch-cli-drops-final-newline`.

The closing outer `npm_config_offline=true npm run test:all` gate also failed: Vitest reported
111/112 passing because IT-005 still expected implementer effort `low` instead of the frozen
`medium`. QA skills passed 23/23; spec, tasks, and state validators reported 0 errors; `git diff
--check` passed. Durable bug: `BUG-20260827-medium-route-contract-test-still-expects-low`.

## Technical Verification — pointer packet delivery (2ea7e80..879b677) — FAIL

Fresh Technical Verifier, not the author. Range `2ea7e80..879b677` (`5bc9e31`, `d4de714`, `88ba1fa`,
`92ac013`, `879b677`) on `feat/host-agnostic-slice-parallelization`, tree clean at `879b677`.

```
VERIFICATION
Claim:        the full gate is green on the final tree
Command:      npm_config_offline=true npm run test:all
Executed:     just now, on 879b677 with a clean tree
Exit code:    0
Output:       vitest Test Files 8 passed (8) / Tests 112 passed (112); python suites 28/28, 9/9 OK;
              9, 5, 67, 53, 18, 14, 6, 44 passed, 0 failed
Warnings:     none
Contract:     spec.md AST-04, tests.md IT-005, dx.md, threat-model.md compared — see findings
QA impact:    QAS-coordinate-assisted-orca-slices left at qa_status: fail (see F5)
Verdict:      PASS for the gate claim only
```

### Per-check disposition

| # | Check | Result |
| --- | --- | --- |
| 1 | Gate is real | PASS — run here, exit 0, counts above |
| 2 | No assertion weakened, skipped or deleted | PASS — IT-005 `expect(` 225 -> 232, `.toContain` 182 -> 189, `not.toContain` 14 -> 15; 8 added, 1 removed, none loosened |
| 3 | No compatibility layer survived | PASS in the text, **FAIL in the gate** — F1 |
| 4 | Every unchanged obligation still stated | PASS — one-send/no-retry/no-replacement `parallelization.md:111-113`; 250 ms / 300000 ms `:118`; acceptance conjunction `:118-126`; `B_PARKED`-only comment `:127`; marker `:111`, `:194`; all mirrored in `spec.md:104` |
| 5 | Contract does not overclaim | PASS — `parallelization.md:203-207` and `BUG-...packet.md:78-83` both keep the honest-limits paragraph |
| 6 | Historical QA narratives intact | PASS — `git diff -U0 2ea7e80..879b677` over the scenario and charter yields exactly 2 hunks, both canonical-contract prose; retest 1-10 paragraphs untouched |
| 7 | `AD-016` well-formed, index regenerated in the same commit | PASS — `5bc9e31` touches only `.specs/STATE.md` and `.specs/AD-INDEX.md`; `python3 tools/ad-index.py` reproduces the tracked index with no drift |
| 8 | Bug record does not overclaim | PASS on substance, F4 on form; `BUG-20260827-assisted-pilot-batch-cli-drops-final-newline.md:3` still `open`, zero commits in range |
| 9 | Context budget | PASS — `parallelization.md` 359 -> 368 lines (+9); `AGENTS.md` and `docs/guidelines/*` unchanged in range; naming inconsistency in F2 |

### Discrimination sensor

Six mutants, each applied to the working tree and reverted, `npx vitest run tools/shared/tests/autonomous-parallelization.test.ts`. Baseline 4/4 passed.

| Mutant | Result |
| --- | --- |
| M1 revert the pointer paragraph to the old inline wording | killed (1 failed) |
| M2 add `If the packet is shorter than 4000 characters ... send the packet body directly and skip the packet file.` | **SURVIVED (4 passed)** |
| M3 replace the honest-limits sentence with `This makes the host transport reliable.` | killed |
| M4 `timeout_ms=300000` -> `timeout_ms=30000` | killed |
| M5 drop the marker clause from the packet-file sentence | killed |
| M6 replace `never quote it twice` with `apply shq to it as well` | killed |

### Findings

- **F1 — Major — `tools/shared/tests/autonomous-parallelization.test.ts:195-198`.** The only guard
  against a reintroduced inline path is one exact-string
  `not.toContain("construct \`task_payload\` as the complete slice packet")`. Mutant M2 inserted a
  length-threshold fallback into `parallelization.md` and IT-005 still passed 4/4. `AGENTS.md`
  forbids compatibility layers, fallbacks, and migrations; the gate does not enforce that. Needs a
  guard on the concept (no threshold, no alternative delivery branch), not on the removed sentence.
- **F2 — Minor — `spec.md:104`, `spec.md:152`, `threat-model.md:23`.** One concept now carries three
  names: `packet path allowlist` (spec, threat model), `packet allowlist`
  (`parallelization.md:125`), `changed-path allowlist` (`parallelization.md:196`). The
  disambiguating clause "so it can never dirty a worktree or appear in a changed-path allowlist"
  exists only in `parallelization.md:195-196`. `spec.md:104` names "a coordinator-owned packet file"
  and "packet path allowlist" in the same sentence with no clarifier, so a reader of the normative
  spec alone can read the phrase as "the allowlist that contains the packet file path". The author's
  "resolved in substance" argument holds for the contract file and not for the two that lack the
  clause.
- **F3 — Minor — `parallelization.md:193-199`.** Nothing states that the worker must be able to read
  `packet_file` from outside its own worktree, or what happens when it cannot. It fails closed (no
  marker -> bounded reconciliation -> serialize), so this is not a correctness hole, but an
  unreadable packet path is indistinguishable from a stalled turn and burns the full 300000 ms.
- **F4 — Minor — `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet.md:3`.** Status is
  now `contract routed around — awaiting retest; the host transport defect remains open upstream`,
  while line 82 of the same file says "This record stays open against the host". The three other
  still-open bugs in `docs/qa/bugs/` all begin their status with `open`, so this record no longer
  answers `grep '^- \*\*Status:\*\* open'`. Substance is honest; the greppable prefix is lost.
- **F5 — Minor — `docs/qa/scenarios/QAS-coordinate-assisted-orca-slices.md:9`.** Contract behaviour
  changed, but `qa_status` stayed `fail`. `docs/guidelines/QA-SCENARIOS.md:122` says changed
  behaviour resets the affected files to `untested`. No stale-`pass` hazard, so this is a judgment
  call for the planner.

### Judged: the two author flags

- **`shq` double-quoting — correct and unambiguous.** `task_payload` is built by interpolating
  `packet_file` raw into the pointer, then `shq` is applied once to the finished string, which is
  the only correct order. The earlier blanket rule at `parallelization.md:170-171` ("apply `shq` to
  every value that crosses a shell boundary") is the only source of tension, and
  `parallelization.md:203-204` names that exact case and excludes it: "`packet_file` crosses the
  shell boundary inside that pointer and is covered by that single `shq(payload)`; never quote it
  twice". M6 confirms IT-005 pins the exclusion. No finding.
- **"packet path allowlist" — the non-rename does leave a misreadable contract.** See F2.

**Verdict: FAIL (`FIX_BEFORE_SHIP`).** One Major (F1) plus four Minor. The decided design is
implemented faithfully in the text — no inline path, no threshold, no fallback, every unchanged
obligation intact, no assertion loosened — but the gate does not defend the removal, and a
compatibility layer can be reintroduced green. F1 is a fix task for an Implementer; not fixed here.

## Technical Re-verification — remediation batch `119bf77` — PASS

Fresh Technical Verifier, not the author and not the prior Verifier. Confirms the single atomic
remediation batch `119bf77` `test(parallel): pin unconditional pointer packet delivery` against the
five findings of the preceding `2ea7e80..879b677` FAIL. Tree at `119bf77` clean apart from this file.

```
VERIFICATION
Claim:        the full gate is green on the remediated tree
Command:      npm_config_offline=true npm run test:all
Executed:     on 119bf77, working tree clean apart from validation.md
Exit code:    0
Output:       python suites OK (10, 5, 28, 9 tests); shell/py fixture suites
              9, 5, 67, 53, 18, 14, 6, 44 passed, 0 failed
Command:      npx vitest run
Exit code:    0
Output:       Test Files 8 passed (8) / Tests 112 passed (112)
Verdict:      gate is real and green
```

### Finding disposition

| # | Severity (prior) | Status | Evidence |
| --- | --- | --- | --- |
| F1 | Major | **Partially resolved — downgraded to Minor, recorded residual** | The observed mutant is killed; paraphrase is not. See below. |
| F2 | Minor | **Resolved** | `grep -rn -e "packet path allowlist" -e "packet allowlist"` over `.agents`, the feature spec dir, `docs`, `tools` returns 0 hits. Every site now reads `packet-declared changed-path allowlist`: `parallelization.md:125`, `dx.md:106`, `threat-model.md:23`, `spec.md:104`, `spec.md:152`, `autonomous-parallelization.test.ts:417`. The one remaining bare `changed-path allowlist` at `parallelization.md:196` is the disambiguating clause asserting the packet file is *not* in it, pinned at `autonomous-parallelization.test.ts:182`. |
| F3 | Minor | **Resolved** | `parallelization.md:205`-`:207` states the worker's read obligation and immediate unreadable-path report; pinned by a new `toContain` at `autonomous-parallelization.test.ts:188`-`:190`; mirrored into `tests.md` IT-005. |
| F4 | Minor | **Resolved** | `BUG-20260827-orca-terminal-send-truncates-claude-worker-packet.md:3` now begins `open —`. `grep -l '^- \*\*Status:\*\* open' docs/qa/bugs/*.md \| wc -l` returns 4, matching the four open records; substance unchanged. |
| F5 | Minor | **Resolved** | `QAS-coordinate-assisted-orca-slices.md:9` is `qa_status: untested` with a body paragraph stating the pointer contract has never been walked and Retest 11 must walk it, per `QA-SCENARIOS.md` "changed behaviour resets the affected files to `untested`". |

### Regression checks

| Check | Result |
| --- | --- |
| No assertion weakened, skipped or deleted | PASS — `autonomous-parallelization.test.ts` `expect(` 299 -> 303, `.toContain` 245 -> 246, `not.toContain` 17 -> 17, `.skip/.todo/.only/xit` 0 -> 0. `diff` of every `expect(...` prefix at `879b677` against `119bf77` yields zero removals. |
| `parallelization.md` unchanged obligations | PASS — `git diff --word-diff 879b677 119bf77` on the contract is exactly 2 hunks (`:122` allowlist rename, `:202` F3 sentence). One-send / never-retry `:111`-`:112`, `interval_ms=250` / `timeout_ms=300000` `:118`, `B_PARKED` `:127`, `TURN_DONE` marker `:111` `:194`, `never quote it twice` and the honest-limits sentence `:205` all present and unweakened. |
| `spec.md` AST-04 | PASS — sole change is the allowlist rename; every clause of AST-04 including "write the complete packet body ... to a coordinator-owned packet file outside every slice worktree, issue exactly one send carrying only a short fixed-shape pointer to that file, and never retry or replace" is intact. |
| Historical QA narratives verbatim | PASS — `git diff -U0 2ea7e80 119bf77` over the scenario and charter removes 5 lines total, all canonical-contract prose plus the `qa_status` line. Retest 1-10 paragraphs untouched. |
| `BUG-20260827-assisted-pilot-batch-cli-drops-final-newline` | PASS — `git diff 2ea7e80 119bf77` on that file is empty; status still `open`. |
| Context budget | PASS — `parallelization.md` 368 -> 370 (+2); `AGENTS.md` and `docs/guidelines/*` untouched by `119bf77`. |

### Discrimination sensor — the guard's real discriminating power

All mutants appended one sentence immediately after `so truncation still fails closed instead of
silently half-executing.` in `parallelization.md`, then reverted. Runner
`npx vitest run tools/shared/tests/autonomous-parallelization.test.ts`; baseline 4 passed (4).

| Mutant | Appended sentence | Result |
| --- | --- | --- |
| M2 | `If the packet is shorter than 4000 characters, send the packet body directly and skip the packet file.` | **killed** — 1 failed \| 3 passed, `AssertionError: no size threshold may gate packet delivery` |
| M7 | `When convenient the coordinator sends the packet body itself and omits the packet file.` | **SURVIVED — 4 passed (4)** |
| M8 | `The coordinator may send the packet body itself when the host transport permits.` | **SURVIVED — 4 passed (4)** |
| M9 | `A short packet travels as its own body; a long one travels as a pointer.` | **SURVIVED — 4 passed (4)** |
| M10 | `The coordinator chooses between the pointer and the packet body at its discretion.` | **SURVIVED — 4 passed (4)** |
| M13 | `If the packet is small, send the packet body directly and skip the packet file.` | killed — word-list net |
| M14 | `The inline packet body remains a fallback.` | killed — word-list net |
| M11 | `If the worker cannot read the packet file, it reports the unreadable path at once.` | **killed — FALSE POSITIVE**; this is a correct, natural restatement of the contract's own F3 obligation |
| M12 | `The packet file is written before the send.` | survived (correct: benign prose must not fail) |

Net 1 (numeric size gate) killed 1/1 of the mutants carrying a digit-plus-size-unit and produced no
false positive. Net 2 (word list over `/packet/i` sentences) killed 2 mutants that reuse its own
vocabulary, missed 4 of 4 paraphrases that do not, and killed 1 legitimate edit.

### Judged: can a regex word-list pin this concept?

**No, and further widening is the treadmill `REVIEW-ROUNDS.md` caps exist to stop.**

- **The evasion space is unbounded and the word list is finite.** M7-M10 are four ordinary English
  sentences, none of them adversarial, none containing a listed token. Each round that adds
  `when`, `omits`, `chooses`, `discretion`, `travels`, `permits` leaves the next paraphrase
  untouched. The failure is structural, not a gap in this particular list.
- **The list already damages the artifact it protects.** In this workflow the contract prose *is* the
  product. M11 shows net 2 forbids the natural fail-closed phrasing of a rule the contract must
  state. That is not hypothetical: the F3 sentence added in this very batch is written as "The worker
  must be able to read `packet_file` ... and report an unreadable path at once" precisely because
  "If the worker cannot read ..." would fail the gate. A guard that bans the word `if` from every
  sentence containing `packet`, in a fail-closed protocol specification, degrades the deliverable.
- **`TEST-CONTRACT.md` layer rule.** "Pick the cheapest layer that can discriminate the behaviour."
  Evidence says no layer available here discriminates paraphrase from mandate in prose. Enumerating
  banned synonyms is coverage-chasing, which the same document forbids.
- **`REVIEW-ROUNDS.md` rule 9.** The observed failure was a length-threshold fallback — the shape the
  truncation bug actually tempts. Net 1 kills it. Every further control targets an unobserved
  failure and is therefore itself Major overbuild.

Alternatives weighed and rejected:

- **Golden/exact-block pin on the delivery paragraph.** Would kill M7-M10, which were appended inside
  that paragraph. But it is blind to the same sentence placed one paragraph away, and it converts
  every legitimate edit into a gate failure with an unreadable message. It buys nothing against a
  motivated author and taxes every honest one.
- **Assert the count of packet-delivery sentences** (currently 8, pinned only as `> 3`). Defeated by
  one synonym: a sentence saying "the body" rather than "the packet" never enters the filtered set.
  Same treadmill, worse diagnostics.
- **Accept the residual and record it. Chosen.** The seven exact-string `toContain` pins at
  `autonomous-parallelization.test.ts:178`-`:196` already make the mandate unremovable and
  unrewordable — removing or altering "The packet body never crosses `terminal send`", the pointer
  construction, or the no-dirty-worktree clause fails the gate. What no regex can prevent is an
  *added contradicting sentence*, which leaves the contract self-contradictory with the mandate
  still asserted. Detecting self-contradiction in prose is a reader's job, and
  `REVIEW-ROUNDS.md` rule 8 already requires a second reader on a documentation-only slice.

**Recommendation: stop hardening IT-005 here.** Keep both nets as shipped; do not widen the word
list; do not open a round 3. Record the residual as below.

### Recorded residual

> IT-005's guard against a reintroduced inline-payload path defends the mandate's *presence and
> wording* exactly, and defends against *reintroduction phrased in the banned vocabulary or carrying
> a numeric size threshold*. It does not and cannot detect a free-paraphrase sentence added elsewhere
> in `parallelization.md` that contradicts the mandate. That class is caught by the second reader
> required on every slice, not by the gate. Widening the word list is explicitly out of scope.

Advisory (non-blocking, not a finding): `QAS-coordinate-assisted-orca-slices.md:12` keeps
`retest_status: fail` while `fix_status` is `pending`; `QA-SCENARIOS.md:71` makes `retest_status`
meaningful only when `fix_status: fixed`, so the value is stale residue. Cosmetic, pre-existing, file
an issue.

**Verdict: PASS.** F2-F5 resolved, F1's observed failure path closed and its unpinnable remainder
downgraded to a recorded Minor residual, no obligation weakened, no assertion loosened, gate green.

---

## Slice E Technical Verification — 2026-08-27

**Spec:** `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Diff range:** `a627e28..35df588` (`T6` `431c7d3`; `T7` `35df588`)
**Verifier:** independent sub-agent (author != verifier)
**Verdict:** **FAIL**

### Task completion

| Task | Recorded state | Verification result |
| --- | --- | --- |
| T6 | complete | PASS — HST-05 is implemented and discriminated. |
| T7 | complete | FAIL — AST-08 is not fully implemented or discriminated. |

### Spec-anchored acceptance evidence

| Requirement / test | Spec-defined outcome | `file:line` assertion evidence | Result |
| --- | --- | --- | --- |
| HST-05 / UT-007 | Missing mode freezes `assisted`; every explicit `disabled|assisted|safe|full` value survives unchanged. | `tools/test_workflow_config.py:107-113` asserts the exact default snapshot; `tools/test_workflow_config.py:121-152` iterates all four explicit modes and asserts both emitted and stored values. | PASS |
| HST-06 / UT-008 | Assisted planning has `full` readiness and checkpoint-sync semantics. | `tools/test_parallel_plan.py:131-145` asserts exact lane and blocked equality with `full` and `sync_after == ["T1"]`; `tools/test_parallel_plan.py:151-174` asserts waiting, conflict serialization, and malformed-metadata serialization. | PASS |
| HST-06 / IT-006 | Assisted `start` and `resume` expose a coordinator plan without automatic-adapter construction or invocation. | `tools/test_parallel_executor.py:209-240` asserts the assisted coordinator result and an unconstructed injected adapter; `tools/test_parallel_executor.py:246-273` asserts both CLI commands and `calls == []`. | PASS |
| AST-08 / IT-006 — explicit disabled | Sequential result with zero planner, Git, or adapter effects. | `tools/test_parallel_executor.py:1663-1705` instruments the planner, repository preparation, Git adapter, and adapter factory and asserts zero calls. | PASS |
| AST-08 / UT-008 — conflict/malformed DAG | Write conflicts and malformed metadata serialize. | `tools/test_parallel_plan.py:151-174` asserts `fallback is True`, serial lane identity, and exact reason. | PASS |
| AST-08 / IT-006 — fewer than two ready slices | Sequential result; no assisted lane. | No assertion. Existing assisted executor tests provide exactly two ready lanes at `tools/test_parallel_executor.py:226-229,259-262`. Removing the production guard survived all 55 executor tests. | FAIL |
| AST-08 / IT-006 — failed resource proof | Sequential result with zero host effect. | No assertion. Production returns an assisted coordinator plan at `.agents/skills/autonomous/scripts/parallel_execute.py:1278-1281` before resource/provider validation at `.agents/skills/autonomous/scripts/parallel_execute.py:1304-1313`. A real two-lane assisted plan containing `resources: ["gpu"]` and no configured provider returned `fallback: false`. | FAIL |

### Gate evidence

- `rtk proxy python3 tools/test_workflow_config.py` — exit 0, `44 passed, 0 failed`.
- `rtk proxy python3 tools/test_parallel_plan.py` — exit 0, `20 passed, 0 failed`.
- `rtk proxy python3 tools/test_parallel_executor.py` — exit 0, `55 passed, 0 failed`.
- Slice E total: 119 passed, 0 failed, 0 skipped. Baseline command `rtk git show a627e28:<test-file> | rg -c '^def test_'` for the three owning suites returned 44, 18, and 53 test functions: 115 total; delta +4.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/host-agnostic-slice-parallelization/spec.md` — exit 0, 0 errors, 0 warnings.
- `rtk python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/host-agnostic-slice-parallelization/tasks.md` — exit 0, 0 errors, 0 warnings.
- `rtk git diff --check` — exit 0.

### Discrimination sensor

Each mutant ran in a detached temporary worktree at `35df588`; every scratch worktree was removed.

| Mutant | Behavior fault | Targeted command | Result |
| --- | --- | --- | --- |
| M1 | Changed `PARALLELIZATION_DEFAULT` from `assisted` to `disabled`. | `rtk python3 tools/test_workflow_config.py` | KILLED — `test_defaults_and_native_routing` failed its exact snapshot assertion. |
| M2 | Removed `assisted` from the completed cross-slice `sync_after` branch. | `rtk python3 tools/test_parallel_plan.py` | KILLED — `test_assisted_mode_matches_full_readiness_and_checkpoint_plan` failed lane equality. |
| M3 | Disabled the `len(lanes) < 2` assisted serial guard. | `rtk python3 tools/test_parallel_executor.py` | **SURVIVED — 55 passed, 0 failed.** |

**Sensor:** 3 mutations, 2 killed, 1 survived — FAIL. Real-tree porcelain after scratch cleanup matched the empty pre-sensor baseline before this report edit.

### Ranked gaps and fix tasks

1. **Major — assisted resource lanes bypass fail-closed resource proof (AST-08 / IT-006).** Premise: `.agents/skills/autonomous/scripts/parallel_execute.py:1278-1281` returns the coordinator plan before `.agents/skills/autonomous/scripts/parallel_execute.py:1304-1313` checks lane resource metadata and provider availability. Path: two otherwise-ready assisted slices, one declaring `gpu`, with no resource provider configured return `fallback: false`; the main agent receives a certified assisted plan instead of the required sequential result. Fix task: validate assisted isolation/resource prerequisites before returning the coordinator plan, then extend canonical IT-006 with the real resource-bearing plan and assert sequential output plus zero adapter/Git/host effects.
2. **Major — IT-006 does not discriminate the no-ready-overlap fallback (AST-08).** Premise: both assisted fixtures at `tools/test_parallel_executor.py:226-229,259-262` contain two ready lanes. Path: deleting `.agents/skills/autonomous/scripts/parallel_execute.py:1279-1280` leaves all 55 executor tests green, so one ready lane can regress to an uncertified assisted result undetected. Fix task: extend IT-006 with `start` and `resume` plans containing zero and one ready lane; assert exact sequential fallback and zero automatic-adapter/Git/host effects.

### Status

HST-05 and HST-06 are verified for Slice E. AST-08 remains **Needs Fix**. Slice E is not ready to integrate.

---

## Slice E AST-08 Follow-up Remediation — 2026-08-27

**Spec:** `.specs/features/host-agnostic-slice-parallelization/spec.md`
**Scope:** Follow-up to the preceding Slice E technical verification
**Verdict:** **PASS for AST-08**

The assisted branch now performs the existing worktree/resource/provider preflight before it can
return a coordinator plan. A real two-lane plan with `resources: ["gpu"]` and no configured
provider returns `missing-resource-provider` with no adapter or host effect. IT-006 now covers
zero and one ready lane for both `start` and `resume`; each returns `no-ready-overlap` serial
fallback and no automatic effect.

| Requirement | Evidence | Result |
| --- | --- | --- |
| AST-08 — fewer than two ready slices | `tools/test_parallel_executor.py:246-273` asserts exact sequential fallback for zero and one ready lane across both entry points, with empty effects. | PASS |
| AST-08 — failed resource/provider proof | `tools/test_parallel_executor.py:276-313` uses a two-lane `gpu` plan without a provider and asserts `missing-resource-provider`, unchanged lanes, and no adapter effect. | PASS |
| HST-06 — assisted plan boundary | `tools/test_parallel_executor.py:209-240,320-349` continues to assert coordinator planning without adapter construction/selection. | PASS |

### Follow-up gate evidence

- `python3 tools/test_parallel_executor.py` — exit 0; 57 passed, 0 failed, 0 skipped.
- `python3 tools/test_parallel_plan.py` — exit 0; 20 passed, 0 failed, 0 skipped.
- `python3 tools/test_workflow_config.py` — exit 0; 44 passed, 0 failed, 0 skipped.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/host-agnostic-slice-parallelization/spec.md` — exit 0; 0 errors, 0 warnings.
- `python3 .agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/host-agnostic-slice-parallelization/tasks.md` — exit 0; 0 errors, 0 warnings.
- `git diff --check` — exit 0.

Fingerprint `27e805c6f297d78d6b374eee5343c3d6347073c613a19b45a1ce76741ab9eea7` is resolved. T6
and T7 remain complete in `tasks.md`; no spec requirement or historical QA evidence was changed.
