# Parallel Slice Dispatch Test Contract

## Unit

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| UT-001 | PAR-05, PAR-09 | Slice order | Two pending tasks share a slice | Only the first is a candidate; the second is blocked by slice order. |
| UT-002 | PAR-06 | Disabled mode | Any valid graph in disabled mode | One serial lane preserves declaration order. |
| UT-003 | PAR-07 | Safe readiness | Two root slices and one unverified cross-slice consumer | Root slices are candidates; consumer is blocked awaiting verified producer. |
| UT-004 | PAR-08 | Full checkpoint | A complete task unlocks another slice | Consumer is ready and records the producer task as `sync_after`. |
| UT-005 | PAR-10 | Graph failure | Cycle, unknown dependency, missing slice, or ambiguous path | Plan falls back with the exact decisive reason. |
| UT-006 | PAR-10 | Write collision | Two candidates share one exact `Where` path | Plan falls back and names both tasks. |
| UT-007 | PAR-11 | Determinism | Same files and Git head planned twice | JSON bytes are equal. |
| UT-008 | PAR-10 | Missing task input | `tasks.md` is missing or unreadable | CLI exits non-zero, emits empty stdout, and reports the read failure. |

## Integration

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| IT-001 | PAR-01 | Default configuration | `[parallelization]` is absent | Snapshot contains `parallelization.mode = disabled`. |
| IT-002 | PAR-02 | Valid modes | Resolver runs once for each supported mode | Snapshot freezes the selected value. |
| IT-003 | PAR-03 | Invalid mode | Existing snapshot plus unsupported value | Resolver exits non-zero and existing snapshot bytes are unchanged. |
| IT-004 | PAR-04 | Resume | Config changes after snapshot creation | Existing snapshot mode remains authoritative. |
| IT-005 | PAR-05–PAR-11 | Point-in-time plan | Fixture tasks and workflow snapshot | CLI emits the exact expected JSON projection. |
| IT-006 | PAR-12–PAR-16 | Autonomous contract | Shared contract suite reads skill files | Serial fallback, turn-end/follow-up, sync, invalidation, and all review gates remain mandatory. |

## End-to-end

None. This delivery produces a deterministic plan and orchestration contract, not a portable agent runtime.

## Security

None. Inputs are local versioned workflow files; malformed input is covered by fail-closed integration cases.

## Ownership

| Test IDs | Owning task |
| --- | --- |
| IT-001–IT-004 | T1 |
| UT-001–UT-007, IT-005 | T2 |
| UT-008 | T2/TDR1 |
| IT-006 | T3 |
