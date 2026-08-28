# J-adopt-workflow

**Persona:** Workflow adopter
**Goal:** Adopt the workflow without losing consumer-owned repository state.
**Entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`

## Flow

1. Review the target's clean state, managed paths, and existing operational capabilities.
2. Confirm `.specs/features/` is versioned workflow state that travels through worktrees and CI;
   task status and merge-alone closure commits travel with their tasks, while adoption removes exact
   legacy ignore entries and keeps unrelated consumer rules intact.
3. Adopt into a checkout-local disposable target through the documented CLI.
4. Confirm bundled workflow assets are discoverable, the installed instructions activate Ponytail
   at workflow start and keep it active through the full cycle, the copied workflow tour omits the
   source-only pack guide and its links, source-pack-only Bun tests/configuration/preload remain
   absent from the target, no `bun.lock` is created, all three external security skills remain
   absent, and adoption prints their separate authorized installation command without installing
   Bun or editing host settings.
5. Re-adopt a target with a consumer-owned `.my-workflow.toml`, QA profile, model settings,
   template bodies, `tools/ad-index.py`, and unrelated ignore entries.
6. Confirm the local config and consumer-owned template/profile state survive byte-for-byte, runtime
   packets regenerate, and the resulting diff remains reviewable.
7. Pack and clone the adopted source state; confirm tracked example/templates travel while local
   config/runtime packets do not, then regenerate the checkout-local packets from tracked sources.
8. Continue to [`J-enable-external-security-skills`](J-enable-external-security-skills.md) only after
   explicitly authorizing its networked installer step.

## Promises

- [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)
- [`ADP-separate-external-security-skills`](../scenarios/ADP-separate-external-security-skills.md)
- [`ADP-validate-generated-feature-contracts`](../scenarios/ADP-validate-generated-feature-contracts.md)
- [`ADP-validate-feature-completion-state`](../scenarios/ADP-validate-feature-completion-state.md)
- [`QAS-discover-independent-qa-skills`](../scenarios/QAS-discover-independent-qa-skills.md)
- [`QAS-enforce-spec-anchored-qa-contracts`](../scenarios/QAS-enforce-spec-anchored-qa-contracts.md)
- [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md)

## Adjacent canary

After adoption, walk [`J-review-workflow-release`](J-review-workflow-release.md) to confirm the
distributed release still identifies itself and its provenance correctly.

For the configurable-workflow cycle, this journey is also the adjacent canary for
[`J-configure-feature-workflow`](J-configure-feature-workflow.md).
