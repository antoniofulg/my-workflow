# CH-version-feature-state-by-default-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Versioned feature-state adoption and migration
- **Public entry point:** `README.md` → **Adopt the workflow**
- **Adapter candidate:** CLI/manual through the public adoption script and Git inspection
- **Scenarios:** `ADP-adopt-workflow-safely`, `CFG-keep-local-artifacts-out-of-git`, adjacent canary `DOC-read-explicit-workflow-provenance`

## Mission

Adopt into fresh and legacy checkout-local Git targets. Confirm `.specs/features/` remains visible
to Git, exact legacy ignore entries are removed without disturbing consumer lines, and adoption
does not stage or commit files.

## Expected observable

Feature workflow state can travel through worktrees and clean CI checkouts; task-state changes are
ordinary reviewable Git changes; fresh adoption and legacy migration preserve consumer ownership.

## Planned probes

- Fresh target: adopt, create a feature `spec.md` and `tasks.md`, and confirm both are Git-visible.
- Legacy target: seed duplicate exact `.specs/features/` entries, near-match consumer rules, and
  unrelated lines; adopt twice and confirm only exact legacy entries disappear while the second
  adoption is byte-idempotent.
- Confirm adoption leaves the index and `HEAD` unchanged; commit feature state explicitly, then read
  it from a sibling worktree or clean clone and confirm an atomic task-status commit travels with it.
- Adjacent canary: re-read the README provenance and external-skill boundary owned by
  `DOC-read-explicit-workflow-provenance`.

End before product remediation. A confirmed defect returns to an Implementer.
