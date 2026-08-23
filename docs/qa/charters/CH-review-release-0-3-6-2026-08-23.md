# CH-review-release-0-3-6-2026-08-23

- **Date:** 2026-08-23
- **Time-box:** 10 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release consistency and provenance canary
- **Public entry point:** `CHANGELOG.md` → `0.3.6`
- **Adapter candidate:** Manual repository inspection
- **Scenarios:** `REL-report-current-workflow-release`, `DOC-read-explicit-workflow-provenance`

## Mission

Review release `0.3.6` as a repository reader. Confirm the changelog, manifest, lockfile, and full
test command describe one current release, then re-read the provenance and product-neutral scope as
an adjacent canary.

## Expected observable

The newest changelog heading and both package authorities report `0.3.6`; the full test command
scopes discovery to canonical tests under `tools`; credits, skill boundaries, and product-neutral
scope remain explicit.

## Planned probes

- Compare the newest `CHANGELOG.md` heading with `package.json` and both root version fields in
  `package-lock.json`.
- Compare each `0.3.6` Added, Changed, and Fixed claim with its named public workflow contract.
- Confirm the `test` command scopes Vitest discovery to `tools`.
- Re-read README and pack provenance, bundled-versus-external skill boundaries, and product-neutral
  wording without resetting the unchanged canary scenario.
- Preserve checkout status except for this cycle's durable QA artifacts; store raw evidence only
  under `docs/qa/evidence/`.

End before release publication, live defect remediation, or any remote action.
