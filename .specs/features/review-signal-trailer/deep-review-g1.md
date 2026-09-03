# Deep Review — Group 1 (whole feature) — review-signal-trailer

Reviewer: fresh deep-review identity, read-only. Scope: `git diff main...HEAD` on
`feat/review-signal-trailer` @ `58abdba` (5 commits: `7cc8c02`, `f73fcd8`, `c973553`, `f8adcbf`,
`58abdba`). Conformance baseline: `spec.md` (RST-01, RST-02), AD-025, AD-026,
`docs/guidelines/REVIEW-ROUNDS.md`, `docs/guidelines/CONTEXT-BUDGET.md`, `AGENTS.md`. Slice-level
acceptance criteria already proven fresh by `validation-s1.md` / `validation-s2.md`; not re-litigated
here. This report covers only what a single-slice Verifier structurally cannot see: agreement
between the two parsers, the guideline trim, the pointer migration, and the AD-025 squash-merge
weakness in practice.

## Verdict

**FIX_BEFORE_SHIP is not required for the reviewed slice-level acceptance criteria**, but this group
carries **two Major findings** in `tools/review-metrics.py`'s failure-path logic that make the
reviewed-fraction report silently produce a flattering ("all zero, exit 0") result in two real
misuse scenarios instead of failing loudly, which directly undermines RST-02's purpose (a metric a
reader can trust without opening a feature directory). Per `REVIEW-ROUNDS.md`, Major findings block.
No Blocker found. Everything else checked out clean or is Minor/Cosmetic.

---

## Finding 1 — Major: a squash-merged delivery is invisible, not "unsigned"

**Premise.** `tools/review-metrics.py:27-30` restricts what counts as a "delivery" to
`git log --first-parent --merges`, i.e. commits with two or more parents. A squash merge produces a
single-parent commit, even when its message carries a perfectly well-formed `Review-Signal:` trailer.

**Path.** I reproduced this directly: a throwaway repo with a squashed delivery whose commit message
carries `Review-Signal: tier=medium slices=1 verified=1 sensor=1/1 rounds=1 findings=0 fixed=0
dismissed=0` (grammatically valid per `check_commit.py`) produces:

```
{"deliveries": 0, "signalled": 0, "unsigned": 0, "reviewed_fraction": null, ...}
```

The delivery does not appear as `unsigned` (which would at least be visible and honest) — it does
not appear at all. `spec.md`'s own Assumptions section describes the trade-off as "A squash or
fast-forward merge would lose it; the reader treats a missing signal as unproven" — i.e. it predicts
the delivery would show up as *unsigned*. The actual code produces a stronger and undocumented
failure mode: the delivery is excluded from `deliveries` entirely, so a reader sees a smaller,
cleaner-looking total rather than a visible gap. AD-025's trade-off note ("loses its signal") has the
same gap: it does not say the delivery vanishes from the count, only that it "loses its signal."

**Why it matters.** This is exactly the "silence that produces a flattering number" the review was
asked to hunt for. A project that primarily uses "Squash and merge" (a mainstream GitHub default)
would see `review-metrics.py` report a small, tidy set of deliveries with a high reviewed fraction,
while the actual delivered work is many times larger and completely unaccounted for — the report
looks trustworthy precisely because it is silent about the gap.

