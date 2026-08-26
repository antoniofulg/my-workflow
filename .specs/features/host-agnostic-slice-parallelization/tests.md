# Host-Agnostic Slice Parallelization Test Contract

## Unit

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| UT-001 | HST-01 | Disabled execution short-circuit | `start` or `resume` mode is disabled | No adapter import, probe, checkout, or worker effect; explicit `preflight` remains diagnostic. |
| UT-002 | HST-02–HST-04 | Host selection | Auto inside/outside Maestri or explicit backend | Current host only; incompatible result serializes; scheduler stages remain unchanged. |
| UT-003 | ORC-01, ORC-02 | Orca read-only probe | Ready/invalid status or app version `1.4.188` | Exact compatibility result; known-bad version creates no effect. |
| UT-004 | ORC-06, ORC-07 | Compatibility cache | Matching or changed identity | Matching PASS is reused; any changed field invalidates it. |
| UT-005 | MAE-01–MAE-04 | Maestri capability probe | Missing env or documented current capabilities | Exact missing capabilities; no mutation and no text parsing. |

## Integration

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| IT-001 | ORC-03, ORC-04 | Orca lifecycle canary | Candidate build reaches worker_done | Correlated read, ack, release, checkout removal, zero residue, PASS cache. |
| IT-002 | ORC-05 | Orca canary failure | Start, completion, release, or removal fails | No PASS cache; failed stage and retained IDs reported. |
| IT-003 | HST-01–HST-04 | Executor preflight CLI | `preflight` with auto/orca/maestri, including disabled mode | One JSON result; disabled start/resume remains fail-closed while diagnostic preflight can inspect the host. |
| IT-004 | MAE-01–MAE-04 | Maestri current contract | Recording current CLI manifest | `unsupported`; zero floor/recruit/Git effects. |

## End-to-end

No new permanent e2e journey. The existing parallel executor QA scenario owns real slice
concurrency. This feature adds a read-only installed-Orca preflight and a future explicit canary run
after an Orca update is detected.

## Security

| ID | Requirement | Abuse case | Attempt | Expected |
| --- | --- | --- | --- | --- |
| SEC-001 | SEC-001 | Disabled execution mutation | Mutating recording adapter under disabled `start`/`resume` | Adapter is never constructed; explicit diagnostic preflight is the only allowed probe. |
| SEC-002 | SEC-002 | Foreign cache | Copy another repository's PASS receipt | Receipt rejected without host effects. |
| SEC-003 | SEC-003 | Shell/path injection | Metacharacters or external checkout path | Fixed argv/path validation rejects before mutation. |
| SEC-004 | SEC-004, SEC-005 | Unstructured/secret response | Human text or credential fields | Text rejected; diagnostics contain redaction markers only. |
| SEC-005 | SEC-006, SEC-007 | False cleanup | Worker released but checkout retained, or foreign ID supplied | No PASS; foreign cleanup refused; retained ID reported. |

## Ownership

| Test IDs | Owning task |
| --- | --- |
| UT-001, UT-002, IT-003, SEC-001 | T1 |
| UT-003, UT-004, IT-001, IT-002, SEC-002, SEC-003, SEC-005 | T2 |
| UT-005, IT-004, SEC-004 | T3 |
