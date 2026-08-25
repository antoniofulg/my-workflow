# CH-review-release-0-6-0-2026-08-25

- **Date:** 2026-08-25
- **Time-box:** 35 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release identity, package contents, adoption, and parallel-executor claim truth
- **Public entry point:** `CHANGELOG.md` -> `0.6.0`
- **Adapter candidate:** CLI/manual repository and checkout-local disposable-target inspection
- **Scenario:** `REL-report-current-workflow-release`
- **Adjacent canaries:** `ADP-adopt-workflow-safely`, `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, `CFG-fallback-unproven-parallel-execution`, `QAS-bound-verifier-remediation-per-blocker`, `QAS-run-resource-free-parallel-orca-slices`, `QAS-clean-owned-parallel-slice-pilot`

## Mission

Review release `0.6.0` as a repository reader. Confirm one release identity across package
authorities and canonical assertions, confirm the package and adoption path ship the promised
parallel-executor contracts, and compare every release-note claim with the current feature contract,
technical validation, and durable QA. Keep the check local: this private package may be packed for
inspection but must not be published.

## Expected observable

The newest changelog heading, package manifest, both root lockfile fields, canonical release
assertions, package dry-run metadata, adopted files, and documented full test command agree on
`0.6.0`. Shipped contracts expose opt-in `disabled`, `safe`, and `full` modes while preserving
sequential TLC tasks, deterministic slice coordination, checkpoint synchronization, resource
preflight, and fail-closed serial fallback. Release prose reports the real Orca/Codex two-lane
lifecycle and completed-pilot cleanup as `BLOCKED-VERIFY`, not as pass or completed-pilot evidence.
Ignored local state and raw QA evidence stay outside the package, and no npm publication, tag, or
remote action occurs.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| Release identity | User-visible metadata. Walk `J-review-workflow-release` through `REL-report-current-workflow-release`; independently compare `CHANGELOG.md`, `package.json`, both root `package-lock.json` fields, and canonical `0.6.0` assertions. |
| Package and publication boundary | User-visible package metadata and membership. Map to `REL-report-current-workflow-release`; use only `npm pack --dry-run --json`, confirm `private: true`, and never run `npm publish` or contact a registry. |
| Full test command | Public documentation and package script. Confirm README names `npm run test:all`, package metadata defines it as canonical Vitest plus Python discovery, and package membership includes the scripts it invokes. Do not use a narrower gate as release evidence. |
| Opt-in modes and frozen configuration (`EXE-01`, `EXE-18`, `EXE-19`, `EXE-21`) | Public configuration promise. Map release-note truth to `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, and `CFG-fallback-unproven-parallel-execution`; inspect current shipped config/resolver/executor contracts and reuse their terminal reports as canaries. |
| Sequential TLC tasks and deterministic lane coordination (`EXE-02`, `EXE-09`, `EXE-10`) | Public workflow promise. Map to `CFG-plan-parallel-slice-dispatch` and `QAS-run-resource-free-parallel-orca-slices`; confirm installed prose and CLI contracts preserve task order. The real worker lifecycle remains `blocked-verify`. |
| Durable state, idempotency, and recovery (`EXE-03`-`EXE-05`, `EXE-11`) | Internal executor mechanics with public fail-closed outcomes. Do not invent a live mutation walk. Compare the changelog claim with technical validation and inspect the public fallback/recovery contract through `CFG-fallback-unproven-parallel-execution`. |
| Orca worktree/worker/follow-up lifecycle (`EXE-06`-`EXE-10`) | Public CLI journey. Canonical owner is `QAS-run-resource-free-parallel-orca-slices`; preserve its `blocked-verify` external Orca/Codex verdict. Release QA checks claim truth and package/adoption bytes, not a new real-worker run. |
| Checkpoint rebase, evidence invalidation, and deterministic integration (`EXE-12`-`EXE-17`) | Internal Git execution with a documented operator contract. Compare release prose and packaged/adopted bytes with the spec and technical PASS; no destructive checkpoint or integration walk is required for release metadata QA. |
| Resource receipts and cleanup (`EXE-18`-`EXE-22`, `SEC-007`, `SEC-008`) | Public preflight/fallback plus external cleanup boundary. Reuse `CFG-fallback-unproven-parallel-execution` as the passing zero-effect canary and preserve `QAS-clean-owned-parallel-slice-pilot` as `blocked-verify`; do not claim runtime/DB isolation or completed cleanup. |
| Blocker-scoped convergence (`EXE-23`-`EXE-25`) | Public unattended-workflow promise. Map to `QAS-bound-verifier-remediation-per-blocker`; compare changelog wording with the shipped ledger CLI and terminal R19 evidence without mutating the checkout ledger. |
| Security controls (`SEC-001`-`SEC-006`) | Internal trust-boundary mechanics already covered by independent technical verification. Release QA checks that package/adoption contains the validated contracts and that release notes make no broader runtime claim. |
| External Orca/Codex lifecycle truth | User-visible release limitation. Confirm `CHANGELOG.md`, README/profile, scenario records, and the terminal feature report consistently retain `QAS-run-resource-free-parallel-orca-slices` and `QAS-clean-owned-parallel-slice-pilot` as `blocked-verify`. Any pass/completed-pilot wording is a defect. |
| Adoption and package contents | User-visible distribution path. Map to `REL-report-current-workflow-release` with `ADP-adopt-workflow-safely` as adjacent canary; confirm fresh adoption and re-adoption deliver current workflow-config, autonomous, TLC, executor, QA pilot, and documentation contracts while preserving consumer-owned local config. |
| Scoped autonomous authority | Existing public promise touched by the release journey. Confirm current AGENTS, autonomous, README, and workflow docs agree: invocation authorizes scoped feature-branch push, one pull request, and merge after readiness; release and other remote actions remain separately authorized. Perform no remote action. |
| English public/versioned text | Docs-as-interface. Inspect the `0.6.0` changelog section and user-facing tracked/package-member prose added or changed since `v0.5.0`. Names, commands, paths, identifiers, and quoted provider syntax are not prose violations. |
| Changelog and release-note truth | `CHANGELOG.md` is the checkout's release-note candidate. Every Added, Changed, and Fixed bullet needs a shipped-contract pointer and bounded durable evidence. No GitHub release creation or remote lookup belongs to this charter. |

