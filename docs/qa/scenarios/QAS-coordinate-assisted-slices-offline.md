---
id: QAS-coordinate-assisted-slices-offline
area: QAS
title: Coordinate assisted slices with offline providers
persona: Workflow operator
journey: J-execute-parallel-slices
expected: Default assisted execution uses only ready compatible writer lanes, sends packet pointers without packet bodies, issues each fake-provider mutation once, falls back serially when proof is missing, and cleans owned state to zero residue.
entry_points: .agents/skills/workflow-config/scripts/workflow_config.py; .agents/skills/workflow-config/scripts/parallel_plan.py; .agents/skills/autonomous/scripts/parallel_execute.py start; tools/orca_assisted_probe.py dispatch; tools/orca_assisted_probe.py inspect; tools/orca_assisted_probe.py cleanup
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-29-hybrid-slice-execution/summary.json; docs/qa/evidence/2026-08-29-hybrid-slice-execution/commands.json
last_report: docs/qa/reports/2026-08-29-hybrid-slice-execution.md
overlaps: CFG-plan-parallel-slice-dispatch; CFG-fallback-unproven-parallel-execution; QAS-run-resource-free-parallel-orca-slices; QAS-clean-owned-parallel-slice-pilot
---

This is the canonical offline assisted-execution promise. It uses only the public CLI/manual adapter
and checkout-local fake Orca, Git, and resource providers. It does not claim that the live Orca host
can complete a worker lifecycle.

The cycle must independently reload persisted packet, ledger, receipt, and residue evidence. Pointer
transport may contain the repository-relative packet pointer but never packet content. Every logical
mutation must have exactly one physical fake-provider call, including transient-response paths.
