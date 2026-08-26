# Host-Agnostic Slice Parallelization Decisions

## Human decisions

| Decision | Why | Alternatives rejected | Change cost now | User cost today |
| --- | --- | --- | --- | --- |
| Use coordinator-assisted Orca workers until automatic orchestration is fixed. | Direct worktree creation, prompt delivery, and same-terminal follow-up provide useful inter-slice overlap now. | Wait for the upstream fix; remain fully serial. Both discard available wall-time savings. | Remove the assisted section after automatic execution proves equivalent recovery and cleanup. | Main agent must supervise checkpoints and cleanup. |
| Keep TLC and readiness stages unchanged. | Parallelism must reduce wall time without reducing confidence. | Parallel tasks inside a slice; skipped or combined Verifier, review, gate, or QA stages. | None; existing contracts already enforce this. | Some dependencies still serialize and sync can repeat affected gates. |

## Autonomous run decisions

| Decision | Why | Alternatives rejected | Change cost now | User cost today |
| --- | --- | --- | --- | --- |
| Extend existing Slice D before its first PR. | Assisted execution is an adoption/runtime contract extension and the feature is not merged. Frozen slice count and role route remain valid. | Open a stacked feature before merging this branch; silently refresh the frozen workflow. | Split T5 into a follow-up feature and PR. | One additional Slice D verification and incremental grouped review. |
| Use Orca worktree comments as restart handoffs, not as machine receipts. | Native state survives agent turns and can be reconciled against Git and `tasks.md` without new code. | Add a second scheduler or parse free-form comments as authoritative state. | Add a structured ledger only if assisted recovery proves insufficient. | Coordinator performs reconciliation after restart. |
| Keep automatic Orca `1.4.188` preflight unsupported. | Assisted supervision cannot prove transactional worker lifecycle semantics. | Write a compatibility PASS or route the automatic adapter through direct terminal polling. | Remove known-bad version only after upstream release plus canary PASS. | Automatic `safe/full` remains serial until Orca updates. |

AD-015 records the cross-feature ownership boundary.
