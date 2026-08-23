# CH-upsert-deep-review-walkthrough-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 15 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-deep-review`](../journeys/J-run-deep-review.md)
- **Tour:** Walkthrough publication branch and adjacent Deep Review canary
- **Public entry point:** `.agents/skills/deep-review/references/publish-github.md`
- **Adapter candidate:** CLI/manual with the checkout-local fake `gh` owned by `tools/test_deep_review_contract.py`
- **Scenarios:** `QAS-upsert-deep-review-walkthrough`, `QAS-observe-serialized-deep-review-metrics`

## Mission

Run the documented walkthrough recipe twice against a disposable local fixture: once with no
marker id and once with an existing id. Inspect the fake `gh` log, then confirm the adjacent Deep
Review execution contract remains available.

## Expected observable

The absent-marker run lists comments and performs one POST; the existing-marker run lists comments
and performs one PATCH to that id. Neither run performs both mutations or contains `/comments/null`.

## Planned probes

- Extract the public bash recipe from its documented entry point without copying it into QA.
- Put the fake `gh` first on `PATH` and record every argument in checkout-local evidence.
- Return no id and confirm exactly one create call follows the list call.
- Return id `42` and confirm exactly one PATCH follows the list call.
- Search both logs for a second mutation and `/comments/null`.
- Run the existing Deep Review contract command as the adjacent canary.

End before any network request, product fix, or remote mutation.
