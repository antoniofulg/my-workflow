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
evidence:
last_report:
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
