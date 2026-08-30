# J-enable-external-security-skills

**Persona:** Workflow adopter
**Goal:** Enable reviewed external security skills only through an explicit, reversible step.
**Entry point:** `scripts/adopt.py` output → `scripts/install_security_skills.py`

## Flow

1. Adopt into a checkout-local disposable target and inspect the printed second-step command.
2. Run the installer without authorization and confirm it only prints the pinned
   `bunx --bun --no-install` plan.
3. Review the three source, path, CLI-version, commit, and tree-hash authorities in
   `skills-lock.json`.
4. After explicit network/write authorization, run the printed command against the disposable
   target and confirm the locked `skills` version preflight completes before any add operation.
5. Inspect the three installed trees, Claude links, merged lock entries, and consumer sentinels
   through an independent filesystem read.
6. Exercise missing and wrong-version local CLI refusals from a disposable pack copy and confirm no
   npm/npx or fetch fallback runs, the target is restored, and the security gate is reported unavailable.

## Promises

- [`ADP-install-pinned-external-security-skills`](../scenarios/ADP-install-pinned-external-security-skills.md)
- [`ADP-preserve-security-install-target`](../scenarios/ADP-preserve-security-install-target.md)

## Adjacent canary

Walk [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md) to confirm the new
second-step output did not regress bundled adoption or consumer-owned state preservation.
