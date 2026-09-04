# Validation - review-signal-trailer, slice 2 (RST-02)

**Verdict: PASS** (5/5 RST-02 acceptance criteria proven by direct execution against verifier-built
throwaway git repositories; 3 sensor mutations injected, 3 killed; 1 Medium defect recorded on
behaviour the ACs do not cover)

- Checkpoint: `c973553734275abdcc47d188a5e8dcb35af44973` on `feat/review-signal-trailer`
  (slice commits `f73fcd8` then `c973553`).
- Verifier is not the author. No AC verdict below rests on reading the author's tests: every one was
  re-proved by running `tools/review-metrics.py` against git repositories this session built with
  `git init` / `git merge --no-ff`, never the author's fixtures. Exit codes were read from `$?`
  after a redirect, never through a pipe.

## 1. Slice-1 remediation re-proof (mutant M2)

The slice-1 Verifier found that removing the unknown-key branch in `check_commit.py:81` left
`tools/test_tlc_validators.py` green. Re-run independently at `c973553` in a throwaway
`git worktree add --detach`; the real checkout was never touched.

| Run | Mutation | Command | Real exit code | Result |
| --- | --- | --- | --- | --- |
| Baseline | none | `python3 <wt>/tools/test_tlc_validators.py` | `0` | `Ran 35 tests ... OK` |
| M2 | `check_commit.py:81` `elif key not in SIGNAL_KEYS:` -> `elif False:` | same | `1` | `FAILED (failures=1)` |

Failing assertion under mutation: `tools/test_tlc_validators.py:300`
`self.assertEqual(self._exit_code(self._commit(broken)), 1)` -> `AssertionError: 0 != 1`.

**M2 is KILLED.** The remediation in `f73fcd8` changed the probe value from `reviewer=alice` to
`reviewer=3` (`tools/test_tlc_validators.py:297-298`), so the key now passes every other rule and
only the unknown-key branch can reject it. The assertion discriminates the rejection it names.

**Test integrity.** `git diff --numstat main -- tools/test_tlc_validators.py` -> `93 0`
(93 insertions, **0 deletions**). The remediation's only pre-existing-line edit is the probe value
plus a comment; no assertion was weakened or removed - the mutated value makes the assertion
strictly stronger, since the previous value passed for the wrong reason.

## 2. Spec-anchored acceptance criteria check - RST-02

All repositories below were built by the verifier. `M` = `tools/review-metrics.py`.

| Criterion | Spec-defined outcome | Executed proof (real exit code) + `file:line` | Result |
| --- | --- | --- | --- |
| Report the number of deliveries carrying a signal and the number carrying none | both counts present | repoA (2 signalled merges + 1 unsigned merge): `python3 M main` -> exit `0`, `Deliveries in main: 3 (signalled 2, unsigned 1)`. Impl `tools/review-metrics.py:63-67`; test `tools/test_review_metrics.py:87-89` | PASS |
| Reviewed fraction = verified slices over total slices across every signal in range | `sum(verified)/sum(slices)` | repoA signals declare `slices=3 verified=2` and `slices=5 verified=5`; output `Reviewed fraction: 7/8 slices verified (87.5%)`, JSON `reviewed_fraction: 0.875` = 7/8. Impl `tools/review-metrics.py:80`; test `tools/test_review_metrics.py:96-97` | PASS |
| `tier=direct` / `tier=batch` count as reviewed by design, never as an unreviewed delivery | in `reviewed_by_design`, not in `unsigned` | repoB (`tier=direct`, `tier=batch`, one unsigned): exit `0`, `signalled 2, unsigned 1`, `Reviewed by design (tier=direct|batch): 2`. The single unsigned count comes from the trailer-less merge alone. Impl `tools/review-metrics.py:66-70` (`by_design += tier in BY_DESIGN` on the signalled path); test `tools/test_review_metrics.py:104-106` | PASS |
| Range with no `Review-Signal` trailer: zero signalled, unsigned still reported, exit 0 | exit 0, `signalled 0`, unsigned count non-zero | repoC (2 trailer-less merges): exit `0`, `Deliveries in main: 2 (signalled 0, unsigned 2)`, `Reviewed fraction: 0/0 slices verified (n/a)`, no stderr. Impl `tools/review-metrics.py:80` (`if totals["slices"] else None`); test `tools/test_review_metrics.py:119-121` | PASS |
| Aggregate `findings`, `fixed`, `dismissed` and surviving mutants across the range | sums across signals | repoA declares findings 4+2, fixed 3+1, dismissed 1+1, sensor 2/3 + 4/4: output `Findings: 6 (fixed 4, dismissed 2)`, `Surviving mutants: 1 (killed 6 of 7 injected)`. repoF (5 deliveries, mixed tiers): `Findings: 9 (fixed 8, dismissed 1)`, `Surviving mutants: 5 (killed 1 of 6 injected)`. Impl `tools/review-metrics.py:71-75`, `:81`; test `tools/test_review_metrics.py:143-146` | PASS |

## 3. Probes beyond the author's tests (verifier-authored)

