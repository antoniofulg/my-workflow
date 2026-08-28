# Shared feature memory

- S1 owns the hard cut from `tlc-spec-driven` to `workflow-spec-driven`; no alias or dual install.
- The workflow-owned skill preserves CC BY 4.0 attribution in its `NOTICE.md`.
- The coordinator dispatches safe independent slices by default; only concurrent writers use
  worktrees, while tasks inside a slice remain sequential.
- Live Orca is out of scope; later probe tests must use fake providers and import-safety checks.
- Slice packets accept only the nine fields in the surface contract; the builder measures UTF-8 byte
  lengths and writes redacted telemetry before rejecting an oversized packet.
- Re-adoption removes both the obsolete `.agents/skills/tlc-spec-driven` tree and its managed
  `.claude/skills/tlc-spec-driven` pointer while leaving consumer-owned files untouched.
