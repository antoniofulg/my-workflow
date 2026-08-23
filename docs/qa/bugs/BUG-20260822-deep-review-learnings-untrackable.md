# BUG-20260822-deep-review-learnings-untrackable

- **Status:** fixed — retest pending
- **Severity:** major
- **Scenario:** `ADP-adopt-workflow-safely`
- **Expected:** Adoption keeps `.deep-review/learnings.md` eligible for Git even when the consumer already ignores `.deep-review/`, while generated Deep Review artifacts remain ignored.
- **Observed:** The adopted child negation could not override a consumer `.deep-review/` parent rule, so `git check-ignore -q .deep-review/learnings.md` returned `0`.
- **Adapter:** adoption CLI plus `git check-ignore`
- **Exact path:** `python3 scripts/adopt.py <checkout-local-target>`, then `git -C <target> check-ignore -q -- .deep-review/learnings.md`
- **Evidence:** pending QA retest
- **Fix commit:** pending
- **Retest:** pending

## Reproduction

1. Initialize a disposable Git target with `.deep-review/` in `.gitignore`.
2. Run `python3 scripts/adopt.py <target>`.
3. Create `.deep-review/learnings.md` and a generated artifact such as `.deep-review/review.json`.
4. Run `git check-ignore -q` for both paths.

Before the fix, both paths remain ignored because Git will not descend through the ignored parent
directory.

## Smallest remediation

Adoption adds `!.deep-review/` before the managed child patterns, preserves unrelated consumer
entries, and tests the real Git exit codes. Re-adoption must not duplicate or reorder the managed
contract.
