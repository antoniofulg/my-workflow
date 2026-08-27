---
id: ADP-validate-generated-feature-contracts
area: ADP
title: Validate TLC-generated feature contracts
persona: Workflow adopter
journey: J-adopt-workflow
expected: The vendored validators accept TLC-generated task layouts with a merge-alone closure table and still reject incomplete closure contracts, future-phase dependencies, and criteria without SHALL.
entry_points: .agents/skills/tlc-spec-driven/scripts/validate_tasks.py; .agents/skills/tlc-spec-driven/scripts/validate_spec.py
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
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
