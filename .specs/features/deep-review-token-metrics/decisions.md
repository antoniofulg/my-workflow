# Deep Review Token Metrics Decisions

## Human decisions

| Decision | Why | Rejected alternatives | Change cost | User cost today |
| --- | --- | --- | --- | --- |
| Collect numbers without a token limit | Measurement is for comparison, not enforcement. | Fixed or configurable budget enforcement. | Reintroduce a separate policy later. | None. |
| Stop at a draft pull request | Human evaluation precedes merge. | Autonomous merge. | Mark ready and merge later. | Delivery waits for review. |

## Run decisions

| Decision | Why | Rejected alternatives | Change cost | User cost today |
| --- | --- | --- | --- | --- |
| Serialize reviewer jobs | Exactly one active reviewer makes retries and output checkpoints deterministic. | Overlapping worker threads or a worker-concurrency flag. | None. | Reviewers run sequentially. |
| Keep only the Codex adapter now | It is the only verified telemetry source. | Invent Claude/Cursor counters. | Add adapters when stable sources are known. | Claude/Cursor metrics are unavailable. |
| Keep the ledger content-safe and atomic | Metrics need durable integrity without storing reviewed content. | Persist raw provider data. | Relax validation later, not recommended. | None. |
| Persist final totals separately from round delta | Auditors need to distinguish provider totals at completion from consumption since the baseline. | Store only the delta. | Recompute is no longer possible from the ledger alone. | None. |
| Keep optional pinned Graft context | The Antclips trial showed repository maps and symbol lookup improve reviewer context; the local Graft trial was preferred over Graphify. | Replace Graft with Graphify, make Graft mandatory, or require dot-directory indexing. | Keep plain repository inspection as fallback. | `build_jobs.py` attempts build/map/lookup before prompts; failure remains non-blocking. |
