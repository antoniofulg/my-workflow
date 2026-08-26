---
id: CFG-fallback-unproven-parallel-execution
area: CFG
title: Fall back when parallel execution is unproven
persona: Workflow adopter
journey: J-execute-parallel-slices
expected: Disabled mode, an unavailable or incompatible selected host, missing resource metadata, or a resource-bearing lane without a provider reports its decisive serial reason and creates no host, worktree, worker, event, Git, or resource effect.
entry_points: .my-workflow.toml; .agents/skills/workflow-config/scripts/workflow_config.py; .agents/skills/autonomous/scripts/parallel_execute.py preflight; .agents/skills/autonomous/scripts/parallel_execute.py start; .agents/skills/autonomous/scripts/parallel_execute.py resume; .agents/skills/autonomous/scripts/parallel_execute.py status
qa_status: pass
bug_ids: BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree
fix_status: fixed
retest_status: pass
fix_commits: 0ed8b55
evidence: docs/qa/evidence/2026-08-26-host-adapter-compatibility/cli-results.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/residue-after-charter.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/session.md; docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/results.json; docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/session.md
last_report: docs/qa/reports/2026-08-26-host-adapter-compatibility.md
overlaps: CFG-plan-parallel-slice-dispatch; CFG-freeze-feature-workflow; QAS-qualify-orca-host-before-parallel-use; QAS-reject-unverifiable-maestri-host
---

Covers the public fallback portions of EXE-01, EXE-05, EXE-11, EXE-19, EXE-21, HST-01 through
HST-03, SEC-001, and SEC-007.
The canary deliberately proves zero effects; it never supplies a fake product runtime or database
provider to turn this repository's adoption limitation into an apparent pass.

Terminal status is `pass` for all three fallback legs. R18 proved disabled mode and unsupported Orca
capability return their decisive serial reasons with empty actions, fresh-process `state: null`, and
zero new worktree/runtime/Orca effects. R19 retested two ready `Resources: runtime` lanes with
frozen provider `null`: two starts returned `missing-resource-provider` with `actions: []`, two
fresh-process statuses returned `state: null`, Run inventory stayed `12 -> 12`, worker inventory
stayed `151 -> 151`, and no lane worktree, runtime receipt, Task, Dispatch, terminal, or lease was
created. Diagnostic abort and its idempotent repeat left `residual_paths: []`.

The linked worker-start bug remains open for the separate real resource-free lifecycle; its product
root causes do not invalidate this zero-effect fallback result. Evidence: R18 and R19 reports plus
the paths listed in frontmatter.

Reset to `untested` on 2026-08-26 because host selection now requires structured compatibility,
forbids Maestri-to-Orca cross-fallback, and treats Orca `1.4.188` and current Maestri as explicit
zero-effect unsupported results. Historical evidence remains attached but does not cover the new
selection contract.

QA on 2026-08-26 passed the changed fallback surface. Disabled `start` and `resume` returned
`actions: []` before adapter or state construction; Orca `1.4.188` and unavailable Maestri returned
decisive unsupported results; all measured external and checkout-local deltas were zero.

Fresh fix-loop QA at `cd1886f` re-passed each affected fallback leg with every measured delta zero.
