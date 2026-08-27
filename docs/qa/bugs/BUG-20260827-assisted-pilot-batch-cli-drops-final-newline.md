# BUG-20260827-assisted-pilot-batch-cli-drops-final-newline

- **Status:** open
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** The integrated mini CLI preserves newline-delimited output framing and passes grouped Deep Review before final persona QA.
- **Observed:** `python -m pilot.batch` receives stdin ending in `\n` but writes normalized records without the final delimiter; grouped Deep Review returned `FIX_BEFORE_SHIP` with this sole open Major.
- **Adapter:** Installed Orca `1.4.190` assisted CLI/manual flow with Luna-medium workers
- **Exact path:** conflict-free A/B implementation -> per-slice Technical Verification -> deterministic A-then-B integration -> grouped Deep Review
- **Evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-8/deep-review-result.md`

## Impact

The inter-slice coordination flow reached and preserved every stage through deterministic
integration, but readiness correctly stopped before final persona QA. Newline-oriented downstream
consumers would observe changed record framing for a valid newline-terminated input.

## Required fix and retest

Preserve a final newline when stdin has one and add a focused subprocess assertion. An Implementer
must fix the disposable fixture behavior, then a fresh QA Verifier must resume grouped Deep Review,
final CLI persona QA, fixture full gate, and exact cleanup. This bug makes no automatic Orca
compatibility claim.
