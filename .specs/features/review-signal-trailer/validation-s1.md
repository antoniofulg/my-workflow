# Validation - review-signal-trailer, slice 1 (RST-01)

**Verdict: PASS** (5/5 RST-01 acceptance criteria proven by direct execution; 1 surviving mutant on
non-AC behaviour; 2 spec-precision gaps recorded)

- Scope: RST-01 only. RST-02 (`tools/review-metrics.py`) is a later slice; its absence is not a finding.
- Checkpoint: `7cc8c02714abfd97a09d1461ed5da598c674cb5c` on `feat/review-signal-trailer`.
- Verifier is not the author. Every verdict below comes from executing
  `.agents/skills/workflow-spec-driven/scripts/check_commit.py` against a crafted message file and
  reading the process exit code directly (no pipe, no `tail`).

## Spec-anchored acceptance criteria check

### RST-01 - Durable review record

| Criterion | Spec-defined outcome | `file:line` + evidence | Result |
| --- | --- | --- | --- |
| WHEN a message carries a `Review-Signal:` trailer, validate its grammar and reject a malformed trailer with exit 1 | exit 1 on malformed | impl `.agents/skills/workflow-spec-driven/scripts/check_commit.py:68-123`, wired at `:163`; test `tools/test_tlc_validators.py:309` `assertEqual(self._exit_code(...), 1)`, `:317`, `:329`. Executed: bad tier / unknown key / missing tier / `key` without `=` all returned exit 1 | PASS |
| WHEN a message carries no trailer, accept unchanged | exit 0 | impl `check_commit.py:70-72` (`if not found: return []`); test `tools/test_tlc_validators.py:260`. Executed: body without trailer and header-only message both exit 0 | PASS |
| IF tier is other than `direct`/`batch`, THEN require `slices`, `verified`, `sensor`, `rounds`, `findings`, `fixed`, `dismissed` | exit 1 naming each missing key | impl `check_commit.py:51` (`SIGNAL_TIER_KEYS`), `:93-96`; test `tools/test_tlc_validators.py:275`. Executed: each of the 7 keys omitted in turn from a `tier=medium` trailer -> exit 1 with the matching `requires key '<k>'` error, 7/7. Bare `tier=small|large|complex` -> exit 1 listing all 7. Bare `tier=direct` and `tier=batch` -> exit 0 | PASS |
| IF `findings` != `fixed` + `dismissed`, THEN reject | exit 1 | impl `check_commit.py:114-116`; test `tools/test_tlc_validators.py:281`. Executed: `findings=5 fixed=2 dismissed=1` -> exit 1 (`findings=5 but fixed+dismissed=3`); boundary `findings=3 fixed=2 dismissed=1` -> exit 0 | PASS |
| IF `verified` > `slices`, or sensor killed > injected, THEN reject | exit 1 for both | impl `check_commit.py:117-118` and `:121-122`; tests `tools/test_tlc_validators.py:285` and `:289`. Executed: `slices=1 verified=2` -> exit 1; `sensor=5/2` -> exit 1; boundary `slices=2 verified=2`, `sensor=2/2` -> exit 0 | PASS |

### Probes the tests did not cover (verifier-authored, executed against the real script)

| Probe | Result | Reading |
| --- | --- | --- |
| `tier=` (empty value) | exit 1 - `tier '' is not one of: ...` | correct |
| `slices=` (empty value) | exit 1 - not a non-negative integer | correct |
| `sensor=` (empty value) | exit 1 - not `<killed>/<injected>` | correct |
| Trailer indented two spaces, carrying `slices=9 verified=99` | **exit 0** - invisible to `SIGNAL_RE` (`check_commit.py:50` anchors at column 0) | Not an AC failure: git's own trailer parser also ignores an indented line, so such a line is not a trailer. Recorded as a low-severity observation |
| Trailer inside a fenced block in the body | **exit 1** - validated and rejected | Divergence from git trailer semantics (git reads only the final paragraph). A docs commit quoting an example trailer would be rejected. The spec does not say where the trailer lives -> spec-precision gap, not an AC failure |
| Trailer text placed in the subject line | exit 1 - header does not match Conventional Commits; `check()` returns before the signal check | correct, though rejection is for the header reason |
| `remediation-failed=2` | exit 0 | correct (optional key) |
| `remediation-failed=abc` / `remediation-failed=` | exit 1 - not a non-negative integer | correct |
| `tier=batch findings=5 fixed=1 dismissed=1` | exit 1 | confirms present keys are still invariant-checked for `batch` |
| `tier=direct slices=1 verified=7` | exit 1 | same, for `direct` |
| `tier=batch sensor=9/1` | exit 1 | same |
| `tier=direct slices=0` | exit 1 - `slices=0; a delivery carries at least one slice` | correct |
| Two `Review-Signal:` lines | exit 1 | correct |
| Duplicate key (`tier=direct tier=batch`) | exit 1 | correct |
| `slices=-1` | exit 1 | correct |
| `sensor=1/2/3` | exit 1 | correct |
| `Review-Signal:tier=direct` (no space after colon) | exit 0 | acceptable; git tolerates it too |
| Multiple spaces / tabs between pairs | exit 0 | see Separator tolerance below |

