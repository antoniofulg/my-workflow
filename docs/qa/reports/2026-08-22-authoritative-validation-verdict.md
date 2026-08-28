# QA report — authoritative validation verdict

- **Date:** 2026-08-22
- **Adapter:** CLI/manual
- **Environment:** active checkout, checkout-local disposable adoption target
- **Public path:** adopted `.agents/skills/workflow-spec-driven/scripts/validate_state.py`
- **Preflight gate:** `npm test` — 142/142 passed
- **Evidence:** `docs/qa/evidence/2026-08-22-authoritative-validation-verdict/session.md`
- **Limitation:** no browser, API, mobile, auth, server, or production runtime exists for this pack

## Matrix

| Charter | Scenario | Verdict | Observable | Evidence |
| --- | --- | --- | --- | --- |
| `CH-validate-feature-completion-state-2026-08-22` | `ADP-validate-feature-completion-state` | pass | FAIL-over-PASS exited 1; PASS-over-FAIL and legacy Result PASS exited 0 in separate processes. | `docs/qa/evidence/2026-08-22-authoritative-validation-verdict/session.md` |
| Adjacent adoption canary | `ADP-adopt-workflow-safely` | pass | Re-adoption exited 0; consumer config SHA-256 remained identical and installed validator matched source bytes. | `docs/qa/evidence/2026-08-22-authoritative-validation-verdict/session.md` |

## Walk and independent confirmation

The workflow was adopted into a checkout-local disposable target. The adopted CLI was invoked in a
fresh Python process for each report form. Its exit code and terminal diagnostic independently
confirmed the selected verdict. Re-adoption provided the reload canary: the consumer sentinel hash
stayed `f0052271548bdf293cb26187d5a7bce9844b9a841378955b675039911cc41b26`, and the adopted
validator hash matched the source at
`b117eb104c0a237d3d92d6fb5e86add31e750da1dfab501acc29301724b7a26f`.

## Edge probes

Five probes passed: plain lower-case verdict with punctuation, PASS/FAIL words in prose, explicit
placeholder fail-closed behavior, legacy killed-summary PASS, and malformed explicit verdict
fail-closed behavior. No retry was needed.

## Debrief

Both scenarios passed. No product defect, bug record, inaccessible leg, or human-only verification
remains. The package has no browser, API, mobile, auth, server, or production runtime surface.

## Final gate

`npm test` — 11/11 files and 142/142 tests passed after the QA artifact updates.
