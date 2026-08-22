# CH-configure-feature-workflow-2026-08-21

- **Date:** 2026-08-21
- **Time-box:** 35 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Defaults, customization, failure, and recovery tour
- **Public entry point:** `.my-workflow.toml` → `workflow-config` resolver CLI
- **Adapter candidate:** CLI/manual through the command documented by the `workflow-config` skill
- **Scenarios:** `CFG-resolve-deep-review-cadence`, `CFG-route-delegated-role-providers`,
  `CFG-freeze-feature-workflow`

## Mission

Use checkout-local disposable Git repositories to experience the public resolver as a workflow
adopter. Compare its stdout with the reloaded snapshot, then exercise defaults, cadence boundaries,
mixed routing, override precedence, frozen resume, explicit refresh, and recoverable failures.

## Expected observable

The adopter can predict the exact review groups and delegated routes, resume the frozen feature
without drift, and correct any rejected input without silent fallback or loss of valid state.

## Planned probes

- No `.my-workflow.toml`, one and four slices, native provider.
- `slice`, `feature`, and `grouped.3` across boundary counts, including `4 -> 2+2` and `7 -> 3+2+2`.
- Partial mixed profile and one role override demonstrating override > profile > native.
- JSON stdout reloaded independently from `.specs/features/<slug>/workflow.json`.
- Resume after changing config and Git HEAD; explicit refresh after the human-facing decision point.
- Malformed cadence, zero slices, unknown profile, `planner` override, invalid provider, and missing
  provider agent file.
- Write failure with a pre-existing valid snapshot preserved and recovery after write access returns.
- Manual inspection that final review precedes QA and QA remediation reviews only the unreviewed
  commit delta.

End before product remediation. A confirmed defect returns to an Implementer.
