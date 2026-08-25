# BUG-20260825-scenario-pass-report-field

- **Status:** fixed — retest passed
- **Severity:** major
- **Scenario:** `ADP-adopt-workflow-safely`; `REL-report-current-workflow-release`
- **Expected:** A scenario that follows the canonical `QA-SCENARIOS.md` schema can become `qa_status: pass` with its `evidence` and `last_report` fields, and the HSC-09 contract accepts that terminal state.
- **Observed:** HSC-09 reads a non-schema `report:` field when either changed scenario is `pass`. Both scenarios use the required `last_report:` field, so the removal contract fails even though the fresh evidence and report path are present.
- **Adapter:** CLI/manual QA walk plus repository-declared Vitest contract
- **Exact path:** `npx vitest run tools/shared/tests/qa-skills.test.ts -t 'host-owned session continuation removal contract'`
- **Evidence:** `docs/qa/evidence/2026-08-25-release-0-6-0/removal-contract-after-status.log`; `docs/qa/evidence/2026-08-25-release-0-6-0/retest-removal-contract.log`
- **Fix commit:** `1593299`
- **Retest:** pass on 2026-08-25; HSC-09 now reads canonical `last_report`, targeted and full gates pass, and affected ADP/REL journeys pass after independent reloads

## Reproduction

1. Set `qa_status: pass` on either changed scenario and keep the required `last_report:` field.
2. Run the exact path above.
3. Observe HSC-09 fail with `pass requires a v0.6 report` because it searches for `report:` and receives an empty string.

## Smallest remediation

Make HSC-09 read the canonical `last_report:` field defined by `docs/guidelines/QA-SCENARIOS.md`.
Do not add a second scenario field or weaken the terminal-status contract. Re-run the removal
contract and the complete release gate, then retest both linked scenarios in a fresh Verifier QA
session.

## Retest

Fresh QA Execute resumed the original report after fix `1593299`. The exact HSC-09 state-machine
test passed with `last_report:` in both changed scenarios, the complete `npm test` gate passed
113/113, and the affected ADP and REL journeys plus the adjacent QAS canary passed through the
declared CLI/manual adapter. See `docs/qa/reports/2026-08-25-release-0-6-0.md` and the retest
evidence under `docs/qa/evidence/2026-08-25-release-0-6-0/`.
