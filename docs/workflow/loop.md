# The loop

`tlc-spec-driven` owns four phases: Specify, Design, Tasks, Execute. This pack **increments** that
loop. It does not replace it. Auto-size still holds: a one-line change gets no spec; a
multi-component feature gets full planning.

Activate `ponytail` at `full` before specify, design, issue selection, any subagent prompt, and
before writing, refactoring, fixing or reviewing code. Shortest working path. The same instinct as
“delete rather than bridge” and “no test without an invariant”. `AGENTS.md` is the imperative.

## Stages

Walk these in order. The imperative detail lives in `AGENTS.md` and the guideline named in the
last column.

| # | Stage | What it is for | Skip when | Rule |
| --- | --- | --- | --- | --- |
| 1 | **Specify / Design / Tasks** | Name the behaviour, freeze surfaces, enumerate test ids | Auto-sized skip (tiny, obvious change) | `tlc-spec-driven` |
| 2 | **Slice** | One observable behaviour plus the tests that prove it | — | `AGENTS.md` |
| 3 | **Implement** | The cheapest code that makes the slice true | — | `ponytail` |
| 4 | **Scoped gate** | Prove *this* diff, not the whole product | Escalate if the selector cannot scope it | [GATES.md](../guidelines/GATES.md) |
| 5 | **Atomic commit** | One Conventional Commit; update the current local task state first | — | `AGENTS.md` |
| 6 | **Verifier** | Do the tests prove the acceptance criteria? Mutants must die | Filed-issue path; last slice (QA session) | [REVIEW-ROUNDS.md](../guidelines/REVIEW-ROUNDS.md) |
| 7 | **QA walk** | Persona through this slice’s scenarios | No user-visible surface | [QA-SCENARIOS.md](../guidelines/QA-SCENARIOS.md) |
| 8 | **Deep-review** | Correct, safe, maintainable — blocking findings only | Last slice | [REVIEW-ROUNDS.md](../guidelines/REVIEW-ROUNDS.md) |
| 9 | **QA session** | The finished feature, as a person meets it | Feature has no user-visible change | [QA-EXECUTION.md](../guidelines/QA-EXECUTION.md) |
| 10 | **Full gate** | The product gate, once, on the final tree | — | [GATES.md](../guidelines/GATES.md) |
| 11 | **Pull request** | Human merge. Push and merge need an explicit instruction | Halt | [VERIFICATION-EVIDENCE.md](../guidelines/VERIFICATION-EVIDENCE.md) |

The **last slice is the QA session**. It writes no product code, so it gets no Verifier and no
deep-review. Per-slice walks asked “does this behaviour work?”. The session asks “does the finished
thing feel right?” — which has no answer until the last behaviour is in.

## Why slices, not “the whole feature”

Review cost explodes with diff size. Every round re-reads the whole change; every fix moves what
the next round reads. Three rounds over one behaviour is a signal about that behaviour. Twenty
over a finished feature is the size talking.

One pull request still. The slice is how much each reading has to hold.

A slice that is not observable or not complete is not a slice. Tests are never a separate task.
e2e is only for a journey nothing else already walks; a second slice in the same journey proves
itself at integration.

## Two paths

| Work | Path |
| --- | --- |
| **Feature** — a capability the product lacks | The full table above |
| **Filed issue** — already reviewed, then parked | `implement → scoped gate → one commit` |

A defect nobody filed is a feature at auto-sized depth. A “one-line fix” that opens a schema or a
design question stopped being a filed issue; say so and take the feature path.

## Seven rules that hold at every size

Copied as orientation; `AGENTS.md` is canonical:

1. The gate decides done, not self-assessment.
2. One atomic commit per task.
3. The Verifier is a different actor than the author.
4. A round contains only findings not already raised.
5. Only Blocker and Major trigger another round.
6. Stages never loop into each other (worst case: six passes, then a human).
7. Every count or measurement cites the command that produced it.

## Isolated checkouts

If the project isolates checkouts, each owns its runtime. Never `reuseExistingServer: true` across
siblings — a gate in one checkout must not silently test another’s application.
