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
| UT-007 | HST-05 | Default and explicit workflow modes | Resolve without a configured mode, then resolve each explicit mode | Default snapshot is `assisted`; `disabled`, `assisted`, `safe`, and `full` are accepted without changing explicit values. |
| UT-008 | HST-06, AST-08 | Assisted planning semantics | Independent, completed-producer, incomplete-dependency, conflicting-write, and malformed DAG inputs under `assisted` | Ready and `sync_after` outputs equal `full`; incomplete dependencies wait; conflicts and malformed metadata return serial. |

## Integration

| ID | Requirement | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| IT-001 | ORC-03, ORC-04 | Orca lifecycle canary | Candidate build reaches worker_done | Correlated read, ack, release, checkout removal, zero residue, PASS cache. |
| IT-002 | ORC-05 | Orca canary failure | Start, completion, release, or removal fails | No PASS cache; failed stage and retained IDs reported. |
| IT-003 | HST-01–HST-04 | Executor preflight CLI | `preflight` with auto/orca/maestri, including disabled mode | One JSON result; disabled start/resume remains fail-closed while diagnostic preflight can inspect the host. |
| IT-004 | MAE-01–MAE-04 | Maestri current contract | Recording current CLI manifest | `unsupported`; zero floor/recruit/Git effects. |
| IT-005 | AST-01–AST-07 | Assisted coordinator contract | Automatic Orca unsupported with frozen mode `assisted` and at least two safe ready slices | One unique-name create is reconciled without blind retry through the 250 ms / 60000 ms SETTLE WINDOW and final audit; explicit-base worktree proves one new, uniquely owned, unused startup shell with no default/agent activity; a bounded machine-only exact-handle loop sees two consecutive connected `source=screen` frames matching the frozen route and resets on nonmatch; dependency waiting remains event-driven with no model turns; the slice packet body is written to a coordinator-owned file outside every slice worktree and only a short fixed-shape pointer crosses the one mandated send, with no conditional, threshold, fallback, or alternative branch permitting the body onto that send, and the worker obliged to read that file or report it unreadable at once; same exact handle is reused; exact integrated worktree/branch/terminal absence is proven; no compatibility PASS; TLC/review/QA stages are preserved. |
| IT-006 | HST-06, AST-08 | Assisted executor boundary | `start`/`resume` with `assisted`, explicit `disabled`, no ready overlap, or failed isolation/resource proof | Assisted returns a coordinator plan before automatic adapter construction; disabled and every uncertified assisted case execute sequentially with zero new host effect. |
| IT-007 | AST-10, SEC-009 | One-shot mutation reconciliation | Fake Orca injects transient/error/missing receipts for create, send, comment set, terminal stop, and worktree rm | Each logical mutation appears exactly once; only read-only show/list/read/wait/audit calls repeat inside bounds. |
| IT-008 | AST-11 | Pointer-only delivery | Fake Orca records a long packet body and the one terminal send | Sent text equals the short pointer and never contains the packet body, regardless of body length or receipt outcome. |
| IT-009 | AST-02–AST-06, AST-09 | Park, unblock, and same-handle lifecycle | Fake two-slice DAG parks B on A, verifies A's producer commit, syncs it, reruns the affected gate, resumes B, integrates, and cleans | B uses one unchanged startup handle; exact checkpoint and producer commit agree; deterministic integration succeeds; owned residue is zero. |
| IT-010 | AST-09, AST-12 | Standard adopted agent contract | Canonical autonomous contract reads the default workflow and assisted dispatch rules | Main agent owns all cross-slice effects; slice workers cannot spawn siblings; sequential fallback and unchanged readiness stages are explicit. |
| IT-011 | AST-12 | Adoption installs the assisted probe | Real adoption dry-run into a disposable directory, then import the installed module with fake Orca on PATH | `tools/orca_assisted_probe.py` lands at the declared path; import succeeds and records zero Orca calls. |

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
| SEC-007 | SEC-008, SEC-009 | Assisted cleanup preserves foreign resources | Fake Orca inventories one owned lane plus foreign terminal, worktree, branch, and path entries | Cleanup removes each exact owned resource at most once and leaves every foreign identifier unchanged. |

## Ownership

| Test IDs | Owning task |
| --- | --- |
| UT-001, UT-002, UT-006, IT-003, SEC-001 | T1 |
| UT-003, UT-004, IT-001, IT-002, SEC-002, SEC-003, SEC-005 | T2 |
| UT-005, IT-004, SEC-004 | T3 |
| E2E-001, SEC-006 | T5 |
| UT-007 | T6 |
| UT-008, IT-006 | T7 |
| IT-007, IT-008, IT-009, SEC-007 | T8 |
| IT-011 | T9 |
| IT-005, IT-010 | T10 |
