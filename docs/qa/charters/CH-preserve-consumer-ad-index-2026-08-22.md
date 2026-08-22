# CH-preserve-consumer-ad-index-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Fresh-install and re-adoption preservation tour
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the repository's public adoption script
- **Scenarios:** `ADP-adopt-workflow-safely`

## Mission

Adopt into a checkout-local disposable target, confirm `tools/ad-index.py` is installed, replace its
contents with a consumer-owned sentinel, and re-adopt. Confirm the sentinel survives byte-for-byte.

## Expected observable

Fresh adoption creates `tools/ad-index.py`; re-adoption leaves a consumer-modified copy unchanged.

## Planned probes

- Fresh target contains `tools/ad-index.py` after adoption.
- Consumer-modified `tools/ad-index.py` retains its byte checksum after re-adoption.
- Adjacent canary: `J-review-workflow-release` still exposes the adopted workflow's release contract.

End before product remediation. A confirmed defect returns to an Implementer.
