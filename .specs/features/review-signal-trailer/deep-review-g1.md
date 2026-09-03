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

---

## Round 2

Reviewer: fresh deep-review identity, distinct from Round 1's, read-only. Scope: `git show ee46c5c`
and its effect on the tree only, per this round's charter — Round 1's cleared diff is not
re-reviewed. This is the final round (`docs/guidelines/REVIEW-ROUNDS.md` allows no round 3).

### Verdict

**Two new Major findings.** Both Round 1 Majors were partially remediated: the squash-merge fix is
directionally correct and independently verified, and the not-a-repository/bad-range fix is
independently verified, but each remediation has a hole that reproduces on real data — one on this
very repository's own `main` branch, the other on a corrupted-but-present repository, which Round 1's
own Finding 2 named as the residual case ("a corrupted `.git`") and which `ee46c5c` did not close.
Neither issue existed in the form found here before `ee46c5c`; both are directly caused by this
round's remediation and are reported fresh, not re-raised.

### Finding 1 — Major: dropping `--merges` sweeps non-PR direct commits into "unsigned deliveries," demonstrated on this project's own `main`

**Premise.** `tools/review-metrics.py:34` now runs `git log -z --first-parent --format=... rev_range`
with no `--merges` filter. Every first-parent commit — merge, squash, or a plain commit pushed
directly to the branch outside any pull request — is now a "delivery."

**Path.** Reproduced directly against this repository's real `origin/main`:

```
$ git log --oneline --first-parent origin/main | wc -l
60
$ git log --oneline --first-parent --no-merges origin/main | wc -l
9
$ git log --oneline --first-parent --no-merges origin/main | tail -5
d53b832 docs(workflow): fire ponytail full on plan and issue selection
03ad41e docs(guidelines): add Why this exists to every protocol file
f86362f docs(workflow): explain the delivery–reliability loop for humans
eddecdb docs(workflow): extract stack-agnostic agent operating system
d22d4a9 Initial commit
```

