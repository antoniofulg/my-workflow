# Approved Review Loop Decisions

## Human decisions

| Choice | Why | Alternatives rejected | Change cost now | User cost today |
| --- | --- | --- | --- | --- |
| Move the work to a branch, merge it, and publish a `0.3.x` bugfix release | Explicit request in this session | Leave commits local or defer release | Low | Agents can keep asking for redundant approval |

## Run decisions

| Choice | Why | Alternatives rejected | Change cost now | User cost today |
| --- | --- | --- | --- | --- |
| Use `fix/approved-review-loop` | Names the corrected behavior and follows branch policy | Reuse merged `feat/qa-skills`; work on `main` | Low | None |
| Release `0.3.1` | Current published version is `0.3.0`; patch is the next bugfix version | Another minor; overwrite `0.3.0` | Low | None |
| Include the version bump in the same PR | Keeps one PR for this run and tags the merged, gated tree | Separate release PR or direct `main` commit | Low | None |
| Leave the deep-review trivial advisory in the PR follow-up list | Review policy says advisories do not trigger another round | Expand the remediation loop for a non-blocker | Low | One redundant remote-authority reminder remains |
