# BUG-20260829-final-qa-pass-conflicts-with-adoption-gate

- **Status:** fixed
- **Severity:** major
- **Scenario:** `ADP-adopt-workflow-safely`
- **Expected:** After fresh QA proves adoption and updates its scenario to `qa_status: pass` with
  current evidence/report paths, the canonical gate accepts that terminal verdict while continuing
  to require the real Orca/Codex scenario to remain `blocked-verify`.
- **Observed:** `npm_config_offline=true npm run test:all` passes 8/8 Vitest files and 114/114
  tests, then `scripts/test_adopt.py::test_qa_registry_keeps_fake_proof_current_and_live_orca_blocked`
  fails because it permanently asserts `qa_status: untested` for `ADP-adopt-workflow-safely`.
- **Adapter:** canonical package gate after CLI/manual QA Execute
- **Exact path:** prove fresh adoption → update `ADP-adopt-workflow-safely` to `pass` with
  `docs/qa/evidence/2026-08-29-hybrid-slice-execution/summary.json` → run
  `npm_config_offline=true npm run test:all`
- **Evidence:** `docs/qa/evidence/2026-08-29-hybrid-slice-execution/final-gate-failure.txt`;
  `docs/qa/reports/2026-08-29-hybrid-slice-execution.md`

## Reproduction

1. Keep `QAS-run-resource-free-parallel-orca-slices` at `qa_status: blocked-verify`.
2. Set the independently verified adoption scenario to `qa_status: pass` and point it at current
   evidence/report paths.
3. Run `npm_config_offline=true npm run test:all`.
4. Observe 114/114 Vitest tests pass, followed by the hard-coded `qa_status: untested` assertion.

## Remediation recommendation

Update the owning adoption suite to validate the terminal offline invariant: adoption is `pass`
with the 2026-08-29 evidence/report, while live Orca remains `blocked-verify` with its upstream
reason. Do not weaken or remove the live-host assertion. Run the full gate, then use a fresh QA
Execute Verifier to re-walk the adoption charter and its package/configuration canaries.

## Fix

The canonical adoption assertion now accepts the current independently verified `pass` verdict and
requires its dated evidence/report paths. The live Orca assertion remains `blocked-verify`. A fresh
Verifier retest is still pending; this fix records no retest result.
