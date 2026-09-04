# Validation: review-signal-trailer — post-cap remediation (`9cadb1d`)

**Verdict: PASS ✅**

Fresh Technical Verifier, independent identity. Did not author `9cadb1d`. Scope: the post-cap
remediation of deep-review Round 2 Findings 2 and 3 only. Finding 1 is out of scope by AD-027.
Every repository used below was built by this session; no implementer fixture was reused.

- Checkout: `/Users/antoniofulg/Projects/my-workflow`, HEAD `9cadb1d`, worktree clean.
- Diff surface: `tools/review-metrics.py` (+8 −5), `tools/test_review_metrics.py` (+26 −4).

---

## 1. Completed work

Both open fingerprints in `review-fingerprints.json` are addressed by `9cadb1d`:

| Fingerprint | Root cause | Remediation | Ruling |
| --- | --- | --- | --- |
| `4daf4b43…` | `f2-untested-default-range` | `tools/test_review_metrics.py:139-148` | close |
| `038a8b98…` | `f3-corrupted-repo-zeroes` | `tools/review-metrics.py:43-49`, test at `tools/test_review_metrics.py:150-158` | close |

---

## 2. Spec-anchored acceptance criteria check (RST-02, the criteria this remediation touches)

| Criterion (spec.md) | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| WHEN `review-metrics.py` runs in a git repository, it shall read `Review-Signal` trailers from the commit range it is given and report signalled and unsigned counts | signalled/unsigned split over the given range | `tools/test_review_metrics.py:103-105` — `assertEqual(report["deliveries"], 2)`, `assertEqual(report["signalled"], 1)`, `assertEqual(report["unsigned"], 1)` | ✅ PASS |
| The report shall state the reviewed fraction as verified over total slices | `4/5` | `tools/test_review_metrics.py:112-113` — `assertEqual((report["verified"], report["slices"]), (4, 5))` | ✅ PASS |
| WHERE `tier=direct` or `tier=batch`, count as reviewed by design | `reviewed_by_design == 2`, `unsigned == 0` | `tools/test_review_metrics.py:120-122` | ✅ PASS |
| WHEN the range contains no trailer, report zero signalled, still report unsigned, exit 0 | zeros + exit 0 | `tools/test_review_metrics.py:135-137`; unborn case `tools/test_review_metrics.py:160-164` | ✅ PASS |
| Aggregates sum across the range | `findings 6, fixed 4, dismissed 2, surviving 2` | `tools/test_review_metrics.py:210-214` | ✅ PASS |
| Documented **default** range (no argument) reads the whole history — the behaviour AD-027 pins | bare `HEAD`, root commit counted unsigned: `deliveries 3, signalled 1, unsigned 2` | `tools/test_review_metrics.py:144-148` — `assertEqual(report["range"], "HEAD")`, `assertEqual(report["deliveries"], 3)`, `assertEqual(report["unsigned"], 2)` | ✅ PASS (new) |
| A repository whose refs are broken while commits survive is a usage error, not zeros | exit 2, empty stdout, git's diagnostic on stderr | `tools/test_review_metrics.py:156-158` — `assertEqual(result.returncode, 2)`, `assertEqual(result.stdout, "")`, `assertIn("HEAD", result.stderr)` | ✅ PASS (new) |

---

## 3. Independent proof of the load-bearing `--reflog` claim

The implementer asserted, against the review packet's own suggestion, that `--all` alone does **not**
discriminate and that `--reflog` does. Both halves re-derived here on repositories built by this
session (`git version` as installed; `GIT_*` identity forced; `commit.gpgsign` irrelevant in a fresh
`init`).

**Case A — corrupted: two squash commits, `.git/refs/heads/main` deleted, no `packed-refs`, reflog intact.**

```
$ ls .git/packed-refs                    -> No such file or directory
$ ls .git/logs/refs/heads/               -> main
$ git rev-list -n 1 --all                -> exit 0, stdout EMPTY      # does NOT discriminate
$ git rev-list -n 1 --all --reflog       -> exit 0, 3e1008fa5316b0…  # DOES discriminate
```

**Case B — unborn: `git init` only.**

```
$ git rev-list -n 1 --all                -> exit 0, stdout empty
$ git rev-list -n 1 --all --reflog       -> exit 0, stdout empty
```

**Ruling: the implementer's claim is correct on both halves, and the packet's suggestion was wrong.**
`--all` alone returns exit 0 with empty stdout in *both* the corrupted and the unborn repository, so
the condition `anywhere.returncode or anywhere.stdout.strip()` would be false in both and the tool
would still fabricate a zero report at exit 0 on the corrupted repo. Adding `--reflog` makes the two
states distinguishable, because a deleted branch ref leaves `.git/logs/refs/heads/main` behind and
`rev-list --reflog` walks it. This is verified by mutation M1 below, which drops `--reflog` from the
real code and is killed.

### Attack on the discriminator — Case C: reflog also absent

Built a repository with two commits, then `rm .git/refs/heads/main` **and** `rm -rf .git/logs`, with
no `packed-refs`. The commit objects survive (`git cat-file --batch-all-objects --batch-check` lists
3 objects).

