# CH-validate-feature-completion-state-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Completion-verdict precedence and adoption canary
- **Public entry point:** vendored `validate_state.py` CLI
- **Adapter candidate:** CLI/manual in a checkout-local disposable target
- **Scenarios:** `ADP-validate-feature-completion-state`, adjacent canary `ADP-adopt-workflow-safely`

## Mission

Use the adopted completion validator as a developer would. Confirm an explicit `Verdict` controls
the outcome despite a conflicting nested `Result`, while legacy reports without `Verdict` remain
supported.

## Expected observable

`Verdict: FAIL` with `Result: PASS` exits non-zero; `Verdict: PASS` with `Result: FAIL` exits zero;
and a legacy `Result: PASS` without `Verdict` exits zero. Adoption still installs the validator in
the disposable target without replacing consumer-owned state.

## Planned probes

- Adopt the workflow into a checkout-local disposable target and locate `validate_state.py`.
- Validate a report containing explicit `Verdict: FAIL` followed by legacy `Result: PASS`.
- Validate a report containing explicit `Verdict: PASS` followed by legacy `Result: FAIL`.
- Validate a legacy report containing `Result: PASS` and no explicit `Verdict`.
- Adjacent canary: re-adopt the same target and confirm consumer-owned state remains byte-identical.

End before product remediation. A confirmed defect returns to an Implementer.
