# Shared feature memory

- S1 owns the hard cut from `tlc-spec-driven` to `workflow-spec-driven`; no alias or dual install.
- The workflow-owned skill preserves CC BY 4.0 attribution in its `NOTICE.md`.
- The coordinator dispatches safe independent slices by default; only concurrent writers use
  worktrees, while tasks inside a slice remain sequential.
- Live Orca is out of scope; later probe tests must use fake providers and import-safety checks.
