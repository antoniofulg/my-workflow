---
id: QAS-reject-unverifiable-maestri-host
area: QAS
title: Reject unverifiable Maestri execution
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Maestri preflight reports unsupported with the decisive missing or unimplemented machine contract and creates no floor, agent, worker, or Git worktree effect.
entry_points: .agents/skills/autonomous/scripts/parallel_execute.py preflight --adapter maestri; .agents/skills/autonomous/scripts/parallel_execute.py preflight --adapter auto
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-26-host-adapter-compatibility/cli-results.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/residue-after-charter.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/session.md; docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/results.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/session.md
last_report: docs/qa/reports/2026-08-26-host-adapter-compatibility.md
overlaps: CFG-fallback-unproven-parallel-execution
---

Covers MAE-01 through MAE-04 and the observable structured-receipt boundary of SEC-004 and SEC-007.
Current Maestri remains unsupported even when a capability manifest looks complete: host-owned
execution and machine floor cleanup are not implemented, human-readable output is not an ownership
receipt, and `auto` in a Maestri terminal never crosses to Orca.

QA on 2026-08-26 found no installed Maestri executable. Explicit preflight and `auto` with Maestri
terminal identity/socket context both returned `unsupported: adapter-unavailable`; `auto` did not
cross to installed Orca. No floor/agent inventory was reachable, while Git and Orca inventories
independently retained zero delta.

Fresh fix-loop QA at `cd1886f` re-passed explicit and Maestri-context rejection with no cross-fallback
and zero measured external delta.
