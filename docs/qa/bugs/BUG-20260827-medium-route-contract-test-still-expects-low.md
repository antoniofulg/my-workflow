# BUG-20260827-medium-route-contract-test-still-expects-low

- **Status:** fixed
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** The canonical assisted-parallelization contract test agrees with the frozen Luna-medium worker route introduced by `40f2d55`, and the outer full gate is green.
- **Observed:** `tools/shared/tests/autonomous-parallelization.test.ts:155` still asserts `implementer.effort === "low"`; the final full gate failed with 111 passed and 1 failed.
- **Adapter:** Repository structural gate
- **Exact path:** `npm_config_offline=true npm run test:all` -> Vitest -> IT-005
- **Evidence:** `docs/qa/reports/2026-08-27-assisted-orca-slices.md`

## Impact

The route configuration and durable QA scenario say Luna medium, but the canonical contract suite
still encodes Luna low. The feature tree is not ready regardless of the live pilot result.

## Required fix and retest

Update the canonical contract assertions and any paired charter expectation to the frozen medium
route, rerun the focused suite and outer full gate, then resume fresh QA after the separate mini CLI
review defect is fixed. Never weaken or remove IT-005.

## Resolution

Changed the four `low` expectations in IT-005 (`tools/shared/tests/autonomous-parallelization.test.ts`
lines 155, 157, 160, 163) to `medium` — no other lines touched, IT-005 still asserts the exact tuple.
Focused suite: 4 passed, 0 failed. Outer full gate (`npm_config_offline=true npm run test:all`):
112 passed, 0 failed. `git diff --check`: clean.

## Independent retest

Retest 9 (fresh QA Verifier, 2026-08-27) reran `npm_config_offline=true npm run test:all` on
`83954ec`: exit `0`, Vitest `112/112` across 8 files, all Python lanes `OK`. Confirmed fixed at
`395a691`; not reopened.
