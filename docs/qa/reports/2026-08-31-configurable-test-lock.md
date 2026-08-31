# Configurable Test Lock — QA Execute

**Date:** 2026-08-31
**Candidate:** `fc2ab02`
**Adapter:** CLI/manual through `scripts/adopt.py`, the installed `tools/resource_lock.py`, and independent filesystem/Git reads
**Environment:** checkout-local disposable adoption targets, Git repositories, linked worktree, and private temporary directories; Python 3; no live Orca or network
**Opening prerequisite:** technical PASS in `.specs/features/configurable-test-lock/validation.md` — 13/13 requirements, 3/3 mutants killed
**Raw evidence:** `docs/qa/evidence/2026-08-31-configurable-test-lock/`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-serialize-heavy-test-resources-2026-08-31` | `QAS-serialize-heavy-test-resources` | pass | Reloaded plans, installed bytes, manifest, statuses, process order, exits, diagnostics, sentinels, Git state, and residue. | `summary.json`; `commands.json`; command stdout/stderr captures |
| Adjacent serial-planning canary | `CFG-plan-parallel-slice-dispatch` | pass retained | Reloaded JSON and Git inventory showed one serial lane, no worktree mutation, and zero fake-Orca calls. | `serial-canary.stdout.txt`; `summary.json` |

## Session

### Adoption and installed surface

`plan` and `apply` into separate checkout-owned targets passed for `core` and `parallel`. Core
resolved only `core` and omitted `tools/resource_lock.py`; parallel resolved `core,parallel`,
installed a byte-identical wrapper, and recorded it in schema-1 `.my-workflow/adoption.json`.
Independent hashes confirmed the fixture's consumer-owned `package.json` and `Makefile` commands
were unchanged. Both `status` calls were clean. The installed module imported with exit 0 and its
public `run --help` exposed project/machine scope without invoking a command.

### Contention and concurrency

The installed wrapper serialized linked worktrees under omitted/default project scope in exact
order `first-start, first-end, second-start, second-end`. Two unrelated repositories, each with a
different `TMPDIR`, produced the same order under explicit machine scope. Separate `browser` and
`database` resources overlapped: database started and ended before browser ended.

### Failure, privacy, and recovery

The wrapper preserved child exit 17 and returned 127 for an unavailable executable. A contending
request timed out at status 75 without creating its child sentinel. Its stderr contained exactly
one 173-character JSON diagnostic with resource, scope, holder PID, hashed project identifier, and
holder start time; command and environment secrets occurred zero times.

Invalid scope, traversal resource, negative timeout, absent literal separator, absent command, and
project scope outside Git each exited 2. Independent reads found no child sentinel and no change to
the lock-directory listing. Shell metacharacters `;`, `$()`, `*`, and a spaced argument arrived as
exact argv, and no injected file appeared.

Terminating a holder wrapper did not release the resource while its child retained the inherited
descriptor; after the child ended, acquisition succeeded without deleting the lock first.
Terminating an independent waiter started no child, left the holder running, and permitted later
acquisition.

### Adjacent canary

The installed public planner resolved a disabled two-slice fixture to exactly one
`serial-integration` lane with `worktree: false`; the peer reported `disabled-mode`. Repository
porcelain and worktree inventory were byte-identical before and after, and a call-counting fake
Orca recorded zero calls.

## Edge probes and lenses

All planned probe groups passed: adoption boundary; linked-worktree project contention;
cross-project machine contention with distinct `TMPDIR`; different-resource overlap; status and
timeout; invalid input; literal argv and diagnostic privacy; holder/waiter recovery; serial canary
and cleanup.

- **Comprehension/language:** Help and JSON statuses named the scopes, required separator, wait
  state, missing executable, and refusal boundaries without source inspection.
- **Recovery/trust:** Exact process order, sentinel absence, independent Git/filesystem readback,
  inherited-lock recovery, and zero secret occurrences made the safety boundary observable.
- **Speed:** Only the same named resource queued; distinct resources demonstrably overlapped.
- **Accessibility:** No browser or visual surface exists. The documented CLI and machine-readable
  JSON were reachable through the declared adapter.

The first two harness attempts misclassified a checkout-nested directory as outside Git. Both
attempts cleaned every fixture and lock; a separately proven `GIT_CEILING_DIRECTORIES` boundary
fixed the QA fixture. The subsequent clean public walk passed. This was a harness correction, not a
product divergence.

The first closing gate also caught that this session had appended current evidence to the already
passing historical canary scenario. Its current behavior was unchanged, so that bookkeeping edit
was restored and the fresh canary observation remains only in this dated report, as required by the
history guard. No product code or test changed.

## Limitations and boundaries

No live Orca, network, browser, external security-skill installer, real consumer repository, release,
publication, or product-code mutation is authorized. Internal directory-replacement race coverage
belongs to technical validation and is not repeated here.

## Cleanup and final gate

The harness removed both adoption targets, all disposable repositories, the linked worktree, the
fake executable, and every lock file whose unique `qa31fc2` resource belonged to this session.
Fresh reads reported `fixture_root_remaining: false`, `linked_worktree_remaining: false`, and an
empty `new_lock_residue` list. The full gate intentionally exercised an unowned-sentinel refusal
and retained one exact disposable pilot directory; it was moved recoverably to
`/tmp/my-workflow-test-lock-qa-residue.qB4524/.parallel-slice-pilot-aswm13qv-parallel-slices`.
Final readback reported no QA fixture, linked-worktree, unique lock, or gate-pilot residue at its
original path. The source checkout retained only this report and the planned new-scenario status
update; raw evidence remains ignored.

Evidence accounting commands:

```text
jq 'length' docs/qa/evidence/2026-08-31-configurable-test-lock/commands.json
# 30
wc -l docs/qa/evidence/2026-08-31-configurable-test-lock/*-events.txt
# 16 total
jq '.checks.failure_privacy_recovery.wait_diagnostic_count' docs/qa/evidence/2026-08-31-configurable-test-lock/summary.json
# 1
git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | wc -l
# 18
```

Final command:

```text
npm_config_offline=true rtk bun run test:all &&
rtk bun run knowledge &&
rtk git diff --check origin/main...HEAD
```

Exit `0`. Bun reported 123 passed, 0 failed, 1,123 assertions across 8 files. All 18 tracked Python
suites exited zero, including adoption `ok (65 tests)`, resource lock `ok (6 tests)`, and assisted
probe `24/24 passed`. Knowledge reported 0 errors and 36 existing gap warnings. Diff check exited
zero. Raw output: `final-gate.txt`; final cleanup: `residue-check.txt`; accounting:
`accounting.txt`.

**Verdict:** pass. No product defect was found or filed.
