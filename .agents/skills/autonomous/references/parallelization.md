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
default to select the worker route. The following are non-normative command shapes; no route command
is sent before exact startup-handle proof:

```bash
codex --model <shq(model)> -c <shq(model_reasoning_effort=<effort>)>
claude --model <shq(model)> --effort <shq(effort)>
cursor agent --model <shq(model[effort=<effort>])>
```

Here `shq(value)` means the output of an actual POSIX-shell quoting function (for example
`shlex.quote`), not literal quote characters concatenated around an identifier. The command forms
are argv shapes; use a fixed-argv/no-shell wrapper where possible, and otherwise apply `shq` to every
interpolated provider, model, effort, slice, base-branch, branch, ref, and handle value. Merge the
Cursor effort into an existing parameter block instead of adding a duplicate block. Use the selected
executable's `--help` and availability check to confirm the command is expressible.

The canonical launch sequence is the only normative order: create once; reconcile the receipt;
prove the exact startup handle; send `exec` once; run the bounded route loop; then send the task
payload. Before that sequence reaches the route commands. Do not edit `tasks.md`, start a task, or
continue in parallel.

Before every logical packet—including route promotion, the initial task packet, and each
follow-up—record the exact handle, a unique turn ID/phase, `pre_head`, the current task statuses,
worktree comment and affected-gate state, and the expected marker form
`TURN_DONE <phase> head=<40-hex-sha>` (exactly one SHA). Issue exactly one send for that packet;
never retry after a success, error, missing receipt, or `agent_prompt_stalled`, and never launch a
replacement worker.

A successful send follows the normal 300-second worker-turn barrier. An error, missing receipt, or
`agent_prompt_stalled` enters bounded machine-only effect reconciliation on the same exact
startup/current handle; a different handle is rejected:
inspect it every `interval_ms=250` for at most `timeout_ms=300000`, with no model turns. Accept an
effect only when exactly one expected turn is proven end-to-end: the same handle remains connected;
the exact unique phase marker has one 40-hex SHA; two fresh non-Working `source=screen` frames and
a `tui-idle` reading agree; Git HEAD equals that marker; required task statuses, atomic commits,
and gates match; and, for a parked B turn, the exact checkpoint comment matches. Record the
receipt/effect divergence and continue without resending.

No effect by the deadline, partial state, conflicting or multiple marker SHAs, dirty state, gate
failure, wrong handle, or ambiguity serializes the lane and retains it for exact recovery. Never
clean or adopt a foreign effect, and never report success from a commit alone. This bounded probe is
not a dependency waiter or watchdog: dependency waiting remains event-driven and spends no model
turns polling unchanged state.

Before the one mutating create, snapshot the exact repository worktree and terminal inventory into
`before_inventory` and generate a unique logical slice name. Invoke exactly one create with an explicit base and setup
policy:

```bash
orca worktree create --name <slice> --base-branch <base-branch> --setup inherit --json
```

If the create result is missing or times out, it is never retried blindly: never retry or issue a second create. Enter a machine-
only SETTLE WINDOW for at most `timeout_ms=60000`, re-listing the exact repository worktree and
terminal inventories every `interval_ms=250` and computing the cumulative `current - before_inventory`
difference, i.e. computing the cumulative observed set `current - before_inventory` (the
`after_inventory - before_inventory` difference over the window).
Filter that cumulative set by the exact repository and generated unique logical slice name; entries
that do not match both are foreign and are never adopted or cleaned. Adopt exactly one matching
candidate only after a complete immutable receipt and ownership proof
can be reconstructed from the receipt and the same inventory identities. Zero, multiple, or ambiguous
candidates serialize; exact-clean only matching candidates when provably owned, then serialize. At the deadline, perform one
final inventory/audit after the last re-list; only a proven zero-candidate result may serialize as zero
effect. Never invent a receipt or claim compatibility from an ambiguous result.

Record an immutable ownership receipt immediately from the create result or the one reconciled
candidate: repository, complete worktree id, instance, absolute path, gitdir, branch, `pre_head`, and the exact
`startupTerminal.handle`.

