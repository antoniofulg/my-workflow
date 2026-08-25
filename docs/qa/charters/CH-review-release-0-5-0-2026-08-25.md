# CH-review-release-0-5-0-2026-08-25

- **Date:** 2026-08-25
- **Time-box:** 30 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release identity, package contents, adoption, and release-note truth
- **Public entry point:** `CHANGELOG.md` → `0.5.0`
- **Adapter candidate:** CLI/manual repository and disposable-target inspection
- **Scenario:** `REL-report-current-workflow-release`
- **Adjacent canaries:** `ADP-adopt-workflow-safely`, `CFG-centralize-agent-model-routing`, `CFG-freeze-feature-workflow`, `QAS-run-bounded-parallel-deep-review`, `QAS-observe-serialized-deep-review-metrics`

## Mission

Review release `0.5.0` as a repository reader. Confirm one release identity across package
authorities and canonical assertions, confirm the package and adoption path ship the promised
public contracts, and compare every release-note claim with the merged PRs and durable feature QA.
Keep the check local: this private package may be packed for inspection but must not be published.

## Expected observable

The newest changelog heading, package manifest, both root lockfile fields, canonical release
assertions, package dry-run metadata, and adopted files agree on `0.5.0`; the packaged and adopted
contracts support each release-note claim; current public/versioned prose is English; ignored local
state and raw QA evidence are absent from the package; and no npm publication, tag, or remote action
occurs.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| Release identity | User-visible metadata. Walk `J-review-workflow-release` through `REL-report-current-workflow-release`; independently compare `CHANGELOG.md`, `package.json`, both root `package-lock.json` fields, and canonical `0.5.0` assertions. |
| Package and publication boundary | User-visible package metadata and membership. Map to `REL-report-current-workflow-release`; use only `npm pack --dry-run --json`, confirm `private: true`, and never run `npm publish` or contact a registry. |
| PR #61 — optional ai-memory handoff | Already released and certified as `0.4.0`. Preserve the immutable `0.4.0` charter/report and current `WFL-ai-memory-handoff` verdict; confirm `0.5.0` does not re-claim it or contradict its public boundary. |
| PR #62 — centralized agent model routing | Public configuration and adoption behavior. The canonical feature owners are `CFG-centralize-agent-model-routing`, `CFG-freeze-feature-workflow`, `CFG-route-delegated-role-providers`, `CFG-keep-local-artifacts-out-of-git`, and `ADP-adopt-workflow-safely`; reuse their current reports as canaries and map release-note truth to the release scenario. |
| PR #63 — autonomous scoped delivery | Public authority contract. Map the `0.5.0` release-note claim to the release scenario and compare the current autonomous, AGENTS, README, loop, and pack contracts directly. Do not reuse the 2026-08-22 `DOC-require-explicit-remote-action-approval` pass as evidence because PR #63 changed that promise. |
| PR #64 — direct correction | Public workflow contract. Map release-note truth to the release scenario; inspect the current TLC, autonomous, AGENTS, branching, and review-round paths without starting a correction. |
| PR #65 — refreshed adoption guide | Docs-as-interface and package membership. Map to the release scenario with `ADP-adopt-workflow-safely` as adjacent canary; confirm README and `docs/adoption-prompt.md` agree and both are packaged/adopted where promised. |
| PR #66 — remediation stall bound | Public configuration behavior. Reuse the current `CFG-resolve-deep-review-cadence`, `CFG-freeze-feature-workflow`, and adoption report as canaries; map the changelog summary to the release scenario. Live agent-loop behavior remains technical-validation-only per the profile. |
| PR #67 — bounded parallel Deep Review | Public CLI/package behavior. Reuse `QAS-run-bounded-parallel-deep-review`, `QAS-observe-serialized-deep-review-metrics`, and the adoption canary; map every concurrency, retry, block, resume, determinism, and metrics release-note claim to those durable reports and shipped contracts. |
| English public/versioned text | Docs-as-interface. Map to the release scenario; inspect the `0.5.0` changelog section and user-facing tracked/package-member prose added or changed by PRs #62–#67 plus the release-preparation commit. Names, commands, paths, identifiers, and quoted provider syntax are not prose violations. |
| Changelog and release notes | `CHANGELOG.md` is the checkout's release-note candidate. Map to the release scenario; every Added, Changed, and Fixed bullet needs a shipped-contract pointer and bounded durable evidence. No GitHub release creation or remote lookup is part of this charter. |

