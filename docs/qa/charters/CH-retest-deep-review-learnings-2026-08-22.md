# CH-retest-deep-review-learnings-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Adoption and Git-visibility retest
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the public adoption script and `git check-ignore`
- **Scenarios:** `ADP-adopt-workflow-safely`, adjacent canary
  `CFG-keep-local-artifacts-out-of-git`

## Mission

Adopt into a checkout-local disposable Git target whose consumer-owned `.gitignore` already ignores
`.deep-review/`. Confirm the durable learnings file remains eligible for Git, generated review
artifacts remain ignored, consumer rules survive, and re-adoption changes no bytes.

## Expected observable

Git can track `.deep-review/learnings.md`, still ignores `.deep-review/review.json`, preserves every
consumer ignore line, and leaves `.gitignore` byte-identical after re-adoption.

## Planned probes

- Initialize a disposable Git target with `.deep-review/` and an unrelated consumer rule.
- Run the documented adoption command and create `learnings.md` plus one generated review artifact.
- Inspect both paths independently with `git check-ignore` and record their exit codes.
- Confirm the unrelated consumer rule and the managed Deep Review rules each occur once.
- Re-adopt and compare the complete `.gitignore` bytes with the pre-re-adoption copy.
- Adjacent canary: confirm generated Deep Review artifacts remain ignored.

End before product remediation. A confirmed defect returns to an Implementer.
