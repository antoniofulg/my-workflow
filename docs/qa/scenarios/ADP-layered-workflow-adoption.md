---
id: ADP-layered-workflow-adoption
area: ADP
title: Adopt workflow capabilities incrementally
persona: Workflow adopter
journey: J-adopt-workflow
expected: A project can plan and apply fixed core, parallel, quality, and extras layers incrementally; conflicts fail before writes, consumer prose and Bun package metadata survive, and status reports clean state.
entry_points: README.md#adopt-the-workflow; docs/adoption-prompt.md; scripts/adopt.py
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-30-layered-workflow-adoption/summary.json; docs/qa/evidence/2026-08-30-layered-workflow-adoption/opening-gate.txt; docs/qa/evidence/2026-08-30-layered-workflow-adoption/package-dry-run.txt
last_report: docs/qa/reports/2026-08-30-layered-workflow-adoption.md
overlaps: ADP-adopt-workflow-safely
---

This feature-specific handoff supersedes no historical result. Fresh QA must start with a read-only
`plan`, apply `core`, then add dependent layers. Verify manifest ownership, managed instruction
blocks, all-preflight conflict refusal, no-removal semantics, preserved `package.json` and
`bun.lock`, Bun knowledge execution, and `status` exit codes. Record new evidence after the public
journey is executed.

The current cycle also covers `full`, legacy-command refusal, JSON stdout isolation, staged provider
packet synchronization, and importing the installed assisted probe through a call-counting fake
`orca`. Exact hash, path-containment, manifest-schema, and publication-order mechanics remain
technical-verification evidence; QA observes their public no-write and atomic-publication outcomes.

QA Execute on 2026-08-30 passed all three layered-adoption charters at `714716c`. Read-only plans
kept the target byte-identical; incremental and full applies produced a clean four-layer manifest,
preserved consumer instructions, package metadata, local config, QA profile, custom skill pointer,
and missing-only files, and refused drift, collisions, unsafe symlinks, invalid blocks, and invalid
manifests without writes. Bun knowledge exited 0, probe import made zero Orca calls, reapply was
byte-stable, and the adopted target contained no repository test files or transaction residue. Live
Orca scenarios remain unchanged and outside this offline adoption verdict.

The legacy-adoption-resolution cycle changes the shared planning and publication path while
promising unchanged normal `plan`, `apply`, and `status` behaviour. The previous report remains as
history, but this promise is reset to `untested` for an adjacent disposable-target canary.
