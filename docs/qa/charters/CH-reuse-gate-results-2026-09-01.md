# CH-reuse-gate-results-2026-09-01

- **Date:** 2026-09-01
- **Scope:** `3ce7a2e..7bb7331` for `gate-result-cache`
- **Time-box:** 45 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-project-gates`](../journeys/J-run-project-gates.md)
- **Tour:** Cache-hit, invalidation, and scope-binding tour
- **Public entry point:** `python3 tools/gate_cache.py run --gate <label> -- <command>`, reached from [`docs/guidelines/GATES.md`](../../guidelines/GATES.md)
- **Adapter candidate:** CLI/manual through the checkout-local disposable Git repository declared in [`docs/qa/README.md`](../README.md)
- **Scenarios:** [`QAS-reuse-gate-result-for-unchanged-tree`](../scenarios/QAS-reuse-gate-result-for-unchanged-tree.md)
- **Adjacent canary:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md) / [`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md), planned by [`CH-adopt-gate-cache-canary-2026-09-01`](CH-adopt-gate-cache-canary-2026-09-01.md)

## Mission

Experience the cache as an operator who gates repeatedly inside one slice. In a checkout-local
disposable Git repository, drive a counting stand-in gate through the public wrapper and read every
verdict from the counter, the record file, and the log — never from elapsed time. Establish a hit,
then attack it: content edits of all three kinds, a content-free commit, a changed label, a changed
command. Finish by reading the four wired documents an operator is actually told to follow.

## Expected observable

A second identical invocation on an identical tree exits 0 without advancing the counter and prints
a hit line naming gate, fingerprint and log path. A tracked edit, a staged-but-uncommitted change,
an untracked unignored file, a different `--gate` label, and a different command each produce a
different fingerprint and advance the counter. A commit that changes no worktree content leaves the
fingerprint and the counter alone. `GATES.md`, `autonomous`, `implement.md` and `qa-execute` each
name the cached invocation, and a `scoped` record cannot be presented as a full-gate result because
`--gate full` fingerprints differently.

## Criterion disposition ledger

| Criterion | Class | Canonical disposition |
| --- | --- | --- |
| GRC-01 | Public CLI | `J-run-project-gates` → `QAS-reuse-gate-result-for-unchanged-tree`; a miss executes, streams to stdout and a log, exits with the command's status, and writes a record. |
| GRC-02 | Public CLI | `J-run-project-gates` → `QAS-reuse-gate-result-for-unchanged-tree`; a matching passing record exits 0 without executing. |
| GRC-03 | Public CLI | `J-run-project-gates` → `QAS-reuse-gate-result-for-unchanged-tree`; tracked/staged/untracked content, gate label, and command each change the fingerprint; a content-free commit does not. |
| GRC-04 | Public CLI | Refusal half — `QAS-run-the-gate-when-the-cache-cannot-vouch`, charter `CH-refuse-cache-authority-over-gates-2026-09-01`. |
| GRC-05 | Public CLI | Refusal half — `QAS-run-the-gate-when-the-cache-cannot-vouch`, charter `CH-refuse-cache-authority-over-gates-2026-09-01`. |
| GRC-06 (P2 AC1–AC3) | Docs-as-interface | `J-run-project-gates` step 6 → `QAS-reuse-gate-result-for-unchanged-tree`; the guideline, `autonomous` readiness row, `implement.md` gate step, and `qa-execute` close step each name the cached invocation. |
| GRC-06 (P2 AC4) | Public adoption CLI | `J-adopt-workflow` → `ADP-adopt-workflow-safely`, charter `CH-adopt-gate-cache-canary-2026-09-01`. |
| `AD-021` evidence authority | Public CLI + docs | Walked as scope binding in step 7: the fingerprint, not a judgement call, is what stops a `scoped` record from covering a full gate. |
| `AD-022` fingerprint material | Internal keying rule | No separate user promise. The operator observes only hit-versus-execute, which GRC-03 already covers; the hashing construction is a technical-verification surface. |
| Atomic record write (`os.replace`) | Internal durability rule | No separate user promise. A torn record is observable only mid-write; the CLI/manual adapter cannot induce the race. Technical-verification surface. |

## Planned probes

- Create a disposable Git repository owned by this checkout, with a counting gate script that
  appends to a file **outside** the repository and exits 0.
- Run the wrapper twice unchanged; independently read the counter, `.gate-cache/<fingerprint>.json`,
  and the log before accepting the hit.
- Per invalidation leg — tracked edit, `git add` without commit, new untracked unignored file —
  run once, record the fingerprint and counter, then revert before the next leg.
- Commit with no content change (`--allow-empty`, or a commit whose tree equals the previous one)
  and require an unchanged fingerprint and counter.
- Re-run the same command under a second `--gate` label, then the first label with an altered
  command; require two additional distinct record files.
- Read the four wired documents in the source checkout and quote the invocation each names.
- Attempt the scope-binding claim explicitly: same tree, same command, `--gate scoped` then
  `--gate full`; require the second to execute.

## Scenario state and limitations

`QAS-reuse-gate-result-for-unchanged-tree` is a new promise at `qa_status: untested` with no linked
bug. No prior evidence exists for this journey. This repository's own gate is `bun run test:all` and
nothing in it shells out to `rg`; a gate failure from outside the cache is still recorded by the
tool, so clear `.gate-cache/` before reading a later leg. This repository has no browser,
API, mobile, auth, server, or production runtime. Use only the profile's CLI/manual adapter and
checkout-owned disposable repositories; install nothing, contact no remote, and do not run the
networked external-security installer. Do not treat this repository's own `.gate-cache/` contents as
evidence — the walk owns its disposable repository.

## QA Execute handoff

A distinct fresh Verifier session with `phase: qa-execute` must use the canonical `qa-execute` skill
and the CLI/manual adapter from `docs/qa/README.md`. Walk this charter alongside
`CH-refuse-cache-authority-over-gates-2026-09-01` and `CH-adopt-gate-cache-canary-2026-09-01`, store
ignored raw evidence under `docs/qa/evidence/2026-09-01-gate-result-cache/`, write a new dated
durable report, and update scenario verdicts only after independent observable reads. No product
fix, remote action, or release action belongs in that session.
