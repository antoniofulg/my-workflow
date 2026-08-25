# QA report — parallel slice executor

- **Date:** 2026-08-24
- **Scope:** public parallel executor, Orca lifecycle, serial fallback, and convergence ledger
- **Adapter:** CLI/manual through `parallel_execute.py`, real local Orca `orchestration.contract.v1`, planner/config CLIs, and convergence CLI
- **Environment:** checkout-local disposable Git repositories; source `18a3c9cce0699712119c1874aba9f8fc4da7e6b0`
- **Preflight gate:** `npm run test:all` — pass (110 Vitest; all discovered Python suites passed)
- **Raw evidence:** `docs/qa/evidence/2026-08-24-parallel-slice-executor/`
- **Limitation:** this repository has no product runtime, port allocator, database, or configured consumer resource provider; no isolation claim is made for those resources.

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | fail | Valid dry-run reached Orca, but worker start fell back after creating a hidden partial worktree/Run/Task; no concurrent workers existed | `docs/qa/evidence/2026-08-24-parallel-slice-executor/orca-pilot/`; `BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | fail | Normal cleanup accepted an incomplete lifecycle with zero terminal receipts and removed the fixture | `docs/qa/evidence/2026-08-24-parallel-slice-executor/orca-pilot/`; `BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle` |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-freeze-feature-workflow` | untested | Not walked: QA stopped at the first product-defect cycle after safe cleanup | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-fallback-unproven-parallel-execution` | untested | Not walked: QA stopped at the first product-defect cycle after safe cleanup | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | untested | Not walked: QA stopped at the first product-defect cycle after safe cleanup | — |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `QAS-bound-verifier-remediation-per-blocker` | untested | Not walked: QA stopped at the first product-defect cycle after safe cleanup | — |

## Debrief

The production-parity public path failed before concurrency. `start --adapter auto` created the
slice-A detached worktree and an Orca Run/Task, then returned `worker-failed` with `actions: []`;
slice B never started and the pilot Run had no worker. Public status independently exposed the
accepted worktree and pending worker action.

Normal cleanup then accepted this incomplete lifecycle despite no passing `lifecycle-check` and no
terminal read/ack/release receipt. Cleanup removed the exact disposable fixture; a second call was
idempotent and residue inspection found neither the fixture root nor derived sibling.

Per the QA fix loop, the remaining fallback and convergence charter was not executed. No workflow
or product code was changed. No runtime, port, or database isolation claim is made.
