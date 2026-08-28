# Hybrid Slice Execution: CP-S3 Validation

**Verdict:** FAIL
**Date:** 2026-08-28
**Phase:** Technical
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Diff range:** `9d5f9cc..63bb15c`
**Verifier:** fresh independent Technical Verifier (author != verifier)

## FAIL

CP-S3 is not releasable. Healthy admission, refill, checkpoint parking, redaction, normal gate
serialization, and six discrimination mutations pass. Two untested restart/correlation paths violate
the exact spec: a persisted scheduler cap can bypass a smaller explicit `max_workers`, and forged
persisted heavy-gate state can release a foreign lease.

## Task completion

| Task | Status | Notes |
| --- | --- | --- |
| T9 | Done, verification gap | Normal health and redaction paths pass. |
| T10 | Needs fix | Persisted scheduler capacity is not clamped to the current explicit cap. |
| T11 | Needs fix | Persisted `heavy_gates` state lacks correlation validation before release. |

## Spec-anchored acceptance criteria

| Requirement | Spec-defined outcome | Evidence and assertion | Result |
| --- | --- | --- | --- |
| HSE-16 | One healthy settle window admits at most one lane, up to four. | `tools/test_machine_health.py:24`-`:31` asserts 2→3→4 and ceiling; `tools/test_parallel_executor.py:2302`-`:2327` asserts exactly one selected lane and cap 3. | PASS |
| HSE-17 | Missing, malformed, stale, or pressured health admits no lane above two. | `tools/test_machine_health.py:34`-`:45` enumerates missing, invalid schema, stale, CPU, memory, and disk pressure and asserts `False`. | PASS |
| HSE-18 | Integer `max_workers` is never exceeded and health remains required above two. | `tools/test_machine_health.py:29`-`:31` covers fresh helper calls, but `.agents/skills/autonomous/scripts/parallel_execute.py:663`-`:665` restores a persisted cap against ceiling 4 rather than the current explicit cap. Calibration with `max_workers=1`, saved cap 4 selected `['T1','T2','T3','T4']`. | FAIL |
| HSE-19 | A freed lane receives the next compatible ready slice. | `tools/test_parallel_executor.py:2330`-`:2342` keeps the conflicting candidate parked and asserts `T3` fills the slot. | PASS |
| HSE-20 | Only concurrent Implementer writers receive persistent worktrees. | `tools/test_parallel_plan.py:198`-`:215` asserts two selected writer worktrees and `False` for Planner, coordinator, Explorer, Verifier, Deep Review, and QA roles. | PASS |
| HSE-21 | Heavy gates acquire and release through the configured provider. | `tools/test_parallel_executor.py:2345`-`:2378` asserts one acquire, competing gate parked, one correlated release. | PASS |
| HSE-40 | Malformed or foreign state/receipts fail before the next mutation. | `.agents/skills/autonomous/scripts/parallel_execute.py:182`-`:310` validates lanes/actions but never `heavy_gates`; `:1428`-`:1457` trusts that unvalidated record for release. A forged `foreign-run-lease` produced one physical `provider.release`. | FAIL |
| HSE-42 | Health diagnostics expose only normalized, redacted values. | `tools/test_machine_health.py:48`-`:64` asserts exact key/value types; `:67`-`:77` asserts a home/path/command/env marker is absent. | PASS |
| HSE-45 | A moved checkpoint remains parked until synchronization and re-verification. | `tools/test_parallel_executor.py:1624`-`:1671` asserts `gate_required`, no worker before gate, and worker only after matching passing receipt. | PASS |
| HSE-48 | Failed/foreign heavy-gate lease cannot authorize work or release while light work remains eligible. | Normal contention is asserted at `tools/test_parallel_executor.py:2372`-`:2378`, but forged persisted gate state bypasses correlation and physically releases another run's lease. | FAIL |

**Spec result:** 8/10 scoped requirements match exact outcomes; HSE-18 and HSE-40/HSE-48 fail.

