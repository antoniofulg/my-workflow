---
id: DOC-require-explicit-remote-action-approval
area: DOC
title: Require explicit approval for each remote delivery action
persona: Repository reader
journey: J-review-workflow-release
expected: The workflow stops at readiness unless the current session explicitly authorizes the exact next push, pull request, or merge action.
entry_points: AGENTS.md; README.md; docs/workflow/loop.md; docs/workflow/pack.md; .agents/skills/autonomous/SKILL.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-22-explicit-remote-approval/session.md
last_report: docs/qa/reports/2026-08-22-explicit-remote-approval.md
overlaps:
---

Covers the public remote-delivery boundary from issue #25. Local approval and readiness evidence do
not authorize a remote action, and authorization for one action does not authorize the next. The
current pass includes a disposable adoption and independent reload of the installed contracts.
