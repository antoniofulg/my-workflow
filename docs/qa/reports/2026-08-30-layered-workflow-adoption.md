# Layered Workflow Adoption QA Execute

**Date:** 2026-08-30
**Candidate:** `714716c419874fdb85de24c34f741ecfa96550e8`
**Adapter:** CLI/manual through `scripts/adopt.py` and independent filesystem reads
**Environment:** checkout-local disposable targets; Bun 1.4.0; Python 3; fake `orca` only
**Opening gate:** `bun run test:all` — exit 0; 123 Bun tests passed, 0 failed across 8 files; Python adoption suite ended `ok (64 tests)`
**Raw evidence:** `docs/qa/evidence/2026-08-30-layered-workflow-adoption/`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-plan-layered-workflow-adoption-2026-08-30` | `ADP-layered-workflow-adoption` | pass | A recursive target snapshot stayed identical through text, JSON, normalized, full, unknown-layer, and legacy-command plans. | `plan-*.stdout.txt`; `plan-*.stderr.txt`; `summary.json` |
| `CH-apply-layered-workflow-adoption-2026-08-30` | `ADP-layered-workflow-adoption`; canary `ADP-adopt-workflow-safely` | pass | Reloaded manifest, instructions, packets, sentinels, hashes, symlinks, status JSON, and snapshots confirmed cumulative state and all-preflight refusal. | `apply-*.stdout.txt`; `status-*.stdout.txt`; `summary.json` |
| `CH-adopt-full-layered-workflow-2026-08-30` | `ADP-layered-workflow-adoption`; canary `REL-report-current-workflow-release` | pass | Reloaded installed inventory, Bun output, fake-Orca call file, package metadata, changelog, package listing, and post-reapply snapshot. | `full-*.stdout.txt`; `package-dry-run.txt`; `bun-version.txt`; `summary.json` |

## Session

### Plan-first walk

`python3 scripts/adopt.py plan <target> --layers parallel,quality` produced deterministic text on
two reads. The JSON form emitted one parseable stdout object, empty stderr, resolved
`core,parallel,quality`, and listed 147 unique path actions. Duplicate and whitespace input
normalized to the same order; `full` resolved exactly `core,parallel,quality,extras`. Unknown-layer
and removed positional commands each exited 2 with actionable stderr. The target snapshot remained
byte-identical across every plan and refusal.

### Incremental walk

`apply core`, `apply parallel`, then `apply quality,extras` produced schema 1 with all four layers,
122 recorded files, four managed instruction blocks, and 15 generated provider packets. Independent
reads confirmed consumer prose outside managed blocks, `package.json`, `bun.lock`, local config, QA
profile, `tools/ad-index.py`, unrelated bytes, custom skill source, and its Claude symlink remained
unchanged. Clean status exited 0. Reapply and `--skip-agents` were byte-stable.

After one managed-file mutation, status exited 1 without writes and apply returned the complete
conflict before writes. Missing and unsupported manifests exited 2 unchanged. An unowned collision,
unsafe parent symlink, and invalid managed-block marker each refused the complete operation; the
target and external referent snapshots remained identical. Restoring the managed byte returned
status to exit 0.

### Full-profile walk

Fresh `plan full` listed 157 unique actions. `apply full` recorded 122 files and four blocks; all
remaining 31 actions were present as derived packets, Claude links, merged files, local config, or
the manifest. `bun tools/knowledge/src/cli.ts` exited 0 without installing packages or changing the
consumer package/lock. Importing `tools/orca_assisted_probe.py` with a call-counting fake `orca`
exited 0 and recorded 0 Orca calls. Reapply was byte-identical. The installed target contained 0
repository test files and 0 temporary/package residue paths.

## Edge probes and lenses

- Edge probes passed: duplicate/whitespace layers; unknown layer; legacy command; skip-agents;
  managed drift; missing manifest; unsupported manifest; unowned collision; unsafe symlink; invalid
  block marker; repeated apply; no adopted tests or residue.
- Comprehension/language: README commands, help, resolved layers, action verbs, and stderr made the
  next action visible; JSON kept diagnostics off stdout.
- Recovery/trust: status distinguished clean/drift/invalid with exits 0/1/2; restoring the one
  changed byte recovered clean state; every rejected mutation kept target and external snapshots.
- Speed: plan, incremental apply, full apply, status, Bun knowledge, and probe import completed in
  one local CLI session without package installation, network, or interactive waits.
- Accessibility: no browser/UI surface exists; the documented CLI and machine-readable JSON were
  both reachable through the declared adapter.

## Adjacent canaries

- `ADP-adopt-workflow-safely`: pass retained. Consumer config/profile/package/lock/custom skill
  bytes and pointer survived; 15 provider packets regenerated; probe import caused no Orca effect.
- `REL-report-current-workflow-release`: pass retained. `package.json` version `0.7.0`, newest
  changelog heading `0.7.0`, `packageManager` `bun@1.4.0`, `bun.lock`, README Bun 1.4.x commands, and
  `bun pm pack --dry-run --ignore-scripts` agreed. Dry-run listed 453 files and created no `.tgz`.

## Limitations and boundaries

No live Orca, network, external security-skill installation, registry, publication, release, or
non-disposable target was used. Existing live Orca/Codex bugs and blocked scenarios remain unchanged.
No browser, API, mobile, auth, server, or production-health surface exists for this repository.

## Cleanup and residue

The session harness removed both disposable project targets and the preliminary shape target.
`summary.json` records `disposable_targets_remaining: false`; package residue was absent. Source
checkout changes before the closing gate are limited to this durable report and the planned scenario
status update; raw evidence remains ignored under the declared evidence path.

## Final gate

`bun run test:all` exited 0 after the durable status update: 123 Bun tests passed, 0 failed
across 8 files, and every tracked Python suite passed, including `ok (64 tests)` for adoption.
Skipped tests: none. Evidence: `final-gate.txt`.
