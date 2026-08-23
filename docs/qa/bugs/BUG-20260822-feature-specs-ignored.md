# BUG-20260822-feature-specs-ignored

- **Status:** fixed — retest passed
- **Severity:** major
- **Scenario:** `CFG-keep-local-artifacts-out-of-git`; `ADP-adopt-workflow-safely`
- **Expected:** `.specs/features/` is versioned workflow state. Fresh adoption leaves feature files
  visible to Git and removes only duplicate exact legacy `.specs/features/` ignore lines from an
  existing target, without staging or committing files.
- **Observed:** The source pack and adoption script add `.specs/features/` to `.gitignore`, so fresh
  feature state is hidden from Git; adoption does not migrate the legacy line.
- **Adapter:** `scripts/adopt.py`, `scripts/test_adopt.py`, and Git visibility inspection
- **Exact path:** `python3 scripts/adopt.py <target>`, then `git -C <target> check-ignore --no-index --quiet -- .specs/features/example/spec.md`
- **Evidence:** `docs/qa/evidence/2026-08-22-version-feature-state-by-default/session.md`
- **Fix commit:** `a7397d2`; `43e9910`; `a3fc718`
- **Retest:** passed on 2026-08-22 through fresh and duplicate legacy adoption, Git visibility,
  idempotence, index/HEAD preservation, sibling worktree, and clean-clone inspection

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

## Fix awaiting retest

`a7397d2` changes the public policy and adoption migration, while `43e9910` and `a3fc718` version the
existing feature workflow state. Fresh QA confirmed the public observable and both independent Git
handoff paths.
