# BUG-20260824-release-overstates-lifecycle-qa

- **Status:** fixed
- **Severity:** major
- **Scenario:** `REL-report-current-workflow-release`
- **Expected:** Release `0.4.0` describes lifecycle procedures without claiming runtime QA coverage
  beyond the enable/setup, provider-handoff, and cleanup paths present in the durable QA report.
- **Observed:** `CHANGELOG.md:20` claims QA runtime walks cover lifecycle-control paths, while the
  durable runtime report covers AIM-01-AIM-08 and contains no disable, re-enable, or operator purge
  walk.
- **Adapter:** CLI/manual repository inspection
- **Exact path:** open `CHANGELOG.md` at release `0.4.0`, follow its QA runtime claim to
  `docs/qa/reports/2026-08-24-ai-memory-handoff.md`, and compare the matrix and nine probe results
  with mandatory charter probe 3 in `CH-review-release-0-4-0-2026-08-24.md`
- **Evidence:** `docs/qa/evidence/2026-08-24-release-0-4-0/session.md`
- **Fix commit:** `61f2e74`
- **Retest:** pass at `dbe11cf`; fresh technical validation, release journey, adjacent adoption canary, package dry-run, lifecycle help/dry-run, reviewer pointer, and full gates passed

## Reproduction

1. Read `CHANGELOG.md:20` and note the claim that QA runtime walks cover lifecycle-control paths.
2. Read `docs/qa/reports/2026-08-24-ai-memory-handoff.md:14-51`.
3. Observe that the report scopes runtime QA to AIM-01-AIM-08 and records enable/setup, handoff,
   wrapper, adoption, cleanup, and gates, but no disable, re-enable, or operator purge walk.
4. Compare with `docs/qa/charters/CH-review-release-0-4-0-2026-08-24.md:43-46`, which requires all
   four lifecycle controls behind this claim and mandates failure when coverage is absent.

## Smallest remediation

Change the changelog sentence to state only the runtime paths actually covered by the durable report;
keep reviewer isolation labeled technical validation. Do not manufacture missing lifecycle evidence
or execute destructive machine operations to preserve the broader wording.

Extend the canonical release assertion so unsupported lifecycle-QA wording fails when the durable
report remains scoped to AIM-01-AIM-08. A fresh Verifier must run the technical gate, resume this
release charter, and re-walk `REL-report-current-workflow-release` plus the adjacent adoption canary.

## Retest evidence

Fresh QA Execute on 2026-08-24 confirmed that `CHANGELOG.md:20` no longer claims runtime lifecycle-
control coverage. It distinguishes runtime-walked handoff evidence, lifecycle documentation and
command checks/dry-run, and technical reviewer-isolation validation. The scoped suite passed 23/23,
package/version/adoption/lifecycle/reviewer probes passed, and the full 108/108 gate passed.
Evidence: `docs/qa/evidence/2026-08-24-release-0-4-0/session.md`; report:
`docs/qa/reports/2026-08-24-release-0-4-0.md`.
