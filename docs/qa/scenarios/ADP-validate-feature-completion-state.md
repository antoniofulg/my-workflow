---
id: ADP-validate-feature-completion-state
area: ADP
title: Validate a feature completion report through the public CLI
persona: Workflow adopter
journey: J-adopt-workflow
expected: The public validate_state CLI honors an explicit Verdict over legacy Result text and accepts a supported legacy Result PASS report.
entry_points: .agents/skills/tlc-spec-driven/scripts/validate_state.py
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Covers the public completion-gate behavior reported in issue #27. An explicit `Verdict: FAIL`
must remain a failure even when a legacy `Result: PASS` appears later, and an explicit `Verdict:
PASS` must remain a pass even when a legacy `Result: FAIL` appears later. Reports without an explicit
verdict retain the supported legacy `Result: PASS` form.
