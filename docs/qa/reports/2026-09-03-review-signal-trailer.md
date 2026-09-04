# QA report — review-signal-trailer (2026-09-03)

**Scope:** feature-closing QA for `review-signal-trailer` (RST-01, RST-02).
**Branch:** `feat/review-signal-trailer`, HEAD `0916394`.
**Persona:** Workflow operator.
**Adapter:** CLI/manual, per `docs/qa/README.md` — the two shipped commands run from the active
checkout, plus one disposable checkout-local git repository built by this session.
**Evidence:** `docs/qa/evidence/2026-09-03-review-signal-trailer/` (ignored).
**Gate:** `python3 tools/test_review_metrics.py` → exit 0, 14 tests OK;
`python3 tools/test_tlc_validators.py` → exit 0, 35 tests OK.
**Residue:** `git status --short` shows only the pre-existing
`.specs/features/review-signal-trailer/review-fingerprints.json` modification carried into this
session; the disposable repository was removed.

## Matrix

| Charter leg | Scenario | Verdict | Evidence |
| --- | --- | --- | --- |
| Compose a real delivery trailer and validate it | `QAS-validate-the-review-signal-trailer` | pass | `04-check-commit.log` §A |
| Mistyped payload key | same | pass | `04-check-commit.log` §B |
| `findings` that does not balance | same | pass | `04-check-commit.log` §C |
| Mistyped trailer key itself | same | defect — `BUG-20260903-mistyped-review-signal-key-passes-silently` | `04-check-commit.log` §E |
| Default range, no argument | `QAS-report-the-reviewed-fraction-from-git` | pass | `01-noargs.log` |
| `--json` | same | pass | `02-json.log` |
| Narrowed range | same | pass | `03-range.log` |
| Unreadable range | same | pass — exit 2, git's own diagnostic on stderr | `03-range.log` |
| `--help` read cold | same | defect — `BUG-20260903-review-metrics-help-omits-the-range-caveat` | `01-noargs.log` |
| Decision aid on a history that carries signals | same | pass | `05-nextmonth.log` |

## Trailer reconciliation

The packet proposed `sensor=10/10 … findings=5 fixed=5 dismissed=0`. Reconciled against the
artifacts, the message this session validated reads:

```
Review-Signal: tier=medium slices=2 verified=2 sensor=10/10 rounds=2 findings=5 fixed=4 dismissed=1
```

- **`sensor=10/10`** — four sensor passes, not three: `validation-s1.md:64` 4 injected / 3 killed
  (M2 survived); `validation-s2.md:14-30` re-injects M2 alone after remediation `f73fcd8` and kills
  it; `validation-s2.md:107` 3/3 on `review-metrics.py`; `validation-postcap.md:188` 3/3. Counting
  every injection event gives 11/10 and would report one surviving mutant that does not survive.
  Counting distinct mutations at their final verdict gives **10 injected, 10 killed, 0 surviving**,
  which is the true end state and the one the aggregate is for.
- **`findings=5 fixed=4 dismissed=1`** — Round 1 raised 2 Major (`deep-review-g1.md:217-218`), both
  remediated in `ee46c5c`. Round 2 raised 3 Major (`:399-401`); Findings 2 and 3 were remediated in
  `9cadb1d`, and Finding 1 was ruled not-a-defect by AD-027. So one of the five was dismissed, not
  fixed. `findings=5 fixed=5 dismissed=0` passes the validator — `5 == 5 + 0` — which is the point
  worth recording: the validator enforces arithmetic, never truth. A self-consistent wrong signal is
  indistinguishable from a right one, and that is correct behaviour for a commit-message check.
- `slices=2 verified=2 rounds=2 tier=medium` confirmed against the two slice validations plus the
  post-cap pass.

## Is it a decision aid?

Yes, on a history that carries signals — with one caveat that became a bug record.

Simulated a plausible next month in a disposable repository: six deliveries, four signalled, three
of them real reviews that found nothing.

```
Deliveries in HEAD: 6 (signalled 4, unsigned 2)
Reviewed fraction: 4/4 slices verified (100.0%)
Reviewed by design (tier=direct|batch): 1
Findings: 0 (fixed 0, dismissed 0)
Surviving mutants: 0 (killed 9 of 9 injected)
  tier=direct: 1
```

`Findings: 0` beside `signalled 4` and `killed 9 of 9 injected` reads unambiguously as *four reviews
ran and found nothing*, which is the spec criterion that a run of zero-finding reviews stays visible.
That criterion holds on real output.

The caveat: `Reviewed fraction: … (100.0%)` is computed over signalled deliveries only, so the two
unsigned ones cannot pull it down. The headline reads 100% while a third of deliveries were never
measured. Line 1 carries the correction, but the percentage is the number that gets quoted.

On this repository today the report is honest and uninformative by construction — 67 deliveries, 0
signalled — because backfilling is explicitly out of scope. That is the expected starting state, not
a defect.

## Findings, ranked

1. **Major (usability)** — `--help` withholds the explanation AD-027 depends on.
   `tools/review-metrics.py:116`. See `BUG-20260903-review-metrics-help-omits-the-range-caveat`.
2. **Minor (usability)** — the headline reviewed fraction hides its own coverage.
   `tools/review-metrics.py:105-106`. Recorded in the same bug file.
3. **Minor (decision required)** — a typo in the trailer key is a silent miss.
   `check_commit.py:50`. See `BUG-20260903-mistyped-review-signal-key-passes-silently`.

None blocks delivery. All three are one-line or documentation changes on surfaces that are already
correct.

## Verdict

Both promises walked and passing. Two bug records open, both usability, neither an acceptance-criteria
failure and neither producing a wrong number.