Six of these nine (`d22d4a9` "Initial commit", the four `docs(workflow):`/pre-workflow commits, and
`0a906a4 build: set version 0.1.0`) were never a pull request at all — they predate the PR-based
delivery process this feature's own AD-025 defines ("One `Review-Signal` trailer per delivered pull
request, carried on its merge commit"). Running `python3 tools/review-metrics.py` exactly as
documented (no arguments, the tool's own default) against this project's `main` reports these six as
`unsigned` deliveries, inflating both `deliveries` and `unsigned` and pulling the reported "reviewed
by design"/"unsigned" ratio away from reality for a repository this tool will actually be run
against.

**Why it matters.** This is the same defect class Round 1 was written to catch — a silent, wrong
number a reader would trust — just inverted in direction: Round 1's Major 1 hid real deliveries
(flattering the fraction by shrinking the denominator); this sweeps in non-deliveries (unflattering
the fraction by padding the denominator with items that were never subject to review at all, most
concretely a repository's own bootstrap "Initial commit," which by construction cannot carry a PR
trailer). The tool's own docstring (`tools/review-metrics.py:9-11`) and the rewritten spec assumption
(`.specs/features/review-signal-trailer/spec.md:67`, "Every first-parent commit on the default
branch arrived through a pull request, merge or squash alike") both assert the premise this
reproduction falsifies on the project's actual history.

**Verdict: Major.** Untested: every test in `tools/test_review_metrics.py` that builds a repo with
more than one commit calls `Repo.root()` first and lets `Repo.run()`'s new default narrow the range
to `base..HEAD` (see Finding 2 below), so no test ever asks the tool to count deliveries over a range
that contains a non-PR direct commit sitting anywhere but at the very start of an otherwise-empty
history. `file:line` — `tools/review-metrics.py:34` (the dropped `--merges` filter); contradicted
premise at `.specs/features/review-signal-trailer/spec.md:67` and `tools/review-metrics.py:9-11`.

### Finding 2 — Major: the test fixture's new default range structurally cannot exercise the scenario in Finding 1, and one test masks (rather than proves) the widened definition is safe

**Premise.** `tools/test_review_metrics.py:49-52` adds `Repo.root()`, which commits scaffolding and
records `self.base`; `tools/test_review_metrics.py:71-73` makes `Repo.run()` default to
`f"{self.base}..HEAD"` whenever `self.base` is set and no explicit range is given. Every existing
test that calls `root()` (all of them except `test_an_empty_history_exits_zero`) therefore has its
default `.metrics()` call silently rewritten from "read the whole visible history, the tool's own
documented default" to "read everything after the scaffolding commit" — precisely so the pre-existing
assertions keep their exact old numbers unchanged after `--merges` was dropped.

**Path.** `git diff 58abdba..ee46c5c -- tools/test_review_metrics.py` confirms: no pre-existing
assertion's expected numbers changed. But this narrowing is exactly the mechanism, not a side effect
of it — before `Repo.run()` learned to auto-narrow, dropping `--merges` would have made `root()`'s own
"chore(repo): root" commit newly count as an extra unsigned delivery in every one of those tests,
which would have forced every old assertion's numbers to change. The fixture was adjusted specifically
to keep the numbers stable, and in doing so it removed the one thing that would have surfaced Finding
1 in-suite: **no test in this file invokes the tool's actual documented default (bare `HEAD`, no
range argument) against a history containing more than one commit.** `test_an_empty_history_exits_zero`
(`tools/test_review_metrics.py:138-142`) is the only test that reaches the true default, and it does
so on a repo with zero commits (unborn `HEAD`), so it cannot exercise "does a non-delivery commit that
isn't scaffolding-and-excluded get correctly excluded from the count" at all.

**Why it matters.** This is exactly the risk the round charter named: "A fixture narrowed so that
tests keep their old numbers can hide the very behaviour change it was introduced for." It did. The
new `test_a_squash_merged_delivery_is_counted` (`tools/test_review_metrics.py:144-152`) also calls
`root()` and inherits the same narrowing, so even the test written specifically to prove Finding-1's
premise-in-miniature never asks the question Finding 1 answers on real data.

**Verdict: Major**, tied to Finding 1 above rather than independent of it: the fixture change is the
reason Finding 1 shipped green. `file:line` — `tools/test_review_metrics.py:71-73` (the auto-narrowing
default), `tools/test_review_metrics.py:49-52` (`Repo.root()`), absence confirmed across
`tools/test_review_metrics.py:97-202` (every multi-commit test narrows via `root()`).

### Major 1 (Round 1) remediation — otherwise sound

The squash-merge counting itself is correctly fixed and independently verified: `test_a_squash_merged_delivery_is_counted` (`tools/test_review_metrics.py:144-152`) builds two real single-parent
commits via `Repo.squash`, one with a valid trailer and one without, and the tool correctly reports
`signalled: 1, unsigned: 1` rather than excluding either — closing the "invisible, not unsigned"
defect Round 1 raised. This part of the fix is not in question; Finding 1 above is a distinct,
newly-introduced side effect of the same code change, not a re-statement of the original defect.

### Finding 3 — Major: Major 2 (Round 1) is only partially closed — a corrupted/unresolvable `HEAD` in a genuine repository still returns a fabricated zero report at exit 0

**Premise.** `tools/review-metrics.py:38-44`:
```python
inside = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True)
unborn = subprocess.run(["git", "rev-parse", "--verify", "-q", "HEAD"], capture_output=True)
if inside.returncode or not unborn.returncode:
    print(proc.stderr.strip(), file=sys.stderr)
    raise SystemExit(2)
return []
```
This closes exactly one sub-case of Round 1's Finding 2: "not a git repository at all" (`inside`
fails). Round 1's Finding 2 named a second, harder sub-case in the same paragraph: "any other
`rev-parse` failure — e.g. a corrupted `.git`." That sub-case is not distinguished from a genuinely
unborn `HEAD` by this branch: both make `inside.returncode == 0` (a `.git` directory is present and
identifiable) and `unborn.returncode != 0` (verify fails), which is the same combination the code uses
to mean "no commits yet, return `[]`."

