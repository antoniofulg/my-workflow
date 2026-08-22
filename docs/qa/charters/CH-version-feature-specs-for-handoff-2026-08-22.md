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

Adopt into a checkout-local disposable target. Confirm feature specs remain ignored by default and
the public guidance tells projects using worktree handoffs or spec-reading gates/CI to remove that
managed ignore entry and version the relevant specs, without claiming automatic detection or
migration.

## Expected observable

The default target ignores `.specs/features/`; README and artifact-lifecycle guidance agree on when
and how to version it; the adjacent public documentation remains explicit and internally consistent.

## Planned probes

- Confirm fresh adoption adds the managed `.specs/features/` ignore entry.
- Compare README and artifact-lifecycle wording for both qualifying conditions and the manual action.
- In the disposable target, remove the managed entry and confirm a feature spec becomes visible to
  Git for worktree handoff and clean-checkout gates.
- Confirm neither document promises automatic detection or migration.
- Adjacent canary: inspect the public README surfaces owned by
  `DOC-read-explicit-workflow-provenance` for intact scope and provenance statements.

End before product remediation. A confirmed defect returns to an Implementer.
