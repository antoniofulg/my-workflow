# Merge-Alone Slice Derivation Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| MAS-UT-001 | Parses the Praxis migration as one slice | Five primary tasks, three cohorts, one closure row `A` | Contract contains slice `A` and every primary task belongs to it |
| MAS-UT-002 | Parses independent capabilities as two slices | Tasks assigned once across closure rows `A` and `B` | Contract contains exactly `A` and `B` |
| MAS-UT-003 | Rejects incomplete closure fields | One row missing outcome or independent gate | Validation names slice and missing field |
| MAS-UT-004 | Rejects a non-mergeable row | Merge-alone cell is empty, `no`, `Yes`, or `true` | Validation names slice `A` and requires exact lowercase `yes` |
| MAS-UT-005 | Rejects inconsistent membership | Primary task unassigned, assigned twice, or assigned to unknown slice | Validation names task and membership defect |
| MAS-UT-006 | Rejects orphan and duplicate closures | Closure has no primary task or repeats a slice ID | Validation names invalid slice |
| MAS-UT-007 | Ignores remediation records for slice count | Valid primary tasks plus `T2R1` and `TDR1` records, one mis-tagged `**Slice:** B` | Primary contract and derived count are unchanged |
| MAS-UT-008 | Emits a deterministic contract | `--slice-contract-json` on the two-slice fixture, run twice | Identical stdout; task and slice ids in document order |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| MAS-IT-001 | Resolves Praxis regression from validated tasks | Initial resolver call for Praxis fixture without `--slices` | Review groups cover exactly slice `1` |
| MAS-IT-002 | Resolves two merge-alone capabilities | Initial resolver call for two-slice fixture | Review groups cover slice ordinals `1` and `2` exactly once |
| MAS-IT-003 | Uses optional count only as assertion | Initial or refresh call with `--slices` unequal to derived count, or `0`/negative | Non-zero error naming supplied and derived counts; prior snapshot absent or byte-for-byte unchanged |
| MAS-IT-004 | Defaults correctly without Tasks | Feature directory has no `tasks.md` | Snapshot review groups cover exactly slice `1` |
| MAS-IT-005 | Fails closed on malformed Tasks | Present task document lacks a valid closure contract | Non-zero error naming the validator failure; no snapshot written, existing snapshot bytes unchanged |
| MAS-IT-006 | Preserves normal resume | Frozen one-slice snapshot, tasks later declare two slices or become malformed | Resume returns byte-for-byte frozen snapshot without reading tasks |
| MAS-IT-007 | Re-derives explicit refresh | Same changed tasks followed by `--refresh` | Refreshed groups cover slices `1` and `2`; snapshot schema unchanged |
| MAS-IT-008 | Keeps downstream task membership aligned | Two-slice fixture passed to `parallel_plan.plan` after resolution | Lanes plus blocked membership equals `validated_slice_contract(...)["task_slices"]` |
| MAS-IT-009 | Publishes the task-planning contract | Template, workflow-config skill, README | Template shows `**Slice:**` per task and the closure table; skill and README show `--slices` only as optional assertion |
| MAS-IT-010 | Planner ignores remediation record fields | Valid two-slice document with a `### T2R1:` record after `T2` carrying `**Status:** complete`, `**Resources:** db`, and `**Depends on:** T3` | `T2` plans exactly as it does without the record: same lane or blocked placement, resources `none`, dependencies unchanged |

## End-to-end

No separate browser or external journey. `MAS-IT-001` and `MAS-IT-002` exercise the public local CLI
boundary through repository fixtures.

## Security

No security surface changes. All inputs are repository-local Markdown and existing configuration;
malformed inputs fail before snapshot replacement under `MAS-IT-003` and `MAS-IT-005`.
