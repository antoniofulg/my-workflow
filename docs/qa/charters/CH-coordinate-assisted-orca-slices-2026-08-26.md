# CH-coordinate-assisted-orca-slices-2026-08-26

- **Date:** 2026-08-26
- **Time-box:** 60 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-execute-parallel-slices`](../journeys/J-execute-parallel-slices.md), assisted flow
- **Tour:** Explicit authorization, parked dependency, same-terminal continuation, and exact cleanup
- **Public entry point:** [assisted Orca policy](../../../.agents/skills/autonomous/references/parallelization.md) with the feature's frozen [`workflow.json`](../../../.specs/features/host-agnostic-slice-parallelization/workflow.json)
- **Declared adapter:** CLI/manual through installed Orca direct worktree and terminal interfaces; frozen implementer route `codex` / `gpt-5.6-luna` / `low`
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Adjacent canaries:** `QAS-qualify-orca-host-before-parallel-use`; `CFG-fallback-unproven-parallel-execution`; `QAS-clean-owned-parallel-slice-pilot`

## Mission

Walk E2E-001 in a checkout-owned disposable Git fixture after explicit human authorization. Start B
after the early verified `A:T1` dependency, park its sole worker at the later exact
`B:T12 depends_on A:T7` checkpoint, synchronize the exact `A:T7` producer commit, rerun B's affected
gate, continue through the same terminal, integrate in deterministic slice order, and remove only
the exact clean integrated owned resources.

## Expected observable

The automatic adapter remains unsupported and records no compatibility PASS. Each assisted terminal
renders `source=screen` with the exact frozen provider/model/effort tuple before prompt delivery;
A missing, error, or `agent_prompt_stalled` send receipt is reconciled once on the same handle through
the bounded machine-only marker/state proof, never retried or replaced;
A and B overlap; B runs sequentially through its first unmet dependency; its clean comment records
slice B, completed-through task, next `B:T12`, dependency `A:T7`, and current HEAD; the exact A
producer commit enters B; the declared affected gate passes; the same terminal or its sole
reacquired handle completes B; all task, Technical Verifier, grouped deep-review, final QA, and full
gate stages remain ordered; worktree, Git path, exact branch ref, and terminal absence are proven.

## Planned probes

- Record explicit assisted authorization, source checkout HEAD, disposable root, frozen route, and
  before-state Orca/Git inventories. Do not send a prompt until the terminal screen proves
  `codex` / `gpt-5.6-luna` / `low` exactly.
- Use one direct two-step Orca worktree plus its promoted startup shell per ready slice. Record immutable
  repository/worktree/instance/path/gitdir/branch/`pre_head` ownership separately from mutable
  `current_head` and worker handle state.
- Use a disposable task graph where B starts only after verified `A:T1`, then reaches the exact
  `B:T12 depends_on A:T7` boundary. Require one worker for B and no task polling while parked.
- Reconcile the parked comment against `tasks.md` and Git. After verified `A:T7`, synchronize its
  exact producer commit, run the affected gate declared by the fixture, and follow up the same B
  terminal; if its handle is stale, reacquire only the sole handle from B's owned worktree.
- For every route, task, or follow-up packet, record the exact handle/turn phase, pre-head,
  task/comment/gate state, and expected marker; send once. On an ambiguous receipt, inspect only the
  same handle every 250 ms for at most 300000 ms and accept only one complete marker/HEAD/status/
  commit/gate/comment effect, otherwise serialize for exact recovery.
- Record atomic task commits and scoped gates, one Technical Verifier per code-changing slice, the
  frozen `grouped.3` deep-review cadence, final QA, deterministic slice integration, and one final
  full gate. The packet reports the exact HEAD `d28cbf1` full gate already passed with Vitest
  `112/112` and all Python lanes; that is baseline evidence, not the pilot's final-tree gate.
- Before cleanup, prove the immutable receipt still matches Orca and Git, the worktree is clean with
  no Git operation in progress, branch tip equals `current_head`, and the slice commit is integrated.
  Stop the exact current handle, detach the worktree when necessary, safely delete the exact owned
  branch and prove ref absence, then remove only by full worktree id and independently prove
  worktree/path/branch-ref/terminal absence and zero owned residue.
- As a read-only adjacent check, preserve the prior host-preflight evidence and do not infer a
  candidate compatibility result: this charter authorizes no `preflight --canary`, and the current
  packet contains no durable candidate-canary receipt. Do not treat assisted success as automatic
  compatibility.
- Preserve unrelated worktrees, terminals, branches, ignored evidence, and deep-review artifacts.
  Any dirty, missing, ambiguous, conflicting, mismatched, failed-gate, or unproven-cleanup state
  stops that lane and hands it to serial recovery without automatic resolution or broad deletion.

## Criterion disposition

- `AST-01` — `QAS-coordinate-assisted-orca-slices`: explicit authorization, automatic unsupported,
  no PASS receipt, and exact rendered frozen-route proof before prompt or task edit.
- `AST-02`, `AST-03` — `QAS-coordinate-assisted-orca-slices`: B starts after verified `A:T1`, runs
  sequentially, and parks once at `B:T12 depends_on A:T7` with the full checkpoint identity.
- `AST-04`, `AST-05` — `QAS-coordinate-assisted-orca-slices`: exact `A:T7` commit sync, affected gate,
  same-terminal continuation, and fail-closed serial recovery for ambiguity or failure.
- `AST-06`, `SEC-008` — `QAS-coordinate-assisted-orca-slices`: deterministic integration, exact
  ownership revalidation, safe branch deletion, and worktree/path/ref/terminal absence.
- `AST-07` — `QAS-coordinate-assisted-orca-slices`: atomic task commits, scoped gates, per-slice
  Technical Verification, frozen grouped review, final QA, and final full gate remain intact.
- `ORC-01` through `ORC-07` — adjacent `QAS-qualify-orca-host-before-parallel-use`: preserve the
  prior read-only host-preflight evidence; no candidate canary is authorized or evidenced by this
  charter.
- `HST-01` through `HST-04`, `MAE-01` through `MAE-04`, and `SEC-001` through `SEC-007` — unchanged
  internal or previously mapped public promises; assisted E2E-001 does not alter their behavior.

## QA Execute handoff

Fresh Verifier must invoke canonical `qa-execute`, read `docs/qa/README.md`, and use its declared
CLI/manual adapter in one checkout-owned disposable Git fixture. Prerequisites are explicit human
authorization for assisted Orca effects, reachable installed Orca direct worktree/terminal
interfaces, a fixture encoding `B` start after `A:T1` and `B:T12 depends_on A:T7`, and an exact
fixture-owned affected gate. Save raw evidence below
`docs/qa/evidence/2026-08-26-assisted-orca-slices/`, write a new durable report under
`docs/qa/reports/`, and update `QAS-coordinate-assisted-orca-slices` from `untested` only from the
observed result.

Limitations: no automatic `preflight --canary` is authorized and no candidate compatibility result is
claimed by this charter. Existing automatic lifecycle and completed-cleanup scenarios retain their
current statuses unless their own public contracts are independently walked. Any product defect goes
to an Implementer, ends this session, and requires a fresh Verifier after the fix.
