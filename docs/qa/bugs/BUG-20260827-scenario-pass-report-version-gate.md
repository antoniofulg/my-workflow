# BUG-20260827-scenario-pass-report-version-gate

- **Status:** open — fresh QA blocked by stale version-specific pass-state gate
- **Severity:** major
- **Scenarios:** `REL-report-current-workflow-release`; `ADP-adopt-workflow-safely`
- **Expected:** A canonical scenario marked `qa_status: pass` with fresh evidence and its current dated `last_report` passes the HSC-09 state contract; report paths are not required to contain a historical package version.
- **Observed:** HSC-09 hard-codes `/v?0[._-]6[._-]0/i` against both `evidence` and `last_report`. The fresh 2026-08-27 evidence and report paths correctly use the required current names, so the targeted contract fails before the release QA verdict can close.
- **Adapter:** CLI/manual QA state update plus Bun structural test contract
- **Exact path:** mark both changed scenarios `qa_status: pass` with `last_report: docs/qa/reports/2026-08-27-bun-test-runner.md`, then run `bun test ./tools/shared/tests/qa-skills.test.ts -t "HSC-09 keeps changed QA scenarios fresh until v0.6 evidence exists"` or `npm run test:all`
- **Evidence:** `docs/qa/evidence/2026-08-27-bun-test-runner/hsc09-failure.log`
- **Related history:** `BUG-20260825-scenario-pass-report-field` fixed the non-schema `report:` lookup; this new symptom occurs with the canonical `last_report:` field and is the stale `v0.6.0` path requirement.

## Reproduction

1. Complete a fresh QA walk and record its evidence under the dated 2026-08-27 evidence directory.
2. Set both changed scenarios to the canonical `qa_status: pass`, point `evidence` to the fresh paths, and set `last_report` to `docs/qa/reports/2026-08-27-bun-test-runner.md`.
3. Run the exact HSC-09 targeted command.
4. Observe the contract reject the fresh adoption evidence because it lacks a `v0.6.0` token.

## Remediation recommendation

Make HSC-09 validate canonical fresh evidence/report paths or the current report date/charter, not a
hard-coded historical package version. Keep the `last_report:` schema and require non-empty paths;
do not weaken the requirement that a pass carries fresh evidence. A fresh technical Verifier must
rerun the full gate, then a fresh QA Execute must retest both affected journeys and the adoption
canary before closing this bug.

