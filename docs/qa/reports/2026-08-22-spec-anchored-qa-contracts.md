# QA report — spec-anchored QA contracts

- **Date:** 2026-08-22
- **Scope:** issue #32 QA charter lifecycle, test derivation, and filed-issue dispatch contract
- **Adapter:** manual repository inspection
- **Environment:** active checkout `docs/reconcile-qa-test-contract` at `e70a8a6`
- **Gate before walk:** PASS — `npm test` (11 files passed; 145 tests passed)
- **Evidence:** `docs/qa/evidence/2026-08-22-spec-anchored-qa-contracts/session.md`

## Matrix

| Charter | Scenario | Verdict | Independent confirmation |
| --- | --- | --- | --- |
| `CH-spec-anchored-qa-contracts-2026-08-22` | `QAS-enforce-spec-anchored-qa-contracts` | pass | Reloaded committed files agree across the QA skill and three guidelines; focused `IT-022` passed |
| Adjacent provenance canary | `DOC-read-explicit-workflow-provenance` | pass | README, pack guide, both QA skill credits, and all three immutable external-skill pins were re-read |

## Result

PASS. The branch adds one dated charter and changes no existing charter. QA Plan and QA Execution
both instruct a fresh charter while QA Scenarios remains the independent immutability authority.
The test contract maps every case to an acceptance criterion, rejects component- or boundary-only
cases, and requires the spec to be clarified before such a case is added.

The filed-issue shortcut flags and walks public fixes. The general QA trigger independently keeps
purely internal refactors on technical verification only. No defect found.

## Probes

- Existing charter mutation: none; the only charter diff is one added dated file.
- QA Execution wording: new dated charter; existing charters never edited.
- QA Plan wording: new dated charter; existing charters never updated.
- QA Scenarios wording: charters immutable once written.
- Test mapping: every case maps to a spec acceptance criterion.
- Missing behaviour: acceptance criterion clarified before a case is added.
- Component/boundary-only case: forbidden; superseded wording absent.
- Public filed-issue fix: scenario flagged and walked.
- Internal refactor: technical verification only.
- Focused structural canary: `IT-022` passed (1 test; 21 skipped in the selected file).
- Provenance canary: credits, local-adaptation boundary, separate installer, and three pinned external
  security skills unchanged.

**Final gate:** PASS — `npm test` (11 files passed; 145 tests passed).

## Limitation and residue

No browser, API, mobile, server, or live agent-execution harness exists. The declared manual adapter
verified published repository contracts and the structural test, but cannot prove future model
compliance. Raw evidence remains ignored; source changes are limited to durable QA report/status
artifacts planned by this cycle.
