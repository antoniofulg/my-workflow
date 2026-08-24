# Parallel Slice Executor Test Contract

## Unit

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| UT-001 | EXE-01, EXE-02 | Mode and slice state | Disabled plan or two tasks in one slice | Disabled emits only serial; at most one task in a slice becomes active. |
| UT-002 | EXE-03, EXE-04 | At-most-once restart | The same ready lane is started, state reloaded, and started again | One idempotency key, worktree, worker, and lease effect exist. |
| UT-003 | EXE-05 | Foreign or malformed state | Repository/feature identity differs or JSON is invalid | No adapter runs; serial recovery names the cause. |
| UT-004 | EXE-12, EXE-13 | Exact checkpoint sync | Clean consumer with producer commit absent/present in ancestry | Rebase targets the exact commit, or reports a byte-stable no-op. |
| UT-005 | EXE-14 | Checkpoint conflict | Producer and consumer change the same line | Rebase aborts; pre-sync HEAD and clean status are restored; lane halts. |
| UT-006 | EXE-15–EXE-17 | Evidence and integration | Sync changes HEAD, verified slices merge, or merge conflicts | Affected receipts invalidate; merge order is stable; conflict aborts cleanly. |
| UT-007 | EXE-18–EXE-20 | Resource acquisition | `none` lane or conforming provider receipt | `none` starts without provider; declared resources start only after correlated lease. |
| UT-008 | EXE-21, EXE-22 | Resource failure and cleanup | Missing, duplicate, malformed, timed-out, failed, or repeated provider call | Dispatch is refused; accepted lease releases exactly once and retry returns its receipt. |

## Integration

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| IT-001 | EXE-01–EXE-05 | Executor CLI | `start`, `resume`, and `status` run against a recording adapter | Each command emits one JSON object naming its verb; resume reconciles persisted state and status has no effect. |
| IT-002 | EXE-06, EXE-07 | Orca worker start | Ready lane with exact source base | Child worktree precedes worker start and receipt contains every correlated ID. |
| IT-003 | EXE-08–EXE-10 | Orca events and follow-up | `worker_done`, clean waiter, dependency event, and timeout | Result is read before release; same terminal receives follow-up; timeout leaves state unchanged. |
| IT-004 | EXE-11 | Orca failure recovery | Dirty, mismatched, duplicate, escalated, or failed receipt | Lane halts and no replacement worker starts. |
| IT-005 | EXE-19–EXE-22 | Frozen provider config | Missing, valid, external, directory, or symlinked provider path | Snapshot freezes the safe executable or resolution fails without replacing prior state. |
| IT-006 | EXE-18–EXE-21 | Planned resource requirements | Valid, missing, or ambiguous task `Resources` metadata | Plan exposes exact names or selects serial fallback before execution. |
| IT-007 | EXE-01–EXE-22 | Autonomous contract | Shared workflow suite reads executor policy | Core/adapter boundary, serial fallback, TLC order, checkpoints, evidence, and lifecycle remain mandatory. |

## End-to-end

| ID | Requirement | Journey | Steps | Expected |
| --- | --- | --- | --- | --- |
| E2E-001 | EXE-06–EXE-11, EXE-18 | Real Orca concurrency | Create a disposable run, dispatch two `Resources: none` slices to separate child worktrees, observe both active before accepting results, then release them | Distinct worktree/branch/dispatch/terminal receipts, two correlated completion events, clean worktrees, and owned-terminal cleanup. |

The repository has no product runtime or database. The pilot proves real worktree/worker concurrency;
resource-bearing runtime isolation remains a conformance obligation for each consuming project's
provider and QA adapter.

## Security

| ID | Requirement | Abuse case | Attempt | Expected |
| --- | --- | --- | --- | --- |
| SEC-001 | SEC-001 | Foreign runtime state | Reuse state from another repository or feature | State rejected before any adapter call. |
| SEC-002 | SEC-002 | Torn or versioned state | Interrupt replacement or inspect Git worktree | Prior complete JSON survives; no runtime receipt is tracked. |
| SEC-003 | SEC-003 | Shell injection | Put metacharacters in feature/task/provider inputs | Exact argv reaches the recording process; no shell expansion occurs. |
| SEC-004 | SEC-004 | Filesystem escape | Use `..`, external absolute path, or unsafe symlink for repo/worktree/provider | Action fails before any write or process start. |
| SEC-005 | SEC-005 | Receipt spoofing | Return a different lane or idempotency key | Receipt rejected and lane halted. |
| SEC-006 | SEC-006 | Secret persistence | Provider returns credential-shaped environment values | Output/state retain keys and redaction markers only. |
| SEC-007 | SEC-007 | Unleased runtime | Declare port/database with no accepted provider | Worker never starts and serial fallback is recorded. |
| SEC-008 | SEC-008 | Cross-lane cleanup | Release another lane's lease or repeat release | Foreign release rejected; owned repeat is idempotent. |

## Ownership

| Test IDs | Owning task |
| --- | --- |
| UT-001, UT-003, SEC-001–SEC-004 | T1 |
| UT-002, UT-007, UT-008, IT-001, SEC-007, SEC-008 | T2 |
| IT-002–IT-004, SEC-005, SEC-006 | T3 |
| UT-004–UT-006 | T4 |
| IT-005 | T5 |
| IT-006 | T6 |
| IT-007, E2E-001 | T7 |
