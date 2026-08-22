# CH-adopt-configurable-workflow-2026-08-21

- **Date:** 2026-08-21
- **Time-box:** 20 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Installation, preservation, and adjacent artifact canary
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the repository's public adoption script
- **Scenarios:** `ADP-adopt-workflow-safely`, `CFG-keep-local-artifacts-out-of-git`

## Mission

Adopt into checkout-local disposable targets and re-adopt a pre-populated target. Confirm the new
workflow-configuration skill and resolver arrive while `.my-workflow.toml` and other consumer-owned
state remain byte-for-byte unchanged. Walk the artifact-policy scenario as the adjacent canary.

## Expected observable

The adopted target gains the resolver and hierarchy instructions without gaining or changing a
consumer configuration file, while generated feature state remains local and reviewable policy
files remain visible to Git.

## Planned probes

- Fresh target receives the `workflow-config` skill and resolver but no `.my-workflow.toml`.
- Pre-populated sentinel `.my-workflow.toml` retains its byte checksum after adoption and re-adoption.
- QA profile, provider model pin, and unrelated ignore entries remain unchanged.
- Installed instructions expose `Feature -> Vertical Slice -> Task` and require resolution before
  dispatch.
- Adjacent canary: a generated workflow snapshot stays ignored while `.my-workflow.toml` remains
  eligible for review.

End before product remediation. A confirmed defect returns to an Implementer.
