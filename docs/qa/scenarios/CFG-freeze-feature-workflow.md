---
id: CFG-freeze-feature-workflow
area: CFG
title: Freeze and safely resume a feature workflow
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: Resolution atomically produces feature state that remains stable on resume until an explicit refresh, and JSON output that is that state plus the resolved-now remediation.
entry_points: .agents/skills/workflow-config/scripts/workflow_config.py; .specs/features/<slug>/workflow.json; .agents/skills/workflow-config/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-23-stall-based-halt/resolver-session.md
last_report: docs/qa/reports/2026-08-23-stall-based-halt.md
overlaps:
---

Covers `CWF-STATE-1` through `CWF-STATE-4`: complete snapshot fields, repeat stability, preservation
of a prior valid snapshot on atomic-write failure, and frozen resume until a human requests refresh.

Reset to `untested` for the `stall-based-halt` cycle. The promise changed: the JSON output is no
longer identical to the snapshot — it is the snapshot plus a resolved-now `remediation` — and resume
behaviour changed with it. A resume must stay inert to an unrelated schema edit in
`.my-workflow.toml`, still fail closed on an invalid `[remediation]` value, and still fail on a TOML
that cannot be parsed at all. Overlaps `CFG-bound-remediation-stall-attempts` only on the value's
validity; this scenario owns the snapshot-versus-output boundary and resume.
