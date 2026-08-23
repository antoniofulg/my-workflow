---
id: DOC-halt-remediation-only-on-a-stall
area: DOC
title: Halt an unattended run only when remediation stops making progress
persona: Workflow operator
journey: J-run-deep-review
expected: Every surface an operator reads states one halt rule — remediation continues while an attempt reaches a new minimum failing-test set and halts only after stall_attempts consecutive stalls or an unrunnable gate — and none still halts on an open blocker alone.
entry_points: docs/guidelines/REVIEW-ROUNDS.md; .agents/skills/autonomous/SKILL.md; .agents/skills/workflow-config/SKILL.md; README.md; .my-workflow.toml.example
qa_status: pass
bug_ids: BUG-20260823-workflow-tour-states-retired-halt-rule
fix_status: fixed
retest_status: pass
fix_commits: 3dee592
evidence: docs/qa/evidence/2026-08-23-stall-based-halt/halt-rule-session.md; docs/qa/evidence/2026-08-23-stall-based-halt/retest-session.md
last_report: docs/qa/reports/2026-08-23-stall-based-halt.md
overlaps:
---

New promise from `AD-007`. This pack ships instruction text, so the halt rule an operator relies on
to know when an unattended run stops *is* the public interface. Covers `HALT-01` … `HALT-04`.

The risk this scenario exists to catch is drift, not wording: the rule changed three times during the
feature and three consumer surfaces were caught restating a retired version. The walk therefore reads
every surface that states or cites the rule and checks they agree on one rule, that the retired
"blocker remains reproducible" formulation survives nowhere, and that `autonomous/SKILL.md` cites the
guideline rather than restating the threshold.

Live agent-loop behaviour is not walkable here — `docs/qa/README.md` declares that no
agent-execution harness exists and that live model behaviour is a manual observation. The observable
above is deliberately the documented contract, which is what this repository actually publishes.
