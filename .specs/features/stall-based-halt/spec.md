# Stall-Based Halt Specification

## Problem Statement

A run that still reproduces a blocker after the review cap halts and ends, even when every attempt
is making progress and the next fix is already named. The operator always answers "continue", so the
halt costs a full unattended run and buys nothing. The cap counts review rounds, which is the wrong
quantity: rounds bound how often a reviewer produces new findings, while what actually needs
bounding is a remediation loop that stops converging.

## Goals

- [ ] A post-cap blocker whose set of failing tests reaches a new minimum each attempt never halts a run.
- [ ] A remediation loop that fails to shrink its set of failing tests `stall_attempts` times in a
      row halts and reports, with `stall_attempts` defaulting to 3.
- [ ] The threshold is consumer-owned in `.my-workflow.toml` and validated by the resolver.
- [ ] Remote authorization is unchanged: push, pull request, merge and deploy still each need an
      explicit go-ahead.

## Out of Scope

| Feature | Reason |
| --- | --- |
| The `≤3` Technical Verifier and `≤2` deep-review round caps | They bound review, which already converges. Only the post-cap remediation halt is miscalibrated. |
| Freezing `stall_attempts` in `.specs/features/<feature>/workflow.json` | The snapshot exists to keep routing stable mid-feature. A halt threshold is an operator preference that should take effect on the next attempt, not at the next feature. |
| Relaxing any remote-action authorization | Orthogonal to this halt, and the reason the run is safe to leave unattended. |
| Automatic detection of a wrong fix strategy | A shrinking set of failing tests is progress by definition here; judging fix quality is the reviewer's job, not the halt's. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| What a "failure signature" is | The sorted set of failing test identifiers for the scoped gate's failing command, normalized to drop timings, absolute paths, and line numbers. The assertion message is reported as diagnosis and is never compared | The set is the one part a real fix shrinks. Line numbers shift on any edit, and an assertion message churns with flaky ordering and with embedded PIDs, ports and object addresses, so comparing either would make every attempt look like progress and the bound would never fire | y |
| What counts as progress | Only a set of failing tests strictly smaller than the fewest seen so far in this remediation loop; anything else is a stalled attempt | Comparing against the previous attempt alone lets a flaky test drive the counter in both directions: it buys a round by failing then passing again, and it erases a real fix by flipping the other way. A running minimum only decreases, so returning to a count already reached is not progress and the loop is finite by construction. The accepted cost is a halt report for a person to read, not a broken tree | y |
| `stall_attempts = 0` | Means unbounded: never halt for a stall | Gives the operator the "never stop on a blocker" behaviour without a second key. One key, one meaning per value | y |
| Where the threshold lives | `.my-workflow.toml`, table `[remediation]`, key `stall_attempts` | `CONFIG_KEYS` in the resolver is a strict allowlist, so an unknown table already fails the run. The key has to be taught to the resolver either way | y |
| A run halted for a stall is ended, not paused | Matches the existing `autonomous` halt semantics | A paused run stays stopped until someone looks, which is the cost the operator was avoiding | y |

**Open questions:** none — all resolved or logged above.

---

## User Stories

### P1: A diagnosed blocker does not end the run ⭐ MVP

**User Story**: As an operator of an unattended run, I want remediation to continue while each
attempt changes the failure, so that a blocker with a known root cause does not cost me a run.

**Why P1**: This is the reported failure. Everything else is the bound that makes it safe.

**Acceptance Criteria**:

1. The escalation rule in `docs/guidelines/REVIEW-ROUNDS.md` SHALL bound post-cap remediation by
   consecutive stalled attempts and SHALL NOT bound it by review-round count.
2. WHEN an attempt's set of failing tests is strictly smaller than the fewest seen so far in this remediation loop THEN the run SHALL start another remediation attempt without new human authorization.
3. WHILE post-cap remediation is running the run SHALL run the scoped gate after each attempt and
   record that attempt's failure signature.
4. The run SHALL NOT open a new review round while remediating post-cap.

