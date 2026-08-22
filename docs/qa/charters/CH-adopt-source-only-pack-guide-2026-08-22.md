# CH-adopt-source-only-pack-guide-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Source-only guide and copied-tour canary
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the public adoption script and filesystem inspection
- **Scenarios:** `ADP-adopt-workflow-safely`, adjacent canary `DOC-read-explicit-workflow-provenance`

## Mission

Adopt into a checkout-local disposable target. Confirm the pack guide remains in the source
repository but neither it nor dead links to it reach the target, while every adjacent workflow page
still arrives. Re-adopt once to preserve the canonical adoption promise.

## Expected observable

The source tour retains its working pack-guide link; the adopted tour omits that guide and both of
its links, contains the other five pages, and preserves consumer-owned state on re-adoption.

## Planned probes

- Confirm source `docs/workflow/pack.md` exists and both source-tour links resolve to it.
- Run adoption against a fresh disposable target and independently inspect the copied workflow tree.
- Confirm `pack.md` and both links to it are absent, with no dead local tour links.
- Confirm `purpose.md`, `loop.md`, `reviews.md`, `decisions.md`, and `guidelines.md` arrived.
- Re-adopt a target with one consumer-owned sentinel and compare its bytes.
- Adjacent canary: confirm the source pack guide still carries the public provenance promise.

End before product remediation. A confirmed defect returns to an Implementer.
