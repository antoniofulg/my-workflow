# CH-refuse-cache-authority-over-gates-2026-09-01

- **Date:** 2026-09-01
- **Scope:** `3ce7a2e..7bb7331` for `gate-result-cache`
- **Time-box:** 40 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-project-gates`](../journeys/J-run-project-gates.md)
- **Tour:** Hostile-record and fail-open tour
- **Public entry point:** `python3 tools/gate_cache.py run --gate <label> -- <command>`; the record and log files under `<root>/.gate-cache/`
- **Adapter candidate:** CLI/manual through the checkout-local disposable Git repository declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** [`QAS-run-the-gate-when-the-cache-cannot-vouch`](../scenarios/QAS-run-the-gate-when-the-cache-cannot-vouch.md)
- **Adjacent canary:** [`J-run-project-gates`](../journeys/J-run-project-gates.md) reuse tour, planned by [`CH-reuse-gate-results-2026-09-01`](CH-reuse-gate-results-2026-09-01.md) — after every refusal leg, confirm an honest hit is still reachable.

## Mission

Take the operator's side against the cache. Every leg here damages, removes, or starves the cache and
then asks one question: did the operator still get the gate's own answer? This is the highest-risk
tour of the cycle — an earlier build of this tool exited non-zero on a record that was valid JSON but
not an object, which means the cache blocked the gate instead of running it. Walk it as a refusal
tour, not a happy path with negatives appended.

## Expected observable

In every leg the gate command executes and the process exits with the command's own status. No leg
produces a traceback, and no leg produces a non-zero exit that the gate command did not itself
produce. A failing run keeps its record and log for diagnosis and never short-circuits a later
identical invocation. With no obtainable tree object the gate still runs and nothing is recorded. An
invocation with no command after `--` refuses with a usage error and writes nothing.

## Criterion disposition ledger

| Criterion | Class | Canonical disposition |
| --- | --- | --- |
| GRC-04 | Public CLI | `J-run-project-gates` step 8 → `QAS-run-the-gate-when-the-cache-cannot-vouch`; a failing record is retained for diagnosis and re-executes. |
| GRC-05 | Public CLI | `J-run-project-gates` step 10 → `QAS-run-the-gate-when-the-cache-cannot-vouch`; no fingerprint means run and record nothing. |
| Edge: unreadable record | Public CLI | Step 9(a) — a truncated record is absent, never an error. |
| Edge: non-object JSON record | Public CLI | Step 9(b) — the regression this tour exists for; `[]` or a bare string must cost a re-run, never the gate. |
| Edge: unexpected schema version | Public CLI | Step 9(c) — treated as absent. |
| Edge: record whose log is missing | Public CLI | Step 9(d) — treated as absent. |
| Edge: missing command after `--` | Public CLI | Step 11 — usage error, nothing cached. |
| Edge: interrupted command | Public CLI, partially reachable | Attempt one interrupt of a long-running gate and confirm no passing record appears. If the adapter cannot deliver the signal deterministically, leave the leg unwalked and say so; do not simulate it. |
| Concurrent/torn write | Internal durability rule | No separate user promise reachable here; the CLI/manual adapter cannot induce the mid-write race. Technical-verification surface. |

## Planned probes

- Reuse the disposable Git repository pattern from the reuse charter, with both a passing and a
  failing variant of the counting gate.
- Failing leg: run the failing gate, capture the exit status and the record's `status`; run it again
  and require the counter to advance and the earlier log to remain readable.
- Damaged-record legs, each starting from a freshly earned passing record and each mutating the
  record file **by hand**: truncate mid-object; overwrite with `[]`; overwrite with a bare JSON
  string; bump the version field to an unexpected value; delete the log the record names. After each,
  run the identical invocation and capture stdout, stderr, and the exit status.
- Starved-fingerprint legs: invoke with `--root` pointing at a directory that is not a Git
  repository, and invoke with `git` removed from `PATH`. Require the command to run and the cache
  directory to gain nothing.
- Usage leg: invoke with `--` and no following command; require a non-zero usage refusal and an
  unchanged cache directory.
- After the last refusal leg, repeat one clean run-then-rerun pair to prove the cache still earns an
  honest hit rather than having been left permanently disabled.

## Scenario state and limitations

`QAS-run-the-gate-when-the-cache-cannot-vouch` is a new promise at `qa_status: untested` with no
linked bug. Any traceback, or any non-zero exit not produced by the gate command itself, is a product
defect: hand it to an Implementer, close the session, and require a fresh Verifier after the fix.
Record files must be damaged by hand because the tool only ever writes well-formed records. This
repository's own gate is `bun run test:all` and nothing in it shells out to `rg`. This repository has no
browser, API, mobile, auth, server, or production runtime. Install nothing and contact no remote.

## QA Execute handoff

A distinct fresh Verifier session with `phase: qa-execute` must use the canonical `qa-execute` skill
and the CLI/manual adapter from `docs/qa/README.md`. Walk this charter with
`CH-reuse-gate-results-2026-09-01` and `CH-adopt-gate-cache-canary-2026-09-01`, store ignored raw
evidence under `docs/qa/evidence/2026-09-01-gate-result-cache/`, and write a new dated durable report.
Capture the exact stdout, stderr, and exit status of every refusal leg; a leg without a captured exit
status is not walked. No product fix belongs in that session.
