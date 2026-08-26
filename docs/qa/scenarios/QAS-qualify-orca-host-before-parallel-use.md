---
id: QAS-qualify-orca-host-before-parallel-use
area: QAS
title: Qualify Orca before parallel execution
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Read-only preflight rejects Orca 1.4.188 without effects, reuses only an identity-matched clean PASS, and allows a candidate runtime only after an explicit correlated canary proves worker completion and zero residue.
entry_points: .agents/skills/autonomous/scripts/parallel_execute.py preflight --adapter orca; .agents/skills/autonomous/scripts/parallel_execute.py preflight --adapter orca --canary; .agents/skills/autonomous/scripts/parallel_execute.py start --adapter orca
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-26-host-adapter-compatibility/cli-results.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/residue-after-charter.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/session.md; docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/results.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/session.md
last_report: docs/qa/reports/2026-08-26-host-adapter-compatibility.md
overlaps: CFG-fallback-unproven-parallel-execution; QAS-run-resource-free-parallel-orca-slices
---

Covers ORC-01 through ORC-07 and the user-observable diagnostics, redaction, cleanup proof, and
ownership outcomes of SEC-005 through SEC-007. Current-cycle execution is limited to read-only
preflight against installed Orca `1.4.188`, which must report `unsupported` without creating a Run,
Task, worker, or worktree. A live candidate `--canary` requires a later packet after Orca changes;
it is not authorized by the 2026-08-26 charter.

The installed-runtime leg passed on 2026-08-26: explicit and automatic preflight returned
`known-incompatible-version:1.4.188`, cleanup `not-run`, cache `false`, and zero measured residue.
The scenario remains `untested` because its candidate-runtime and cached-PASS legs require a future
authorized candidate `--canary`; no positive compatibility claim was made.

Fresh fix-loop QA at `cd1886f` re-passed the installed-runtime rejection and zero-effect checks.
Candidate qualification remains honestly `untested`; no candidate version existed and no canary ran.