The release diff changes the existing release promise but does not change its journey route, so
`J-review-workflow-release` remains unchanged. No new scenario id is needed.

## Planned probes

1. Independently read the newest `CHANGELOG.md` heading, `package.json` version, both root
   `package-lock.json` version fields, and canonical version assertions. Confirm all report
   `0.5.0`, and confirm the full test command remains `vitest run --dir tools`.
2. Run `npm pack --dry-run --json` from the active checkout. Reload the JSON from evidence; confirm
   package name/version, required public files for every `0.5.0` claim, and exclusion of ignored
   `.my-workflow.toml`, generated provider runtimes, `docs/qa/evidence/`, `node_modules`, and tarball
   residue. Confirm `package.json` remains `private: true`. Do not run `npm publish`.
3. Compare every `0.5.0` Added, Changed, and Fixed bullet with the exact merged PR range: #62
   `da08aee`, #63 `03c4479`, #64 `33b1c38`, #65 `70e447d`, #66 `da5571e`, and #67 `c4490b1`.
   Treat #61 `647b8d7` as the immutable `0.4.0` boundary, not a new `0.5.0` claim.
4. Follow the package/adoption read path into a checkout-local disposable target. Run fresh
   adoption and re-adoption; reload installed bytes; confirm central configuration/templates,
   direct-correction instructions, remediation settings, Deep Review concurrency contracts, and
   the refreshed guide arrive as documented while consumer-owned local config survives.
5. Confirm adoption prints but does not invoke the separately authorized external-security
   installer. Do not use network access, install external skills, or touch a non-disposable target.
6. Read the autonomous delivery contract across `.agents/skills/autonomous/SKILL.md`, `AGENTS.md`,
   `README.md`, `docs/workflow/loop.md`, and `docs/workflow/pack.md`. Confirm invocation authority is
   scoped to the feature-branch push, one pull request, and merge after readiness, while release,
   deploy, production mutation, force-push, direct `main` push, and unrelated remote work remain
   separately authorized. Perform no Git remote action.
7. Read the direct-correction contract across TLC, autonomous, AGENTS, branching, and review-round
   docs. Confirm an exact human-defined correction uses the short path without weakening its local
   validation, commit, or independent-verifier boundary.
8. Reconcile the routing, remediation, and parallel-review changelog claims with their current
   feature scenarios/reports and shipped public contracts. Re-walk only the release-level package
   and adoption paths; if a canary contradicts HEAD, record that contradiction instead of silently
   preserving its prior pass.
9. Inspect the `0.5.0` changelog section and all user-facing tracked/package-member prose changed
   since #61 for English. Record each inspected path. Exclude proper names, commands, paths,
   identifiers, and provider syntax from the prose judgment.
10. Capture ignored raw evidence under `docs/qa/evidence/2026-08-25-release-0-5-0/`, write
    `docs/qa/reports/2026-08-25-release-0-5-0.md`, and update only
    `REL-report-current-workflow-release` unless a current canary contradiction requires a defect.
    Preserve all `0.4.0` charters, reports, and evidence references.
11. Confirm checkout-local cleanup and residue. Record that no `npm publish`, tag, push, pull
    request, merge, release creation, deploy, product edit, or remote action occurred.

## QA Execute handoff

Use a fresh Verifier with the canonical `qa-execute` skill and the CLI/manual adapter declared in
`docs/qa/README.md`. Work only in `/Users/antoniofulg/Projects/my-workflow-release-0.5.0` at
`b719dbb9e7c7aaa50a6ef4092e67cd60b296b38f`. Start at `CHANGELOG.md` → `0.5.0`; use
`npm pack --dry-run --json`, checkout-local disposable Git/adoption targets, independent file/JSON
reloads, and the existing feature reports named above. Write raw evidence to
`docs/qa/evidence/2026-08-25-release-0-5-0/`, the durable report to
`docs/qa/reports/2026-08-25-release-0-5-0.md`, and the verdict to
`docs/qa/scenarios/REL-report-current-workflow-release.md`. Do not modify product code, historical
`0.4.0` artifacts, journeys, or unrelated scenarios. Do not run `npm publish`, create a tag or
release, contact GitHub/npm, install external skills, or perform any push, pull request, merge,
deploy, machine lifecycle, or non-disposable target action. If a product contradiction appears,
record a bug and hand it to an Implementer; end this Verifier session and require a fresh Verifier
after the fix.
