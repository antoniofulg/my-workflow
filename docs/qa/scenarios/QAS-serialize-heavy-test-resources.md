---
id: QAS-serialize-heavy-test-resources
area: QAS
title: Serialize only the contested heavy test resource
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Same-resource heavy commands queue at the selected scope while unrelated resources remain concurrent
entry_points: python3 tools/resource_lock.py run
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps:
---

Use disposable Git repositories and commands that write timestamped sentinels. Walk both `project`
and `machine` scope, then prove a different resource can overlap without running a live Orca pilot.
