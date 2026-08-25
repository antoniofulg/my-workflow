# CH-review-release-0-6-0-2026-08-25

- **Date:** 2026-08-25
- **Scope:** `1451afa..984abf2` for `host-owned-session-continuation`
- **Time-box:** 60 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Host-owned continuation, v0.6.0 removal boundary, package, and history
- **Public entry point:** `README.md` → current continuation rule; `CHANGELOG.md` → `0.6.0`
- **Adapter candidate:** CLI/manual repository and disposable-target inspection
- **Scenarios:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md); [`QAS-discover-independent-qa-skills`](../scenarios/QAS-discover-independent-qa-skills.md)
- **Adjacent adoption canary:** [`ADP-adopt-workflow-safely`](../scenarios/ADP-adopt-workflow-safely.md) through [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)

## Mission

Review the locally prepared `0.6.0` state through current documentation, fresh reviewer packets,
disposable adoption, package metadata, release authorities, and historical evidence. Confirm that
continuation is assigned to the host, repository artifacts remain the durable semantic context,
and the retired runtime leaves no current adoption or package promise. This is a plan only; the
next fresh Verifier executes it and writes the dated report.

Required current rule: “Cross-provider session continuation is owned by the host. Repository files,
Git state, feature artifacts, and explicit handoff prompts remain the durable semantic context.”

## Expected observable

