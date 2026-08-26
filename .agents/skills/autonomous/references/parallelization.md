# Parallel Slice Dispatch

This contract adds optional concurrency between slices. It does not change TLC task execution:
TLC remains unchanged, and tasks inside a slice remain sequential.

## Entry gate

1. Resolve the feature workflow with `.agents/skills/workflow-config/SKILL.md`.
2. Read the frozen `workflow.json` before planning. It must use schema version `2`. Never plan from
   current configuration while resuming a feature.
3. Run the read-only planner from the repository root:

   ```bash
   python3 .agents/skills/workflow-config/scripts/parallel_plan.py \
     --root . --feature <feature-slug> [--verified-slice <slice>]
   ```

4. Dispatch parallel lanes only when the frozen mode, plan, and executor capability all allow it.

5. The `auto`/`orca` executor capability gate is proven only when the Orca status is ready,
   `orchestration.contract.v1` is present, the installed version is not known-bad, and an explicit
   lifecycle canary has reached `worker_done`, read, ack, release, checkout removal, and zero
   residue. A matching repository/runtime/executable PASS receipt may be reused; any identity change
   invalidates it. Orca `1.4.188` is a known-bad read-only result. Without a clean PASS, return
   serial recovery with zero worktree, worker, Git, or provider effects.
6. The `auto` selector evaluates the current host only. A Maestri terminal evaluates Maestri and
   never falls through to Orca. The Maestri adapter requires structured terminal, floor, agent,
   completion, dismissal, and floor-deletion capabilities. The current CLI is unsupported and
   remains serial; it never parses human output or creates a floor, agent, or Git worktree during
   preflight.

6. A lane with `Resources: none` bypasses the consumer provider; any declared resource names
   require the frozen executable and a prepared correlated lease before worker start.

`disabled`, an invalid or fallback plan, a missing frozen snapshot, or no capable isolated executor
uses the existing serial path without creating a worker or worktree. Any uncertainty or failure
serializes safely; a capability that cannot prove worktree, runtime, port, and persistence isolation
is not capable for this contract.

## Host compatibility and update verification

Run the read-only gate before starting a feature:

```bash
python3 .agents/skills/autonomous/scripts/parallel_execute.py preflight \
  --root . --feature <feature-slug> --adapter auto
```

To qualify an Orca update, run the explicit disposable canary only after the version is a candidate:

```bash
python3 .agents/skills/autonomous/scripts/parallel_execute.py preflight \
  --root . --feature <feature-slug> --adapter orca --canary
```

The output is one JSON object. Orca is updated for this workflow only when the PR is merged, the
installed executable reports the released version, and the canary returns `status=compatible` with
`proof.cleanup=clean`. A version number or capability flag alone never enables parallel execution.
The result is cached outside `.specs/`, scoped to this repository and executable identity, and is
invalidated when any identity field changes. If the proof is absent or fails, use serial mode.

Maestri can be selected explicitly for diagnostics:

```bash
python3 .agents/skills/autonomous/scripts/parallel_execute.py preflight \
  --root . --feature <feature-slug> --adapter maestri
```

Adoption installs the tracked `.agents/skills/autonomous/scripts/maestri_adapter.py` alongside the
executor and verifies its presence in the adoption contract test. This is a local adapter boundary,
not permission to mutate a Maestri workspace.

The current Maestri CLI is expected to report `unsupported` with missing machine capabilities. A
future complete structured manifest may become compatible; until then, floor creation and deletion
remain the host UI's responsibility and are not silently automated.

## Coordinator-assisted Orca fallback

This is an explicitly authorized operator path for useful overlap while the automatic Orca adapter
is unsupported. It is not an adapter result, does not write a compatibility PASS, and does not
change `start` or `resume` semantics. The main agent is the coordinator and owns the slice
worktree, worker terminal, checkpoint, dependency notification, integration, and cleanup.

Before launch, read `roles.implementer.provider`, `roles.implementer.model`, and
`roles.implementer.effort` from the frozen `workflow.json`. Never trust an unobservable Orca
default to select the worker route. Build and verify an explicit command for the frozen route:

```bash
codex --model <model> -c 'model_reasoning_effort="<effort>"'
claude --model <model> --effort <effort>
cursor agent --model '<model>[effort=<effort>]'
```

Merge the Cursor effort into an existing parameter block instead of adding a duplicate block. Use
the selected executable's `--help` and availability check to confirm the command is expressible.
After `terminal wait --for tui-idle`, use `orca terminal read` to confirm the effective model and
effort before sending the task packet. If the exact frozen route cannot be expressed, is unavailable,
or its effective model/effort cannot be observed, stop and clean only verified owned setup resources;
do not edit `tasks.md`, start a task, or continue in parallel.

Always create the worktree first, then launch the verified explicit command in its sole worker
terminal. This two-step form preserves Orca startup policy and avoids trusting a default terminal:

```bash
orca worktree create --name <slice> --no-parent --json
orca terminal create --worktree id:<repo-id>::<worktree-path> \
  --title <slice> \
  --command '<verified-frozen-agent-command>' --json
orca terminal wait --terminal <worker-handle> --for tui-idle --timeout-ms 60000 --json
orca terminal read --terminal <worker-handle> --json
orca terminal send --terminal <worker-handle> --text "<slice task packet>" --enter --json
```

