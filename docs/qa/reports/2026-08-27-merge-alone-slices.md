# Merge-Alone Slice QA — 2026-08-27

## Session

- **Verdict:** FAIL — public resolver output is incompatible with the public planner
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual through checkout-owned disposable Git repositories
- **Execution path:** adopted disposable repository -> `validate_tasks.py --slice-contract-json` ->
  `workflow_config.py` initial/resume/refresh -> `parallel_plan.py`; adoption charter stopped before
  its separate target walk when the product defect was confirmed
- **Environment:** `fix/merge-alone-slices` at `a5fa189`; no browser, API, mobile, auth, server, or networked installer
- **Technical baseline:** historical Technical Verifier PASS at `802aea9`; this session does not issue a fresh technical verdict
- **Later review baseline:** DR1 (`cf7c43b`) and DR2 (`88a3eee`) recorded green targeted and full gates before QA Plan (`a5fa189`)
- **Closing gate:** PASS — `npm run test:all` exited 0: 116 Bun + 267 Python = 383 passed,
  0 failed, 0 skipped
- **Raw evidence:** `docs/qa/evidence/2026-08-27-merge-alone-slices/`

## Matrix

| Charter / canary | Scenario | Verdict | Independent read / reload | Evidence |
| --- | --- | --- | --- | --- |
| `CH-derive-merge-alone-slices-2026-08-27` | `CFG-resolve-deep-review-cadence` | **PASS** | Resolver stdout matched independently reloaded snapshots for one, two, and no-Tasks features | `derive-validator-one.json`; `derive-validator-two.json`; `independent-initial-read.log` |
| `CH-derive-merge-alone-slices-2026-08-27` | `CFG-freeze-feature-workflow` | **PASS** | Snapshot hashes survived valid/malformed Tasks on resume and rejected refreshes; explicit refresh changed one group to two | `independent-freeze-reload.log`; `refresh-count-mismatch.stderr.log`; `refresh-malformed-tasks.stderr.log` |
| `CH-derive-merge-alone-slices-2026-08-27` | `CFG-plan-parallel-slice-dispatch` | **FAIL** | Resolver snapshot independently reloads as version 2; planner requires version 1 and exits before membership output | `planner-resolve.json`; `defect-reproduction.stderr.log`; `defect-independent-read.log` |
| `CH-adopt-merge-alone-slice-contract-2026-08-27` | `ADP-validate-generated-feature-contracts` | **UNTESTED** | Not reached: `qa-execute` fix-loop requires session close after confirmed product defect | This report; `cleanup.log` |
| Adjacent canary `J-adopt-workflow` | `ADP-adopt-workflow-safely` | **NOT RE-WALKED; PRIOR PASS RETAINED** | No fresh claim; prior current evidence remains in its scenario record | `docs/qa/reports/2026-08-27-bun-test-runner.md` |

## Charter Debriefs

### Derive merge-alone slices — FAIL

The resolver and validator legs behaved as promised. One five-task outcome resolved to `[[1]]`, two
independent outcomes resolved to `[[1, 2]]`, and missing Tasks resolved to `[[1]]`. Independent JSON
reloads matched stdout and snapshot content. Initial mismatch, zero, and negative assertions wrote
no snapshot. Resume ignored changed valid and malformed Tasks and retained frozen bytes. Explicit
refresh adopted the valid two-slice contract; mismatch and malformed refreshes preserved those bytes.

The true downstream end state failed. The same valid two-slice document produced the expected
validator contract and resolver snapshot, but `parallel_plan.py` exited 1 before emitting a plan.
Independent read showed the resolver wrote snapshot version 2 while the planner accepts only version
1. Filed `BUG-20260827-parallel-plan-rejects-workflow-v2`.

### Adopt merge-alone slice contract — UNTESTED

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

## Cleanup and Residue

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
