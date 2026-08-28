# Merge-Alone Slice QA — 2026-08-27

## Session

- **Verdict:** PASS after fresh retest — resolver v2, planner, adopted validators, and adoption canary agree
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual through checkout-owned disposable Git repositories
- **Execution path:** separate adopted disposable Git repositories -> `validate_tasks.py
  --slice-contract-json` -> `workflow_config.py` -> `parallel_plan.py`; `scripts/adopt.py` -> adopted
  task/spec validators -> re-adoption and independent filesystem reload
- **Environment:** `fix/merge-alone-slices` at `933b5ed`; no browser, API, mobile, auth, server, or networked installer
- **Technical baseline:** fresh Technical Verifier PASS at `5dee2e2`, recorded at `933b5ed`; this QA session does not issue a technical verdict
- **Later review baseline:** DR1 (`cf7c43b`) and DR2 (`88a3eee`) recorded green targeted and full gates before QA Plan (`a5fa189`)
- **Closing gate:** PASS — `npm run test:all` exited 0: 116 Bun + 267 Python = 383 passed,
  0 failed, 0 skipped
- **Raw evidence:** `docs/qa/evidence/2026-08-27-merge-alone-slices/`
- **Original failure:** retained below and in `BUG-20260827-parallel-plan-rejects-workflow-v2`; the
  first QA execution at `a5fa189` failed resolver-v2-to-planner and stopped before adoption

## Matrix

| Charter / canary | Scenario | Verdict | Independent read / reload | Evidence |
| --- | --- | --- | --- | --- |
| `CH-derive-merge-alone-slices-2026-08-27` | `CFG-resolve-deep-review-cadence` | **PASS** | Resolver stdout matched independently reloaded snapshots for one, two, and no-Tasks features | `derive-validator-one.json`; `derive-validator-two.json`; `independent-initial-read.log` |
| `CH-derive-merge-alone-slices-2026-08-27` | `CFG-freeze-feature-workflow` | **PASS** | Snapshot hashes survived valid/malformed Tasks on resume and rejected refreshes; explicit refresh changed one group to two | `independent-freeze-reload.log`; `refresh-count-mismatch.stderr.log`; `refresh-malformed-tasks.stderr.log` |
| `CH-derive-merge-alone-slices-2026-08-27` | `CFG-plan-parallel-slice-dispatch` | **PASS AFTER RETEST** | Resolver version 2 independently reloaded; two planner reads were identical and matched validator membership | `retest-933b5ed/planner-resolver.json`; `retest-933b5ed/planner-output-initial.json`; `retest-933b5ed/planner-output-reload.json`; `retest-933b5ed/planner-independent-read.log` |
| `CH-adopt-merge-alone-slice-contract-2026-08-27`; `CH-validate-generated-feature-contracts-2026-08-22` | `ADP-validate-generated-feature-contracts` | **PASS AFTER RETEST** | One/two-slice and historical valid fixtures passed; named invalid fixtures failed before and after re-adoption | `retest-933b5ed/adopt-merge-one.json`; `retest-933b5ed/adopt-merge-two.json`; `retest-933b5ed/adoption-independent-read.log` |
| Adjacent canary `J-adopt-workflow` | `ADP-adopt-workflow-safely` | **PASS AFTER RETEST** | Source-identical installed surfaces and consumer sentinels survived re-adoption; source-only and external boundaries held | `retest-933b5ed/adopt-sentinels-before.sha256`; `retest-933b5ed/adopt-sentinels-after.sha256`; `retest-933b5ed/adoption-independent-read.log`; `retest-933b5ed/cleanup.log` |

## Fresh Retest at `933b5ed` — PASS

The fixed public resolver-to-planner path passed in an adopted disposable Git consumer. Resolver
stdout independently matched the frozen version 2 snapshot, and two planner invocations were
byte-identical. The planner exposed the validator's exact `T1`/`T2` → `A` and `T3`/`T4` → `B`
membership, excluded remediation `T2R1` and `TDR1`, and retained deterministic serial behavior for
the disabled-mode fixture. Installed parallel guidance still requires tasks within a slice to run
sequentially and preserves per-task gates, Technical Verifier, frozen Deep Review groups, final QA,
and the final full gate.

The previously halted adoption charter and the complete 2026-08-22 generated-contract charter also
passed in a separate adopted disposable Git consumer. The adopted task validator accepted one- and
two-slice merge-alone documents, nested phase tasks, and diagram-plus-breakdown tasks. It rejected
missing outcome/gate/reason, non-exact `Yes`, zero/multiple/unknown membership, orphan closure,
duplicate closure, and a future-phase dependency with the required identity. The adopted spec
validator accepted the annotated acceptance-criteria heading and rejected the missing-`SHALL`
criterion at line 25. Re-adoption preserved the two-slice result and both historical refusal paths.

The fresh adoption canary passed. Installed validator, task template, and parallelization reference
bytes matched the active checkout. Consumer-owned `.my-workflow.toml`, `docs/qa/README.md`, and
`tools/ad-index.py` sentinels remained byte-identical. Source-pack-only Bun assets and external
security skill trees stayed absent; adoption printed the explicit installer command but did not
invoke it.

