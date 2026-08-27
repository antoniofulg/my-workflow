# BUG-20260827-luna-low-worker-commits-before-green-gate

- **Status:** closed — fixed and retest passed
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** A worker executes each task's canonical gate successfully before creating exactly
  one atomic task commit, then reports the completed checkpoint.
- **Observed:** The frozen Luna-low Slice B worker ran the B:T15 gate, observed one failure, still
  created `92fd6dd feat(pilot): add batch CLI`, then changed the implementation and created an extra
  `e75f856 fix(pilot): preserve batch CLI newline`. Final gate passed 9/9, but B:T15 no longer had
  one green-gated atomic task commit.
- **Adapter:** Installed Orca `1.4.190` direct CLI/manual worktree and terminal interfaces
- **Exact path:** same Luna-low B worker after exact A:T7 sync -> affected gate 7/7 -> B:T12 task
  commit -> B:T15 failing gate -> prohibited task commit -> corrective commit -> final gate 9/9
- **Evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-7/b-turns.jsonl`

## Impact

The coordinator correctly rejected the final effect because commit count and subjects differed
from the packet. Implementation bytes and final tests were green, but task atomicity and the
gate-before-commit invariant were not. Technical Verification, deterministic feature integration,
grouped Deep Review, and final persona QA therefore could not begin.

The other worker turns, overlap, parking, producer sync, and exact same-handle continuation passed.
All four worker sends returned successful receipts. This symptom does not reopen or close the
automatic Orca lifecycle bug and makes no automatic compatibility claim.

## Required fix and retest

Change the assisted-pilot implementer route from Luna low to a route capable of reliably following
the gate/commit contract, then run a fresh complete E2E walk. A passing retest must keep exactly one
green-gated commit per task, run fresh per-slice Technical Verifiers, integrate without conflict,
complete grouped Deep Review and final CLI persona QA, and prove exact zero-residue cleanup.

## Retest 8

Fix commit `40f2d55` raised the frozen worker route to Luna medium. Retest 8 produced exactly one
green-gated commit for each of A:T1, A:T7, A:T8, B:T9, B:T12, and B:T15; no corrective commit or
post-red-gate commit occurred. The route-specific task-integrity defect is closed. A separate mini
CLI framing defect later stopped grouped review and does not reopen this worker-process bug.
