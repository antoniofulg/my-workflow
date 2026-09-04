---
id: ADP-validate-generated-feature-contracts
area: ADP
title: Validate TLC-generated feature contracts
persona: Workflow adopter
journey: J-adopt-workflow
expected: The vendored validators accept both TLC-generated task layouts and its annotated acceptance-criteria heading while still rejecting future-phase dependencies and criteria without SHALL.
entry_points: .agents/skills/workflow-spec-driven/scripts/validate_tasks.py; .agents/skills/workflow-spec-driven/scripts/validate_spec.py
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-validate-generated-feature-contracts/session.md
last_report: docs/qa/reports/2026-08-22-validate-generated-feature-contracts.md
overlaps: ADP-require-impact-on-large-specs
---

Covers the public developer CLI behaviour reported in issue #39. Valid feature files produced from
the TLC templates must pass without hand edits; the same validators must retain their discriminating
failures for a dependency on a future phase and an acceptance criterion without `SHALL`.

QA on 2026-08-22 ran both adopted validator CLIs from a disposable target. Both generated task
layouts and the annotated acceptance-criteria template passed; future-phase dependency and missing
`SHALL` probes failed with precise diagnostics before and after re-adoption.
