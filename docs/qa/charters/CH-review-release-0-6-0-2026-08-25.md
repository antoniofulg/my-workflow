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
- **Parallel release scope:** release identity, package contents, adoption, public parallel-executor
  claims, and the retained Orca/Codex limitation
- **Parallel time-box:** 35 minutes
- **Parallel scenarios:** `REL-report-current-workflow-release` with adjacent canaries
  `ADP-adopt-workflow-safely`, `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`,
  `CFG-fallback-unproven-parallel-execution`, `QAS-bound-verifier-remediation-per-blocker`,
  `QAS-run-resource-free-parallel-orca-slices`, and `QAS-clean-owned-parallel-slice-pilot`

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
## Parallel executor mission

Review release `0.6.0` as a repository reader. Confirm one release identity across package
authorities and canonical assertions, confirm the package and adoption path ship the promised
parallel-executor contracts, and compare every release-note claim with the current feature contract,
technical validation, and durable QA. Keep the check local: this private package may be packed for
inspection but must not be published.

## Parallel executor expected observable

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
| HSC-16 | Internal decision-index invariant. Verify `AD-015`/`AD-008` state with the owning index checks; no direct user journey changes. |
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
## Parallel executor criterion disposition

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
