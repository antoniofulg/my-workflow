# BUG-20260826-deep-review-peak-bound-gate-flakes

- **Status:** fixed
- **Fix commit:** pending delivery hash
- **Severity:** major
- **Scenario:** `QAS-run-bounded-parallel-deep-review` (gate owner; its prior public verdict is not disproven by the below-bound observations)
- **Expected:** The declared full gate is deterministic. Peak-concurrency fixtures either prove the contracted exact occupancy with deterministic synchronization or assert only the owning bounded-overlap invariant.
- **Observed:** Two clean `npm_config_offline=true npm run test:all` attempts failed in different exact-peak assertions. Gate 1 observed `5` instead of `6` in `test_drm02_peak_active_is_exact_bound_and_effective_min`; the isolated owning test then passed. Gate 2 observed `2` instead of `3` in `test_drm04_retries_do_not_expand_peak_worker_bound`. Both observed peaks still showed overlap and stayed below the configured cap.
- **Adapter:** Checkout-local CLI/manual through the package-owned full gate
- **Exact path:** `npm_config_offline=true npm run test:all` → `npm run test:python` → `python3 tools/test_deep_review_token_metrics.py`
- **Evidence:** `docs/qa/evidence/2026-08-26-host-adapter-compatibility/final-gate.json`; `docs/qa/reports/2026-08-26-host-adapter-compatibility.md`

## Reproduction

1. From the active checkout, run `npm_config_offline=true npm run test:all`.
2. Observe one exact-peak assertion may underfill its expected scheduler occupancy while remaining within the configured bound.
3. Re-run the isolated failed test; the first observed failure passed alone.
4. Re-run the full gate once; a second exact-peak assertion failed with another below-bound value.

Both full-gate attempts left Git and Orca Run/Task/worker/worktree/terminal inventories unchanged and retained the same eight pre-existing pilot sibling residues.

## Smallest remediation

Keep the contracted assertion strong. Make the peak fixture deterministically rendezvous the initial worker wave before any helper exits, including the retry wave, so exact saturation is evidence rather than an OS-scheduling race. If the owning acceptance criterion does not promise exact saturation, clarify that criterion first and then assert the named bounded-overlap invariant; do not weaken the test merely to make the gate pass.

Regression recommendation: run both peak tests repeatedly under the canonical `tools/test_deep_review_token_metrics.py` suite and then run the declared full gate. A fresh Verifier must re-run this host-adapter charter plus the bounded Deep Review adjacent canary after the fix.