**Independent Test**: `REVIEW-ROUNDS.md` and `autonomous/SKILL.md` state the progress rule and no
longer halt on an open blocker alone; the doc-contract suite asserts both.

---

### P1: A stuck loop still stops ⭐ MVP

**User Story**: As an operator, I want a run that stops converging to halt and report, so that
removing the old halt does not let an agent burn hours on one failure.

**Why P1**: Without this the change is an unbounded loop, which is the failure the cap existed to
prevent.

**Acceptance Criteria**:

1. WHEN `stall_attempts` consecutive attempts fail to shrink the set of failing tests below the fewest seen so far THEN the run SHALL halt, write the halt report, and merge nothing.
2. WHERE `stall_attempts` is `0` the run SHALL NOT halt for a stall.
3. The halt report SHALL name the repeated failure signature, the number of attempts, and every fix
   that was tried.
4. IF the scoped gate cannot be made to run THEN the run SHALL halt regardless of the stall count.

**Independent Test**: the halt conditions in `autonomous/SKILL.md` name the stall count and the
`0` case; the doc-contract suite asserts them.

---

### P1: The threshold is consumer-owned ⭐ MVP

**User Story**: As a project owner, I want the stall threshold in `.my-workflow.toml`, so that a
project can pick its own tolerance without editing a vendored guideline.

**Why P1**: The resolver's `CONFIG_KEYS` allowlist rejects an unknown table, so a `[remediation]`
table is a hard failure until the resolver learns it.

**Acceptance Criteria**:

1. WHERE `.my-workflow.toml` declares `[remediation] stall_attempts` the resolver SHALL resolve that
   value and report it in its resolved output.
2. WHERE `.my-workflow.toml` declares no `[remediation]` table the resolver SHALL resolve
   `stall_attempts` to `3`.
3. IF `stall_attempts` is not an integer, or is negative, THEN the resolver SHALL exit non-zero with
   a message naming `remediation.stall_attempts`.
4. IF the `[remediation]` table contains any key other than `stall_attempts` THEN the resolver SHALL
   exit non-zero and name the unknown key.
5. The resolver SHALL NOT write `stall_attempts` into
   `.specs/features/<feature>/workflow.json`.

**Independent Test**: run the resolver against a fixture project with and without the table, and
with each invalid value; assert exit codes and resolved output.

---

## Edge Cases

- IF `.my-workflow.toml` is absent THEN the resolver SHALL resolve `stall_attempts` to `3`.
- IF `[remediation]` is present but empty THEN the resolver SHALL resolve `stall_attempts` to `3`.
- WHEN two consecutive attempts fail with the same test identifiers but different assertion messages
  THEN the run SHALL treat the second attempt as stalled.
- WHEN an attempt makes the gate green THEN post-cap remediation SHALL end and the stall count
  SHALL reset.
- IF a blocker remains open and the run halts for a stall THEN the run SHALL NOT push, open a pull
  request, merge, or deploy.

---

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| HALT-01 | P1: A diagnosed blocker does not end the run | Execute | Done |
| HALT-02 | P1: A diagnosed blocker does not end the run | Execute | Done |
| HALT-03 | P1: A stuck loop still stops | Execute | Done |
| HALT-04 | P1: A stuck loop still stops | Execute | Done |
| HALT-05 | P1: The threshold is consumer-owned | Execute | Done |
| HALT-06 | P1: The threshold is consumer-owned | Execute | Done |

**Coverage:** 6 total, 6 mapped to tasks, 0 unmapped

---

## Success Criteria

- [ ] A run reaching a new minimum failing count each attempt never asks for authorization to continue.
- [ ] A run that stalls `stall_attempts` times halts with a report naming the repeated signature.
- [ ] `python3 .agents/skills/workflow-config/scripts/workflow_config.py` accepts `[remediation]`
      and rejects every malformed value with a message naming the key.
- [ ] `npx vitest run --dir tools` and `python3 tools/test_workflow_config.py` pass.
