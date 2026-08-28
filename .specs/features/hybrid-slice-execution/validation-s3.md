# Hybrid Slice Execution: CP-S3 Validation

**Verdict:** PASS
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `9d5f9cc..0340cbe`
**Verifier:** fresh independent Technical Verifier (author != verifier)

## PASS

CP-S3 is releasable. The scheduler preserves the configured cap across resume, malformed scheduler
state fails before effects, and persisted heavy-gate state must match its lane, action, request,
receipt, lease, resources, and idempotency identities before authorization or release. Nine
discrimination mutations were killed. Direct provider calibration recorded zero releases for
forged, mismatched, and reused leases, and exactly one release for an owned matching lease.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T9 | Done | Normalized, redacted health evidence controls admission above two. |
| T10 | Done | Dynamic refill, checkpoint parking, and current-cap resume are proved. |
| T11 | Done | Heavy gates use one correlated provider lease path and fail closed on foreign state. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | Evidence and assertion | Result |
| --- | --- | --- | --- |
| HSE-16 | One healthy settle window admits at most one lane, up to four. | `tools/test_machine_health.py:26`-`:28` asserts healthy 2→3→4 admission bounds; `tools/test_parallel_executor.py:2326`-`:2327` asserts one added task and cap 3. | PASS |
| HSE-17 | Missing, malformed, stale, or pressured evidence admits no lane above two. | `tools/test_machine_health.py:34`-`:45` enumerates each invalid or pressured case and asserts `False` while the fresh case remains `True`. | PASS |
| HSE-18 | An integer cap is never exceeded and health remains required above two. | `tools/test_machine_health.py:29`-`:31` asserts caps 3 and 1; `tools/test_parallel_executor.py:2423`-`:2446` resumes saved cap 4 under current cap 1 and asserts only T1, one active lane, and zero adapter/provider/worktree effects. | PASS |
| HSE-19 | A free lane receives the next dependency-, path-, and resource-compatible slice. | `tools/test_parallel_executor.py:2330`-`:2342` parks the overlapping task and asserts T3 refills the slot. | PASS |
| HSE-20 | Only concurrent Implementer writers receive persistent worktrees. | `tools/test_parallel_plan.py:198`-`:215` asserts exactly two selected writer worktrees and `False` for Planner, coordinator, Explorer, Verifier, Deep Reviewer, QA Plan, and QA Execute. | PASS |
| HSE-21 | Heavy gates acquire and release through the configured provider. | `tools/test_parallel_executor.py:2345`-`:2378` asserts one acquire, exclusive contention, light-lane eligibility, and one correlated release. | PASS |
| HSE-40 | Malformed or foreign scheduler/state/provider identities fail before the next mutation. | `.agents/skills/autonomous/scripts/parallel_execute.py:315`-`:323` enforces the scheduler schema; `parallel_execute.py:175`-`:278` validates every heavy-gate identity and receipt; `tools/test_parallel_executor.py:2451`-`:2463` and `:2468`-`:2499` assert invalid cap and forged lease rejection with zero release. | PASS |
| HSE-42 | Health diagnostics expose only normalized, redacted values. | `tools/test_machine_health.py:48`-`:64` asserts the exact bounded schema and primitive values; `tools/test_machine_health.py:67`-`:77` asserts the injected absolute path/command/env marker never appears. | PASS |
| HSE-45 | A moved checkpoint remains parked until synchronization and re-verification. | `tools/test_parallel_executor.py:1624`-`:1671` asserts `gate_required`, zero worker before the matching passing receipt, and dispatch only after re-verification. | PASS |
| HSE-48 | Failed or foreign heavy-gate lease cannot authorize/release while unrelated light work remains eligible. | `tools/test_parallel_executor.py:2369`-`:2378` asserts lane B remains eligible while the conflicting gate parks; `tools/test_parallel_executor.py:2383`-`:2411` asserts a foreign lane releases zero; `:2468`-`:2499` asserts a forged persisted lease releases zero. | PASS |

**Spec result:** 10/10 scoped requirements match their exact outcomes.

## Gate evidence

- `python3 tools/test_machine_health.py` -> exit 0, 4 passed, 0 failed.
- `python3 tools/test_parallel_plan.py` -> exit 0, 23 passed, 0 failed.
- `python3 tools/test_parallel_executor.py` -> exit 0, 55 passed, 0 failed.
- `npm_config_offline=true npm run test:all` -> exit 0; Vitest 8/8 files and 114/114 tests
  passed; every Python contract suite passed with no reported failure or skip.
