# QA report — version feature specs for Git handoff

- **Date:** 2026-08-22
- **Scope:** issue #38 documentation fix
- **Adapter:** CLI/manual (`scripts/adopt.py`, Git filesystem inspection)
- **Environment:** active checkout plus disposable Git target and sibling worktree
- **Gate before walk:** PASS — `npm test` (10 files, 139 tests, 0 failed)
- **Evidence:** `docs/qa/evidence/2026-08-22-version-feature-specs-handoff/session.md`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation |
| --- | --- | --- | --- |
| `CH-version-feature-specs-for-handoff-2026-08-22` | `ADP-adopt-workflow-safely` | pass | Versioned marker present in sibling worktree and clean clone |
| Adjacent provenance canary | `DOC-read-explicit-workflow-provenance` | pass | Source contracts, 2/2 QA skill credits, and 3/3 external pins reloaded |

## Result

PASS. Fresh adoption ignored `.specs/features/` by default. Following the documented manual action
made the spec trackable; commit `241bb83` then exposed the same marker in both a sibling worktree and
a `--no-local` clean clone. README and artifact-lifecycle guidance name both qualifying conditions,
the same remove-and-commit action, and explicitly deny automatic detection or migration.

Unchanged adoption legs retain their passing evidence from
`2026-08-22-preserve-consumer-ad-index` and `2026-08-22-source-only-pack-guide`; this cycle re-walked
the changed issue #38 promise and its provenance canary.

Eight probes passed: default ignore, manual recovery, staging visibility, sibling handoff, clean
clone read, documentation agreement, no automation claim, and comprehension/language. No product
defect found.

## Final gate and residue

- `npm test`: PASS — 10 files, 139 tests, 0 failed.
- `git diff --check`: PASS.
- Disposable target, sibling worktree, and clean clone removed after evidence capture.
- Source checkout changes are limited to the planned durable QA artifacts.

## Limitation

No browser, API, mobile, or server exists. The repository-declared CLI/manual adapter covered the
public adoption and documentation surface; no framework was installed and no command was invented.