The README and workflow index contain the exact host-owned rule; every Verifier and Deep Reviewer
provider packet is fresh and evidence-scoped; clean and repeated disposable adoption is stable and
host-neutral; `npm pack --dry-run --json` yields a reloaded manifest with no retired paths; package,
lockfile, release scenario, and release assertions all report `0.6.0`; every final-scan match has
one explicit allowlist category; all 65 protected `v0.5.0` files remain byte-identical; the
migration note points to the tagged guide without executing cleanup; and no publication or external
operator-state mutation occurs.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| HSC-01 | Internal repository/package absence invariant. Cover through the adoption and package walks; no separate user promise. |
| HSC-02 | User-visible adoption behavior. Canonical `J-adopt-workflow` → `ADP-adopt-workflow-safely`; inspect a clean disposable target for every named absence. |
| HSC-03 | User-visible adoption retry behavior. Canonical `J-adopt-workflow` → `ADP-adopt-workflow-safely`; re-adopt the same disposable target and compare project, shell, hook, and host-setting sentinels. |
| HSC-04 | User-visible package membership. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect the actual dry-run manifest. |
| HSC-05 | User-visible continuation documentation. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; read both current entry points and compare the exact rule. |
| HSC-06 | User-visible current guidance. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect current public/reviewer surfaces for retired lifecycle guidance. |
| HSC-07 | User-visible reviewer workflow contract. Canonical `J-adopt-workflow` → `QAS-discover-independent-qa-skills`; inspect all six provider packets and the review guideline. Scenario reset to `untested`. |
| HSC-08 | User-visible host-neutral guidance. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect current generic guidance and its provider-neutral boundary. |
| HSC-09 | User-visible current QA promise. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; verify profile, journey, and scenarios expose only current promises. |
| HSC-10 | User-visible closing QA contract. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`, with `ADP-adopt-workflow-safely` and `QAS-discover-independent-qa-skills` as canaries; this charter is the plan-phase output, and the next fresh Execute session must add the report. |
| HSC-11 | User-visible release evidence trust. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; compare the 65 protected files with `v0.5.0` and preserve prior changelog sections. |
| HSC-12 | User-visible release-scan trust. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; record every match as historical changelog, historical QA evidence, or the `0.6.0` removal note. |
| HSC-13 | User-visible release identity. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; compare package, lockfile, scenario, and assertion authorities. |
| HSC-14 | User-visible release-note contract. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect the `0.6.0` removal entry for host responsibility, durable context, and external-state boundary. |
| HSC-15 | User-visible migration guidance. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; verify the tagged `v0.5.0` guide link and do not run lifecycle commands. |
| HSC-16 | Internal decision-index invariant. Verify `AD-011`/`AD-008` state with the owning index checks; no direct user journey changes. |
| HSC-17 | User-visible release boundary plus local safety guard. Canonical `J-review-workflow-release` → `REL-report-current-workflow-release`; inspect private package state and record that no tag, push, publication, release, deploy, or operator mutation is part of this walk. |

The current `ADP-adopt-workflow-safely`, `REL-report-current-workflow-release`, and
`QAS-discover-independent-qa-skills` scenarios remain `qa_status: untested` until independent
execution evidence and a fresh report exist. Existing charters and historical reports stay
immutable.

## Planned probes

1. Read `README.md`, `docs/workflow/README.md`, and `docs/guidelines/REVIEW-ROUNDS.md`. Confirm the
   exact host-owned continuation rule and inspect current generic guidance for retired lifecycle
   instructions or provider-specific commands.
2. Read the six provider packet sources under `templates/agents/` (Verifier and Deep Reviewer for
   Cursor, Claude, and Codex). Confirm each packet starts from fresh role context, excludes the
   Implementer's transcript and operator handoff, and names the spec, diff, tests, and assigned
   evidence as its conclusion sources.
3. Use only checkout-local disposable targets. Walk the public adoption CLI once on a clean target,
   re-run it in the same target, reload the managed tree, and compare shell, Git-hook, and host-setting
   sentinels. Also run the canonical `python3 scripts/test_adopt.py` smoke authority. Do not inspect
   or alter any real operator path.
4. Run `npm pack --dry-run --json` from the active checkout. Reload the JSON evidence and inspect the
   actual package manifest for name/version, public files, private-package state, and absence of
   retired paths or ignored QA residue.
5. Compare `package.json`, both root `package-lock.json` version fields, the current release
   scenario, and canonical release assertions. Run the focused CT-003 contract and record that every
   authority equals `0.6.0`.
6. Run the focused CT-001 allowlist contract and inspect its explicit map. Record every match with
   its path and one of the three allowed classifications; any unclassified match blocks the walk.
7. Run the focused CT-004 history contract. Record 65 protected files, zero missing files, zero byte
   differences against `v0.5.0`, and unchanged `0.4.0`/`0.5.0` changelog sections.
8. Read the `0.6.0` migration note and reload its tagged `v0.5.0` guide URL without contacting a
   remote service. Confirm the note gives no invented cleanup procedure and no cleanup command runs.
9. Inspect `package.json` private state and checkout status before and after the walk. Do not create
   a tag or release, publish, push, merge, deploy, contact a remote, or mutate operator state.
10. Capture ignored raw evidence under `docs/qa/evidence/2026-08-25-release-0-6-0/`, then let the
    fresh `qa-execute` Verifier write `docs/qa/reports/2026-08-25-release-0-6-0.md` and update only
    the three flagged scenarios after independent reloads confirm their observables.

## Risk and limitation

A pre-existing external operator shell hook might survive and call an executable no longer shipped.
This plan observes only disposable shell and hook sentinels; it must not inspect, remove, or alter
real operator state. Host-native continuation itself is outside this repository's executable
surface, so the walk verifies its documented ownership boundary and durable repository context,
not host internals.

## QA Execute handoff

Use a fresh Verifier with phase `qa-execute`, the CLI/manual adapter in `docs/qa/README.md`, and the
same checkout-local repository at HEAD `984abf2`. Walk the public adoption CLI and package dry-run,
reload all captured files/JSON, and record exact paths, command outputs, counts, and limitations in
the report. Do not launch a product server, install a framework, invent an adapter, or write product
code. If a public contradiction appears, file a bug for an Implementer and stop this session; do
not weaken a test or alter historical evidence.

## Status

QA Plan complete. HSC-10/QA-001 remains pending for the distinct fresh `qa-execute` packet. No live
walk, report, package publication, release action, operator-state inspection, or product change was
performed by this charter.
