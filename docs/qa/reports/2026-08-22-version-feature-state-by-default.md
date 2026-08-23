# QA report — version feature state by default

- **Date:** 2026-08-22
- **Scope:** issue #31 fresh adoption, legacy migration, and Git handoff
- **Adapter:** CLI/manual (`scripts/adopt.py`, Git filesystem inspection)
- **Environment:** active checkout; isolated targets under `/tmp/my-workflow-qa31.sAf8yj`
- **Gate before walk:** PASS — `npm test` (11 files passed; 144 tests passed)
- **Evidence:** `docs/qa/evidence/2026-08-22-version-feature-state-by-default/session.md`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation |
| --- | --- | --- | --- |
| `CH-version-feature-state-by-default-2026-08-22` | `ADP-adopt-workflow-safely` | pass | Fresh and legacy adoption preserved `HEAD` and an empty index; second legacy adoption reproduced the same `.gitignore` hash |
| `CH-version-feature-state-by-default-2026-08-22` | `CFG-keep-local-artifacts-out-of-git` | pass | Sibling worktree and clean clone independently exposed versioned `spec.md`, completed `tasks.md`, and the atomic task output |
| Adjacent provenance canary | `DOC-read-explicit-workflow-provenance` | pass | README/skill credits and all three immutable external skill pins were re-read; fresh adoption kept them external |

## Result

PASS. Fresh adoption left feature `spec.md` and `tasks.md` visible to Git without changing `HEAD` or
the index. Legacy adoption removed both exact `.specs/features/` entries, preserved comments,
unrelated lines, and near-match consumer rules, and produced the same `.gitignore` SHA-256 on the
second run.

An explicit feature-state commit traveled to a sibling worktree and clean clone. The following
task commit contained both the completed `tasks.md` status and its observable marker, and both read
paths saw the completed state after checkout. Bugs `BUG-20260822-feature-specs-ignored` and
`BUG-20260822-feature-state-gate-conflicts` passed retest.

## Probes

- Fresh `spec.md` and `tasks.md`: Git-visible.
- Duplicate exact legacy lines: removed.
- Consumer comment, unrelated rules, and near matches: preserved.
- Second adoption: byte-idempotent for the migrated ignore contract.
- Fresh and legacy adoption: no stage or commit.
- Sibling worktree and clean clone: feature state present.
- Atomic task-status commit: `tasks.md` and task output share one commit.
- Provenance canary: credits, immutable pins, and external installation boundary preserved.

**Final gate:** PASS — `npm test` (11 files passed; 144 tests passed).

## Limitation and residue

No browser, API, mobile, or server exists; the declared CLI/manual adapter remains appropriate.
Disposable targets were checkout-isolated and removed after capture. Source checkout changes are
limited to planned durable QA documents.
