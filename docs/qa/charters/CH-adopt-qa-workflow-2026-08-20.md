# CH-adopt-qa-workflow-2026-08-20

- **Date:** 2026-08-20
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Capability, preservation, and recovery tour
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the repository's public adoption script
- **Scenarios:** `ADP-adopt-workflow-safely`, `QAS-discover-independent-qa-skills`,
  `CFG-keep-local-artifacts-out-of-git`

## Mission

Use checkout-local disposable targets to evaluate fresh adoption and re-adoption. Confirm the
generated workflow exposes both QA skills and provider Verifier packets, creates a missing QA
profile, merges workflow ignore rules, and preserves a consumer-owned profile, model pin, and
unrelated ignore entries.

## Expected observable

The adopted tree is reviewable and complete for the declared workflow surfaces, while every
consumer-owned fixture remains byte-for-byte intact after re-adoption.

## Planned probes

- Fresh empty target.
- Existing target with unrelated ignore entries.
- Existing target with a consumer-owned QA profile.
- Existing provider packet with a local model pin.
- Existing non-stencil product paragraph and its documented refusal path.
- Selective `.deep-review/` and `.specs/features/` ignore behavior.
- Skill discovery through canonical and Claude-linked paths.

End before any product remediation. A confirmed defect returns to an Implementer.
