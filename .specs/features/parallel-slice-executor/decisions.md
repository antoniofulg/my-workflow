# Parallel Slice Executor Decisions

## Human decisions

| Decision | Why | Rejected alternatives | Cost to change now | Cost to users today |
| --- | --- | --- | --- | --- |
| Keep TLC tasks sequential and parallelize only eligible slices. | The current execution and verification loop is reliable. | Parallel tasks inside one slice. | Redesign task ownership, gates, commits, and Verifier packets. | Some work remains serial even when files differ. |
| Preserve every gate, Verifier, grouped deep-review, QA, and full-gate stage. | Wall-time savings cannot reduce confidence. | Review or gate shortcuts. | Low because the stages remain unchanged. | Revalidation can consume part of the parallel speedup. |
| End a waiting worker turn and resume it by follow-up. | Event-driven idle time uses no model polling tokens. | Watchdog agent or periodic status prompts. | Change worker lifecycle and runtime adapter. | A dependency event creates one later worker turn. |
| Make execution IDE-agnostic with Orca as the first adapter. | Teams may move IDEs while keeping the workflow. | Orca-specific policy core. | Replace or extend the adapter conformance boundary. | Non-Orca environments remain serial until an adapter exists. |
| Keep versioned feature specs and local runtime receipts separate. | Specs are shared truth; terminal/lease IDs are host state. | Ignore feature state or commit runtime identifiers. | Migrate local state discovery and cleanup. | Resume needs access to the same Git repository metadata. |

## Autonomous run decisions

| Decision | Why | Rejected alternatives | Cost to change now | Cost to users today |
| --- | --- | --- | --- | --- |
| Use a deterministic state machine and action receipts. | Restart safety and at-most-once effects should not depend on agent prose. | Direct command instructions only. | Rewrite adapters and state migration. | Adds a small local state file and schema. |
| Rebase only a dependent private lane at a declared checkpoint. | It receives the exact producer before the dependent task with less churn than per-task sync. | Rebase every task; defer all sync to final integration. | Change Git adapter and evidence invalidation rules. | Changed lanes repeat affected gates. |
| Merge verified slices into the feature branch. | Verification references keep their commit identity. | Rebase every verified slice at integration. | Rewrite integration order and review evidence. | Feature history includes explicit slice merges. |
| Require explicit `Resources` metadata. | Absence is uncertainty, and uncertainty must serialize. | Guess resource needs from paths or commands. | Update planning templates and existing in-flight tasks. | Maintainers add one field to parallelizable tasks. |
| Use a consumer executable for resources. | Orca exposes no proven port/DB reservation verb and projects own runtime semantics. | Fake an Orca API; bundle a universal allocator. | Replace provider config/protocol and conformance tests. | Resource-bearing parallelism needs one project adapter. |
| Bound the real pilot to this repository's actual surface. | It has Git and Orca worktrees but no app server or database. | Claim unobservable runtime/DB isolation. | Add a product fixture or run adoption QA in a consumer. | Each consumer must prove its provider once. |

## Durable project decisions promoted

| Decision | Record |
| --- | --- |
| Parallel execution policy is provider-neutral; Git owns prevalidated worktree creation, Orca owns worker/events, and missing resource capability serializes. | `AD-011` in `.specs/STATE.md` supersedes `AD-010`. |

## Halt report

The autonomous run halted during Slice A after the third Technical Verifier fix round. All 26
executor tests pass and the final sensor kills pending-worker and recovered-lease regressions, but
IT-001 exercises public CLI `resume` only in `disabled`. Removing adapter construction from the
parallel `resume` path still passes the suite.

T3-T7 have not started. Continuing requires a human decision because `docs/guidelines/REVIEW-ROUNDS.md`
caps this loop. The recommended choice is one exceptional fix limited to safe-mode persisted-state
`resume`, followed by a fresh Technical Verifier. Accepting the gap or weakening IT-001 conflicts
with the user's reliability requirement.
