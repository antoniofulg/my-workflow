# CH-validate-generated-feature-contracts-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 15 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Generated-contract compatibility and rejection canaries
- **Public entry point:** vendored `validate_tasks.py` and `validate_spec.py` CLIs
- **Adapter candidate:** CLI/manual in a checkout-local disposable target
- **Scenarios:** `ADP-validate-generated-feature-contracts`, adjacent canary `ADP-adopt-workflow-safely`

## Mission

Use the adopted validators as a developer would. Confirm feature contracts produced from both TLC
task layouts and the annotated acceptance-criteria template pass unchanged, while deliberately
invalid contracts retain precise non-zero failures.

## Expected observable

Both valid task layouts and the annotated acceptance-criteria heading exit successfully. A task
depending on a future phase and a criterion without `SHALL` each exit non-zero with the matching
diagnostic. Adoption still places the same vendored validator scripts in the disposable target.

## Planned probes

- Adopt the workflow into a checkout-local disposable target and locate both validator CLIs.
- Validate tasks nested under phase headings.
- Validate phase diagrams whose task definitions appear later under Task Breakdown.
- Add a dependency from an earlier phase to a later phase and observe a non-zero, task-specific
  diagnostic.
- Validate an `Acceptance Criteria` heading with the template's parenthesized suffix and blank line.
- Remove `SHALL` from one criterion and observe a non-zero criterion-specific diagnostic.
- Adjacent canary: confirm adoption still completes and installs the validators without replacing
  consumer-owned state.

End before product remediation. A confirmed defect returns to an Implementer.
