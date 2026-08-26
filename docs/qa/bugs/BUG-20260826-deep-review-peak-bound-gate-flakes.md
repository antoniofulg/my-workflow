# BUG-20260826-deep-review-peak-bound-gate-flakes

- **Status:** closed — technical verification and fresh QA retest PASS
- **Fix commits:** `ae1b7d06c22d9431dba91e5ef64d00fd0561169b`, `cd1886f125da26c7792333bda777728d41fd4ee2`
- **Severity:** major
- **Scenario:** `QAS-run-bounded-parallel-deep-review` (gate owner; its prior public verdict is not disproven by the below-bound observations)
- **Expected:** The declared full gate is deterministic. Peak-concurrency fixtures either prove the contracted exact occupancy with deterministic synchronization or assert only the owning bounded-overlap invariant.
- **Observed:** Two clean `npm_config_offline=true npm run test:all` attempts failed in different exact-peak assertions. Gate 1 observed `5` instead of `6` in `test_drm02_peak_active_is_exact_bound_and_effective_min`; the isolated owning test then passed. Gate 2 observed `2` instead of `3` in `test_drm04_retries_do_not_expand_peak_worker_bound`. Both observed peaks still showed overlap and stayed below the configured cap.
- **Adapter:** Checkout-local CLI/manual through the package-owned full gate
- **Exact path:** `npm_config_offline=true npm run test:all` → `npm run test:python` → `python3 tools/test_deep_review_token_metrics.py`
- **Evidence:** `docs/qa/evidence/2026-08-26-host-adapter-compatibility/final-gate.json`; `docs/qa/reports/2026-08-26-host-adapter-compatibility.md`; `.specs/features/parallel-deep-review/validation.md`

## Reproduction

1. From the active checkout, run `npm_config_offline=true npm run test:all`.
2. Observe one exact-peak assertion may underfill its expected scheduler occupancy while remaining within the configured bound.
3. Re-run the isolated failed test; the first observed failure passed alone.
4. Re-run the full gate once; a second exact-peak assertion failed with another below-bound value.

Both full-gate attempts left Git and Orca Run/Task/worker/worktree/terminal inventories unchanged and retained the same eight pre-existing pilot sibling residues.

## Smallest remediation

Keep the contracted assertion strong. Make the peak fixture deterministically rendezvous the initial worker wave before any helper exits, including the retry wave, so exact saturation is evidence rather than an OS-scheduling race. If the owning acceptance criterion does not promise exact saturation, clarify that criterion first and then assert the named bounded-overlap invariant; do not weaken the test merely to make the gate pass.

Regression recommendation: run both peak tests repeatedly under the canonical `tools/test_deep_review_token_metrics.py` suite and then run the declared full gate. A fresh Verifier must re-run this host-adapter charter plus the bounded Deep Review adjacent canary after the fix.

The retry-wave remediation also records a lock-protected participant/attempt/occupancy ledger. The
regression assertion requires the retry worker and still-active siblings to prove the exact peak
occupancy, so removing either retry rendezvous cannot produce a false PASS.

## Technical revalidation

Commit `cd1886f` passed 20 consecutive focused iterations (40 test executions) and the declared
`npm_config_offline=true npm run test:all` gate. The exact saturation assertions remain unchanged,
and production `.agents/skills/deep-review/scripts/run_jobs.py` has blob
`649ff2ed10900f759bc637c3f73ee0e1ee9ce447` at both `ae1b7d0` and `HEAD`.

The retry-wave ledger assertion names exactly three participants, exact participant/attempt pairs,
retry occupancy `3`, and positive sibling occupancy at
`tools/test_deep_review_token_metrics.py:369-377`. Isolated file-copy sensors killed both removal of
the initial-wave rendezvous (`2 != 6`) and full bypass of retry readiness plus both retry
rendezvous calls (missing `retry-wave.ledger`). Full verification preserved all 11 existing
checkout changes, six worktrees, 131 project pilot residue directories, eight temp pilot residue
directories, and zero focused Deep Review residue; every measured delta was zero.

## Fresh QA retest

At `cd1886f125da26c7792333bda777728d41fd4ee2`, a fresh Verifier ran both formerly flaky owning tests
together: exit `0`, `2/2` passed. The declared `npm_config_offline=true npm run test:all` gate then
exited `0`: Vitest `8/8` files and `110/110` tests passed, and every package-discovered Python suite
passed. The affected host-adapter journey also passed, and all measured Git, Orca, pilot, and focused
Deep Review residue deltas were zero. Retest evidence:
`docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/`; report:
`docs/qa/reports/2026-08-26-host-adapter-compatibility.md`.
