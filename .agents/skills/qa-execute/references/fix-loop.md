# QA fix loop

Read this reference in full when a walk finds a product defect.

## Handoff

Deduplicate the symptom, file or update the bug record, link every affected scenario, and return the
smallest clear remediation to the Implementer. Include the expected observable, observed result,
adapter, exact path, evidence, and a regression-test recommendation when the project can own one.

**Done when:** the Implementer has a bug id, reproducible path, evidence, expected result, and
affected scenario list.

## Fresh verification

End the current QA execution session before the product changes. After the Implementer reports the
fix, a fresh Verifier runs the technical gate and retests the affected journey plus its adjacent
canary. QA then resumes from the affected charter and records the retest result in the original
report.

**Done when:** the fix has a fresh Verifier result, the affected journey is re-walked, and the bug
and scenario statuses carry matching evidence.
