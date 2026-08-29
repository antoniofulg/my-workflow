# T4 task memory

- Planner accepts only v3 frozen snapshots and exposes `decision`, `compatibility`, and lane
  execution metadata. Assisted mode starts with two selected writer lanes; disabled mode selects one
  serial integration lane.
- Cross-slice consumers require an explicitly verified producer and carry its dependency paths in
  `sync_after`; no fixed parity or odd/even ownership is used.
- Ready lanes are recomputed against path-prefix overlaps and shared resource names. A conflict
  blocks only the later claimant with exact IDs and paths/resource; independent work stays eligible.
- A dirty integration checkout returns `dirty-baseline` with no lanes or effect intents. The feature's
  generated workflow snapshot is ignored for this read-only check because refresh edits that file.
