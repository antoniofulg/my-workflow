# CH-remote-delivery-approval-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 15 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Remote-delivery authority and provenance canary
- **Public entry point:** `README.md`
- **Adapter candidate:** Manual repository inspection
- **Scenarios:** `DOC-require-explicit-remote-action-approval`, `DOC-read-explicit-workflow-provenance`

## Mission

Read the public workflow contract and confirm that readiness stops before each unauthorized remote
action while the existing provenance and external-security boundary remain intact.

## Expected observable

Push, pull request creation, and merge each require explicit current-session authorization for that
exact action, while the workflow's existing provenance and external-skill promises remain visible.

## Planned probes

- Compare the remote-action boundary across `AGENTS.md`, `README.md`, `docs/workflow/loop.md`,
  `docs/workflow/pack.md`, and `.agents/skills/autonomous/SKILL.md`.
- Confirm autonomous readiness without exact authorization stops and reports the next action.
- Confirm authorization for one remote action does not imply authorization for a later action.
- Re-read the existing provenance and external-security-skill wording as an adjacent canary.

End before live execution or defect remediation.