| Probe | Real exit code | Observed | Reading |
| --- | --- | --- | --- |
| Range of non-merge commits only (repoD) | `0` | `Deliveries in main: 0 (signalled 0, unsigned 0)`, no stderr | correct; `--merges` yields nothing and git itself returns 0 |
| Merge whose trailer carries only `tier=direct` (repoB) | `0` | counted signalled + reviewed-by-design, `tiers {direct:1}` | correct; matches `check_commit.py`, which requires no other key for `direct` |
| `--json` shape, parsed by `python3 -c "import json,sys; json.load(sys.stdin)"` | `0` / parse `0` | 16 keys incl. `signalled`, `unsigned`, `reviewed_by_design`, `reviewed_fraction`, `surviving_mutants`, `tiers` | valid JSON; `reviewed_fraction` is `null` (not `NaN`) when `slices` is 0, so it stays parseable |
| `sum(slices) == 0` (repoB, direct/batch only) | `0` | `Reviewed fraction: 0/0 slices verified (n/a)`, JSON `null` | no `ZeroDivisionError`; guarded at `tools/review-metrics.py:80` |
| Trailer using tab separators between pairs (repoE) | `0` | `signalled 1`, `Reviewed fraction: 1/4 (25.0%)` | correct; `str.split()` tolerance matches `check_commit.py`, closing the slice-1 coupling note |
| Range spanning 5 deliveries, mixed `direct`/`batch`/`medium`/`large`/unsigned (repoF) | `0` | `signalled 4, unsigned 1`, `by design 2`, `5/8 (62.5%)`, tiers sorted | correct |
| Explicit sub-range `<sha>..main` (repoF) | `0` | `2 deliveries, signalled 2, 3/6 (50.0%)` | the range argument really limits what is read |
| **Mistyped rev-range** `mian` and `man..maim` (repoF) | `0` | full zeros report on **stdout**, git's `fatal: ambiguous argument` on stderr only | see section 4 |
| Mistyped rev-range with `--json` | `0` | valid JSON, `signalled 0, unsigned 0` | a machine consumer receives a clean, false report |

## 4. Ruling on the author's flagged trade-off (`deliveries()` omits `check=True`)

`tools/review-metrics.py:39-46` prints git's stderr and returns `[]` on a non-zero git exit, so a
mistyped rev-range is indistinguishable in the exit code from a legitimately empty history.

**Ruling: this is a defect, ranked Medium - not an acceptable cost.**

The AC it is claimed to protect ("WHEN the range contains no `Review-Signal` trailer, report zero
signalled deliveries, still report the unsigned count, and exit 0 rather than fail") does not
require swallowing a git failure, because **git does not fail on an empty history**. Measured
directly in repoD: `git log -z --first-parent --merges --format=%H main` on a merge-free history
returned **exit `0` with empty stdout and empty stderr**. Honouring `proc.returncode` would
therefore leave all four "empty range" behaviours untouched; the two cases are already separable at
the source. The trade-off is not forced, so nothing is being bought by it.

What is being paid: a typo produces `signalled 0, unsigned 0, reviewed_fraction null` on stdout with
exit 0 - a metric that lies, in exactly the tool whose purpose is to answer "what fraction of
delivered work was really reviewed". A human skims the report, not stderr; a script reading `--json`
sees no error channel at all. The failure mode is silent and biased toward the flattering answer
("nothing unsigned").

No RST-02 acceptance criterion is left unproven by it - every AC holds on a well-formed range - so
this does not sink the slice. It is recorded as a fix task, not fixed here.

## 5. Gate

| Command | Real exit code | Result |
| --- | --- | --- |
| `python3 tools/test_review_metrics.py` | `0` | `Ran 9 tests in 5.425s ... OK` |
| `python3 tools/test_tlc_validators.py` | `0` | `Ran 35 tests in 0.126s ... OK` |

Test count: 35 (`main` baseline 17) + 9 new = 44 across both suites. No suite lost a test.

## 6. Discrimination sensor - `tools/review-metrics.py`

Isolated throwaway `git worktree add --detach` at `c973553`; the file was mutated only inside that
worktree and restored from a `.orig` copy between runs (`diff` confirmed byte-identical restore).
`git status --porcelain` on the real checkout was captured before any sensor work and re-captured
after `git worktree remove --force`: **both empty, identical**; `git rev-parse HEAD` unchanged at
`c973553`. `git stash` was never used.

Baseline in the scratch worktree: `python3 <wt>/tools/test_review_metrics.py` -> exit `0`,
`Ran 9 tests ... OK`.

**3 mutations injected, 3 killed, 0 survived.**

| # | Mutation (behaviour level) | Real exit code | Result |
| --- | --- | --- | --- |
| S1 | `tools/review-metrics.py:62` `if tier is None:` -> `if tier is None or tier == "direct":` (a `direct` delivery falls into the unsigned bucket) | `1`, `FAILED (failures=2)` | KILLED |
| S2 | `tools/review-metrics.py:80` reviewed fraction inverted to `slices/verified` | `1`, `FAILED (failures=1)` | KILLED |
| S3 | `tools/review-metrics.py:24` drop `"dismissed"` from `SUMMED` so it is reported but never aggregated | `1`, `FAILED (failures=1)` | KILLED |

## 7. Ranked gaps

1. **Medium - a mistyped rev-range reports zeros and exits 0.**
   `tools/review-metrics.py:39-46` (`deliveries()` ignores `proc.returncode`). A typo yields a
   complete, plausible, false report on stdout with exit 0; git's `fatal:` reaches stderr only.
   Proven separable: git returns 0 on a legitimately empty history, so failing on a non-zero git
   exit does not touch the empty-range AC. Fix task for a new Implementer session; no AC is
   unproven, so the slice still passes.

No other gaps. No surviving mutants in this slice.
