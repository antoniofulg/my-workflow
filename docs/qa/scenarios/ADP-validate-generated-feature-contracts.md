---
id: ADP-validate-generated-feature-contracts
area: ADP
title: Validate TLC-generated feature contracts
persona: Workflow adopter
journey: J-adopt-workflow
expected: The vendored validators accept TLC-generated task layouts with a merge-alone closure table and still reject incomplete closure contracts, future-phase dependencies, and criteria without SHALL.
entry_points: .agents/skills/tlc-spec-driven/scripts/validate_tasks.py; .agents/skills/tlc-spec-driven/scripts/validate_spec.py
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/adopt-merge-one.json; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/adopt-merge-two.json; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/adoption-independent-read.log; docs/qa/evidence/2026-08-27-merge-alone-slices/retest-933b5ed/cleanup.log
last_report: docs/qa/reports/2026-08-27-merge-alone-slices.md
overlaps:
---

Covers the public developer CLI behaviour reported in issue #39. Valid feature files produced from
the TLC templates must pass without hand edits; the same validators must retain their discriminating
failures for a dependency on a future phase and an acceptance criterion without `SHALL`.

QA on 2026-08-22 ran both adopted validator CLIs from a disposable target. Both generated task
layouts and the annotated acceptance-criteria template passed; future-phase dependency and missing
`SHALL` probes failed with precise diagnostics before and after re-adoption.

The merge-alone closure contract changes this current promise. A fresh QA walk must exercise valid
one- and two-slice task documents plus named failures for closure and membership defects.

The 2026-08-27 execution stopped before this separate adoption charter when the preceding public
resolver-to-planner journey found `BUG-20260827-parallel-plan-rejects-workflow-v2`. The disposable
targets were removed and this scenario remains `untested` for the required fresh post-fix Verifier.

Fresh QA retest at `933b5ed` completed both pending charters. Adopted validators accepted generated
one- and two-slice contracts, both historical task layouts, and the annotated criteria heading;
they rejected all nine closure/membership defects, the future-phase dependency, and missing `SHALL`
with the expected task, slice, field, phase, or criterion identity. Re-adoption preserved these
results and installed source-identical validators and task guidance.
