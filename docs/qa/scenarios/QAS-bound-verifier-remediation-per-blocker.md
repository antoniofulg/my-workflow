---
id: QAS-bound-verifier-remediation-per-blocker
area: QAS
title: Continue verification for distinct blockers
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Distinct verifier blockers receive independent remediation counts while the same requirement, root cause, and failure path halts only after its third failed remediation.
entry_points: .agents/skills/workflow-spec-driven/scripts/review_convergence.py; .agents/skills/autonomous/SKILL.md; .agents/skills/autonomous/references/parallelization.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/convergence-replays.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/convergence-threshold.json; docs/qa/evidence/2026-08-25-parallel-slice-executor-r19/ledger-bounds.json
last_report: docs/qa/reports/2026-08-25-parallel-slice-executor-final.md
overlaps:
---

Covers the operator-facing unattended-delivery promise in EXE-23–EXE-25. The walk uses the public
ledger CLI and installed workflow contracts; it does not manufacture model turns or alter a real
feature's verification history.

R19's public `review_convergence.py` walk used a disposable ledger copy for mutation. Two existing
closed fingerprints replayed with no count increment, while a distinct fingerprint halted exactly
on its third failed remediation; the checkout ledger read stayed at 21 total/21 closed/0 open with
maximum count 2 before and after. The same command log records the later failure and replay staying
at halted count 3.
