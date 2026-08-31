# CH-review-release-0-8-0-2026-08-31

- **Date:** 2026-08-31
- **Scope:** `origin/main...9751bd7` on `release/0.8.0`
- **Time-box:** 45 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release identity, private package, adoption, first-use locking, and honest Orca boundary
- **Public entry point:** `CHANGELOG.md` -> `0.8.0`; `package.json`; `scripts/adopt.py`;
  `tools/resource_lock.py`
- **Adapter candidate:** Existing CLI/manual adapter with checkout-owned disposable Git targets,
  declared by [`docs/qa/README.md`](../README.md)
- **Scenario:** [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)
- **Adjacent canaries:** `ADP-layered-workflow-adoption`,
  `ADP-resolve-legacy-adoption-conflicts`, `QAS-serialize-heavy-test-resources`,
  `QAS-coordinate-assisted-slices-offline`, `QAS-run-resource-free-parallel-orca-slices`,
  `QAS-clean-owned-parallel-slice-pilot`

## Mission

Review candidate 0.8.0 through its public repository and installed CLI surfaces. Prove that one
private source pack contains the advertised adoption, lock, assisted-probe, and remediation tools;
that new and legacy disposable consumers can adopt it; and that two repositories safely serialize
the first use of one machine-scoped resource. Preserve the live Orca boundary as unverified.

## Expected observable

Fresh reads agree on 0.8.0 and the private package boundary. Frozen Bun install and the full gate
pass offline. Bun's dry-run pack contains `tools/qa_parallel_pilot.py`, `tools/resource_lock.py`,
`tools/orca_assisted_probe.py`, `.agents/skills/autonomous/remediation.py`, and `scripts/adopt.py`.
Layered and exact-conflict legacy adoption reach clean, byte-stable re-adoption. Two initially
absent, machine-scoped lock invocations from different disposable repositories each execute once,
never overlap, and produce exactly one waiter diagnostic. Importing the installed assisted probe
with a call-counting fake `orca` makes zero Orca calls. Live Orca scenarios remain
`blocked-verify`, and cleanup leaves no release-owned fixture, package, process, worktree, or lock
residue.

## Criterion disposition

- `RLS-01`: primary scenario; independently reload all release and Bun dependency authorities.
- `RLS-02`: primary scenario; inspect private dry-run package membership and residue.
- `RLS-03`: primary scenario; this charter owns fresh release QA.
- `RLS-04`: primary scenario plus both live-host adjacent canaries; retain `blocked-verify`.
- `RLS-05`: outside this charter; verify only after authorized remote delivery.

## Planned walk

1. Record candidate `HEAD`, source status, worktree inventory, running release-owned fixture
   processes, and root `.tgz` names. Use only uniquely named paths owned by this checkout. Never
   touch active CRM or Creatista checkouts.
2. Independently reload `package.json`, `CHANGELOG.md`, `bun.lock`, the current release scenario,
   and canonical release assertions. Require manifest and newest changelog identity `0.8.0`,
   `private: true`, the Bun root package and dependency graph, and the unchanged
   `blocked-verify` language.
3. Run the public offline frozen gate from the candidate checkout:

   ```bash
   npm_config_offline=true bun install --frozen-lockfile
   npm_config_offline=true bun run test:all
   ```

   Record exact exits and counts. Do not install from a network or change package authorities.
4. Run `bun pm pack --dry-run --ignore-scripts`, save its output, and reload it independently.
   Require the five named release-critical members, package identity, and absence of ignored
   runtime/evidence state. Compare root `.tgz` names before and after; the dry run must add none.
5. Create one disposable Git consumer for layered adoption. Use public `plan`, `apply`, and
   `status` for `core` plus `parallel`; require read-only planning, clean managed status, installed
   release-critical files, preserved consumer-owned instructions/config/profile, and byte-stable
   re-adoption.
6. Create a separate clean legacy Git consumer with `HEAD`, no adoption manifest, and a deliberate
   tracked conflict set. Require `plan` to report the exact sorted conflicts, an incomplete
   `resolve` to refuse without writes, and successful `resolve` to repeat every and only reviewed
   `--replace` path. Preserve instruction bytes with `--skip-agents`, then require clean `status`
   and byte-stable normal re-apply.
7. From the two disposable repositories, choose one unique machine-scoped resource whose lock is
   absent at preflight. Start synchronized public wrapper invocations without prewarming the lock.
   Each child writes start/end/call sentinels. Require exactly one child call per repository,
   non-overlapping intervals, both successful exits, and exactly one bounded wait diagnostic.
8. Put a call-counting fake `orca` first on `PATH` and import the assisted probe installed by
   adoption in a fresh Python process. Require import success, zero fake-Orca calls, and no probe
   ledger or other mutation. Do not dispatch to live Orca.
9. Map every 0.8.0 changelog claim to a shipped public path and current technical or QA evidence.
   Confirm offline fake-provider evidence does not claim the real Orca/Codex lifecycle or completed
   pilot cleanup. Keep both live-host scenarios `blocked-verify` with pending retest.
10. After independent readback, stop only current-run processes and remove only exact current-run
    consumers, fake executable, sentinels, and the uniquely attested QA lock namespace. Require the
    original worktree inventory and package-residue snapshot, no disposable target, and source
    status changed only by planned durable QA report/scenario artifacts.
11. Store raw evidence under `docs/qa/evidence/2026-08-31-release-0-8-0/`, write
    `docs/qa/reports/2026-08-31-release-0-8-0.md`, and update the release scenario from observed
    evidence. Record limitations and exact commands. Do not push, merge, tag, publish, contact
    GitHub, invoke live Orca, or perform any other remote action.

## QA Execute handoff

Use a distinct fresh Verifier with `phase: qa-execute` and the canonical `qa-execute` skill. Read
[`docs/qa/README.md`](../README.md), this charter, the primary scenario, and every named adjacent
canary. Use its existing CLI/manual adapter only in the clean candidate checkout and isolated
disposable Git targets. Preserve every live-host and historical evidence path.

If a public observable contradicts the charter, create or update its deduplicated bug, hand the
defect to an Implementer, stop execution, and require another fresh Verifier after the fix. This
charter authorizes no product change, live Orca operation, network access, remote delivery, or
write to a real consumer project.
