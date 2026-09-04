# Review Signal Trailer

## Problem Statement

Every review artifact this workflow produces dies with its feature directory. `validation.md`
(Verifier verdict, sensor killed/injected) and `review-fingerprints.json` (rounds, failed
remediations) live under `.specs/features/<slug>/`, which is a rolling window that gets pruned. Once
pruned, nothing in the repository can answer whether a merged change was actually reviewed.

Merged pull requests are trivial to count; the fraction that received real review is the signal that
matters, and today it is unrecoverable. `check_commit.py:83-86` parses only the header and one
`BREAKING CHANGE:` footer, so no durable per-delivery review record exists in git.

## User Stories

### RST-01 - Durable review record

As the workflow owner, I want each delivered pull request to carry its review outcome as a git
trailer, so the record survives the pruning of `.specs/features/`.

**Acceptance Criteria:**

- WHEN a commit message carries a `Review-Signal:` trailer, `check_commit.py` shall validate its
  grammar and reject a malformed trailer with exit code 1.
- WHEN a commit message carries no `Review-Signal:` trailer, `check_commit.py` shall accept the
  message unchanged.
- IF a `Review-Signal:` trailer declares a tier other than `direct` or `batch`, THEN `check_commit.py`
  shall require the keys `slices`, `verified`, `sensor`, `rounds`, `findings`, `fixed`, and
  `dismissed`.
- IF a `Review-Signal:` trailer declares `findings` unequal to `fixed` plus `dismissed`, THEN
  `check_commit.py` shall reject it.
- IF a `Review-Signal:` trailer declares `verified` greater than `slices`, or a `sensor` value whose
  killed count exceeds its injected count, THEN `check_commit.py` shall reject it.

### RST-02 - Reviewed fraction reported

As the workflow owner, I want a command that reads the trailers already in git history, so I can see
what fraction of delivered work was really reviewed without opening any feature directory.

**Acceptance Criteria:**

- WHEN `tools/review-metrics.py` runs in a git repository, it shall read `Review-Signal` trailers
  from the commit range it is given and report the number of deliveries carrying a signal and the
  number carrying none.
- The report shall state the reviewed fraction as verified slices over total slices across every
  signal in range.
- WHERE a delivery declares `tier=direct` or `tier=batch`, `review-metrics.py` shall count it as
  reviewed by design rather than as an unreviewed delivery.
- WHEN the range contains no `Review-Signal` trailer, `review-metrics.py` shall report zero signalled
  deliveries, still report the unsigned count, and exit 0 rather than fail.
- The report shall aggregate `findings`, `fixed`, `dismissed`, and surviving mutants across the
  range so a run of zero-finding reviews is visible.

## Out of Scope

- Emitting the trailer automatically from CI or a git hook. The consuming project owns hook and CI
  wiring; this feature ships the validator and the reader only.
- Backfilling trailers onto historical merge commits.
- Per-task or per-slice trailers. One signal per delivered pull request aggregates its slices through
  the `slices` and `verified` counts.
- Any change to how reviews are conducted, to the review-round cap, or to `remediation.py`.

## Assumptions & Open Questions

**Assumptions:**

- Every first-parent commit on the default branch arrived through a pull request, merge or squash
  alike, so each one is a delivery the reader counts. A squash merge keeps its signal when the squash
  message carries the trailer and reads as unsigned when it does not - unproven, never invisible.
- `git log --format=%(trailers:key=Review-Signal,valueonly)` is available in the installed git.
- Python standard library only, consistent with every existing tool under `tools/`.

**Open questions:** none - all resolved or logged as AD-025 and AD-026.

## Requirement Traceability

| ID | Requirement | Status |
| --- | --- | --- |
| RST-01 | `Review-Signal` trailer grammar validated at commit time | verified |
| RST-02 | Reviewed fraction reported from git history | verified |
