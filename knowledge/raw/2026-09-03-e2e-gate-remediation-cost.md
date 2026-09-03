# Remediation cost on a slow end-to-end gate

Recorded 2026-09-03, from a working session on this repository.

## The observation

An end-to-end gate of roughly 500 tests takes close to 20 minutes for a full run. A run came back
with 4 failures.

The instruction given was: fix all 4, re-run only those 4 until they are green, then run the full
gate once to close.

The reasoning stated for it: fixing serially and re-running the full gate after each fix means
waiting 20 minutes to learn that 2 of the 4 are still red. Four failures at one full run per fix is
80 minutes minimum, more when a fix is wrong, to learn what a single run at the end tells you.

## Why it was recorded

`docs/guidelines/VERIFICATION-EVIDENCE.md` said "Re-verify from scratch. The full command, not the
previously-failing subset" and "Multiple failures: fix the first one first". Neither said a scoped
re-run is legitimate while iterating, and the second is unit-test advice that costs three redundant
fixes when four end-to-end failures share one cause.

## Standing conditions on the machine this was measured on

The gate flakes above roughly load 20, so a red result on this suite is not on its own proof of a
defect in the diff.