## Gate

| Command | Real exit code | Result |
| --- | --- | --- |
| `python3 tools/test_tlc_validators.py` | `0` | `Ran 35 tests ... OK` |

**Test integrity.** `git diff --numstat main -- tools/test_tlc_validators.py` -> `92 0` (92 insertions,
**0 deletions**). `git diff main -- tools/test_tlc_validators.py \| grep -c '^-[^-]'` -> `0`. Test
count `main` 17 -> checkpoint 35 (18 added, none removed). **No pre-existing assertion was changed,
weakened, or deleted.**

## Discrimination sensor

Isolated throwaway `git worktree add --detach` at `7cc8c02`; the file was mutated only inside that
worktree and restored from a `.orig` copy between runs. `git status --porcelain` on the real checkout
was empty before and empty after; `git rev-parse HEAD` unchanged. `git stash` was never used.

**4 mutations injected, 3 killed, 1 survived.**

| # | Mutation (behaviour level) | Gate result | Verdict |
| --- | --- | --- | --- |
| M1 | `check_commit.py:115` invert `total != findings` -> `total == findings` | exit 1, 3 failures | KILLED |
| M2 | `check_commit.py:88` drop the unknown-key rejection (`elif key not in SIGNAL_KEYS:` -> `elif False:`) | exit 0, 35 tests OK | **SURVIVED** |
| M3 | `check_commit.py:51` `SIGNAL_TIER_KEYS = []` (no required keys for non-`direct` tiers) | exit 1, 1 failure | KILLED |
| M4 | `check_commit.py:117` `verified > slices` -> `verified >= slices` | exit 1, 2 failures | KILLED |

**M2 detail.** `tools/test_tlc_validators.py:297-301` builds its unknown key as `reviewer=alice`.
With the unknown-key branch removed, `reviewer` falls through to the integer check and still produces
`Review-Signal reviewer='alice' is not a non-negative integer` - exit 1, and the substring `reviewer`
is still in the error - so the test passes for the wrong reason. Confirmed directly: with the mutation,
`Review-Signal: tier=direct bogus=3` exits **0**; on the unmutated script the same message exits **1**
(`key 'bogus' is unknown`). The assertion does not discriminate the rejection it names.

Not fixed here (verifier does not modify inspected code). Ranked as a low-severity fix task: the
unknown-key rejection is defence-in-depth for RST-02's reader, not itself an RST-01 acceptance
criterion, so no AC is left unproven by it.

## Separator tolerance (author-flagged risk)

`found[0].split()` accepts runs of spaces and tabs between `key=value` pairs, while the grammar in the
docstring (`check_commit.py:22-31`) and in `docs/guidelines/REVIEW-ROUNDS.md` shows single spaces.
Executed: double spaces -> exit 0; tabs -> exit 0.

**Judgment: acceptable tolerance, not a defect.** RST-01's acceptance criteria say nothing about
separator strictness; "malformed" is defined there by tier, key set, and the three numeric invariants,
all of which the split preserves exactly. Whitespace-run tolerance is the standard `str.split()`
contract and costs nothing in signal fidelity. Recorded as a **spec-precision gap** rather than a pass:
the spec leaves separator strictness undefined, so this is a deliberate reading, not a proven outcome.
One coupling note for the RST-02 slice - `review-metrics.py` must parse the value with the same
whitespace-run tolerance, or a trailer this validator accepts will be unreadable by the reader.

## Ranked gaps

1. **Low - surviving mutant M2**: `tools/test_tlc_validators.py:297-301` does not discriminate the
   unknown-key rejection (`check_commit.py:88`). Fix: assert with an unknown key whose value is a
   valid integer, e.g. `reviewer=3`, so removing the branch changes the exit code. Fix task, not an
   AC failure.
2. **Informational - spec-precision, trailer location**: the spec does not say where in the message
   the trailer must appear; the implementation scans the whole body, so a trailer quoted inside a
   fenced block is validated. Either the spec pins the location (git's last-paragraph rule) or this
   stands as accepted behaviour.
3. **Informational - spec-precision, separator strictness**: see above.

## Compact chat summary

```markdown
## Validation: review-signal-trailer slice 1 (RST-01) - PASS

**Spec-anchored check**: 5/5 ACs matched the spec outcome | 2 spec-precision gaps flagged
**Gate**: `python3 tools/test_tlc_validators.py` exit 0 - 35 passed, 0 failed (main: 17; +18, -0)
**Sensor**: 4 mutations injected, 3 killed, 1 survived
**Report**: `.specs/features/review-signal-trailer/validation-s1.md`

**Ranked gaps**:
1. Surviving mutant M2 - unknown-key rejection not discriminated - `tools/test_tlc_validators.py:297`
2. Spec-precision: trailer location undefined (whole body scanned) - `check_commit.py:50`
3. Spec-precision: separator strictness undefined (`.split()` tolerates runs) - `check_commit.py:76`
```
