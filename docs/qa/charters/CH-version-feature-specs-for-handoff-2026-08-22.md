# CH-version-feature-specs-for-handoff-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Feature-spec handoff guidance and documentation canary
- **Public entry point:** `README.md` → **Adopt the workflow**
- **Adapter candidate:** CLI/manual through the public adoption script and repository inspection
- **Scenarios:** `ADP-adopt-workflow-safely`, adjacent canary `DOC-read-explicit-workflow-provenance`

## Mission

Adopt into a checkout-local disposable target. Confirm feature specs are visible to Git by default
and adoption removes duplicate exact legacy ignore entries while preserving unrelated consumer
rules, without staging or committing files automatically.

## Expected observable

The target keeps `.specs/features/` versioned; README and artifact-lifecycle guidance agree on the
managed legacy-line migration contract; the adjacent public documentation remains consistent.

## Planned probes

- Confirm fresh adoption does not add a `.specs/features/` ignore entry.
- Seed duplicate exact legacy entries and unrelated comments/rules, then confirm only the legacy
  entries are removed.
- Re-adopt and confirm the `.gitignore` bytes remain unchanged and a feature spec is visible to Git.
- Adjacent canary: inspect the public README surfaces owned by
  `DOC-read-explicit-workflow-provenance` for intact scope and provenance statements.

End before product remediation. A confirmed defect returns to an Implementer.
