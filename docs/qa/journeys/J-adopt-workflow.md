# J-adopt-workflow

**Persona:** Workflow adopter
**Goal:** Adopt the workflow without losing consumer-owned repository state.
**Entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`

## Flow

1. Review the target's clean state, managed paths, and existing operational capabilities.
2. Adopt into a checkout-local disposable target through the documented CLI.
3. Confirm bundled workflow assets are discoverable, all three external security skills remain
   absent, and adoption prints their separate authorized installation command.
4. Re-adopt a target with a consumer-owned `.my-workflow.toml`, QA profile, model pin, and unrelated
   ignore entries.
5. Confirm consumer-owned state survives byte-for-byte and the resulting diff remains reviewable.
6. Continue to [`J-enable-external-security-skills`](J-enable-external-security-skills.md) only after
   explicitly authorizing its networked installer step.

## Promises

- [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)
- [`ADP-separate-external-security-skills`](../scenarios/ADP-separate-external-security-skills.md)
- [`QAS-discover-independent-qa-skills`](../scenarios/QAS-discover-independent-qa-skills.md)
- [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)

## Adjacent canary

After adoption, walk [`J-review-workflow-release`](J-review-workflow-release.md) to confirm the
distributed release still identifies itself and its provenance correctly.

For the configurable-workflow cycle, this journey is also the adjacent canary for
[`J-configure-feature-workflow`](J-configure-feature-workflow.md).