## Gate evidence

- `python3 tools/test_machine_health.py` -> exit 0, 4/4 passed.
- `python3 tools/test_parallel_plan.py` -> exit 0, 23/23 passed.
- `python3 tools/test_parallel_executor.py` -> exit 0, 52/52 passed.
- `npm_config_offline=true npm run test:all` -> exit 0; 8/8 Vitest files and 114/114 tests passed;
  every Python contract suite passed with no reported failure or skip.
- `git diff --check 9d5f9cc..63bb15c` -> exit 0.
- No live Orca command ran.

## Discrimination sensor

All mutations ran in detached disposable worktrees at `63bb15c`.

| Mutation | Fault | Result |
| --- | --- | --- |
| M1 | Pressured/stale normalized health sets `admit_one=true`. | KILLED: health suite exits 1 at the deny-above-baseline assertion. |
| M2 | Initial auto scheduler capacity starts at four instead of two. | KILLED: executor suite exits 1 on one-lane healthy admission. |
| M3 | A scheduler with an existing lane never refills a free slot. | KILLED: executor suite exits 1 on expected `T3`. |
| M4 | Dirty integration baseline bypasses planner rejection. | KILLED: planner suite exits 1 on expected `decision == 'blocked'`. |
| M5 | Foreign lane may release a heavy-gate lease. | KILLED: executor suite detects forbidden release. |
| M6 | Overlapping exclusive heavy gates may acquire concurrently. | KILLED: executor suite expected second acquire to return `None`. |

**Sensor result:** 6/6 injected mutants killed, 0 survived. Two separate calibration cases exposed
the untested real defects above.

Isolation proof:

- Before sensor: `git status --porcelain` empty; `git worktree list --porcelain | rg '^worktree' | wc -l` returned `2`.
- During each mutation: one detached scratch raised count to `3`.
- After cleanup: porcelain empty; worktree count returned to `2`.

## Ranked gaps and fingerprints

1. **Major — HSE-18.** Premise: `.agents/skills/autonomous/scripts/parallel_execute.py:663`-`:665`
   restores saved scheduler capacity without clamping to explicit `max_workers`. Path: resume state
   with `max_workers=1`, `scheduler.cap=4` -> scheduler selects four writers -> user cap is bypassed.
   Fingerprint `8ccdc7b20fdcb442684ec6b293d0edae62d75345bb9219cd43bb97ac73f1e294`,
   generation 1, failed remediations 1, status open.
2. **Blocker — HSE-40/HSE-48.** Premise: runtime validation at
   `.agents/skills/autonomous/scripts/parallel_execute.py:182`-`:310` omits `heavy_gates`. Path: a
   foreign persisted lease is placed under the current gate/lane -> release trusts it ->
   `provider.release('foreign-run-lease')` executes once. Fingerprint
   `bf15da19f4be51b558f1c3cd35c5af541f78e57ef476a6ca3f759b0baa43f040`, generation 1,
   failed remediations 1, status open.

## Required fix tasks

1. Clamp restored scheduler capacity to the resolved configured cap and add a restart case proving
   cap 1 and cap 3 cannot inherit a larger prior cap.
2. Validate every persisted heavy-gate identity against its lane, gate, action, resources,
   idempotency key, and acquire receipt before authorization or release; add a forged-state case
   asserting zero acquire/release calls while unrelated light work remains eligible.

## Code quality

New code is stdlib-only and localized. Normal paths are small and readable. Release cannot pass while
persisted state bypasses explicit user policy or can mutate a foreign provider lease. Guidelines:
`.agents/skills/workflow-spec-driven/references/validate.md`, `docs/guidelines/TEST-CONTRACT.md`, and
`docs/guidelines/REVIEW-ROUNDS.md`.

## Summary

**Overall:** FAIL. CP-S3 stays blocked until both fingerprints receive implementation fixes, focused
green gates, a green full gate, and fresh independent re-verification.
