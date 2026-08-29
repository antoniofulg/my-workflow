# CH-review-release-0-7-0-2026-08-29

- **Date:** 2026-08-29
- **Time-box:** 40 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release identity, package membership, adoption, and hybrid-slice claim truth
- **Public entry point:** `CHANGELOG.md` -> `0.7.0`
- **Adapter candidate:** CLI/manual repository and checkout-local disposable-target inspection
- **Scenario:** `REL-report-current-workflow-release`
- **Adjacent canaries:** `ADP-adopt-workflow-safely`, `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, `CFG-fallback-unproven-parallel-execution`, `QAS-coordinate-assisted-slices-offline`, `QAS-run-resource-free-parallel-orca-slices`, `QAS-clean-owned-parallel-slice-pilot`

## Mission

Review release candidate `0.7.0` as a repository reader. Confirm one release identity across the
package authorities, package membership, changelog, and canonical assertions. Re-adopt the packaged
workflow into a disposable consumer and compare every hybrid-slice release claim with installed
public contracts and current durable evidence. Keep the review local and offline: inspect the
private package, but do not publish it, create a tag or release, contact a registry, or invoke live
Orca.

## Expected observable

The newest changelog heading, package manifest, both root lockfile fields, dry-run package metadata,
canonical assertions, and independently reloaded adopted files agree on `0.7.0`. The package and
adoption paths contain the assisted-by-default workflow, `workflow-spec-driven`, adaptive scheduler,
and pointer-only probe; re-adoption preserves consumer-owned state byte-for-byte; importing the
installed probe makes zero Orca calls; hybrid configuration and offline coordination canaries still
match their current passing promises; cleanup leaves no disposable target, package residue, or
extra worktree. The real Orca/Codex lifecycle and completed-pilot cleanup remain `blocked-verify`,
and no npm publication, tag, GitHub release, push, merge, deploy, or live Orca action occurs.

## Criterion disposition

| Changed promise | Disposition |
| --- | --- |
| `0.7.0` version metadata | User-visible package identity. Walk `J-review-workflow-release` through `REL-report-current-workflow-release`; compare `package.json`, both root `package-lock.json` version fields, the newest changelog heading, dry-run package JSON, and canonical version assertions. |
| Changelog truth for `v0.6.0..candidate` | Docs-as-interface. Map every `0.7.0` Added, Changed, and Fixed claim to shipped files or durable validation in the exact local Git range from `v0.6.0` through the candidate HEAD. Any claim broader than its evidence is a release defect. |
| Package membership | User-visible distribution promise owned by `REL-report-current-workflow-release`. Inspect only `npm pack --dry-run --json`; confirm required workflow, scheduler, probe, templates, tests invoked by the public full gate, license/notice, and adoption files are members while ignored runtime/evidence state and tarball residue are absent. |
| Adoption and re-adoption | User-visible installation promise. Use `ADP-adopt-workflow-safely` as the adjacent canary; adopt into a checkout-local disposable Git target, reload installed bytes, then re-adopt after changing consumer-owned `.my-workflow.toml` and `docs/qa/README.md` and prove exact preservation. |
| Pointer-only probe import | User-visible installed-tool safety. Through the adoption canary, import the installed `tools/orca_assisted_probe.py` with a call-counting fake `orca` on `PATH`; require zero Orca calls and no ledger or other effect. Do not invoke live Orca. |
| Assisted-by-default hybrid workflow | User-visible configuration and operator promise. Reconfirm `CFG-freeze-feature-workflow`, `CFG-plan-parallel-slice-dispatch`, `CFG-fallback-unproven-parallel-execution`, and `QAS-coordinate-assisted-slices-offline` through their public offline CLIs and independently reloaded state. Do not substitute technical tests for the observable canaries. |
| Sequential slice tasks, dependency release, leases, exactly-once effects, and owned cleanup | Public outcomes with internal mechanics. Compare release prose with installed contracts and current technical validation; walk only the safe offline fake-provider canaries needed to prove observable decisions, pointer transport, one physical mutation per logical effect, and zero owned residue. |
| Full test command and canonical assertions | Public package command with internal supporting evidence. Confirm `package.json` still exposes `npm run test:all`, its member scripts are packaged, and the independent closing gate succeeds. It supports but does not replace the package/adoption walk. |
| No npm publish, tag, or release | User-visible authority boundary. Confirm `private: true` and current authority prose keep publication, tagging, GitHub release creation, deploy, and other remote actions separately authorized. Record that none occurred; `npm pack --dry-run --json` is the only package operation. |
| Live Orca limitation | User-visible release limitation. Preserve `QAS-run-resource-free-parallel-orca-slices` and `QAS-clean-owned-parallel-slice-pilot` as `blocked-verify`; reconcile changelog, profile, scenarios, and retained report language. Offline fakes cannot convert either scenario to pass. |
| Release assertion updates | Internal test maintenance that does not create another user promise. Keep it mapped to the version-metadata disposition as supporting evidence; do not mint a scenario or add QA purely for coverage. |

The existing version-neutral release scenario is already reset to `untested`; no new scenario id is
needed. The journey route still covers package identity, hybrid claims, adoption, configuration,
and the external-host limitation, so `J-review-workflow-release` needs no change.

## Planned probes

1. Record candidate HEAD and independently read the newest `CHANGELOG.md` heading, `package.json`
   version/private flag, both root `package-lock.json` version fields, and canonical version
   assertions. Require one `0.7.0` identity.
2. Run `npm pack --dry-run --json` from the active checkout and save its stdout as raw evidence.
   Reload the JSON in a fresh process; confirm name/version and required public members, and confirm
   ignored local config, generated provider runtimes, raw QA evidence, dependencies, and tarball
   residue are absent. Never run `npm publish`.
3. Enumerate `git diff --name-status v0.6.0..HEAD` and `git log --oneline v0.6.0..HEAD`. Compare every
   `0.7.0` changelog claim with its shipped contract and current durable technical/QA evidence.
   Keep offline PASS, technical PASS, and live `blocked-verify` as distinct evidence classes.
4. Create a checkout-local disposable Git consumer and run the public `scripts/adopt.py` entry
   point. Reload the installed managed files and compare their hashes with package/source members,
   including `workflow-spec-driven`, autonomous parallelization, workflow configuration, agent role
   templates, `tools/orca_assisted_probe.py`, and the QA pilot. Confirm the obsolete TLC skill is
   absent.
5. Put a call-counting fake `orca` on the disposable target's `PATH`, import the installed probe in a
   fresh Python process, and require zero calls, no ledger, and no mutation.
6. Modify only consumer-owned `.my-workflow.toml` and `docs/qa/README.md`, record hashes, re-run
   adoption, reload both files, and require exact byte identity. Confirm managed release files are
   restored to current source bytes.
7. Through installed public CLIs, reconfirm adjacent hybrid canaries: one ready slice uses
   `serial-integration` without a new worktree; compatible writers plan concurrently; disabled,
   conflicting, dependency-blocked, or unproven-resource paths fail closed with zero effects; the
   offline assisted probe sends only the packet pointer and reconciles repeated logical effects to
   one physical fake-provider mutation. Use no live Orca endpoint.
8. Reload the fake-provider ledgers and cleanup result independently. Require owned residue `[]`,
   preservation of an unrelated canary, removal of every disposable target/worktree, and the same
   project worktree inventory observed at preflight.
9. Reconcile the release note and QA registry with `QAS-run-resource-free-parallel-orca-slices` and
   `QAS-clean-owned-parallel-slice-pilot`. Both must remain `blocked-verify`; do not stop, clean, or
   otherwise touch retained live-host evidence.
10. Confirm `package.json` remains `private: true`, the full gate command is
    `npm_config_offline=true npm run test:all`, and public authority prose does not authorize release
    publication. Record zero tag, GitHub release, registry, push, pull-request, merge, deploy, or live
    Orca actions.
11. Capture raw evidence under `docs/qa/evidence/2026-08-29-release-0-7-0/`, write the immutable
    durable report `docs/qa/reports/2026-08-29-release-0-7-0.md`, and update only
    `REL-report-current-workflow-release` unless a current adjacent canary contradiction requires a
    defect and its owning scenario.

## QA Execute handoff

Use a distinct fresh Verifier with the canonical `qa-execute` skill and the CLI/manual adapter from
`docs/qa/README.md`. Work only in the clean release-candidate checkout and checkout-owned disposable
paths at the candidate commit provided by the coordinator. Start at `CHANGELOG.md` -> `0.7.0`; use
`npm pack --dry-run --json`, local Git history from `v0.6.0` through candidate HEAD, disposable
adoption/re-adoption, a call-counting fake `orca`, installed workflow CLIs, and independent
file/JSON/hash reloads. Write raw evidence to
`docs/qa/evidence/2026-08-29-release-0-7-0/`, the durable report to
`docs/qa/reports/2026-08-29-release-0-7-0.md`, and the verdict to
`docs/qa/scenarios/REL-report-current-workflow-release.md`.

Do not modify release/product code or historical QA artifacts. Do not run `npm publish`, create or
push a tag, create a GitHub release, contact GitHub/npm, push, open or merge a pull request, deploy,
install external skills, invoke live Orca, clean retained host evidence, or touch a non-disposable
target. Preserve both live Orca scenarios as `blocked-verify`. If a product contradiction appears,
record a bug, hand it to an Implementer, end the QA Execute session, and require a fresh Verifier
after the fix.
