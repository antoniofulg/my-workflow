# Host-Agnostic Slice Parallelization Test Contract

## Unit

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| UT-001 | HST-01 | Disabled execution short-circuit | `start` or `resume` mode is disabled | No adapter import, probe, checkout, or worker effect; explicit `preflight` remains diagnostic. |
| UT-002 | HST-02–HST-04 | Host selection | Auto inside/outside Maestri or explicit backend | Current host only; incompatible result serializes; scheduler stages remain unchanged. |
| UT-003 | ORC-01, ORC-02 | Orca read-only probe | Ready/invalid status or app version `1.4.188` | Exact compatibility result; known-bad version creates no effect. |
| UT-004 | ORC-06, ORC-07 | Compatibility cache | Matching or changed identity | Matching PASS is reused; any changed field invalidates it. |
| UT-005 | MAE-01–MAE-04 | Maestri capability probe | Missing env, current capabilities, or complete-looking claims | Exact unsupported reason/capabilities; no mutation, generic Git execution, or text parsing. |
| UT-006 | HST-01 | Workflow snapshot schema | Current v2 snapshot or obsolete v1 snapshot | v2 is accepted; v1 is rejected before planning or host effects. |

## Integration

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| IT-001 | ORC-03, ORC-04 | Orca lifecycle canary | Candidate build reaches worker_done | Correlated read, ack, release, checkout removal, zero residue, PASS cache. |
| IT-002 | ORC-05 | Orca canary failure | Start, completion, release, or removal fails | No PASS cache; failed stage and retained IDs reported. |
| IT-003 | HST-01–HST-04 | Executor preflight CLI | `preflight` with auto/orca/maestri, including disabled mode | One JSON result; disabled start/resume remains fail-closed while diagnostic preflight can inspect the host. |
| IT-004 | MAE-01–MAE-04 | Maestri current contract | Recording current CLI manifest | `unsupported`; zero floor/recruit/Git effects. |
| IT-005 | AST-01–AST-07 | Assisted coordinator contract | Automatic Orca unsupported with explicit assisted authorization | Explicit-base worktree promotes one new unused startup shell with the frozen route, uses the same handle, cleans exact owned resources, records no compatibility PASS, and preserves TLC/review/QA stages. |

## End-to-end

| ID | Requirement | Journey | Steps | Expected |
| --- | --- | --- | --- | --- |
| E2E-001 | AST-01–AST-07 | Assisted two-slice Orca pilot | Start B after an early A dependency, park B at a later A dependency, sync its exact producer commit, follow up the same terminal, integrate, and clean owned resources | Measured slice overlap, sequential tasks, one parked/resumed B worker, all required gates/stages, and zero owned residue. |

## Security

| ID | Requirement | Abuse case | Attempt | Expected |
| --- | --- | --- | --- | --- |
| SEC-001 | SEC-001 | Disabled execution mutation | Mutating recording adapter under disabled `start`/`resume` | Adapter is never constructed; explicit diagnostic preflight is the only allowed probe. |
| SEC-002 | SEC-002 | Foreign cache | Copy another repository's PASS receipt | Receipt rejected without host effects. |
| SEC-003 | SEC-003 | Shell/path injection | Metacharacters or external checkout path | Fixed argv/path validation rejects before mutation. |
| SEC-004 | SEC-004, SEC-005 | Unstructured/secret response | Human text or credential fields | Text rejected; diagnostics contain redaction markers only. |
| SEC-005 | SEC-006, SEC-007 | False cleanup | Worker released but checkout retained, or foreign ID supplied | No PASS; foreign cleanup refused; retained ID reported. |
| SEC-006 | SEC-008 | Assisted foreign or dirty cleanup | Missing coordinator ownership, unintegrated commit, or dirty worktree | No deletion; exact retained worktree reported and lane serialized. |

## Ownership

| Test IDs | Owning task |
| --- | --- |
| UT-001, UT-002, UT-006, IT-003, SEC-001 | T1 |
| UT-003, UT-004, IT-001, IT-002, SEC-002, SEC-003, SEC-005 | T2 |
| UT-005, IT-004, SEC-004 | T3 |
| IT-005, E2E-001, SEC-006 | T5 |
