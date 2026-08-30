# BUG-20260829-bun-history-gate-rejects-new-qa-charters

- **Status:** open
- **Severity:** major
- **Scenario:** `REL-report-current-workflow-release`
- **Expected:** The documented `bun run test:all` command accepts new immutable QA charters created
  for the current feature while still rejecting edits to QA artifacts that existed at the frozen
  historical baseline.
- **Observed:** The gate exits `1` because
  `changedHistoricalQaArtifacts()` reports all three newly added Bun QA charters as changed
  historical evidence.
- **Adapter:** public Bun full-gate CLI
- **Exact path:** at `1f44ad358fb717b440cd5497f07dda115d55eba1`, run `bun run test:all`
- **Evidence:** `docs/qa/evidence/2026-08-29-bun-tooling-runtime/opening-gate.txt`;
  `docs/qa/reports/2026-08-29-bun-tooling-runtime.md`

## Reproduction

1. Keep the frozen history baseline at `69914e831cb8001307dfa69219265c8e2e9700fb`.
2. Add a new immutable charter under `docs/qa/charters/` for the current feature.
3. Run `bun run test:all`.
4. Observe `IT-006 keeps Bun as the active command authority while allowing historical evidence`
   fail because the new path appears in `changedHistoricalQaArtifacts()`.

The 2026-08-29 run reported 121 passing tests, 1 failing test, and 1113 assertions across 8 Bun
suites before the mixed-language gate stopped. No public adoption, package, or installer walk ran
after this preflight failure.

## Remediation recommendation

Make the owning historical-integrity assertion distinguish a newly created charter for the active
cycle from modification of an artifact present at the frozen baseline. Keep the mutation sensor
that changes an existing historical report. After the fix, dispatch a fresh QA Execute Verifier to
rerun all three Bun charters from the opening gate.
