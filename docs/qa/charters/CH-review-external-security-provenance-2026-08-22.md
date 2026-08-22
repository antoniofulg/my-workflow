# CH-review-external-security-provenance-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Bundled-versus-external provenance canary
- **Public entry point:** `README.md`
- **Adapter candidate:** Manual repository and documentation inspection
- **Scenarios:** `DOC-read-explicit-workflow-provenance`, `REL-report-capability-version-0-3-0`

## Mission

Read the public onboarding and pack guide as a maintainer evaluating supply-chain provenance.
Confirm all three external security skills are named, pinned through one authoritative lock, and
clearly excluded from bundled adoption.

## Expected observable

README and pack guide agree that the three security skills require a separate authorized networked
step, identify immutable reviewed metadata in `skills-lock.json`, reject `latest`, and leave local
authorship, source credits, and stack-neutral scope unambiguous.

## Planned probes

- Follow each public source link and compare its named skill with `skills-lock.json`.
- Confirm source type, canonical path, CLI version, 40-character commit, and 64-character tree hash
  are represented as reviewed authorities rather than update instructions.
- Confirm bundled skill lists exclude all three external security trees.
- Adjacent release canary: package and root lockfile still agree on capability version `0.3.0`.

End before live installation or product remediation.
