# Hybrid Slice Execution Test Contract

Every case derives from `.specs/features/hybrid-slice-execution/spec.md`. Canonical suites are
extended in place. No case exists only for coverage, prose, or generated-file snapshots.

## Unit

| ID | Requirements | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| UT-001 | HSE-01, HSE-02, HSE-04 | Workflow skill is one attributed slice-native authority | Inspect the source/adoption manifest and activate the installed skill | `workflow-spec-driven` and `NOTICE.md` exist; TLC path, phase batches, opt-in wording, and feature-only Verifier wording are absent |
| UT-002 | HSE-03 | Slice packet allowlist | Build S3 packet with tasks, cited ACs, tests, gate, excerpt, memory, plus a transcript field | Allowed fields render; unknown transcript field is rejected and no packet is usable |
| UT-003 | HSE-05 | Packet byte budgets stop dispatch | Build a 3,073-byte role packet and 10,241-byte slice packet | Non-zero result reports exact counts; provider runner receives zero calls |
| UT-004 | HSE-06 | Normal packet telemetry is content-free | Build a valid packet containing unique marker text in its body | JSON contains component/total counts and budgets; marker and body are absent |
| UT-005 | HSE-07, HSE-08, HSE-09 | Version-3 defaults resolve | Resolve minimal v3 config without a parallelization table | Snapshot has `assisted`, `auto`, baseline 2, ceiling 4 |
| UT-006 | HSE-08, HSE-09, HSE-11 | Invalid public config fails | Resolve modes `safe`/`full`, caps `0`/`1.5`/object, and config v2 | Each returns its specified error and produces no snapshot/effect plan |
| UT-007 | HSE-10, HSE-11 | Snapshot version is coherent | Freeze v3 then plan it; plan v1/v2 active snapshots | v3 round-trips exact policy; v1/v2 fail with `--refresh` instruction |
| UT-008 | HSE-12 | Disabled is explicit serial mode | Plan three independent slices under `disabled` | One serial writer, zero concurrent worktrees |
| UT-009 | HSE-13, HSE-14 | Empty and single-ready plans stay cheap | Plan a fully blocked DAG, then a DAG with one ready slice | First names blockers and dispatches none; second selects one integration-checkout writer |
| UT-010 | HSE-44, HSE-46 | Dirty or overlapping writers fail safely | Plan overlapping paths; execute from dirty integration checkout | Overlap serializes with exact paths; dirty baseline performs zero effects |
| UT-011 | HSE-15, HSE-19, HSE-20 | Initial writer selection is dynamic and role-scoped | Plan four compatible ready slices with read-only roles present | Exactly two implementer worktrees are selected; no read-only worktree; no odd/even binding |
| UT-012 | HSE-16, HSE-18 | Admission obeys one-step scale and cap | Feed consecutive healthy settle windows under `auto`, cap 3, and cap 1 | Active writers change 2→3→4 for auto, stop at 3, and stay serial at 1 |
| UT-013 | HSE-17 | Unproved health denies extra lanes | Feed missing, malformed, stale, CPU-pressure, memory-pressure, and disk-pressure evidence | Each denies lane 3+ without stopping the two active lanes |
| UT-014 | HSE-42 | Health output is normalized | Probe a fake host exposing marker paths, usernames, commands, and env values | Output contains only schema, enums, counts, monotonic age, and admission boolean |
| UT-015 | HSE-30 | Slice tasks remain sequential | Materialize a slice with three tasks and inspect its execution order | Task N+1 cannot start before task N gate and atomic commit checkpoint |
| UT-016 | HSE-31, HSE-32, HSE-33, HSE-34 | Author-independent role routing | Route a code slice, integrated review group, QA Plan, and QA Execute | Every proof role has a fresh identity; final implementer packet ends at handoff |

## Integration

| ID | Requirements | Behaviour | Given / When | Expected |
| --- | --- | --- | --- | --- |
| IT-001 | HSE-07, HSE-10, HSE-11 | Resolver, planner, and executor share v3 | Resolve config, freeze snapshot, plan, and start fake execution | Every reader accepts v3; no component expects v1/v2 |
| IT-002 | HSE-15, HSE-20 | Two concurrent writers get isolated checkouts | Execute two compatible ready slices | Two owned sibling worktrees and writer handles exist; integration checkout and read-only roles remain unisolated |
| IT-003 | HSE-19, HSE-45 | Verified checkpoint unlocks dependent work | Park a consumer on producer commit A, move producer to B, verify B, then continue | Consumer stays parked until B is synchronized and reverified, then resumes on B |
| IT-004 | HSE-21, HSE-48 | Heavy gates share existing leases | Two lanes request the same exclusive gate resource while a light lane is ready | One correlated gate lease runs, second waits, light work proceeds, and release occurs once |
| IT-005 | HSE-16, HSE-17, HSE-18, HSE-19 | Ready queue refills adaptively | Complete one of two lanes while two more slices become ready across health changes | Scheduler assigns next compatible slice and admits at most one extra healthy lane per window within cap |
| IT-006 | HSE-22, HSE-23 | Orca receives pointer only | Dispatch a packet containing a unique body marker through fake Orca | On-disk packet is complete; one `terminal send --text` contains pointer and no marker/body |
| IT-007 | HSE-24 | Happy lifecycle mutates once | Run create/send/set/stop/rm, Git, and lease logical operations | Fake call ledger records exactly one mutation for each planned logical operation |
| IT-008 | HSE-25 | Settle retries only inspections | Induce transient failure after each mutation and make read observations fail twice before success | Mutation counts stay one; bounded read-only inspections repeat and settle succeeds |
| IT-009 | HSE-26 | Effect identity is fully correlated | Return matching repository, path, handle, route, task, operation, commit, and lease observations | Coordinator accepts one effect and persists every identity needed for restart |
| IT-010 | HSE-28 | Proven cleanup reaches residue zero | Integrate a clean verified slice, stop its worker, release lease, and remove owned checkout/ref | All owned effects are absent and normalized residue list is empty |
| IT-011 | HSE-29 | Probe import is inert | Import installed module with call-counting fake executables on PATH | Import succeeds and every fake call count remains zero |
| IT-012 | HSE-31, HSE-32, HSE-33, HSE-34 | Proof pipeline sees correct trees | Run a two-slice fake trace through slice verification, integration, Deep Review, QA Plan, QA Execute | Slice verifier sees its commit; reviewer/QA see integrated head; no author identity is reused |
| IT-013 | HSE-01, HSE-35 | Adoption installs the hard cut | Adopt into an empty disposable project | New skill, probe, executor, resolver, templates, config example, and guidance are byte-identical; old skill path is absent |
| IT-014 | HSE-36 | Re-adoption preserves consumer ownership | Edit consumer `.my-workflow.toml` and QA profile, then re-adopt | Owned workflow files update; both consumer files remain byte-identical to their edits |
| IT-015 | HSE-37 | Offline canonical gate owns complete automation | Run `npm_config_offline=true npm run test:all` with live Orca unavailable | Schema, packets, scheduler, health, leases, fake Orca, adoption, and import lanes all pass; live Orca call count is zero |
| IT-016 | HSE-38 | QA registry distinguishes fake proof from live host | Parse affected CFG/QAS/ADP scenarios after fake-provider and adoption QA | Fake/adoption journeys cite current evidence; live Orca journey is `blocked-verify` and names upstream limitation |

