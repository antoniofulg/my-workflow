# CH-adopt-external-security-skills-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 15 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Explicit-boundary and bundled-adoption canary tour
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the public adoption script and filesystem inspection
- **Scenarios:** `ADP-separate-external-security-skills`, `ADP-adopt-workflow-safely`

## Mission

Adopt into a checkout-local disposable target. Confirm external security skills are not silently
copied, the exact second-step command and gate warning are visible, and bundled adoption still
preserves consumer-owned state.

## Expected observable

Adoption output separates bundled workflow skills from three external dependencies; the target
contains none of those external trees before authorization, the exact second step is visible, and
the existing adoption-preservation canary still holds.

## Planned probes

- Capture the printed installer command and compare its pack path, target path, and `--yes` flag.
- Independently inspect `.agents/skills/` and `.claude/skills/` for absence of all three names.
- Re-adopt a pre-populated target and compare consumer configuration and ignore sentinels byte-for-byte.
- Stop before running the printed networked command; that belongs to the enablement charter.

End before product remediation. A confirmed defect returns to an Implementer.
