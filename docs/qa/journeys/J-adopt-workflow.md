# J-adopt-workflow

**Persona:** Workflow adopter
**Goal:** Adopt the workflow without losing consumer-owned repository state.
**Entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`

## Flow

1. Review the target's clean state, managed paths, and existing operational capabilities.
2. Adopt into a checkout-local disposable target through the documented CLI.
3. Confirm the QA skills, existing provider Verifier packets, workflow ignore rules, and initial QA
   profile are discoverable.
4. Re-adopt a target with a consumer-owned profile, model pin, and unrelated ignore entries.
5. Confirm consumer-owned state survives and the resulting diff remains reviewable.

## Promises

- [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)
- [`QAS-discover-independent-qa-skills`](../scenarios/QAS-discover-independent-qa-skills.md)
- [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)

## Adjacent canary

After adoption, walk [`J-review-workflow-release`](J-review-workflow-release.md) to confirm the
distributed release still identifies itself and its provenance correctly.
