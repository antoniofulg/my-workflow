# Parallel Slice Dispatch

This contract adds optional concurrency between slices. It does not change TLC task execution:
TLC remains unchanged, and tasks inside a slice remain sequential.

## Entry gate

1. Resolve the feature workflow with `.agents/skills/workflow-config/SKILL.md`.
2. Read the frozen `workflow.json` before planning. Never plan from current configuration while
   resuming a feature.
3. Run the read-only planner from the repository root:

   ```bash
   python3 .agents/skills/workflow-config/scripts/parallel_plan.py \
     --root . --feature <feature-slug> [--verified-slice <slice>]
   ```

4. Dispatch parallel lanes only when the frozen mode, plan, and executor capability all allow it.

`disabled`, an invalid or fallback plan, a missing frozen snapshot, or no capable isolated executor
uses the existing serial path without creating a worker or worktree. Any uncertainty or failure
serializes safely; a capability that cannot prove worktree, runtime, port, and persistence isolation
is not capable for this contract.

## Dispatch boundary

- Use one worker per slice. The orchestrator owns the slice worktree, runtime, and checkpoint.
- A worker runs its slice's tasks in TLC order. Tasks inside a slice remain sequential.
- Each task still has its own implementation, scoped gate, `tasks.md` update, and atomic commit.
- The orchestrator never starts a later task in a slice before the planner marks its dependencies
  available.
- A worker does not create another worker and does not edit another slice's worktree.

The plan's `ready` lane is permission to start the named task, not permission to skip a gate. A
`waiting` or `in_progress` task is never a fresh worker; the planner's state transition is part of
the dispatch decision.

## Waiting and follow-up

When a worker reaches an unavailable dependency, it must first leave a clean committed checkpoint
and report the exact dependency and current head. It must then end the clean worker turn. The
orchestrator records the waiter and resumes the same worker with a follow-up after the dependency completion event. It does not poll, spin, or spend model turns checking unchanged state.

If the worker is dirty, cannot report its checkpoint, or the event cannot be correlated to the
declared dependency, it is not a valid waiter: pause the lane and use the existing serial recovery
path. A follow-up re-plans the point-in-time state; it does not bypass the task gate or create a
second worker for the same task.

## Synchronization

- Synchronize at declared dependency checkpoints before the dependent task consumes a newer
  upstream commit.
- Use the exact upstream commit recorded by the dependency event, then run the affected gate before
  continuing.
- Do not rebase after every task. Checkpoint sync is the normal cadence.
- Reconcile the final upstream base only when it advanced. If the consumed checkpoint already equals
  the final base, final reconciliation is a no-op.
- A conflict, ambiguous integration, failed gate, or missing checkpoint serializes safely or halts
  the lane; it never silently chooses one side.

## Evidence invalidation

If synchronization, integration, or remediation changes a reviewed tree, invalidate every affected gate, Verifier, and deep-review verdict. Repeat the affected gate on the resulting tree before the next task or review stage. Evidence from a prior commit is not evidence for a rebased tree.

The normal evidence contract remains intact:

- one atomic commit and scoped gate per task;
- one technical Verifier per code-changing slice;
- deep-review at the frozen groups;
- final QA;
- one full gate on the final tree.

Parallel dispatch may reduce wall time, but it never removes, merges, or postpones these readiness
stages past their required source freeze.

## Serial fallback

Serial fallback is the default recovery for disabled mode, missing or invalid metadata, conflicting
ready lanes, unavailable isolation, dirty waiting state, checkpoint failure, integration conflict,
or any uncertainty. The fallback follows the existing autonomous serial path and creates no parallel
worker or worktree for the rejected plan.
