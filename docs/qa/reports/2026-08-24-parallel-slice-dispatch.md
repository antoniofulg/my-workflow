# QA report — parallel slice dispatch

- **Date:** 2026-08-24
- **Scope:** frozen parallelization modes and deterministic slice planning
- **Adapter:** CLI/manual
- **Environment:** checkout-local disposable Git repositories; no worker runtime
- **Preflight gate:** `npm_config_offline=true npm test` — PASS, 9 files and 109 tests
- **Raw evidence:** `docs/qa/evidence/2026-08-24-parallel-slice-dispatch/session.md`

## Matrix

| Charter | Scenario | Verdict | Observable |
| --- | --- | --- | --- |
| `CH-configure-parallel-slice-dispatch-2026-08-24` | `CFG-freeze-feature-workflow` | pass | Default and exact modes persisted; invalid refresh preserved snapshot; resume used frozen route |
| `CH-configure-parallel-slice-dispatch-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | pass | Mode-specific ready/blocked/follow-up/checkpoint output and decisive fallback matched the charter |
| Adjacent canary | `ADP-adopt-workflow-safely` | pass | Separate adoption installed matching planner/policy bytes and preserved consumer configuration |

## Session

The Workflow adopter entered through the documented resolver and planner CLIs in a disposable Git
repository. Fresh processes independently reloaded persisted snapshots and point-in-time task
state. Both scenarios passed without retry or divergence.

The agent-facing policy inspection confirmed:

- tasks stay sequential inside each slice;
- a waiting worker leaves a clean committed checkpoint, ends its turn, and receives event-driven
  follow-up without polling;
- synchronization occurs at consumed dependency checkpoints, reruns affected gates, and does not
  rebase after every task;
- a final reconciliation is conditional and becomes a no-op when the consumed checkpoint is already
  the final base;
- changed-tree evidence is invalidated while per-task gates and commits, per-slice Verifier,
  grouped deep-review, final QA, and the final-tree full gate remain mandatory.

Independent confirmation used persisted snapshot reads, repeat CLI processes, byte comparisons,
Git HEAD readback, and installed-source SHA comparisons. Raw values and command shapes are in the
linked evidence file.

## Edge probes

Ten relevant probes passed:

1. absent configuration default;
2. exact supported-mode persistence plus invalid-mode snapshot preservation;
3. frozen resume after configuration and Git HEAD changes;
4. disabled serial lane;
5. safe mode before and after verified producer evidence;
6. full-mode checkpoint metadata;
7. waiting-to-`follow_up` dependency event;
8. incomplete dependency with same-slice no-leapfrog ordering and deterministic byte output;
9. combined missing metadata, ambiguous write, unknown dependency, and cycle fallback;
10. ready-candidate write collision fallback.

The adjacent adoption canary also passed. No new or regressed product symptom was found; no bug
record was created.

## Limitations

The repository exposes no portable worker-execution harness. QA can validate public planner output
and installed orchestration policy, but cannot claim real agent, worktree, rebase, runtime, port, or
database execution.

## Final gate

`npm_config_offline=true npm test` exited `0` after cleanup: 9 test files and 109 tests passed.
Both disposable targets were moved to Trash, so cleanup is recoverable; the residue check found no
target repository or adopted tree in the checkout.
