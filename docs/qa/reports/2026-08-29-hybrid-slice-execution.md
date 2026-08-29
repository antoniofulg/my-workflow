# Hybrid slice execution — QA Execute

- **Date:** 2026-08-29
- **Reviewed HEAD:** `89e8b31c95a76f6f1b6a2c96c355be0b42e7b763`
- **Personas:** Workflow adopter; Workflow operator
- **Adapter:** CLI/manual through installed resolver, planner, executor, packet builder, assisted
  probe, convergence CLI, adoption CLI, and filesystem readback
- **Environment:** checkout-local disposable Git consumer with fake Orca, Git, and resource
  providers on `PATH`; Python bytecode disabled so adapter did not dirty consumer
- **Raw evidence:** `docs/qa/evidence/2026-08-29-hybrid-slice-execution/summary.json` and
  `docs/qa/evidence/2026-08-29-hybrid-slice-execution/commands.json`
- **Live Orca:** not invoked

## Gate

Opening command:

```text
npm_config_offline=true npm run test:all
```

Exit `0`: 8/8 Vitest files and 114/114 tests passed; adoption and all 15 Python suites also
exited `0`. Closing run appears below.

## Matrix

| Charter | Scenarios | Verdict | Independent readback |
| --- | --- | --- | --- |
| `CH-adopt-hybrid-slice-workflow-2026-08-29` | `ADP-adopt-workflow-safely` | pass | Reloaded installed files, hashes, telemetry, probe import ledger, and package manifest from fresh processes |
| `CH-configure-assisted-slice-execution-2026-08-29` | `CFG-freeze-feature-workflow`; `CFG-plan-parallel-slice-dispatch`; `CFG-fallback-unproven-parallel-execution` | pass | Reloaded v3 snapshots and repeated byte-equivalent plans; inspected Git worktree inventory and fake-provider ledgers |
| `CH-coordinate-assisted-slices-offline-2026-08-29` | `QAS-coordinate-assisted-slices-offline`; `QAS-bound-verifier-remediation-per-blocker` | pass | Reloaded packet, state, mutation ledgers, cleanup residue, and both convergence generations |
| Preserved live-host limitations | `QAS-run-resource-free-parallel-orca-slices`; `QAS-clean-owned-parallel-slice-pilot` | blocked-verify | Current offline summary plus retained live-host evidence; no live action performed |

Walk result: 3/3 charters terminal; 6 scenarios pass and 2 remain `blocked-verify`. Closing gate
found `BUG-20260829-final-qa-pass-conflicts-with-adoption-gate`, so feature QA is not closed.

## Adoption and packet walk

`python3 scripts/adopt.py <disposable-consumer>` installed 65 selected hybrid managed files
byte-for-byte. Installed tree contained `workflow-spec-driven`, autonomous scheduler, workflow
resolver, role templates, pointer probe, pilot, config example, and guidelines; obsolete
`.agents/skills/tlc-spec-driven` was absent. Installed `NOTICE.md` matched source attribution and
CC BY 4.0 notice.

Fresh-process import with call-counting fake `orca` made 0 Orca calls. Re-adoption preserved exact
SHA-256 bytes of consumer `.my-workflow.toml` and `docs/qa/README.md`. Target was disposed.

Installed packet builder emitted a 257-byte slice packet plus a 4-byte role packet and reloaded
telemetry with `within_budget: true`. A 3,073-byte role failed with `role_budget_exceeded`, recorded
exact byte count, and produced no replacement packet. Telemetry contained no packet body.
`npm pack --dry-run --json` listed 406 files and included probe plus skill notice; no publication
occurred.

## Configuration and execution walk

Resolver stdout and reloaded snapshots agreed on schema v3, `assisted`, `auto`, baseline 2,
ceiling 4, routes, and cadence. Public CLI results:

- One ready slice: `serial-integration`, `worktree: false`, `worktree_id: integration`; registered
  worktree count stayed 1.
- Two compatible ready slices: `concurrent-writers`, 2 lanes; inventory reached exactly 3
  worktrees including integration checkout.
- No ready slice: 0 lanes with `in-progress:T0` and `dependency-incomplete:T0`.
- Overlapping paths: serial result with `write-conflict:T1:T2:src/shared.py:src/shared.py`.
- Disabled mode: `disabled-mode`, 0 actions.
- Exclusive-resource contention: T1 and unrelated light T3 remained eligible while T2 was blocked
  by `resource-conflict`; denied lease produced `resource-acquire-failed` after exactly 1 physical
  acquire and no worker mutation for denied lane.
