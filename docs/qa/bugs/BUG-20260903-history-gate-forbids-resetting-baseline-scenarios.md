# BUG-20260903-history-gate-forbids-resetting-baseline-scenarios

- **Status:** fixed — retest pass
- **Severity:** major
- **Scenario:** `REL-report-current-workflow-release`
- **Expected:** `bun run test:all` accepts a QA Plan resetting an affected scenario's `qa_status` to
  `untested`, as `docs/guidelines/QA-SCENARIOS.md` requires, while still rejecting edits to
  historical evidence, reports, and bugs that existed at the frozen baseline.
- **Observed:** The gate exits `1`. `changedHistoricalQaArtifacts()` treats
  `docs/qa/scenarios/` as frozen history, so any scenario file that existed at baseline
  `b3b42c7bd0a8ab8e72d4c5367f4559df31f8d647` can never be flagged again.
- **Adapter:** public Bun gate CLI
- **Exact path:** at `e4df550e` on `feat/phase-skills`, reset an affected baseline scenario to
  `qa_status: untested` and run `bun test tools/shared/tests/qa-skills.test.ts`
- **Evidence:** `docs/qa/evidence/2026-09-03-phase-skills/80-history-gate-retest.txt`

## Reproduction

1. Start from a clean `feat/phase-skills` at `e4df550e`, where the assertion passes.
2. Change `qa_status: pass` to `qa_status: untested` in
   `docs/qa/scenarios/ADP-adopt-workflow-safely.md`, per the flag-then-verify rule in
   `docs/guidelines/QA-SCENARIOS.md`.
3. Run `bun test tools/shared/tests/qa-skills.test.ts`.
4. Observe `IT-006 keeps Bun as the active command authority while allowing historical evidence`
   fail, reporting the scenario as changed historical evidence.

The 2026-09-03 QA Plan for `phase-skills` reset six affected scenarios. Five of them
(`ADP-adopt-workflow-safely`, `ADP-layered-workflow-adoption`, `CFG-centralize-agent-model-routing`,
`DOC-read-explicit-workflow-provenance`, `QAS-discover-independent-qa-skills`) existed at the
baseline and are reported. `CFG-derive-merge-alone-slices` was minted after the baseline and is
accepted, which is why the `phase-skills` diff could already edit that one file in place.

## Impact

`docs/guidelines/QA-SCENARIOS.md` is the sole authority for statuses and states that a changed
promise resets its scenario to `untested`, because "a stale `pass` is worse than no verdict". The
gate makes that rule unexecutable for every scenario minted before 2026-08-29. The workflow's own
critical rule forbids weakening the plan to make the gate pass, so the honest reset stands and the
gate is the artifact that must change.

## Remediation recommendation

Narrow the frozen set to what the assertion was built to protect: `docs/qa/evidence`,
`docs/qa/reports`, and `docs/qa/bugs` are append-only history; `docs/qa/scenarios` is a live
tracker whose whole purpose is to change status between cycles. Keep `docs/qa/charters` frozen —
charters are immutable once written. Keep the mutation sensor that catches a rewritten historical
report. Route this to an Implementer; a fresh Verifier confirms the fix, then QA Execute runs
`CH-adopt-phase-skills-2026-09-03` from the opening gate.

## Retest — 2026-09-03

Fixed by `50ca157b`. Retested during QA Execute
([report](../reports/2026-09-03-phase-skills.md)) on `feat/phase-skills` @ `ef18f54c`, whose tree
carries the five reset baseline scenarios:

- `bun test tools/shared/tests/qa-skills.test.ts` → exit `0` with the resets in place.
- The mutation sensor still bites: appending a line to the historical report
  `docs/qa/reports/2026-08-31-release-0-8-0.md` made `IT-006` fail with exit `1`; restoring the file
  returned the gate to `0`.
- `bun run test:all` → exit `0` as both the opening and closing gate of that cycle.

`retest_status: pass` on `REL-report-current-workflow-release`.
