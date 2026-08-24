# Parallel Slice Dispatch Decisions

## Human decisions

| Decision | Why | Rejected alternatives | Cost to change now | Cost to users today |
| --- | --- | --- | --- | --- |
| Keep TLC task execution sequential inside each slice. | The current workflow is reliable and should not be redesigned for concurrency. | Parallel tasks inside one TLC batch. | Redesign planner, validators, and worker ownership. | Some potential intra-slice speedup remains unavailable. |
| Apply parallelization only when it preserves every existing quality stage. | Wall-time reduction cannot weaken readiness. | Skipping or postponing gates, reviews, or QA. | Low; serial fallback remains available. | Features without proven concurrency remain serial. |
| Use `disabled`, `safe`, and `full` modes. | Teams need explicit risk posture per feature. | One implicit adaptive mode. | Snapshot schema and policy migration. | Maintainers must choose a mode only when they want concurrency. |
| End a waiting worker turn and resume by follow-up. | Event-driven waiting avoids LLM polling cost. | Watchdog or worker polling loops. | Change orchestrator lifecycle contract. | A follow-up requires one later model turn. |
| Keep `.specs/features/` versioned and durable. | Worktrees, gates, handoffs, and audits need shared workflow state. | Ignore or auto-delete completed feature state. | Repository-history and tooling migration. | The repository retains small historical planning artifacts. |

## Autonomous run decisions

| Decision | Why | Rejected alternatives | Cost to change now | Cost to users today |
| --- | --- | --- | --- | --- |
| Deliver a deterministic plan before a generic executor. | The repository has no provider-independent spawn/runtime API. | Documentation only; unsafe generic worktree executor. | Add a provider-specific executor in a later feature. | Capable orchestrators must perform mutations themselves. |
| Reuse `tasks.md` with optional `Slice` metadata. | A second manifest would duplicate dependencies and drift. | Separate parallel DAG manifest. | Add a manifest and synchronization validator. | Missing metadata forces serial fallback. |
| Keep plans ephemeral and workflow snapshots durable. | Plans are point-in-time projections; modes must survive resume. | Commit every ready-set recalculation. | Change storage and cleanup rules. | Operators regenerate plans after task events. |