```
$ git rev-list -n 1 --all --reflog       -> exit 0, stdout empty
$ python3 tools/review-metrics.py --json -> exit 0
   {"range":"HEAD","deliveries":0,"signalled":0,"unsigned":0,"reviewed_fraction":null, …all zeros}
```

**The tool does fabricate a zero report at exit 0.** Exact reproduction:

```sh
git init -q -b main d && cd d
git commit -q --allow-empty -m "feat(one): work (#1)"
git commit -q --allow-empty -m "feat(two): work (#2)"
rm .git/refs/heads/main && rm -rf .git/logs
python3 /path/to/tools/review-metrics.py --json ; echo $?   # -> zeros, 0
```

**Judgement: an acceptable limit, not a defect (residual R1, Minor).** With no loose ref, no
`packed-refs` and no reflog, git offers no in-band signal that separates "nothing was ever committed"
from "everything that pointed at the commits was erased". The only remaining distinguisher is a full
object-database scan (`git cat-file --batch-all-objects`), which is O(repository) and would make every
healthy run pay for a state that requires deliberately destroying two independent structures. The
review's own finding named the reachable case — a deleted ref — and that case is now closed. Recorded
as a documentation residual rather than a code gap: the comment at `tools/review-metrics.py:41-42`
("refs and reflogs both come up empty only when there is genuinely nothing committed yet") is stated
as an absolute and Case C falsifies it; a one-clause qualifier would make it true.

### Confirming the other three exits still hold

| State | Command | Real exit | Output |
| --- | --- | --- | --- |
| Unborn repository (`git init` only) | `python3 tools/review-metrics.py --json` | **0** | full zeros report, `reviewed_fraction: null` |
| Corrupted (ref deleted, reflog intact) | `python3 tools/review-metrics.py --json` | **2** | stdout empty; stderr `fatal: ambiguous argument 'HEAD': unknown revision…` |
| Bad rev-range on a healthy repo | `python3 tools/review-metrics.py no-such-ref..HEAD --json` | **2** | stdout empty; stderr `fatal: ambiguous argument 'no-such-ref..HEAD'…` |
| Non-repo directory | `python3 tools/review-metrics.py --json` | **2** | stderr `fatal: not a git repository…` |
| Healthy multi-commit history, default range | `python3 tools/review-metrics.py` | **0** | `Deliveries in HEAD: 2 (signalled 1, unsigned 1)`, `Reviewed fraction: 3/3 slices verified (100.0%)` |

One further degenerate state found while probing: a **bad rev-range inside an unborn repository**
(`no-such-ref..HEAD` with zero commits) exits **0** with zeros rather than 2, because the failure path
correctly concludes the repository has no commits. Recorded as residual R2, Minor — the number
reported is still true (there are no deliveries), and the state is unreachable in the operator flow
this tool documents.

---

## 4. Finding 2 — the default range is genuinely pinned

`test_the_documented_default_range_reads_the_whole_history` (`tools/test_review_metrics.py:139-148`)
calls `self.repo.metrics(whole_history=True)`, which routes through `Repo.run(whole_history=True)`
(`tools/test_review_metrics.py:71-74`) and therefore passes **no** range argument to the tool. The
history is three commits (`root()` + two `deliver()` merges). It asserts `report["range"] == "HEAD"`
— proving the tool's own `argparse` default was used, not a fixture-supplied range — and that the
scaffolding root is counted as the third, unsigned delivery. This is the AD-027 behaviour, asserted
on a real multi-commit history through the documented default. Requirement met.

**Narrowing preserved, nothing weakened.** `git diff ee46c5c..9cadb1d -- tools/test_review_metrics.py`
shows only: `run()`/`metrics()` gain a keyword-only `whole_history: bool = False`; the narrowing
condition becomes `if not args and self.base and not whole_history`; and two new test methods are
added. **No pre-existing assertion's expected value, count, or method body changed**, and no test was
renamed or removed. Default `False` means every other test keeps the exact `<root>..HEAD` narrowing it
had at `ee46c5c`.

**Discrimination of the new test, re-derived rather than accepted.** Staged the current test file
against each historical tool body in a scratch directory (`review-metrics.py` from the old commit +
`test_review_metrics.py` from HEAD, side by side so `TOOL` resolves to the old body):

| Tool body | `test_the_documented_default_range…` | `test_a_repository_whose_branch_ref_is_gone…` | Suite exit |
| --- | --- | --- | --- |
| `ee46c5c` | **passes** (no discrimination) | **FAILS** `AssertionError: 0 != 2` | 1 |
| `f8adcbf` | **FAILS** `AssertionError: 2 != 3` | fails (plus 2 others) | 1 |

The implementer's reasoning **holds and is confirmed empirically**. `ee46c5c` had already dropped
`--merges`, so the default-range behaviour under test was already correct there — Finding 2 was a
coverage gap, not a code defect, and a test that closes a coverage gap cannot fail against the body
that already had the behaviour. It discriminates the body that did *not*: at `f8adcbf`
(`tools/review-metrics.py:30` still carries `--merges`) the root commit is not a merge, so the tool
reports 2 deliveries where the pinned contract requires 3, and the test fails. The pin is real.

