# Merge-Alone Slice Derivation Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| MAS-UT-001 | Parses the Praxis migration as one slice | Five primary tasks, three cohorts, one closure row `A` | Contract contains slice `A` and every primary task belongs to it |
| MAS-UT-002 | Parses independent capabilities as two slices | Tasks assigned once across closure rows `A` and `B` | Contract contains exactly `A` and `B` |
| MAS-UT-003 | Rejects incomplete closure fields | One row missing outcome or independent gate | Validation names slice and missing field |
| MAS-UT-004 | Rejects a non-mergeable row | Merge-alone cell is empty, `no`, or another value | Validation requires exact `yes` |
| MAS-UT-005 | Rejects inconsistent membership | Primary task unassigned, assigned twice, or assigned to unknown slice | Validation names task and membership defect |
| MAS-UT-006 | Rejects orphan and duplicate closures | Closure has no primary task or repeats a slice ID | Validation names invalid slice |
| MAS-UT-007 | Ignores remediation records for slice count | Valid primary tasks plus `T2R1` and `TDR1` records | Primary contract and derived count are unchanged |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| MAS-IT-001 | Resolves Praxis regression from validated tasks | Initial resolver call for Praxis fixture | Review groups cover exactly slice `1` |
| MAS-IT-002 | Resolves two merge-alone capabilities | Initial resolver call for two-slice fixture | Review groups cover slice ordinals `1` and `2` exactly once |
| MAS-IT-003 | Uses optional count only as assertion | Initial or refresh call with `--slices` unequal to derived count | Non-zero error; prior snapshot absent or byte-for-byte unchanged |
| MAS-IT-004 | Defaults correctly without Tasks | Feature directory has no `tasks.md` | Snapshot review groups cover exactly slice `1` |
| MAS-IT-005 | Fails closed on malformed Tasks | Present task document lacks a valid closure contract | Non-zero error; no snapshot written |
| MAS-IT-006 | Preserves normal resume | Frozen one-slice snapshot, tasks later declare two slices | Resume returns byte-for-byte frozen workflow state without revalidation |
| MAS-IT-007 | Re-derives explicit refresh | Same changed tasks followed by refresh | Refreshed groups cover slices `1` and `2` |
| MAS-IT-008 | Keeps downstream task membership aligned | Validated task contract passed to parallel planning | Parallel slice membership equals validator membership |
| MAS-IT-009 | Publishes the task-planning contract | Adopted TLC template and workflow-config skill | Template distinguishes slice/phase/batch and resolver docs omit manual count ownership |

## End-to-end

No separate browser or external journey. `MAS-IT-001` and `MAS-IT-002` exercise the public local CLI
boundary through repository fixtures.

## Security

No security surface changes. All inputs are repository-local Markdown and existing configuration;
malformed inputs fail before snapshot replacement under `MAS-IT-003` and `MAS-IT-005`.
