# CH-coordinate-assisted-slices-offline-2026-08-29

- **Date:** 2026-08-29
- **Time-box:** 45 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-execute-parallel-slices`](../journeys/J-execute-parallel-slices.md)
- **Tour:** Pointer delivery, transient reconciliation, audit resume, owned cleanup, and live-host limitation
- **Public entry point:** `parallel_execute.py start|status|resume` → `orca_assisted_probe.py dispatch|inspect|cleanup`
- **Adapter candidate:** CLI/manual with checkout-local fake Orca, Git, and resource providers
- **Scenarios:** `QAS-coordinate-assisted-slices-offline`, `QAS-bound-verifier-remediation-per-blocker`
- **Preserved limitations:** `QAS-run-resource-free-parallel-orca-slices`, `QAS-clean-owned-parallel-slice-pilot`
- **Adjacent canary:** `CFG-fallback-unproven-parallel-execution`

## Mission

Use the shipped public probe and fake providers to prove pointer-only delivery, exactly-once logical
effects under transient responses, bounded same-identity reconciliation, authorized audit resume,
and owned zero-residue cleanup. Keep the separate real Orca/Codex journey untouched and
`blocked-verify`.

## Expected observable

Importing the probe performs no call. Dispatch persists the packet but fake terminal transport sees
only its short pointer. Each logical Orca, Git, or lease mutation appears once in its physical log;
transient paths reconcile through reads. Cleanup acts only on correlated owned identities and a
fresh read reports zero owned residue while an unrelated canary remains.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| HSE-22 | User-visible probe behavior. Walk `QAS-coordinate-assisted-slices-offline`; reload the persisted packet and fake transport log separately. |
| HSE-23 | User-visible transport invariant. Require the sent text to equal the pointer and search it for zero packet-body fragments. |
| HSE-24 | Internal mutation control with public count evidence. Count physical fake Orca/Git/provider calls per logical operation. |
| HSE-25 | Public recovery outcome. Induce supported transient responses and require bounded read-only reconciliation with no second mutation. |
| HSE-26 | Internal identity proof with observable refusal. Valid receipts advance; mismatched repository, worktree, handle, route, task, operation, or checkpoint do not. Technical verification owns hostile schema depth. |
| HSE-27 | Public fail-closed outcome. Malformed/stale/reused/contradictory fake observations preserve evidence and authorize no following mutation. |
| HSE-28 | User-visible cleanup. Stop/release/remove only correlated owned identities, preserve an unrelated canary, and independently reload residue zero. |
| HSE-29 | User-visible import safety. Import the installed module with call-counting fakes and compare filesystem/provider logs before and after. |
| HSE-40 | Internal schema/correlation control. QA samples public malformed-input refusals; technical validation owns exhaustive adversarial coverage. |
| HSE-41 | Internal persisted identity invariant. Independently reload state and correlate operation, repository, slice, handle, commit, worktree, and lease fields. |
| HSE-42 | Public diagnostic boundary. Search captured JSON/logs for secrets, environment values, packet bodies, terminal text, and absolute home prefixes. |
| HSE-43 | Public cleanup refusal. Incomplete ownership or release proof reports unresolved residue and performs no destructive next step. |
| HSE-47 | Public reused-identity refusal. A foreign repository/slice/operation observation authorizes neither acceptance nor cleanup. |
| HSE-49 | Public convergence CLI. Resume one disposable halted fingerprint with an explicit authorization reference and observe generation 2. |
| HSE-50 | Public audit history. Reload both generations and confirm prior failure count/halt are unchanged while only the new local count starts at zero. |
| HSE-51 | Public fail-closed CLI. Unknown/non-halted/missing-authorization/reset/reworded/new-fingerprint attempts leave disposable ledger bytes unchanged. |
| HSE-52 | Public close behavior. Only a fresh independent PASS plus green gate closes generation 2; other verdicts remain open or halt locally at three. |
| HSE-53 | Internal issue-guard invariant. Physical fake ledgers and persisted state support the one-attempt observable; technical validation owns pre-sink atomicity discrimination. |
| HSE-54 | Internal structural routing. QA observes all public dispatch/cleanup operations in the single fake ledger; structural alternate-sink rejection remains technical evidence. |
| HSE-55 | Internal restart control with public outcome. Restart from supported `in_flight`/`unknown` states and require zero new mutation plus same-identity reads. |
| HSE-56 | User-visible offline lifecycle. Happy, timeout, and cleanup paths each show one physical operation and pointer-only terminal text. |
| HSE-57 | Internal atomic persistence control. QA cites independent technical evidence; pre-sink fault injection is not a real-user public-interface walk. |

## Planned probes

1. Create checkout-local fake Orca, Git, and resource-provider executables with append-only physical
   call logs; create an unrelated worktree/path canary.
2. Import the installed probe and require zero calls and unchanged state.
3. Dispatch one complete packet through the public CLI, independently reload packet and transport
   logs, and require pointer equality plus packet-body absence.
4. Exercise happy and documented transient-response paths; compare logical operations with physical
   call counts and read-only reconciliation receipts.
5. Submit mismatched, stale, reused, contradictory, and incomplete observations through supported
   public inputs; require fail-closed JSON and no following mutation.
6. Run cleanup only after full correlated proof, repeat inspection, and require zero owned residue
   while the unrelated canary survives.
7. On a disposable convergence ledger, halt/resume generation 2, reject each bypass, and close only
   on fresh PASS plus green gate evidence.
8. Search all raw outputs for forbidden body, secret, environment, terminal-text, and home-path data.
9. Confirm the two real-Orca scenarios remain `blocked-verify`; do not run, stop, or clean any live
   Orca worker or retained host evidence.

## QA Execute handoff

Use a fresh Verifier with `qa-execute`, the CLI/manual adapter, and only checkout-local fake
providers. Record exact commands, logical/physical counts, independently reloaded evidence, and
residue under `docs/qa/evidence/2026-08-29-hybrid-slice-execution/`; write the durable report to
`docs/qa/reports/2026-08-29-hybrid-slice-execution.md`; update the two untested QAS scenarios. Keep
both live Orca scenarios `blocked-verify`. Do not run live Orca, contact a remote, or remediate a
product defect in the QA session.
