# Host Adapter Compatibility QA — 2026-08-26

## Session

- **Charter:** [`CH-verify-host-adapter-compatibility-2026-08-26`](../charters/CH-verify-host-adapter-compatibility-2026-08-26.md)
- **Persona:** Workflow operator
- **Adapter:** Checkout-local CLI/manual
- **Environment:** Active feature checkout with installed Orca `1.4.188`; no Maestri executable installed
- **Exact path:** Public `parallel_plan.py` and `parallel_execute.py preflight|start|resume|status`; manual inspection of installed parallelization policy and emitted/local compatibility data
- **Production-parity limitation:** This repository distributes a workflow and has no server, browser, API, mobile, auth, or production runtime. Candidate Orca `--canary`, live workers/worktrees, Maestri floors/agents, and external-project mutations are not authorized.
- **Evidence:** `docs/qa/evidence/2026-08-26-host-adapter-compatibility/`
- **Recorded pre-execution gate:** Technical validation records `npm_config_offline=true npm run test:all` PASS at exit 0: 110 Vitest passed, all Python lanes passed, and external Git-worktree/fixture-sibling deltas were zero.
- **Final gate:** PASS after fix-loop retest at `cd1886f`: `npm_config_offline=true npm run test:all` exited `0`; prior two failures remain recorded below.

## Scenario matrix

| Scenario | Charter leg | Expected | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- | --- |
| `CFG-plan-parallel-slice-dispatch` | Schema-v2 plan, schema-v1 rejection, unchanged delivery policy | Current schema only; scheduler and all delivery gates preserved | pass | Fresh v2/v1 processes plus installed-policy line inspection | `cli-results.json`; `session.md` |
| `CFG-fallback-unproven-parallel-execution` | Disabled `start`/`resume` and status | Serial fallback before adapter, runtime, host, or Git effects | pass | Fresh status, fixture state/cache path, Git and Orca inventories | `cli-results.json`; `residue-after-charter.json` |
| `QAS-qualify-orca-host-before-parallel-use` | Explicit and automatic installed-Orca preflight | `1.4.188` is known-incompatible; no Run, Task, worker, or worktree delta | untested overall; installed leg pass | Both preflights returned exact known-incompatible result and zero residue; candidate canary not authorized | `cli-results.json`; `residue-after-charter.json` |
| `QAS-reject-unverifiable-maestri-host` | Explicit Maestri and auto-in-Maestri-context preflight | Unsupported machine contract; no cross-fallback, floor, agent, or worktree delta | pass with limitation | Both returned `adapter-unavailable`; Maestri-context auto did not return installed-Orca result; Git/Orca deltas zero | `cli-results.json`; `session.md` |
| Adjacent canary: `QAS-run-resource-free-parallel-orca-slices` | Read-only status and policy inspection only | Existing real-worker boundary remains `blocked-verify`; no live execution | blocked-verify preserved | Scenario/status re-read from a fresh process; live execution remained prohibited | `session.md` |
| Fix-loop adjacent canary: `QAS-run-bounded-parallel-deep-review` | Formerly flaky normal and retry exact-occupancy cases | Exact bounded overlap and retry occupancy are deterministic | pass | Owning tests passed together; closing full gate passed after durable artifact edits | `retest-after-cd1886f/results.json`; `retest-after-cd1886f/session.md` |

## Probe results

Ten planned public/manual probes completed:

- schema v2 accepted and the otherwise identical v1 rejected before host effects;
- disabled `start`, `resume`, and fresh `status` returned `disabled-mode`, empty actions, and null state;
- explicit and auto Orca preflight returned `unsupported`, `known-incompatible-version:1.4.188`, cache `false`, and cleanup `not-run`;
- explicit Maestri and Maestri-context `auto` returned `unsupported: adapter-unavailable`; the latter did not cross to installed Orca;
- installed policy retained sequential slice tasks, checkpoint invalidation, Technical Verifier, deep-review, final QA, full gate, and serial fallback;
- emitted diagnostics and absent local cache contained no credential-shaped key path.

No `preflight --canary`, worker, Run/Task creation, Git worktree creation, Maestri floor/agent action,
external-project mutation, network install, or public cleanup command ran.

## Residue and redaction

Charter baseline and post-walk inventories matched: Git worktrees `6 -> 6`, Orca Runs `14 -> 14`,
bound-Run Tasks `1 -> 1`, workers `162 -> 162`, Orca worktrees `19 -> 19`, and terminals `15 -> 15`.
The fixture retained one checkout, no lane root, and no runtime/cache file, then was moved to system
Trash after a clean-status check. Direct Maestri floor/agent inventory was unavailable because no
Maestri executable exists; this is the named adapter limitation.

Both final-gate attempts also had zero delta in every listed inventory and in eight pre-existing
pilot sibling residues. See `final-gate.json`.

## Debrief

Host-adapter charter behavior passed on every reachable current-host leg. Orca positive candidate
compatibility remains `untested`, and the existing real Orca execution/cleanup scenarios remain
`blocked-verify`, as required.

Cycle cannot close because the declared full gate failed twice in scheduling-sensitive exact-peak
tests. Attempt 1: expected `6`, observed `5`; its isolated test passed. Attempt 2: expected `3`,
observed `2` in the retry peak case. Both failures stayed below the configured cap and therefore do
not disprove the prior public bounded-overlap scenario, but they make the package gate unreliable.
The new deduplicated defect is
[`BUG-20260826-deep-review-peak-bound-gate-flakes`](../bugs/BUG-20260826-deep-review-peak-bound-gate-flakes.md).

**Original cycle verdict: FAIL.** The defect was handed to an Implementer and fixed by `ae1b7d0`
plus `cd1886f`; the original failure evidence above remains unchanged.

## Fix-loop retest — `ae1b7d0` + `cd1886f`

A fresh Verifier resumed the affected host-adapter charter after
`.specs/features/parallel-deep-review/validation.md` recorded PASS. The checkout-local CLI/manual
walk re-passed schema-v2 planning, schema-v1 rejection, disabled `start`/`resume`/fresh `status`,
installed Orca `1.4.188` rejection, unavailable Maestri rejection without Orca cross-fallback,
installed-policy preservation, redaction, and absent compatibility state.

The bounded Deep Review adjacent canary ran the two formerly flaky owning tests together: exit `0`,
`2/2` passed in `2.207s`. The final declared gate then passed at exit `0`: Vitest `8/8` files and
`110/110` tests passed, and every package-discovered Python suite passed.

Fresh before/after inventories were identical: Git worktrees `6 -> 6`, Orca Runs `14 -> 14`,
bound-Run Tasks `1 -> 1`, workers `164 -> 164`, Orca worktrees `19 -> 19`, terminals `14 -> 14`,
project pilot residues `0 -> 0`, temp pilot residues `0 -> 0`, and focused Deep Review residues
`0 -> 0`. Evidence: `docs/qa/evidence/2026-08-26-host-adapter-compatibility/retest-after-cd1886f/`.

Candidate Orca positive qualification remains `untested`: installed runtime is still `1.4.188`, no
candidate version exists, and `preflight --canary` remained prohibited. Real Orca worker and
completed-pilot cleanup scenarios remain `blocked-verify`.

**Current overall verdict: PASS with the recorded candidate-Orca limitation.**