Before any terminal send, inspect that exact handle:

```bash
orca terminal show --terminal <startupTerminal.handle> --json
```

Prove that the exact `startupTerminal.handle` was newly created by this worktree operation, is
uniquely owned by this just-created worktree, is an unused shell, and has no agent/default-task
activity. Use `terminal show`/`list` for this conjunction. Exactly one coordinator-owned startup
handle must exist for this worktree. Ambiguity, multiple owned handles, or any existing activity
serializes and cleans only verified owned setup resources. Apply `shq` to every value that crosses a
shell boundary and build the fixed provider command only after that proof, then send `exec` to the
exact handle:

Construct `exec_payload` as the complete `exec <validated-frozen-agent-command>` string, then apply
`shq(payload)` once to that complete payload before passing it to `--text`:

```bash
orca terminal send --terminal <startupTerminal.handle> \
  --text <shq(exec_payload)> --enter --json
```

Then run the bounded machine-only TUI materialization probe loop on that same handle. Every
`interval_ms=250`, and for no more than `timeout_ms=60000`, each iteration performs the exact-handle
`orca terminal show --terminal <startupTerminal.handle> --json` plus `orca terminal read --terminal <startupTerminal.handle> --screen --json`. The handle must remain connected. Require two consecutive screen reads from that exact handle with
`source=screen` and provider, model, and effort all present and matching the frozen tuple. Count two
CONSECUTIVE matching frames; any nonmatch resets the count to zero. After the first matching frame,
`terminal wait --for tui-idle` may be checked only as a hint/check; it is never the barrier and the
next matching screen is still required. A timeout, mismatch, disconnect, `screen-unavailable`,
omitted provider, or ambiguity serializes before any task payload or task edit. one screen or one pre-send `tui-idle` result is never sufficient. This probe is not the dependency waiter. This probe
performs no model turns and does not poll or spin on task state; dependency waiting remains event-driven.

After the route loop reaches two consecutive matching frames, construct `task_payload` as the
complete slice packet, then apply `shq(payload)` once to that complete payload before passing it to
`--text`:

```bash
orca terminal send --terminal <startupTerminal.handle> --text <shq(task_payload)> --enter --json
```

Never wrap either payload in literal outer double quotes. Record mutable `current_head` and
`current_handle` separately; the same startup handle remains the worker handle and is updated only
after a commit, sync, or exact-handle reacquisition. Never open a second terminal or create a second
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
5. After verified slice commits are integrated in deterministic slice order, immediately revalidate
   the immutable ownership receipt before cleanup. `orca worktree show`/`list` must still match the
   repository, complete worktree id, instance, absolute path, gitdir, and branch. Git must show the
   exact worktree/gitdir/path, no symlink, a clean state, and no merge/rebase/cherry-pick/revert in
   progress. The mutable `current_head` must be current, the sole `current_handle` must be the exact
   startup handle and closed only for cleanup, the recorded branch tip must equal `current_head`, and
   `git merge-base --is-ancestor <slice-head> <integration-head>` must pass. Do not require
   `current_head` to equal `pre_head`, but never substitute a different terminal handle.
6. Stop the exact startup/current worker handle, then recheck the immutable receipt, current head,
   recorded branch tip, clean state, integration, and no operation in progress. If the worktree is
   attached to the recorded branch, detach it at `current_head` and revalidate those same ownership
   and integration facts. Before removing the worktree, delete only the exact recorded branch with
   safe non-force `git branch --delete <branch>` after its tip equals `current_head` and is integrated,
   then prove the ref is absent with `git show-ref --verify --quiet refs/heads/<branch>` failing.
   Remove only by the complete worktree id after those proofs. Prove Orca, Git, path, branch ref,
   and terminal absence and zero owned residue. Any pre-removal mismatch, missing ownership, dirty
   state, non-ancestor slice head, failed branch deletion, or unproven ref absence retains the exact
   path and serializes; if removal already succeeded, record the exact receipt and identifiers without
   claiming that the removed path remains, then serialize residue cleanup. Never select cleanup by
   name or branch.

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