**Path.** Reproduced directly: a real repository with two real commits, then its current branch's ref
file deleted (a realistic corruption: e.g. a crashed `git gc`, a bad `fsck` state, a partially-restored
backup) with no `packed-refs` fallback:
```
$ git rev-parse --git-dir; echo rc=$?
.git
rc=0
$ git rev-parse --verify -q HEAD; echo rc=$?
rc=1
$ python3 tools/review-metrics.py --json; echo exit=$?
{"deliveries": 0, "signalled": 0, ... "reviewed_fraction": null, ...}
exit=0
```
This is a `.git` directory that is present, identifiable, and was, moments earlier, a repository with
two real commits — not an unborn history. It produces a fully-formed, well-typed, all-zero JSON
report at exit 0, exactly the failure mode Round 1's Finding 2 was written to close, and exactly the
sub-case that finding named as still open one step further out.

**Why it matters.** The round charter asked specifically to check "any case where both subprocesses
could disagree." They do not disagree here — and that is the bug: the code needs `unborn` to mean
"genuinely zero commits," but `unborn.returncode != 0` is also true for "HEAD cannot be resolved for
any other reason," including repository damage, which is a materially different condition that should
fail loudly, not report zeros silently.

**Verdict: Major.** Untested: `tools/test_review_metrics.py` covers "not a git repository"
(`:154-165`, new) and "bad range in a good repository" (`:167-172`, pre-existing), but nothing
exercises a present-but-damaged repository. `file:line` — `tools/review-metrics.py:38-44`.

### Item 3 — spec Assumptions paragraph: wording matches the code

`.specs/features/review-signal-trailer/spec.md:67-69` now reads "Every first-parent commit on the
default branch arrived through a pull request, merge or squash alike, so each one is a delivery the
reader counts. A squash merge keeps its signal when the squash message carries the trailer and reads
as unsigned when it does not - unproven, never invisible." Checked clause-by-clause against
`tools/review-metrics.py:34` (every first-parent commit is read) and `:64-70` (signalled/unsigned
classification by trailer presence): the prose is an accurate, literal description of what the code
does — no divergence between spec and implementation. (The premise itself is empirically false on
this project's own history, per Finding 1, but that is a defect in the code's counting logic and the
premise it rests on, not a mismatch between this paragraph and the code — the paragraph correctly
describes the code's actual behavior.)

### Summary of Round 2 findings

| # | Severity | Finding | Location |
| - | -------- | ------- | -------- |
| 1 | Major | Dropping `--merges` counts non-PR direct commits (an "Initial commit," pre-workflow docs commits, a version-bump commit) as unsigned deliveries; reproduced on this repository's actual `main` (6 of 60 first-parent commits are non-PR) | `tools/review-metrics.py:34`; contradicted by `.specs/features/review-signal-trailer/spec.md:67`, `tools/review-metrics.py:9-11` |
| 2 | Major | Test fixture's new default-range narrowing (`Repo.root()` + auto `base..HEAD`) structurally prevents any test from exercising the tool's actual documented default range on a history with more than one commit, hiding Finding 1 | `tools/test_review_metrics.py:71-73`, `:49-52` |
| 3 | Major | Round 1's Major 2 is only partially closed: a present-but-damaged repository (resolvable `--git-dir`, unresolvable `HEAD` for a reason other than "no commits yet") still silently returns a zero report at exit 0 instead of failing | `tools/review-metrics.py:38-44` |

No advisory (Minor/Cosmetic) items are added this round; Round 1's own advisory list (items 3-5 in
its summary table) stands unchanged and is not re-litigated here per the round's scope.

**This is the final round; no round 3 is available under `docs/guidelines/REVIEW-ROUNDS.md`.** The
findings above are reported as required by the charter, not manufactured — each carries independent,
reproducible evidence against either this repository's real history or a constructed repository, and
each ties to a specific line the remediation touched.
