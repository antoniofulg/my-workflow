# QA report — parallel slice executor terminal QA

- **Date:** 2026-08-25
- **Scope:** terminal consolidation of configuration, zero-effect fallback, convergence, real Orca/Codex execution, and owned-cleanup QA
- **Adapter:** CLI/manual through `parallel_plan.py`, `parallel_execute.py`, `qa_parallel_pilot.py`, `review_convergence.py`, Orca CLI, and read-only Git inspection
- **Environment:** checkout HEAD `cdfa6c0`; Orca `1.4.188` with `orchestration.contract.v1`; Codex `0.149.1` in the R15 external walk
- **Preflight gate:** `rtk npm run test:all` — exit `0`; 9 Vitest files / 110 tests and all discovered Python suites passed, as recorded by the R19 command log item 2
- **Raw evidence:** `docs/qa/evidence/2026-08-25-parallel-slice-executor-r14/`, `r15/`, `r16/`, `r17/`, `r18/`, and `r19/`
- **Consolidation rule:** no worker or lifecycle command was rerun for this report; terminal outcomes use existing durable command logs and evidence
- **Repository limitation:** no configured runtime, port, database, or consumer resource provider; no resource-isolation claim is made

## Overall verdict

**BLOCKED-VERIFY — external Orca/Codex lifecycle boundary.** Configuration, fallback, and
convergence contracts pass. Product parsing, identity, terminal-ownership, recovery, and provider-
preflight root causes have independent technical fixes and validation records. The positive
resource-free Orca/Codex two-lane journey is not a product failure: Orca `1.4.188` revoked the
Dispatch after `agent_prompt_stalled`, Codex `0.149.1` later completed externally, and the exact
public recovery-stop replay returned `alreadySettled` while the owned terminal remained live and
writable. The product correctly refuses release, retry, and cleanup. R14 user-takeover residue and
older `identity_unproven` residue remain separate; no cleanup claim is made.

## Terminal matrix