## End-to-end

No permanent e2e case is added. The public surfaces are checkout-local config, CLIs, adoption, and
provider processes; integration tests discriminate them without a browser or live Orca. Durable QA
scenarios own the real-user journeys.

## Security

| ID | Requirements | Abuse case | Attempt | Expected |
| --- | --- | --- | --- | --- |
| SEC-001 | HSE-39 | Executable or effect path escapes repository ownership | Supply absolute, `..`, symlinked, missing, and non-executable provider/packet/state/worktree paths | Validation fails before subprocess or filesystem mutation; fixed argv receives no attacker text |
| SEC-002 | HSE-40 | Untrusted structured input drives an effect | Supply unknown keys, wrong types, oversized values, invalid versions, and mismatched IDs across config/snapshot/state/provider JSON | Exact schema/correlation error; next external mutation count is zero |
| SEC-003 | HSE-17, HSE-42 | Host telemetry leaks or falsely authorizes | Return raw process/env/home markers, stale time, impossible counts, and unknown enums | Markers are absent; evidence is invalid; active writer count cannot exceed two |
| SEC-004 | HSE-21, HSE-40 | Lease from another gate/run authorizes work | Reuse a lease ID with different operation, resources, worktree, or idempotency key | Gate does not start; unrelated work remains eligible; foreign lease is not released |
| SEC-005 | HSE-23 | Packet body reaches truncating terminal transport | Put a large secret-like marker in packet body and inspect fake Orca argv/stdin/log | Only short pointer appears; marker is absent from transport and diagnostics |
| SEC-006 | HSE-24, HSE-25, HSE-41 | Timeout duplicates a mutation | Make every mutating command apply its effect then return timeout/transient failure | Exactly one mutation per logical operation; only same-handle reads repeat |
| SEC-007 | HSE-26, HSE-27, HSE-47 | Reused or contradictory effect is adopted | Return wrong repo, moved handle, wrong route/task/operation/commit, malformed receipt, and conflicting Orca/Git views | Coordinator fails closed, integrates nothing, and performs no destructive cleanup |
| SEC-008 | HSE-28, HSE-43, HSE-47 | Cleanup deletes foreign or dirty state | Reuse handle/path for another slice, leave dirty files, unmerged commit, running process, live lease, or extra ref | Cleanup stops before the destructive step and reports exact unresolved residue |
| SEC-009 | HSE-46 | Dirty coordinator baseline contaminates writers | Add tracked/untracked changes before dispatch and request serial/concurrent execution | Zero writer, worktree, Orca, Git, lease, or packet-delivery effects |
| SEC-010 | HSE-35, HSE-39 | Adoption installs stale or redirected authority | Place obsolete TLC tree and a symlinked destination in disposable consumer | Adoption refuses unsafe destination; successful clean adoption contains only new byte-identical authority |
| SEC-011 | HSE-06, HSE-42 | Diagnostics expose sensitive packet or host data | Inject unique packet, terminal, env, secret, username, and absolute-home markers into every failure path | JSON/stderr contain logical IDs, enum reasons, and counts only; all markers are absent |

## Invariant Ownership

| Invariant | Owning layer | Canonical suite |
| --- | --- | --- |
| Skill hard cut and packet contract | Unit/contract | Renamed workflow-skill validator suite and `tools/shared/tests/autonomous-parallelization.test.ts` |
| Config/snapshot v3 | Unit/integration | `tools/test_workflow_config.py`, `tools/test_parallel_plan.py` |
| Dynamic admission, health, leases, lifecycle | Unit/integration | `tools/test_parallel_executor.py`, `tools/test_machine_health.py` |
| Orca pointer and exactly-once effects | Integration/security | `tools/test_orca_assisted_probe.py`, `tools/test_orca_adapter.py` |
| Adoption ownership | Integration/security | `scripts/test_adopt.py` |
| Role and QA routing | Unit/integration | `tools/shared/tests/autonomous-parallelization.test.ts`, `tools/shared/tests/qa-skills.test.ts` |
