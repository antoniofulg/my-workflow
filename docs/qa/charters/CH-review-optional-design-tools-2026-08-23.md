# CH-review-optional-design-tools-2026-08-23

- **Date:** 2026-08-23
- **Time-box:** 15 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Optional capability boundary and repository authority
- **Public entry point:** `README.md` → **Optional integrations**
- **Adapter candidate:** Manual repository inspection
- **Scenarios:** `DOC-use-optional-tools-with-repository-authority`

## Mission

Read the optional-integration guidance as a repository reader evaluating adoption. Confirm Graft and
OpenDesign improve a stage without becoming dependencies, the repository remains the fallback and
authority for approved visual handoffs, precedence is explicit, and external writers cannot delete
destination-only content automatically.

## Expected observable

README, UI-UX, SECURITY, and `AD-006` agree on one stack-agnostic contract: optional tools never
replace repository authority, adoption installs neither, and filesystem writes require bounded,
validated, non-destructive handling.

## Planned probes

- Read README discovery language and confirm both integrations are optional and absent from adoption.
- Follow the OpenDesign handoff precedence from `spec.md` through legacy mockups and confirm repository
  fallback when the tool is absent or fails.
- Confirm external writers use isolation or explicit allowed directories, validate paths and
  symlinks before writing, preserve destination-only files, and never delete automatically.
- Confirm operational daemon, port, CLI, and version details stay outside public guidance and route
  to the relevant integration skill.
- Compare `AD-006` and its index entry with the public wording.

End before live execution or defect remediation.
