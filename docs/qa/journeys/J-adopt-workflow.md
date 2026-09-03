# J-adopt-workflow

**Persona:** Workflow adopter
**Goal:** Adopt the workflow without losing consumer-owned repository state.
**Entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py plan/resolve/apply/status`

## Flow

1. Review the target's clean state, managed paths, and existing operational capabilities.
2. Confirm `.specs/features/` is versioned workflow state that travels through worktrees and CI;
   task status commits with its task, while adoption removes exact legacy ignore entries and keeps
   unrelated consumer rules intact.
3. Run a read-only `plan` for the smallest required layer and confirm the target is unchanged. For a
   legacy Git project without an adoption manifest, review every file conflict, move product-owned
   customizations, commit a clean baseline, then `resolve` the exact replacement set with
   `--skip-agents`. Otherwise `apply` the reviewed plan. Use `status` after resolution, each
   incremental apply, and one reversible managed-file drift.
4. Confirm bundled workflow assets are discoverable, including the workflow-owned
   `workflow-spec-driven` router and its five phase skills (`wspecify`, `wdesign`, `wtasks`,
   `wimplement`, `wverify`) reachable through both `.agents/skills/` and the `.claude/skills/`
   links, pointer-only assisted probe, and Bun-native knowledge sources; open each phase skill and
   confirm the templates, references, and validator paths it names exist; the
   installed instructions activate Ponytail at workflow start and keep it active through the full
   cycle, the copied workflow tour omits the source-only pack guide and its links, repository-only
   TypeScript tests remain absent, all three external security skills remain absent, and adoption
   prints their separate authorized installation command. Import the installed probe with a fake
   `orca` on `PATH` and confirm it performs no call; run the installed knowledge CLI with Bun without
   consumer Node packages.
5. Re-adopt a target with a consumer-owned `.my-workflow.toml`, QA profile, model settings,
   template bodies, `tools/ad-index.py`, and unrelated ignore entries.
6. Confirm the local config and consumer-owned template/profile state survive byte-for-byte, runtime
   packets regenerate, and the resulting diff remains reviewable.
7. Pack and clone the adopted source state; confirm tracked example/templates travel while local
   config/runtime packets do not, then regenerate the checkout-local packets from tracked sources.
8. Continue to [`J-enable-external-security-skills`](J-enable-external-security-skills.md) only after
   explicitly authorizing its networked installer step.

For an existing project, start with `core`, add `parallel`, `quality`, and `extras` only when the
project needs them, and keep consumer prose outside the managed instruction blocks. Conflicts stop
the complete apply before any write; this workflow has no layer-removal command.

## Promises

- [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md)
- [`ADP-install-phase-skills`](../scenarios/ADP-install-phase-skills.md)
- [`QAS-resolve-phase-skill-procedures`](../scenarios/QAS-resolve-phase-skill-procedures.md)
- [`ADP-layered-workflow-adoption`](../scenarios/ADP-layered-workflow-adoption.md)
- [`ADP-resolve-legacy-adoption-conflicts`](../scenarios/ADP-resolve-legacy-adoption-conflicts.md)
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

## Latest QA status

QA Execute on 2026-08-31 passed the legacy no-manifest ownership-transfer path and its fresh normal
`plan`/`apply`/`status` canary at `827d629`. Durable result:
[`2026-08-31-legacy-adoption-resolution`](../reports/2026-08-31-legacy-adoption-resolution.md).

The 2026-09-03 `phase-skills` cycle resets `ADP-adopt-workflow-safely` and
`ADP-layered-workflow-adoption` to `untested` and adds `ADP-install-phase-skills` and
`QAS-resolve-phase-skill-procedures`; see
[`CH-adopt-phase-skills-2026-09-03`](../charters/CH-adopt-phase-skills-2026-09-03.md).
