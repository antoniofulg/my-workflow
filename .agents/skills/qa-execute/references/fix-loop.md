# QA fix loop

Read this reference in full when a walk finds a product defect.

## Handoff

Deduplicate the symptom, file or update the bug record, link every affected scenario, and return the
smallest clear remediation to the Implementer. Include the expected observable, observed result,
adapter, exact path, evidence, and a regression-test recommendation when the project can own one.

**Done when:** the Implementer has a bug id, reproducible path, evidence, expected result, and
affected scenario list.

## Severity route

For a Blocker or Major, end the current QA Execute session before the product changes. After the
Implementer reports the fix, a fresh Verifier runs the technical gate and retests the affected
journey plus its adjacent canary.

For a Minor, keep it in the active feature's single remediation batch. After the Implementer reports
the scoped gate, resume the same QA Execute session and re-walk the affected journey plus its
adjacent canary. The Minor batch starts no fresh Technical Verifier, QA session, or deep-review
round.

**Done when:** the severity-selected proof is recorded, the affected journey is re-walked, and the
bug and scenario statuses carry matching evidence.
