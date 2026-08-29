# CH-adopt-hybrid-slice-workflow-2026-08-29

- **Date:** 2026-08-29
- **Time-box:** 30 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Fresh adoption, re-adoption, packet budget, provenance, and package canary
- **Public entry point:** `README.md` → `scripts/adopt.py` → generated target files
- **Adapter candidate:** CLI/manual through the adoption command declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** `ADP-adopt-workflow-safely`
- **Adjacent canary:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)

## Mission

Adopt the workflow into a checkout-local disposable Git project, verify the v3 workflow-owned skill
and assisted tooling arrive at byte-identical destinations, and re-adopt without replacing
consumer-owned configuration or QA profile state. Keep external skill installation and publication
out of scope.

## Expected observable

The target contains the attributed `workflow-spec-driven` skill and no obsolete TLC skill, bounded
slice-only packets, the assisted probe and scheduler, provider role templates, current guidance,
and regenerated local runtime packets. Re-adoption preserves consumer-owned bytes, the installed
probe imports without effects, and the adjacent package inspection contains the shipped assets.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| HSE-01 | User-visible adoption promise. Walk `ADP-adopt-workflow-safely`; inspect the installed skill paths and prove the obsolete path is absent. |
| HSE-02 | User-visible provenance. In the adopted target, read `NOTICE.md` and compare author, source, license, and modification notice with source bytes. |
| HSE-03 | User-visible agent packet. Materialize one adopted slice packet and inspect only cited tasks, criteria, tests, design excerpt, and compact memory. |
| HSE-04 | Docs-as-interface. Inspect the adopted skill for trigger-based guideline loading and absence of phase-batch or feature-only Verifier routing. |
| HSE-05 | Public CLI failure. Exercise the documented packet budget boundary in a disposable target and independently reload redacted byte-count JSON. |
| HSE-06 | Public telemetry. Inspect emitted component/total counts and search captured output for packet bodies, secrets, home paths, and environment values. |
| HSE-35 | User-visible distribution promise. Compare all managed hybrid assets in the adopted target byte-for-byte with the active checkout. |
| HSE-36 | User-visible preservation promise. Re-adopt after changing consumer-owned `.my-workflow.toml` and `docs/qa/README.md`; compare hashes before and after. |
| HSE-37 | Internal gate composition with a public installed-tree outcome. Use the canonical gate only as supporting evidence; the QA walk independently inspects adopted paths and import safety. |
| HSE-38 | User-visible limitation/evidence promise. Require current offline adoption evidence while preserving both real-Orca scenarios as `blocked-verify`. |
| HSE-39 | Internal path/argv control with an observable refusal. Use only disposable repository-owned paths; technical validation owns hostile symlink and foreign-target discrimination. |

## Planned probes

1. Create a checkout-local disposable Git target and run the documented adoption command.
2. Reload the target from a fresh process; compare all hybrid managed paths byte-for-byte and prove
   `.agents/skills/tlc-spec-driven` is absent.
3. Read installed provenance and agent instructions, then materialize one slice packet and reload
   its budget telemetry without exposing its body.
4. Put a call-counting fake `orca` on `PATH`, import the installed probe, and require zero calls and
   no filesystem mutation.
5. Change consumer-owned config and QA profile bytes, re-adopt, and require exact preservation while
   managed workflow files refresh.
6. Use `npm pack --dry-run --json` only as the adjacent release/package canary. Do not publish.
7. Capture raw evidence under `docs/qa/evidence/2026-08-29-hybrid-slice-execution/` and leave the
   disposable target absent after teardown.

## QA Execute handoff

Use a fresh Verifier with `qa-execute` and the CLI/manual adapter in `docs/qa/README.md`. Work in the
active checkout at the reviewed HEAD, use only checkout-local disposable targets, write the durable
report to `docs/qa/reports/2026-08-29-hybrid-slice-execution.md`, and update
`ADP-adopt-workflow-safely`. Do not install external skills, publish, contact a remote, or use live
Orca.
