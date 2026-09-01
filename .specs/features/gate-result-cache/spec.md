# Gate Result Cache Specification

## Problem Statement

`docs/guidelines/GATES.md` already contracts cached gate evidence — fingerprint keyed on tree
content, scope binding, log-backed records — and closes with "This cache is optional tooling for the
consuming project." No such tooling exists, so every gate runs from scratch even when the tree that
last passed it is byte-identical. A slice that gates, commits, verifies, and gates again pays the
full suite each time for a tree nothing changed.

## Out of Scope

| Capability | Reason |
| --- | --- |
| Caching failing gate results as skippable | A red gate is diagnosed, never assumed. Failing records exist only to point at their log. |
| Toolchain or environment in the fingerprint | The tree is the contracted key. A runtime upgrade needs an explicit cache drop; the record carries no proof of interpreter version. |
| Record eviction or size bounds | The cache is checkout-local and disposable; deleting the directory is the eviction policy. |
| Sharing records across checkouts or CI | `docs/guidelines/BRANCHING.md` gives each checkout its own runtime; a shared cache would let one checkout vouch for another. |
| Partial or per-test caching | The contract is a whole gate result, not a test selector. |

## Assumptions & Open Questions

| Decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Evidence authority of a passing record | Admissible at every gate scope, readiness full gate included | The fingerprint proves the identical tree already passed the identical gate; refusing it would keep the largest re-run. | yes, human decision 2026-09-01 |
| Fingerprint material | Git tree object of the whole non-ignored worktree, plus gate label and exact command | One `git write-tree` over a temporary index is exact, ignores nothing the gate can read, and matches "records key on tree content". | yes, recorded as `AD-018` |
| Fingerprint failure | Run the gate, cache nothing | The cache may never block or fake a gate; fail-open loses speed, fail-closed loses the gate. | yes, this spec |
| Cache location | `.gate-cache/` in the checkout, ignored by Git | Checkout-local, disposable, invisible to the tree it fingerprints. | yes, this spec |
| Wiring depth | Tool only in this delivery | The branch was cut from a base 158 commits stale. `implement.md` no longer exists, `package.json` already discovers `scripts/`, and adoption was rewritten as Bun-native layers, so the wiring must be redesigned against the current structure. | yes, human decision 2026-09-01 |

**Open questions:** none.

## User Stories

### P1: Reuse a gate result the tree has already earned

**User Story**: As a workflow operator, I want a gate that passed on this exact tree to be reused
instead of re-run, so that repeated gating inside a slice costs its suite once.

**Why P1**: This is the capability `GATES.md` contracts and the product lacks.

**Acceptance Criteria**:

1. WHEN no passing record matches gate, command, and tree fingerprint THEN the tool SHALL execute
   the command, stream its output to both stdout and a log file, and exit with the command's exit
   status.
2. WHEN a passing record matches gate, command, and tree fingerprint THEN the tool SHALL exit 0
   without executing the command.
3. WHEN an executed command completes THEN the tool SHALL write a record carrying gate label,
   command, tree object, fingerprint, status, exit code, completion time, and log path.
4. WHEN a stored record's status is failing THEN the tool SHALL retain it for diagnosis and SHALL
   execute the command again rather than short-circuit on it.
5. WHEN a tracked, staged, or untracked-unignored file changes THEN the fingerprint SHALL differ
   from the one computed before that change.
6. WHEN only the commit graph changes and worktree content does not THEN the fingerprint SHALL be
   unchanged.
7. WHEN two invocations differ only by gate label or by command THEN their fingerprints SHALL differ.
8. IF the fingerprint cannot be computed THEN the tool SHALL execute the command and SHALL neither
   read nor write a record.
9. WHEN any invocation ends THEN the tool SHALL print one evidence line naming the gate, the
   fingerprint, and the log path.

**Independent Test**: In a scratch repository, run a counting command twice unchanged, then after a
tracked edit, after an untracked-file edit, after a commit alone, under a changed gate label, after
a failing run, and with `git` unavailable; assert execution counts and record contents.

## Edge Cases

- IF the command is absent after `--` THEN the tool SHALL exit non-zero with a usage error and cache
  nothing.
- WHEN a record exists whose log file is missing THEN the tool SHALL treat the record as absent.
- WHEN a stored record is unreadable or carries an unexpected schema version THEN the tool SHALL
  treat it as absent rather than fail the gate.
- WHEN a record does not parse completely, for any reason including a concurrent or interrupted
  write, THEN the tool SHALL treat it as absent, run the gate, and SHALL NOT report a hit.
- WHEN the command is interrupted THEN no passing record SHALL be written.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| GRC-01 | P1: cache miss executes and records | Implementation | implemented |
| GRC-02 | P1: cache hit skips execution | Implementation | implemented |
| GRC-03 | P1: fingerprint keys on tree, gate, and command | Implementation | implemented |
| GRC-04 | P1: failing records diagnose, never short-circuit | Implementation | implemented |
| GRC-05 | P1: fail-open when no fingerprint is available | Implementation | implemented |

**Coverage:** 5 total, 5 mapped to P1, 0 unmapped.

## Success Criteria

- [ ] A second identical gate invocation on an unchanged tree does not execute the command.
- [ ] Any content edit, gate label change, or command change forces execution.
- [ ] A commit with no content change does not force execution.
- [ ] A failing gate is never skipped.
- [ ] A broken or absent Git tree costs the cache, never the gate.
- [ ] `GATES.md` names the invocation that produces a record.