---

## 5. Gate

```
$ bun run test:all > gate.txt 2>&1 ; echo "GATE_EXIT=$?"
GATE_EXIT=0
```

Exit code read from `$?` after a redirect, never through a pipe. **0 failures anywhere.**

- Bun suites: `Ran 124 tests across 8 files`, plus per-suite lines summing **256 passed, 0 failed**
  (`9`, `6`, `59`, `58`, `31`, `13`, `10`, `15`, `55`), and `orca assisted probe contract: 24/24 passed`.
- Python unittest suites: all `OK` — `Ran 10`, `Ran 5`, `Ran 28`, `Ran 14` (this feature's
  `test_review_metrics.py`), `Ran 35`, `Ran 5`.
- Test-integrity: count **increased** by 2 (12 → 14 in `tools/test_review_metrics.py`). No test
  deleted, skipped, or weakened.
- No re-run needed; the suite was green on the first pass.

---

## 6. Discrimination sensor

Scratch-copy isolation (`tools/review-metrics.py` + `tools/test_review_metrics.py` copied into three
throwaway scratch directories, mutated there). **No `git stash` at any point.**

Baseline `git status --porcelain` before: **empty**. After: **empty**, `diff` identical. Isolation
verified.

| # | Behaviour-level mutation | Result | Killed by |
| --- | --- | --- | --- |
| M1 | Drop `--reflog`: `["git","rev-list","-n","1","--all","--reflog"]` → `[…,"--all"]` | **KILLED** (rc 1, 1 failure) | `test_a_repository_whose_branch_ref_is_gone_fails_instead_of_reporting_zeros` |
| M2 | Invert the guard: `if anywhere.returncode or anywhere.stdout.strip():` → `… or not anywhere.stdout.strip():` | **KILLED** (rc 1, 3 failures) | the ref-gone test, `test_an_empty_history_exits_zero`, `test_an_unreadable_rev_range_fails_instead_of_reporting_zeros` |
| M3 | Failure path always returns `[]` (whole discriminator removed) | **KILLED** (rc 1, 3 failures) | the ref-gone test, the unreadable-range test, `test_outside_a_repository_fails_instead_of_reporting_zeros` |

**3 injected, 3 killed, 0 survived.** M1 is the direct empirical confirmation that `--reflog` is
load-bearing and covered.

---

## 7. Code quality

| Check | Pass? |
| --- | --- |
| No features beyond what was asked | Yes |
| No abstractions for single-use code | Yes — one extra `subprocess.run`, one keyword-only test flag |
| No unnecessary flexibility added | Yes |
| Only touched files required for the fix | Yes — the two `tools/` files plus workflow state |
| Didn't improve unrelated code | Yes |
| Matches existing patterns/style | Yes — stdlib only, same `subprocess.run` shape as its neighbours |
| Would a senior engineer approve? | Yes |
| Tests map to acceptance criteria, non-shallow | Yes — both new tests assert exact spec-defined values, and both were shown to fail against a body lacking the behaviour |
| Every test in scope maps to an AC or a review finding | Yes |
| Spec-anchored outcome check | Yes, table in §2 |
| Guidelines followed | `docs/guidelines/TEST-CONTRACT.md` (invariant named, canonical suite extended, no coverage-padding test) |

One accuracy nit, not a defect: `tools/review-metrics.py:41-42` states the reflog/ref emptiness
condition as absolute; Case C in §3 falsifies the absolute reading.

---

## 8. Ranked residual gaps

1. **R1 — Minor, accepted limit.** A repository with its branch ref *and* `.git/logs` deleted and no
   `packed-refs` still yields an all-zero report at exit 0. Reproduction in §3. Empirically
   indistinguishable from an unborn repository without an O(repository) object scan. Recommendation:
   qualify the comment at `tools/review-metrics.py:41-42`; no code change.
2. **R2 — Minor.** A bad rev-range inside an unborn repository exits 0 with zeros instead of 2. The
   reported number is still true; the state is not reachable in the documented operator flow.

Neither residual blocks the verdict, and neither reopens `f2-untested-default-range` or
`f3-corrupted-repo-zeroes`.

## 9. Note on AD-027 (out of scope, not part of the verdict)

Read as instructed and not re-litigated. Recorded only that the new default-range test at
`tools/test_review_metrics.py:139-148` asserts precisely the AD-027 reading — the scaffolding root
counts as an unsigned delivery — so the decision is now pinned in the suite rather than only in
`STATE.md`. No disagreement to register.

## 10. Fingerprint disposition

Both open fingerprints close:

- `4daf4b43db5d033b4a012ff93784704583720a1ea53b535442ad322c4ec77fd1` (`f2-untested-default-range`) — **CLOSE**
- `038a8b98916115fcc9326a4f15ae89961712f10b4ff643daba2b0064feafc04a` (`f3-corrupted-repo-zeroes`) — **CLOSE**