| Charter | Scenario | Terminal status | Evidence and command/source | Outcome |
| --- | --- | --- | --- | --- |
| `CH-configure-parallel-slice-dispatch-2026-08-24` | `CFG-freeze-feature-workflow` | **PASS** | 2026-08-24 resolver session; R19 `setup.json`, `resource-plan.json`, `resource-status.json` | Frozen mode and optional provider boundary remain stable; resource-bearing work serializes before mutation. |
| `CH-configure-parallel-slice-dispatch-2026-08-24` | `CFG-plan-parallel-slice-dispatch` | **PASS** | 2026-08-24 planner session; R19 `parallel_plan.py` command and `resource-plan.json` | Deterministic ready/blocked/checkpoint policy and sequential delivery stages preserved. |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `CFG-fallback-unproven-parallel-execution` | **PASS** | R18 command record and evidence; R19 command log items 5–9 | Disabled, unsupported, and missing-provider fallback produces zero effects and zero residue. |
| `CH-confirm-parallel-execution-fallback-2026-08-24` | `QAS-bound-verifier-remediation-per-blocker` | **PASS** | R19 command log items 10–12; `convergence-replays.json`, `convergence-threshold.json`, `ledger-bounds.json` | Independent closed fingerprints do not increment; third failed remediation halts at count 3. |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-run-resource-free-parallel-orca-slices` | **BLOCKED-VERIFY** | R14 `session.md`; R15 `start.json` / `terminal-watchdog.json`; R17 `r15-resume-1.json` / `r15-resume-2.json` / `r15-orca-reads.json` | External Orca/Codex stop boundary leaves exact owned live terminal; product correctly refuses release/retry. Not pass, fail, or untested. |
| `CH-execute-parallel-slices-2026-08-24` | `QAS-clean-owned-parallel-slice-pilot` | **BLOCKED-VERIFY** | R14 `lifecycle-and-abort.json`; R15 `lifecycle-and-residue.json`; R17 `verdict.json` | Lifecycle never authorized; normal/repeat cleanup not run. No cleanup or zero-residue claim. |

## Pass evidence

### Fallback

R18 command record: one disabled `start` plus one fresh-process `status` returned
`disabled-mode`/empty actions and zero new worktree, runtime, or Orca effects. One unsupported
`parallel_plan`, one hidden-capability `start`, and one fresh-process `status` returned
`unsupported-adapter`/empty actions with the same zero-effect result.

R19 command log items 5–9: two ready `Resources: runtime` lanes with frozen provider `null`
returned `missing-resource-provider` on both `start` calls with `actions: []`; both fresh-process
`status` calls returned `state: null`. Read-only inventory stayed Orca Runs `12 -> 12` and workers
`151 -> 151`; no lane worktree, runtime receipt, Task, Dispatch, terminal, or lease appeared.
Diagnostic abort and repeat returned `residual_paths: []`, with the second call idempotent. These
counts come from `resource-effects.json` and `resource-residue.json`, not inference.

### Fingerprint convergence

R19 command log items 10–12 read the checkout ledger at 21 total / 21 closed / 0 open / 0 halted,
maximum failed-remediation count 2, before and after. On a disposable ledger, the public
`review_convergence.py` command replayed two closed fingerprints without incrementing counts. A
distinct fingerprint reached open counts 1 and 2, halted at failed-remediation count 3, and stayed
at 3 after a later failure and successful replay. Evidence: `convergence-replays.json`,
`convergence-threshold.json`, and `ledger-bounds.json`.

## External blocked lifecycle

R14's fresh fixture reached one A/T1 worktree, Run, Task, Dispatch, terminal, and owned terminal
resource before Orca returned `agent_prompt_blocked`; its watchdog saw `codex-update-prompt` and
diagnostic abort refused `worker-may-be-live`. R15's independent walk used Codex `0.149.1`; Orca
returned `agent_prompt_stalled`, revoked the Dispatch, and left one exact terminal live/writable.
The later external Codex completion is not a `worker_done` receipt accepted by the executor.

R17's public `resume` issued one exact recovery-stop. Orca returned `alreadySettled: true` and
`state: failed`; a second public replay returned the same result with `mutation_replayed: true`.
The exact terminal remained connected/writable, so release and the single retry-of the same Run/Task
were unsafe. Observed R15 counts, from `counts.json`, were 2 ready lanes, 1 started lane, 1
worktree, 1 Run, 1 Task, 1 Dispatch, 1 terminal, 0 accepted `worker_done`, 0 lifecycle chains,
and 1 retained source/derived/runtime/Orca residue set. Observed R17 counts, from `counts.json`,
were 1 stop request, 1 replay, terminal still live/writable, 0 release requests, 0 retry
Dispatches, and incomplete lifecycle.

This is `blocked-verify` external verification debt. It is not a new product bug, and it does not
authorize manual `worker-stop`, release, acknowledgement, reset, force-delete, or cleanup.

## Residue and cleanup boundary

- **R14 user-takeover residue:** separate prompt-bound fixture, live terminal/resource, and A/T1 worktree; diagnostic cleanup refused.
- **R15/R17 recovery residue:** exact Run `run_32d5fc6df479`, Task `task_156a23407567`, Dispatch `ctx_d9be8d183c51`, terminal `term_d339f23b-d3dd-4990-bdfa-c1c447420bc5`, and resource `wtr_3de59cfde75f`; stop replay did not close terminal.
- **Older R8–R11 `identity_unproven` residue:** separate retained Run `run_71671ad17a77`, Task `task_78fcfca161b8`, Dispatch `ctx_5f619d0f6298`, terminal `term_2dcb9465-d91c-4260-baa3-b92859412439`, and resource `wtr_2882893be650`; preserved independently.
- **R19 effect-free fixture:** only disposable provider-free fixture was diagnostically removed; `resource-residue.json` records `residual_paths: []` on first and repeat abort. This is not completed-pilot cleanup evidence.

No normal cleanup, repeated completed-lifecycle cleanup, or zero-owned-residue claim is recorded for
the real worker journey. Retained fixtures remain outside QA cleanup authority.

## Product-fix and bug disposition

`BUG-20260824-parallel-executor-worker-start-fallback-leaks-worktree` remains **open** with live
retest `blocked-verify`: product root causes are technically fixed, but the defined real two-lane
condition lacks durable completion evidence. `BUG-20260824-parallel-pilot-cleanup-allows-incomplete-lifecycle`
remains **open** with live retest `blocked-verify`: fail-closed refusal is verified, but no completed
lifecycle reached normal cleanup. Neither bug is closed.

The canonical scenario and bug records retain historical R8–R19 evidence links while removing
obsolete repeated interim narratives.

## Documentation verification

Fresh documentation-only checks for this consolidation completed after all edits:

- `rtk git diff --check` — exit `0` (no output).
- `rtk python3` QA scenario frontmatter/schema check — `checked_scenarios=26 errors=0`.
- `rtk python3` Markdown relative-link check — `checked_files=15 links=85 missing=0`.
- Markdownlint executables were not installed (`markdownlint`, `markdownlint-cli2`, and
  `pymarkdown` unresolved); no repository Markdown linter is available.
- No product, test, spec-validation, worker, commit, push, or merge action was performed in this
  consolidation.
