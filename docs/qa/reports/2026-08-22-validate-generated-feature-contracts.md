# QA Report: Validate Generated Feature Contracts

- **Date:** 2026-08-22
- **Scope:** issue #39
- **Adapter:** CLI/manual
- **Environment:** active checkout with a checkout-local disposable adoption target
- **Preflight gate:** `python3 -m unittest tools.test_tlc_validators` — 5 passed, 0 failed
- **Final relevant gate:** `python3 tools/test_tlc_validators.py` — 5 passed, 0 failed
- **Final full gate:** `npm test` — 10 files and 139 tests passed, 0 failed
- **Raw evidence:** `docs/qa/evidence/2026-08-22-validate-generated-feature-contracts/session.md`

## Matrix

| Charter | Scenario | Verdict | Evidence |
| --- | --- | --- | --- |
| `CH-validate-generated-feature-contracts-2026-08-22` | `ADP-validate-generated-feature-contracts` | pass | `docs/qa/evidence/2026-08-22-validate-generated-feature-contracts/session.md` |
| Adjacent adoption canary | `ADP-adopt-workflow-safely` | pass | `docs/qa/evidence/2026-08-22-validate-generated-feature-contracts/session.md` |

## Results

- Fresh adoption installed both public validator CLIs into the disposable target.
- Nested phase definitions exited 0 with only the documented manual diagram warning.
- Phase diagrams with later task definitions exited 0 without warnings.
- A future-phase dependency exited 1 and named `T2`, phase 1, `T3`, and phase 2.
- The annotated acceptance-criteria heading plus its blank line exited 0 without warnings.
- A criterion without `SHALL` exited 1 and identified line 25.
- Re-adoption preserved two consumer-owned sentinel files and replaced neither validator with stale
  bytes; representative success and refusal probes retained their results in fresh processes.

## Tour and lenses

- **Comprehension/language:** success summaries and refusal diagnostics named the checked file and
  decisive contract error.
- **Recovery/trust:** invalid files returned non-zero without modifying them; correcting the input is
  the visible recovery path.
- **Speed:** all validator processes completed within the command runner's sub-second wall time.
- **Accessibility:** not applicable to this CLI-only surface; output is plain text with no visual-only
  signal.

## Limitations

The nested-layout validator emits its existing manual diagram cross-check warning because that
layout has no fenced diagram. This is expected and does not weaken its zero-error result. No browser,
API, mobile, auth, or server surface exists for this package.

## Verdict

Both scenarios pass. No product defect found; no bug record created.
The disposable adopted target was removed after the walk; raw evidence remains checkout-local.