- Version 2, mode `always`, and worker cap `0`: each exited `2`, wrote no snapshot, and named the
  refresh/type boundary.
- Live machine-health collection normalized unavailable readings to `unknown`, `admit_next:
  false`; it did not admit lane 3. Malformed/non-finite injection remains technical evidence
  because public health CLI accepts no evidence-input option.

All 3 executor-created disposable writer worktrees were removed. Fresh readback found only the
consumer integration worktree.

## Assisted probe, recovery, and cleanup

Dispatch persisted complete packet and issued exactly 1 pointer send. Terminal transport contained
pointer and 0 occurrences of `SECRET_PACKET_BODY`; public diagnostics emitted `<path>` rather than
an absolute home path. `inspect` reloaded full correlation and changed state from `pointer_sent` to
`settled`.

Seven transient logical mutations were each invoked twice at public dispatch boundary: `create`,
`send`, `set`, `stop`, `rm`, Git mutation, and lease mutation. Physical ledgers contained exactly
1 call each, total 7; second attempt performed only reconciliation and every durable attempt count
remained 1.

Cleanup induced a post-effect stop timeout. First command failed closed. Second reconciled same
stop, released lease once, removed worktree once, preserved unrelated canary, and returned
`residue: []`. Physical cleanup mutations: exactly 1 stop, 1 lease release, and 1 worktree removal.

Diagnostics and telemetry contained 0 occurrences of packet body, credential-shaped sample values,
or `/Users/antoniofulg`.

## Convergence walk

Public convergence CLI recorded same fingerprint three times and halted generation 1 at exactly 3
failures. Explicit repository-relative authorization appended generation 2 with local count 0 while
generation 1 remained field-for-field unchanged. Missing-authorization resume was rejected without
changing ledger bytes. Fresh independent PASS plus green-gate evidence closed generation 2;
generation 1 remained halted in history.

## Edge probes

9/9 passed:

1. schema v2 rejected;
2. unknown parallelization mode rejected;
3. zero worker cap rejected;
4. dependency-blocked DAG dispatched no lane;
5. overlapping writes serialized;
6. disabled mode emitted zero effects;
7. denied exclusive lease occurred once while light work remained planner-eligible;
8. transient mutations were not reissued;
9. missing resume authorization left convergence bytes unchanged.

## Experience lenses

- **Comprehension:** installed docs and JSON decisions named assisted, serial, conflict, dependency,
  and refusal reasons without source inspection.
- **Recovery:** transient response, repeat dispatch, convergence resume, and cleanup replay kept one
  physical mutation and preserved history.
- **Trust:** independent reloads confirmed hashes, receipt correlation, redaction, and zero residue.
- **Speed:** two compatible slices became active together; one ready slice avoided worktree setup.
- **Accessibility:** no browser or visual surface exists; CLI stdout was structured JSON and every
  failure returned machine-readable stderr/exit status.
- **Language:** stable English machine tokens matched documented public contract; no localized UI
  exists.

## Limitations

Real Orca/Codex two-lane lifecycle and completed-pilot cleanup remain `blocked-verify`. External
host previously returned `agent_prompt_stalled`, revoked Dispatch, and left its exact terminal
live/writable. Pointer workaround protects packets from still-unverified
`orca terminal send --text` transport, but offline fakes cannot prove host lifecycle. This session
made 0 live Orca calls and did not stop or clean retained host evidence.

No browser, API, mobile, auth, server, database, or production runtime exists. External
security-skill installation and publication were not authorized and were not run.

## Cleanup and closing gate

Disposable consumer, fake providers, packet/state fixtures, and disposable worktrees were removed.
Source retained only planned durable QA report/scenario/task edits; raw evidence remains ignored.
`git worktree list --porcelain` reported exactly 2 project worktrees: operator main and feature.

Closing command:

```text
npm_config_offline=true npm run test:all
```

Exit `1`. Vitest remained green at 8/8 files and 114/114 tests. Python adoption gate then failed at
`scripts/test_adopt.py:541`:

```text
assert "qa_status: untested" in adoption
AssertionError
```

This conflicts with the fresh independent `pass` verdict recorded by this session. The live-Orca
`blocked-verify` assertion remains correct and must not be weakened. Filed
[`BUG-20260829-final-qa-pass-conflicts-with-adoption-gate`](../bugs/BUG-20260829-final-qa-pass-conflicts-with-adoption-gate.md).
QA Execute stops here; a fresh Verifier must resume the adoption charter plus adjacent package and
configuration canaries after an Implementer fixes the owning assertion.