Record the exact create receipt before sending the packet: the complete worktree id, instance,
absolute path, branch, worker handle, and current HEAD. Use the complete worktree id from that
receipt and one worker handle from that worktree. If a bare worktree create opened a fallback shell,
verify it is unused with `terminal list` or `terminal show` before closing it. Never create a second
worker for the same slice.

The coordinator follows this lifecycle:

1. Start at most one worker for each planner-ready slice whose declared start dependency is
   complete and verified. A worker executes only its slice's sequential TLC tasks and stops at the
   first unmet task dependency.
2. At that dependency, require a clean committed checkpoint and update the Orca worktree comment
   with this exact handoff shape:

   ```text
   slice=<id>; state=parked; completed_through=<task>; next=<task>;
   blocked_on=<slice:task>; head=<sha>
   ```

   The worker ends its turn at the parked checkpoint. The coordinator records the waiter and waits
   for the normal upstream completion/verification event; it does not poll, spin, or spend model
   turns checking unchanged state.
3. When the declared producer completes and is verified, reconcile the comment, `tasks.md`, and
   Git state. Synchronize the exact producer commit into the private dependent worktree, rerun the
   affected gate, then follow up the same worker terminal. If its handle is stale, re-list that
   worktree and reacquire its sole worker handle; never dual-send or launch a replacement.
4. A dirty or missing checkpoint, ambiguous ownership/dependency, sync conflict, or affected-gate
   failure stops that lane and enters the existing serial recovery path. The coordinator does not
   resolve conflicts automatically. A changed checkpoint invalidates affected gate, Verifier, and
   deep-review evidence until the gate is rerun on the new head.
5. After verified slice commits are integrated in deterministic slice order, immediately revalidate the exact
   create receipt before cleanup. `orca worktree show`/`list` must still match the full worktree id,
   instance, absolute path, branch, and worker handle; Git must show the exact worktree/gitdir/path,
   no symlink, the recorded HEAD, a clean state, and no merge/rebase/cherry-pick/revert in progress;
   `git merge-base --is-ancestor <slice-head> <integration-head>` must pass. Stop the exact worker,
   recheck those identities and the clean state, then remove only by the full worktree id. Prove
   Orca, Git, path, and terminal absence and zero owned residue. Any mismatch, missing ownership,
   dirty state, non-ancestor slice head, or unproven absence stops deletion and retains the exact
   path for serial recovery; never select cleanup by name or branch.

Assisted overlap preserves one atomic commit and scoped gate per task, one Technical Verifier per
code-changing slice, the frozen grouped deep-review cadence, final QA, and one full gate on the
final tree. It introduces no parallelism inside a slice and no change to TLC task order. Until the
automatic Orca lifecycle canary passes on the installed runtime, automatic execution remains
unsupported and serial.

## Executor commands

From the repository root, the public verbs are:

```bash
python3 .agents/skills/autonomous/scripts/parallel_execute.py start \
  --root . --feature <feature-slug> --adapter auto
python3 .agents/skills/autonomous/scripts/parallel_execute.py resume \
  --root . --feature <feature-slug> --adapter auto --wait-seconds <1..3600>
python3 .agents/skills/autonomous/scripts/parallel_execute.py status \
  --root . --feature <feature-slug>
```

Each verb emits one JSON object naming `command`; `status` is read-only. `resume` consumes persisted
receipts and at most one correlated delivery, while `start` runs the point-in-time plan. A rejected
capability, invalid plan, missing snapshot, unsupported provider, dirty checkpoint, failed gate,
or cleanup failure returns serial recovery without creating a replacement effect.

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

The event lifecycle is run-scoped and receipt-scoped:

```text
check --run <run> --wait --types worker_done,question,escalation
check --run <run> --ack <delivery-id>
worker-read --dispatch <dispatch-id>
worker-release --dispatch <dispatch-id>
```

The coordinator reads and accepts the correlated worker result before release. A clean waiter is
ended before the dependency event can follow up on the same terminal; a timeout leaves state
unchanged. Missing, duplicate, foreign, escalated, dirty, or failed receipts serialize without a
replacement worker.

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
- A changed checkpoint persists `current_head` and invalidates `gate`, Technical Verifier, and
  deep-review evidence. The lane remains `gate_required` until the affected gate receipt matches
  the lane and current head; only then may waiting follow-up continue.

Verified slices are merged into the feature integration branch in deterministic slice order with
preserved commits. Merge conflicts abort and return serial recovery; no automatic resolution is
attempted.

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

## QA handoff

E2E-001 is an explicit fresh-QA handoff, not an author-run pilot. Its interface, expected receipts,
and cleanup assertions are recorded in `.specs/features/parallel-slice-executor/qa-pilot.md`.
Canonical final QA records E2E-001 as terminal `BLOCKED-VERIFY` at the external Orca/Codex
lifecycle boundary; no completed pilot is claimed.

## Serial fallback

Serial fallback is the default recovery for disabled mode, missing or invalid metadata, conflicting
ready lanes, unavailable isolation, dirty waiting state, checkpoint failure, integration conflict,
or any uncertainty. The fallback follows the existing autonomous serial path and creates no parallel
worker or worktree for the rejected plan.
