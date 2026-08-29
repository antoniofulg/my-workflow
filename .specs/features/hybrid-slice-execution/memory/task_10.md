# T10 task memory

- `LaneScheduler` starts at the two-writer baseline, retains active lanes, and admits only one
  additional compatible lane after a normalized healthy settle; the configured cap is never raised.
- The executor expands a writer-cap plan only when needed, excludes completed runtime tasks, and
  refills freed slots from the recomputed ready queue. Existing point-in-time planner test doubles
  remain supported.
- Active lane state persists declared paths so dependency/path compatibility is fail-closed during
  later scheduling passes.
