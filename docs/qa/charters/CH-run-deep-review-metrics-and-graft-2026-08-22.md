# CH-run-deep-review-metrics-and-graft-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 30 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-deep-review`](../journeys/J-run-deep-review.md)
- **Tour:** Serial execution, observational metrics, and optional-context fallback
- **Public entry point:** `.agents/skills/deep-review/SKILL.md`
- **Adapter candidate:** CLI/manual through the checkout-local Deep Review scripts
- **Scenarios:** `QAS-observe-serialized-deep-review-metrics`, `QAS-use-graft-context-with-plain-fallback`

## Mission

Run a small fixture review as an operator would. Confirm serial reviewer progress and preserved
outputs, inspect compatible and unavailable telemetry paths, then inspect prompt context with Graft
available and unavailable.

## Expected observable

Exactly one reviewer is active, valid outputs survive retries or resume, metrics contain only
allowlisted metadata and honest totals or `unavailable`, and every Graft failure leaves usable
plain-inspection guidance without changing the review result.

## Planned probes

- CLI help and runtime guidance expose only the supported metrics adapter inputs.
- Two pending jobs complete without overlap and retain their valid output files.
- Compatible telemetry yields recomputable start, checkpoint, final, and delta values.
- Missing, invalid, or regressing telemetry records `unavailable` with the same review exit.
- Metrics ledger contains no prompt, response, or reviewed source content.
- Graft success contributes map and symbol orientation before prompt materialization.
- Missing Graft and selected `.agents` paths contribute explicit plain-inspection fallback.

End before live defect remediation.
