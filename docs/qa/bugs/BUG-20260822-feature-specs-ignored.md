# BUG-20260822-feature-specs-ignored

- **Status:** untested
- **Severity:** major
- **Scenario:** `CFG-keep-local-artifacts-out-of-git`; `ADP-adopt-workflow-safely`
- **Expected:** `.specs/features/` is versioned workflow state. Fresh adoption leaves feature files
  visible to Git and removes only duplicate exact legacy `.specs/features/` ignore lines from an
  existing target, without staging or committing files.
- **Observed:** The source pack and adoption script add `.specs/features/` to `.gitignore`, so fresh
  feature state is hidden from Git; adoption does not migrate the legacy line.
- **Adapter:** `scripts/adopt.py`, `scripts/test_adopt.py`, and Git visibility inspection
- **Exact path:** `python3 scripts/adopt.py <target>`, then `git -C <target> check-ignore --no-index --quiet -- .specs/features/example/spec.md`
- **Evidence:** untested
- **Fix commit:** pending
- **Retest:** untested

## Reproduction

1. Run adoption against a fresh disposable Git target.
2. Create `.specs/features/example/spec.md`.
3. Run `git check-ignore --no-index --quiet -- .specs/features/example/spec.md`.
4. Repeat with a target containing duplicate exact `.specs/features/` lines plus consumer comments
   and unrelated rules.

The fresh feature file is ignored, and the legacy target retains the managed lines after adoption.

## Smallest remediation

Stop shipping `.specs/features/` in the managed ignore contract. During adoption, remove only exact
legacy managed lines, preserve all other target content, and leave file staging/committing to the
consumer.
