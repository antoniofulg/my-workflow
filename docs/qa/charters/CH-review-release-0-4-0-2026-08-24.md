# CH-review-release-0-4-0-2026-08-24

- **Date:** 2026-08-24
- **Time-box:** 15 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release identity and public-contract truth
- **Public entry point:** `CHANGELOG.md` → `0.4.0`
- **Adapter candidate:** CLI/manual repository inspection
- **Scenario:** `REL-report-current-workflow-release`
- **Adjacent canaries:** `WFL-ai-memory-handoff`, `ADP-adopt-workflow-safely`

## Mission

Review release `0.4.0` as a repository reader. Confirm one release identity across package
authorities and verify that each new changelog claim accurately points to the shipped public
ai-memory and reviewer-isolation contracts. Reuse the current feature QA verdicts; do not repeat the
provider lifecycle or adoption walks unless repository inspection exposes a contradiction.

## Expected observable

The newest changelog heading, package manifest, and both root lockfile fields report `0.4.0`; the
changelog accurately describes ai-memory as optional and absent from automatic adoption, exposes
enable, reversible disable, re-enable, and separate destructive purge controls, and points readers
to packet-defined reviewer isolation without claiming that capture dropping provides it.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| AIM-01–AIM-04 | Provider handoff behavior is unchanged and already passed through `WFL-ai-memory-handoff` in `docs/qa/reports/2026-08-24-ai-memory-handoff.md`; use that scenario as a current canary and do not repeat its live provider walk. In this release cycle, `REL-report-current-workflow-release` owns only the changelog-to-contract truth check. |
| AIM-05–AIM-08 | Setup, privacy, and repository-authority behavior is unchanged and already passed through `WFL-ai-memory-handoff`; inspect the shipped public documentation only to confirm the release summary remains truthful. |
| AIM-09 | Internal reviewer isolation is technically verified, not a live product surface. The release exposes a docs-as-interface promise: inspect the public README and ai-memory guide for the explicit-role-packet pointer and the statement that capture dropping is only storage/noise control. Map that documentation check to `REL-report-current-workflow-release`. |
| AIM-10 | Public lifecycle documentation changed after feature runtime QA. Map its enable, hook-only disable, re-enable, no-repository-toggle, and separately destructive purge promises to `REL-report-current-workflow-release`; inspect commands and boundaries without running machine-mutating operations. |
| AIM-11 | Release identity is user-visible package metadata. Walk `J-review-workflow-release` through `REL-report-current-workflow-release` and independently read `CHANGELOG.md`, `package.json`, and both root `package-lock.json` version fields. |

## Planned probes

1. Independently read the newest `CHANGELOG.md` heading, `package.json` version, and both root
   `package-lock.json` version fields. Confirm all four report `0.4.0`.
2. Compare every `0.4.0` Added, Changed, and Fixed statement with `README.md`,
   `docs/workflow/ai-memory.md`, the current package metadata, and the durable AI-memory QA report.
3. Mandatory risk probe: require the exact changelog claim that QA walked lifecycle-control paths to
   be supported by the existing durable report and evidence. If enable/disable/re-enable/purge
   coverage is absent, fail the release scenario and register a product defect; do not create the
   missing evidence by changing machine state in this session.
4. Confirm the public adoption contract says ai-memory is opt-in, `scripts/adopt.py` does not install
   it, and lifecycle hooks or shell startup files are never changed automatically.
5. Follow the public lifecycle path from README into the ai-memory guide. Confirm enablement,
   hook-only disablement without data deletion, re-enablement, no `.my-workflow.toml` toggle, and a
   separately labeled irreversible purge are distinct and understandable. Do not execute those
   machine-mutating commands.
6. Follow the reviewer-isolation pointer. Confirm internal Verifier and Deep Reviewer continuity is
   packet-defined, while `drop_subagent_captures` is described only as storage/noise control.
7. Canary check: confirm `WFL-ai-memory-handoff` and `ADP-adopt-workflow-safely` still point to the
   2026-08-24 passing report and that no release-only diff invalidated their observables. Do not
   reset or re-walk them unless a contradiction is found.
8. Record ignored raw evidence under `docs/qa/evidence/2026-08-24-release-0-4-0/`, write a new dated
   report, update `REL-report-current-workflow-release`, and leave checkout-local residue only.

End before provider lifecycle execution, adoption execution, machine configuration changes,
product fixes, commits, tags, publication, or remote actions.

## QA Execute handoff

Use a fresh Verifier with the canonical `qa-execute` skill and the CLI/manual adapter declared in
`docs/qa/README.md`. Start at `CHANGELOG.md`, use checkout-local file inspection as the public read
path, and record the exact path plus independent reload evidence. Update only the release scenario
unless a canary contradiction is observed. Report lifecycle commands as documentation under review;
do not run install, hook, service, shell-startup, disable, re-enable, or purge operations.