The release changes the existing release promise and its journey route, so
`REL-report-current-workflow-release` is reset to `untested` and
`J-review-workflow-release` now includes parallel capability and limitation checks. No new scenario
id is needed.

## Planned probes

1. Independently read the newest `CHANGELOG.md` heading, `package.json` version, both root
   `package-lock.json` version fields, and canonical version assertions. Confirm all report `0.6.0`.
2. Confirm `package.json` remains private and its canonical full gate is `npm run test:all`, with
   scoped Vitest plus deterministic Python test discovery. Confirm README names the same command.
3. Run `npm pack --dry-run --json` from the active checkout. Reload captured JSON; confirm package
   name/version, required public files for every `0.6.0` claim, and exclusion of ignored
   `.my-workflow.toml`, generated provider runtimes, `docs/qa/evidence/`, `node_modules`, and tarball
   residue. Do not run `npm publish`.
4. Compare every `0.6.0` Added, Changed, and Fixed bullet with `v0.5.0..28798c7`, the parallel
   executor spec, post-main technical validation, and terminal feature QA. Keep technical PASS and
   external `blocked-verify` as separate evidence classes.
5. Follow the package/adoption read path into a checkout-local disposable target. Run fresh adoption
   and re-adoption; reload installed bytes; confirm current configuration, planner, executor, Orca/Git
   adapters, convergence helper, QA pilot, TLC pointers, and parallelization documentation arrive as
   promised while consumer-owned local config survives.
6. Resolve one disposable feature for each `disabled`, `safe`, and `full` mode through the profile's
   public resolver path. Independently reload stdout and snapshot JSON; confirm mode/provider freeze,
   deterministic output, and no host-specific runtime state enters versioned specs.
7. Walk only the effect-free planner/executor boundaries needed for release truth: disabled,
   unsupported capability, and resource-bearing lane without a provider. Confirm decisive serial
   reasons, empty actions, and zero new worktree/worker/runtime residue. Do not rerun a real Orca
   worker lifecycle.
8. Inspect packaged/adopted contracts for sequential per-slice tasks, event-driven follow-up,
   checkpoint rebase/integration, evidence invalidation, and deterministic final integration. Use
   current technical validation for unsafe Git/process mechanics; do not create live conflicts.
9. Read the current convergence CLI/ledger contract and retained R19 report. Confirm distinct blocker
   fingerprints count independently and the same fingerprint halts only after its third failed
   remediation. Do not mutate the checkout ledger.
10. Reconcile `QAS-run-resource-free-parallel-orca-slices` and
    `QAS-clean-owned-parallel-slice-pilot` with the terminal feature report and changelog. They must
    remain `blocked-verify`; retained live residues must not be cleaned or reported as success.
11. Confirm adoption prints but does not invoke the separately authorized external-security
    installer. Do not use network access, install external skills, or touch a non-disposable target.
12. Inspect public authority prose. Confirm `autonomous` invocation is limited to scoped branch push,
    one pull request, and merge after readiness; release, deploy, production mutation, force-push,
    direct `main` push, and unrelated remote actions remain separately authorized.
13. Inspect the `0.6.0` changelog and all user-facing tracked/package-member prose changed since
    `v0.5.0` for English. Record each inspected path and exclude proper names, commands, paths,
    identifiers, and provider syntax from the prose judgment.
14. Capture ignored raw evidence under `docs/qa/evidence/2026-08-25-release-0-6-0/`, write
    `docs/qa/reports/2026-08-25-release-0-6-0.md`, and update only the release scenario unless a
    current canary contradiction requires a defect. Preserve all earlier charters and reports.
15. Confirm checkout-local cleanup and residue. Record that no `npm publish`, tag, push, pull request,
    merge, release creation, deploy, product edit, real Orca worker action, or non-disposable target
    action occurred.

## QA Execute handoff

Use a distinct fresh Verifier with the canonical `qa-execute` skill and the CLI/manual adapter in
`docs/qa/README.md`. Work only in
`/Users/antoniofulg/orca/workspaces/my-workflow/feat-parallel-slice-executor` at
`28798c729ac470a0427d430198e70005fc45f089`. Start at `CHANGELOG.md` -> `0.6.0`; use
`npm pack --dry-run --json`, checkout-local disposable Git/adoption/resolver targets, independent
file/JSON reloads, and the current technical and QA reports named above. Write raw evidence to
`docs/qa/evidence/2026-08-25-release-0-6-0/`, the durable report to
`docs/qa/reports/2026-08-25-release-0-6-0.md`, and the verdict to
`docs/qa/scenarios/REL-report-current-workflow-release.md`.

Do not modify product code or historical release artifacts. Do not run `npm publish`, create a tag
or release, contact GitHub/npm, install external skills, or perform push, pull request, merge,
deploy, machine lifecycle, real Orca worker, retained-residue cleanup, or non-disposable-target
actions. Preserve both parallel lifecycle scenarios as `blocked-verify` unless a separate authorized
real-worker cycle produces their own terminal evidence. If any product contradiction appears,
record a bug, hand it to an Implementer, end this Verifier session, and require a fresh Verifier
after the fix.