- `python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py .specs/features/hybrid-slice-execution/tasks.md --strict` -> exit 0, 0 errors, 0 warnings.
- `git diff --check 9d5f9cc..0340cbe` -> exit 0.
- No live Orca command ran.

## Discrimination sensor

All mutations ran at `0340cbe` in detached disposable worktree
`/tmp/hse-s3-sensor.dXhI8w`, removed after the sensor.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Pressured or stale normalized health authorizes an added lane. | KILLED by `tools/test_machine_health.py:44`. |
| M2 | Initial automatic scheduler capacity starts at four instead of two. | KILLED by `tools/test_parallel_executor.py:2298`. |
| M3 | A scheduler with an active lane never refills a free compatible slot. | KILLED by `tools/test_parallel_executor.py:2342`. |
| M4 | A dirty integration baseline bypasses planner rejection. | KILLED by `tools/test_parallel_plan.py:261`. |
| M5 | A foreign lane may release another lane's heavy-gate lease. | KILLED by `tools/test_parallel_executor.py:2408`-`:2411`. |
| M6 | Overlapping exclusive heavy gates may acquire concurrently. | KILLED by `tools/test_parallel_executor.py:2374`-`:2375`. |
| M7 | Resume restores saved cap 4 without clamping current explicit cap 1. | KILLED by `tools/test_parallel_executor.py:2444`-`:2446`. |
| M8 | Runtime-state validation accepts a non-integer scheduler cap. | KILLED by `tools/test_parallel_executor.py:2459`-`:2463`. |
| M9 | Heavy-gate correlation validation is bypassed before release. | KILLED by `tools/test_parallel_executor.py:2494`-`:2499`. |

**Sensor result:** 9/9 injected mutants killed, 0 survived.

Direct effect-count calibration on the unmodified tree:

- saved cap 4/current explicit cap 1 selected one task and created zero adapter/provider/worktree effects;
- invalid cap failed before effects;
- mismatched idempotency: provider acquire 1, release 0;
- reused lease identity: provider acquire 2, release 0;
- forged resources: provider acquire 1, release 0;
- matching owned lease: provider acquire 1, two logical releases, exactly one physical release.

Isolation proof:

- Before sensor: `git status --porcelain` empty; `git worktree list --porcelain | rg '^worktree' | wc -l` returned `2`.
- During sensor: the detached scratch raised the worktree count to `3`.
- After cleanup: porcelain empty; worktree count returned to `2`.

## Runtime-state and resource design check

- `.agents/skills/autonomous/scripts/parallel_execute.py:315`-`:323` validates the exact scheduler
  schema and non-negative integer identities.
- `.agents/skills/autonomous/scripts/parallel_execute.py:168`-`:278` validates the exact heavy-gate
  schema, unique lease IDs, lane/slice/task/gate identity, idempotency, resources, redacted
  environment, acquire action, release action, requests, and receipts.
- `.agents/skills/autonomous/scripts/parallel_execute.py:433` invokes that validator on every runtime
  validation; `parallel_execute.py:1489` and `:1571` invoke it before acquire or release effects.
- `rg -n 'flock|lockfile|daemon|socket|threading|multiprocessing|portalocker|fasteners|filelock' ...`
  returned no matches. No second lock, daemon, service, or dependency was added.

## Fingerprint disposition

- `8ccdc7b20fdcb442684ec6b293d0edae62d75345bb9219cd43bb97ac73f1e294`: remediation
  independently PASSed with the full gate green; close generation 1 without increasing its failure count.
- `bf15da19f4be51b558f1c3cd35c5af541f78e57ef476a6ca3f759b0baa43f040`: remediation
  independently PASSed with the full gate green; close generation 1 without increasing its failure count.

No new lesson is recorded. All scoped criteria and mutants passed; the existing lessons already
capture fail-closed persisted-state validation and effect correlation.

## Code quality

The changes are stdlib-only and reuse the existing scheduler, runtime-state validator, provider,
and idempotency key. No alternate lock or execution service exists. The diff is limited to the
adaptive scheduler, its canonical tests, and workflow evidence. Guidelines followed:
`.agents/skills/workflow-spec-driven/references/validate.md`,
`.agents/skills/workflow-spec-driven/references/coding-principles.md`, and
`docs/guidelines/REVIEW-ROUNDS.md`.

## Summary

**Overall:** PASS. CP-S3 may release S6. No ranked gap remains.