**Verdict: Major.** No test in `tools/test_review_metrics.py` exercises a squash (single-parent)
delivery; every fixture in that suite uses `git merge --no-ff`
(`tools/test_review_metrics.py:47-55`), so this gap shipped untested. Recommend: at minimum, document
this precisely (not just "loses its signal" but "is excluded from the delivery count, not counted as
unsigned") in `spec.md` Assumptions and AD-025, so a reader of the tool's output is not misled.

---

## Finding 2 — Major: an unreadable location (not a git repo at all) is misclassified as "no commits" and silently reports zero

**Premise.** `tools/review-metrics.py:34-40`:
```python
if proc.returncode:
    # A repository with no commits at all has no deliveries; anything else is a bad range.
    unborn = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], capture_output=True)
    if unborn.returncode == 0:
        print(proc.stderr.strip(), file=sys.stderr)
        raise SystemExit(2)
    return []
```
The comment's own claim ("anything else is a bad range") is falsified by the code: `git rev-parse
--verify -q HEAD` fails identically whether the working directory is an empty repository (unborn
branch) **or is not a git repository at all**. Both land in the same `return []` branch.

**Path.** Reproduced directly. Running `python3 tools/review-metrics.py --json` from a plain
directory with no `.git` at all:
```
{"deliveries": 0, "signalled": 0, "unsigned": 0, "reviewed_fraction": null, ...}
exit code: 0
```
and with an arbitrary garbage argument (`"some..range"`) in that same non-repo directory, the result
is identical: a fully-formed, well-typed JSON report, exit 0. This is the same failure mode
`f8adcbf` ("fail on an unreadable rev-range") set out to close — that commit correctly makes a bad
range in a real repository exit 2 (`tools/test_review_metrics.py:129-134` covers that case) — but the
fix's own distinguishing check cannot tell "genuinely no deliveries exist" from "this location cannot
answer the question at all," so the case one degree more broken than a bad ref (no repository, or
any other `rev-parse` failure — e.g. a corrupted `.git`) regresses to the pre-`f8adcbf` behavior: a
green-looking zero report instead of a failure.

**Verdict: Major.** No test exercises "not a git repository" or a `rev-parse` failure for a reason
other than an unborn HEAD, so this is untested. It directly undercuts the point of `f8adcbf`'s own
docstring update ("Unreadable range: usage error, exit 2," `tools/review-metrics.py:28`) in a
scenario one step more broken than the one that commit was written to fix.

---

## The two parsers: agreement checked field-by-field

Diffed `check_review_signal` (`.agents/skills/workflow-spec-driven/scripts/check_commit.py:69-124`)
against `report`/`deliveries` (`tools/review-metrics.py:27-88`) line by line.

- **Grammar surface (keys, tiers, integer shape) matches exactly.** `SIGNAL_KEYS`,
  `SIGNAL_TIERS`, and `SIGNAL_TIER_KEYS` in `check_commit.py` line up with the grammar block quoted
  in `review-metrics.py`'s own docstring (`tools/review-metrics.py:6-8`) and with `SUMMED`
  (`tools/review-metrics.py:24`). `number()` (`tools/review-metrics.py:49-51`) is an intentional,
  correctly-documented restriction to the same `^[0-9]+$` shape as `SIGNAL_INT_RE`
  (`check_commit.py:48`): for every value that would pass `check_commit.py`'s validation, both
  parsers compute the identical integer. No divergence found on the validated path.
- **Divergence on the *invalid* path is real but is a deliberate, documented asymmetry, not a bug.**
  `check_commit.py` rejects an unpartitionable field, an unknown key, a duplicate key, or a
  non-digit value. `review-metrics.py` silently drops an unpartitionable field
  (`tools/review-metrics.py:61-64`, no `else` branch) and silently coerces any non-digit value to `0`
  via `number()`. The reader's docstring states this design explicitly: "this reader only aggregates
  what is already there" (`tools/review-metrics.py:11`). This is consistent with AD-026, which makes
  emission-time validation "an instruction rather than a gate" and accepts that "nothing forces a
  delivery to carry the trailer." Given `check_commit.py` is never wired into CI or an installed
  hook in this repository (`.git/hooks/commit-msg` does not exist; no `.github/workflows` reference
  it — confirmed by search), a malformed-but-present trailer reaching the merge commit is a real,
  not theoretical, possibility, and the reader's leniency means it would silently contribute zeros
  rather than surface as an error anywhere in the report. **Rank: Minor**, not Major — the resulting
  distortion is bounded (defaults to 0, does not inflate anything) and an anomalous tier value would
  still surface visibly in the `tiers` breakdown (`tools/review-metrics.py:86,103`) for a careful
  reader. This is a legitimate advisory, not a defect: **Premise** — the reader trusts unvalidated
  upstream data by design; **Improvement** — `review-metrics.py` could count and surface malformed
  trailers as a distinct bucket (e.g. `"malformed": n`) instead of silently zeroing them; **Fix** —
  not required for this feature's stated scope (RST-02 does not ask for this), file as a follow-up.
- **No key check_commit.py allows goes unhandled by the reader in a way that crashes or throws.**
  Verified `remediation-failed` (accepted by `check_commit.py`, not in `SUMMED`) is silently ignored
  by the reader rather than mishandled — acceptable, since RST-02's acceptance criteria enumerate
  exactly `findings`, `fixed`, `dismissed`, and surviving mutants for aggregation, not
  `remediation-failed`.

## The deleted "Why loops run away" section (`58abdba`)

Compared the deleted 8-line section against the pre-existing `**Why this exists:**` header
(`docs/guidelines/REVIEW-ROUNDS.md:5-6`, unchanged by this diff). The header already states, before
this commit: "Remediating every nitpick in one iteration is unbounded: each fix changes the diff and
the next round finds new nits." The deleted section restated the identical mechanism at greater
length ("The failure has one cause... remediate every confirmed finding and every nitpick... every
nitpick changes the diff, so the next round finds new nitpicks. The loop is unbounded by
construction, not by bad luck."). This is the same claim, not a distinct one. The operative rule
the section existed to justify — "Nitpicks never trigger a round" — survives verbatim as Hard Rule 2
(`docs/guidelines/REVIEW-ROUNDS.md`, unaffected by this diff), and rule 1 ("A round contains only
findings not raised in a prior round") is also untouched. **No finding**: the deletion is genuinely
redundant with content that was already present before this diff, the file is now 157 lines (under
the stated 160-line cap, `wc -l`), and no reasoning an agent needs to act on the rule was removed.

## The grammar's new home (`check_commit.py` docstring) and the two redirected pointers

- `tools/review-metrics.py:10` and `.agents/skills/autonomous/SKILL.md:158-159` both now point to
  "the `check_commit.py` docstring" for grammar and keys. Repo-wide search for `Review-Signal`
  outside `docs/qa/evidence/` (a frozen historical snapshot, correctly not touched) and outside this
  feature's own `validation-*.md` turns up no remaining reference to the old home
  (`docs/guidelines/REVIEW-ROUNDS.md`'s own short section, added in `c973553`, correctly says "that
  validator's docstring owns the field-by-field grammar" rather than restating the grammar). No
  stale pointer found.
- Checked the docstring (`check_commit.py:24-33`) field-by-field against the code that enforces it
  (`check_review_signal`, `check_commit.py:69-124`): required-key set for non-`direct`/`batch` tiers,
  the `fixed + dismissed == findings` invariant, `verified <= slices`, `slices >= 1` (implemented as
  `slices == 0` is rejected, equivalent given the integer regex already excludes negatives), and
  `killed <= injected` all match the code exactly. **No divergence found; the docstring is accurate
  and complete for its stated purpose.**
- **Cosmetic, non-blocking**: the docstring's "What it checks" summary line ("a `Review-Signal:`
  trailer is present but malformed," `check_commit.py:21`) does not spell out that exactly one
  `Review-Signal:` line is permitted (enforced at `check_commit.py:73-74`); it is folded into the
  generic "malformed" catch-all. Not worth a round; filing as a follow-up nit only if the team wants
  the docstring to be a complete standalone reference rather than a summary.

## `Review-Signal` emission is instructed but never validated before the commit it matters on

`.agents/skills/autonomous/SKILL.md:157-159` (new in `c973553`) tells the delivering agent to attach
the trailer to the merge commit and points at the grammar, but neither this addition nor the
surrounding "prove readiness, then deliver" section instructs running `check_commit.py` against that
specific merge-commit message before finalizing it. `check_commit.py` is invoked elsewhere only "on
each [task] commit" (`.agents/skills/workflow-spec-driven/SKILL.md:43`) and as an optional,
not-installed git hook (`references/implement.md:290`, `.git/hooks/commit-msg` absent) — neither of
which necessarily fires on a PR merge commit created via `gh pr merge`. **Rank: Minor.** `spec.md`'s
"Out of Scope" already excludes "Emitting the trailer automatically from CI or a git hook. The
consuming project owns hook and CI wiring," and AD-026 explicitly accepts the emitting step staying
"an instruction rather than a gate" — so this is a known, accepted design choice, not an oversight
this diff introduced silently. Flagging only because the new instruction text was the right place to
add a one-line reminder to run the existing validator manually before merging, and it does not.

## Tests that mirror the implementation

Read both new suites (`tools/test_review_metrics.py`, and the `ReviewSignalTrailerTests` class added
to `tools/test_tlc_validators.py` in `7cc8c02`) end to end.

- **One instance already found and fixed inside the diff itself**: `f73fcd8`'s own commit message
  documents that `test_an_unknown_key_is_rejected_and_named` originally used
  `broken = self.GOOD + " reviewer=alice"` — a non-integer value, so the assertion passed even with
  the unknown-key branch deleted (it would still fail on the separate integer-format check). The
  fix (`reviewer=3`) makes it fail for the correct reason. This is exactly the class of test AGENTS.md
  forbids, and it was self-corrected within the reviewed commit range rather than shipped. No
  remaining instance of this pattern found elsewhere in either suite — every other assertion in
  `ReviewSignalTrailerTests` isolates exactly one invariant per test (one field changed from `GOOD`)
  and asserts the externally observable exit code and/or error text, not an internal code path.
- `tools/test_review_metrics.py` builds real git repositories with real merge commits
  (`Repo.deliver`, `tools/test_review_metrics.py:47-55`) and asserts on the tool's JSON output, not on
  its internals — this is testing the actual git-trailer contract, not mirroring the implementation.
  No further mirrored-test instances found in either suite.

## Suite registration (`58abdba`, `tools/shared/tests/qa-skills.test.ts`)

Confirmed necessary, not scaffolding: `expectedPythonSuites` (line ~1104) is checked against every
tracked `tools/test_*.py` / `scripts/test_*.py` file via `trackedRepositoryPaths()`
(`tools/shared/tests/qa-skills.test.ts:1113-1141`). `c973553` added `tools/test_review_metrics.py`
without registering it, which would have failed this existing contract test; `58abdba` closes that
gap. This is required plumbing for an existing invariant, not unrequested abstraction.

---

## Summary of ranked findings

| # | Severity | Finding | Location |
| - | -------- | ------- | -------- |
| 1 | Major | Squash-merged delivery with a valid trailer is excluded from `deliveries` entirely (not counted as `unsigned`), contradicting `spec.md`'s own Assumptions text and undocumented as such | `tools/review-metrics.py:27-30` |
| 2 | Major | "Not a git repository" (or any other `rev-parse` failure) is misclassified as "no commits," silently returns a zero report at exit 0 instead of failing, contradicting the failure path's own comment and undermining `f8adcbf`'s stated fix | `tools/review-metrics.py:34-40` |
| 3 | Minor (advisory) | Reader silently coerces a malformed-but-present field to `0` rather than surfacing it, relying entirely on emission-time validation that is never CI/hook-enforced in this repo | `tools/review-metrics.py:61-64`, `49-51` |
| 4 | Minor (advisory) | New delivery instruction tells the agent to attach the trailer but not to validate it with `check_commit.py` before finalizing the merge commit | `.agents/skills/autonomous/SKILL.md:157-159` |
| 5 | Cosmetic | Docstring's "What it checks" summary folds the one-trailer-line rule into the generic "malformed" catch-all rather than naming it | `check_commit.py:21` |

Clean, no finding: the `REVIEW-ROUNDS.md` section deletion (genuinely redundant with the pre-existing
header, operative rule intact, file under its 160-line cap); the grammar-pointer migration (no stale
references remain, docstring verified accurate and complete against the enforcing code); the
`qa-skills.test.ts` suite registration (required, not scaffolding); the bulk of both new test suites
(assert observable behavior, do not mirror implementation) aside from the one instance the diff
itself already fixed.
