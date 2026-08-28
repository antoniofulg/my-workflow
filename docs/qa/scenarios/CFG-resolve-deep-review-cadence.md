---
id: CFG-resolve-deep-review-cadence
area: CFG
title: Resolve review cadence and remediation controls before QA
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver derives balanced review groups from validated merge-alone task outcomes, defaults missing Tasks to one slice, reports the effective nonnegative remediation stall bound, and rejects invalid inputs before writing state.
entry_points: .my-workflow.toml.example; .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .agents/skills/workflow-config/SKILL.md; docs/guidelines/REVIEW-ROUNDS.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-27-merge-alone-slices/derive-validator-one.json; docs/qa/evidence/2026-08-27-merge-alone-slices/derive-validator-two.json; docs/qa/evidence/2026-08-27-merge-alone-slices/independent-initial-read.log; docs/qa/evidence/2026-08-27-merge-alone-slices/edge-count-mismatch.stderr.log; docs/qa/evidence/2026-08-27-merge-alone-slices/edge-count-zero.stderr.log; docs/qa/evidence/2026-08-27-merge-alone-slices/edge-count-negative.stderr.log
last_report: docs/qa/reports/2026-08-27-merge-alone-slices.md
overlaps:
---

Covers `CWF-CAD-1` through `CWF-CAD-7`: the v2 config's default `grouped.3`, `slice`, `feature`, balanced
`grouped.N`, validation failures, final implementation review before QA, and delta-only review after
QA remediation. `SRH-01` adds the public `[remediation].stall_attempts` contract: default `3`, exact
nonnegative integers, `0` as unbounded, and rejection before snapshot creation for invalid values or
unknown remediation keys.

The 2026-08-24 evidence remains historical. The stall-bound change at `cada159` resets the current
verdict until the CLI/manual path is walked again. QA on 2026-08-25 confirmed default `3`, positive
`5`, zero `0`, a large nonnegative integer, balanced `grouped.3` output, and five invalid input
families rejected before snapshot creation.

The merge-alone slice contract changes this current promise. A fresh QA walk must cover derived
counts, closure validation, optional count assertions, and the no-Tasks default.

QA on 2026-08-27 passed this promise through the public validator/resolver path. Independent reloads
confirmed one outcome as `[[1]]`, two outcomes as `[[1, 2]]`, and missing Tasks as `[[1]]`; mismatch,
zero, negative, and malformed closure/membership probes failed with named identities before writes.