Eleven relevant refusal probes were attempted and clean: nine merge-alone closure/membership
families, future-phase dependency, and missing `SHALL`. Comprehension/language passed through named
task, slice, field, phase, and line diagnostics. Recovery/trust passed after re-adoption and
independent reload. Local CLI duration stayed bounded to seconds. Accessibility is not applicable
to this repository's nonvisual public surface.

## Charter Debriefs

### Original derive merge-alone slices run — FAIL

The resolver and validator legs behaved as promised. One five-task outcome resolved to `[[1]]`, two
independent outcomes resolved to `[[1, 2]]`, and missing Tasks resolved to `[[1]]`. Independent JSON
reloads matched stdout and snapshot content. Initial mismatch, zero, and negative assertions wrote
no snapshot. Resume ignored changed valid and malformed Tasks and retained frozen bytes. Explicit
refresh adopted the valid two-slice contract; mismatch and malformed refreshes preserved those bytes.

The true downstream end state failed. The same valid two-slice document produced the expected
validator contract and resolver snapshot, but `parallel_plan.py` exited 1 before emitting a plan.
Independent read showed the resolver wrote snapshot version 2 while the planner accepts only version
1. Filed `BUG-20260827-parallel-plan-rejects-workflow-v2`.

### Original adopt merge-alone slice contract run — UNTESTED

Not started. The session stopped at the confirmed planner defect as required by the QA fix loop.
No adopted-validator or re-adoption verdict is claimed. `ADP-validate-generated-feature-contracts`
remains `untested`; `ADP-adopt-workflow-safely` retains its prior pass without fresh confirmation.

## Edge Probes and Lenses

Nine relevant edge families were selected for the durable result:

- Count mismatch, zero, and negative assertions: rejected before snapshot creation, with exact
  derived/bounds diagnostics.
- Missing outcome, gate, and reason: each rejected with slice `A` and the missing field named.
- Non-exact `Yes`: rejected with slice `A` and exact lowercase `yes` named.
- Zero and multiple membership: rejected with task `T1` named.
- Unknown membership: rejected with slice `Z` named.
- Orphan closure: rejected with slice `B` named.
- Duplicate closure: rejected with duplicate slice `A` named.
- Changed or malformed Tasks during resume: frozen JSON and bytes survived reload.
- Rejected mismatch and malformed refresh: prior version 2 snapshot bytes survived reload.

Comprehension and trust passed for validator/resolver diagnostics and independent hashes. Recovery
passed for frozen resume and rejected refresh. Speed was bounded to local CLI calls. Accessibility
and UI language lenses do not apply because this repository has no visual or interactive UI. The
planner trust/completion lens failed at its public snapshot boundary.

## Original Cleanup and Residue

The exact disposable runtime directory was removed after the defect stop; `cleanup.log` confirms it
no longer exists. Before cleanup, the derivation target contained only expected untracked feature
fixtures/snapshots and the untouched adoption target was clean. The source checkout contains only
this cycle's expected durable QA report, bug, and four scenario updates; raw evidence remains under
the ignored evidence directory. No network, installer, browser, server, commit, push, merge, release,
or operator-setting mutation occurred.

The requested closing `npm run test:all` gate passed at checkout head `a5fa189`: 116 Bun tests and
267 Python tests, 383 total, with 0 failures and 0 skips. Raw output and exit code are in
`closing-test-all.log` and `closing-test-all.exit`. This is a green automated gate, not a fresh
Technical Verifier verdict and not evidence that the public resolver-to-planner journey works.
One gate-owned symlink-sentinel fixture remained after its safety test; its exact birth time and
shape tied it to this run, so the disposable sibling root was removed. `closing-residue.log` confirms
zero remaining gate-named sibling paths, zero QA runtime, and `host-sentinel-compare.log` confirms
the host-boundary sentinel stayed byte-identical.

## Limitations

This source pack has no browser, API, mobile, auth, server, or production runtime. The declared
CLI/manual adapter can observe command exits, JSON, snapshot bytes, planned membership, adopted
bytes, Git state, and filesystem residue. Networked external-security installation remains outside
this authorized QA packet.

## Fresh Retest Cleanup and Residue

Both exact disposable Git consumer roots under `retest-933b5ed/runtime` were removed after capture.
The checkout-owned boundary sentinel remained byte-identical. Raw evidence records no network use,
external-installer invocation, remote mutation, or operator-setting change. Original failure logs
remain untouched beside the new `retest-933b5ed/` evidence. Source status after the walk contained
only planned durable QA bookkeeping; no disposable target remained. The closing `npm run test:all`
exited 0 with 116 Bun and 267 Python checks, 383 total, 0 failures, and 0 skips. Its one current-run
gate-owned sibling sentinel root was moved to Trash after exact path and content inspection; all
current gate-named residue and the QA runtime are absent. Exact output, count calculation, exit code,
and residue confirmation are in `retest-933b5ed/closing-*`.
