# CH-review-release-0-9-2-2026-09-04

- **Date:** 2026-09-04
- **Scope:** `main...f0099a87` on `fix/deep-review-defects-in-run`
- **Time-box:** 20 minutes
- **Persona:** Repository reader
- **Journey:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md)
- **Tour:** Release identity, packaged deep-review closeout contract, and package residue
- **Public entry point:** `CHANGELOG.md` -> `0.9.2`; `package.json`;
  `docs/guidelines/REVIEW-ROUNDS.md`; `docs/workflow/reviews.md`
- **Adapter candidate:** Existing CLI/manual adapter in the active checkout, declared by
  [`docs/qa/README.md`](../README.md)
- **Scenario:**
  [`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md)
- **Adjacent canary:** Release 0.9.1 adoption and real 0.8.0 migration verdict in
  [`2026-09-04-release-0-9-1`](../reports/2026-09-04-release-0-9-1.md)

## Mission

Review candidate 0.9.2 through its public repository and private package surfaces. Prove that the
release identity is consistent, the package contains the changed deep-review closeout contract,
the canonical structural assertion recognizes that contract, the supplied closing full gate is
green, and package inspection leaves no archive or checkout residue. Do not repeat adoption or
migration: those public surfaces are unchanged from the passing 0.9.1 report.

## Expected observable

Fresh reads agree on version 0.9.2 across the manifest, newest changelog heading, adoption version,
lock entry, release scenario, and canonical assertions. The changelog's claim matches the packaged
contract: every confirmed deep-review defect closes in the originating feature run; Blocker and
Major defects retain capped review rounds; Minor defects close in one current-run batch with one
scoped gate and commit but no fresh Technical Verifier, QA phase, or deep-review round; Cosmetics
and advisories remain follow-ups. The targeted structural assertion passes, supplied full-gate
evidence identifies the exact candidate and exits zero, the private dry-run package contains the
changed contract and excludes ignored evidence/dependency paths, and no `.tgz` or other
release-owned residue remains.

## Criterion disposition

- `RLS-092-01` — release identity is user-visible package metadata. Map to
  `J-review-workflow-release` through `REL-report-current-workflow-release`; independently compare
  `package.json`, the newest `CHANGELOG.md` heading, `scripts/adopt.py`, `skills-lock.json`, the
  release scenario, and version assertions.
- `DRC-01` — every confirmed deep-review defect closes in the originating feature run. This is a
  public installed-workflow promise owned by the release scenario; inspect the packaged
  `REVIEW-ROUNDS.md`, `docs/workflow/reviews.md`, and readiness/output contracts.
- `DRC-02` — Blocker and Major defects may trigger the next capped review round. Same public
  disposition; compare the changelog claim with packaged policy prose.
- `DRC-03` — Minor defects close in one current-run batch with one scoped gate and commit, without
  a new Technical Verifier, QA phase, or deep-review round. Same public disposition; additionally
  run the single canonical structural assertion that binds all installed references.
- `DRC-04` — Cosmetics and advisories remain follow-ups and do not block delivery. Same public
  disposition; inspect packaged policy and readiness/output contracts.
- `RLS-092-02` — package membership and zero residue are user-visible distribution promises. Map
  to the release scenario and inspect only Bun's private dry-run package output plus before/after
  checkout state.
- `RLS-092-03` — a green full gate on the exact final candidate is release evidence. Map to the
  release scenario; consume the coordinator-supplied exact command, commit, exit, and counts. Run a
  fresh gate only when that evidence is absent, stale, or not tied to the candidate under review.
- `ADP-091-CANARY` — adoption and real 0.8.0 `--skip-agents` migration are unchanged. Reuse the
  passing 0.9.1 report as the adjacent canary after confirming this release diff does not alter
  adoption behavior beyond version identity; do not create consumers or repeat migration.
- `RLS-092-04` — tag, GitHub release, and publication are outside QA Execute. Verify only after
  separately authorized remote delivery.

## Planned walk

1. Record candidate `HEAD`, source status, worktree inventory, and root `.tgz` names. Use only
   paths owned by this checkout. Do not touch CRM, Creatista, or another consumer checkout.
2. Independently reload the six identity authorities named by `RLS-092-01`. Require version
   `0.9.2`, `private: true`, `bun@1.4.0`, a matching Bun root package, and no `package-lock.json`.
3. Read the 0.9.2 changelog section, then inspect the source policy and installed-package member
   bytes covering `DRC-01` through `DRC-04`. Require one coherent contract across:
   `docs/guidelines/REVIEW-ROUNDS.md`, `docs/workflow/reviews.md`,
   `.agents/skills/autonomous/SKILL.md`, `.agents/skills/wimplement/SKILL.md`, and
   `.agents/skills/deep-review/references/output-contracts.md`. Do not infer that Cosmetic or
   advisory findings are defects.
4. Run only the canonical Bun structural assertion:

   ```bash
   bun test tools/shared/tests/qa-skills.test.ts \
     -t "fixes every deep-review defect inside the originating feature run"
   ```

   Record the exact command, exit, and assertion result. Do not substitute a broad suite for this
   targeted structural check.
5. Consume the coordinator's closing `bun run test:all` evidence. Require exact candidate commit,
   exit `0`, Bun test count, and every discovered Python suite result. If any field is absent or the
   evidence predates the final commit, run `bun run test:all` once and record it; never claim a
   cached, partial, or differently based gate.
6. Run `bun pm pack --dry-run --ignore-scripts` from the active candidate and save its output.
   Require package identity 0.9.2; membership of every contract file in step 3 and the canonical
   test file; absence of `node_modules`, `docs/qa/evidence`, and package archives; and no `.tgz`
   added between the before/after snapshots.
7. Re-read the immutable 0.9.1 release report. Confirm `main...HEAD` changes no adoption or
   migration behavior except release identity updates in `scripts/adopt.py` and its assertions.
   Carry its passing real 0.8.0 migration result as the adjacent canary without running adoption,
   creating a consumer, or rewriting its evidence.
8. Independently reload the candidate files and captured outputs. Remove only exact current-run
   disposable material, if any, and require checkout status to differ from preflight only by the
   planned durable QA report and scenario update.
9. Store ignored raw evidence under `docs/qa/evidence/2026-09-04-release-0-9-2/`, write the immutable
   report `docs/qa/reports/2026-09-04-release-0-9-2.md`, and update only the current release
   scenario unless a canary contradiction proves another owner stale. Record all limitations and
   exact commands. Do not push, merge, tag, publish, contact GitHub/npm, install external skills,
   invoke live Orca, or modify product/policy code.

## QA Execute handoff

Dispatch a distinct fresh Verifier with `phase: qa-execute` and the canonical `qa-execute` skill.
It must read [`docs/qa/README.md`](../README.md), this charter,
[`REL-report-current-workflow-release`](../scenarios/REL-report-current-workflow-release.md), and
the immutable [`0.9.1 release report`](../reports/2026-09-04-release-0-9-1.md). Use the declared
CLI/manual adapter in the clean candidate checkout. The exact execution path is: identity readback
-> installed/package contract readback -> one named structural assertion -> supplied closing-gate
validation (or one fresh full gate only if stale/incomplete) -> dry-run package membership and
residue -> 0.9.1 adjacent-canary reconciliation -> independent reload and cleanup.

Expected durable outputs are
`docs/qa/reports/2026-09-04-release-0-9-2.md` and the updated
`docs/qa/scenarios/REL-report-current-workflow-release.md`; ignored raw evidence belongs under
`docs/qa/evidence/2026-09-04-release-0-9-2/`. If a public observable contradicts this charter,
create or update its deduplicated bug, hand the defect to an Implementer, stop execution, and
require a fresh Verifier after the fix. This charter authorizes no product change, real consumer
write, network access, or remote/release action.
