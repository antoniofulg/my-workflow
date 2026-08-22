# QA Execute — configurable workflow

- **Date:** 2026-08-21
- **Phase:** qa-execute
- **Persona:** Workflow adopter
- **Adapters:** resolver CLI in a checkout-local disposable Git repository; adoption CLI/manual in a separate checkout-local disposable target
- **Environment:** `feat/configurable-workflow` at `8190b8b`
- **Evidence:** `docs/qa/evidence/2026-08-21-configurable-workflow/`
- **Limitation:** No live-model harness exists; agent behavior is inspected through installed contracts and provider packets.

## Preflight

| Gate | Result |
| --- | --- |
| `validate_spec.py` | PASS — 0 errors, 0 warnings |
| `validate_tasks.py` | PASS — 0 errors, 0 warnings |
| `python3 tools/test_workflow_config.py` | PASS — 8 passed, 0 failed |
| `python3 scripts/test_adopt.py` | PASS — `ok` |
| `npm test` | PASS — 6 files, 61 tests |
| `npm run knowledge` | PASS — 0 errors, 5 warnings |

## Matrix

| Charter | Scenario | Disposition | Evidence | Independent confirmation |
| --- | --- | --- | --- | --- |
| `CH-configure-feature-workflow-2026-08-21` | `CFG-resolve-deep-review-cadence` | pass | `docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md` | JSON stdout matched the reloaded snapshot; installed policy placed final review before QA. |
| `CH-configure-feature-workflow-2026-08-21` | `CFG-route-delegated-role-providers` | pass | `docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md` | Reloaded role map and existing provider files matched override > profile > native. |
| `CH-configure-feature-workflow-2026-08-21` | `CFG-freeze-feature-workflow` | pass | `docs/qa/evidence/2026-08-21-configurable-workflow/resolver-session.md` | Checksum survived resume and forced write failure; explicit refresh and recovery replaced it successfully. |
| `CH-adopt-configurable-workflow-2026-08-21` | `ADP-adopt-workflow-safely` | pass | `docs/qa/evidence/2026-08-21-configurable-workflow/adoption-session.md` | Four independent SHA-256 checks stayed identical after re-adoption. |
| `CH-adopt-configurable-workflow-2026-08-21` | `CFG-keep-local-artifacts-out-of-git` (adjacent canary) | pass | `docs/qa/evidence/2026-08-21-configurable-workflow/adoption-session.md` | `git check-ignore` distinguished disposable paths from reviewable config and durable files. |

## Probes and debrief

Ten probe groups covered defaults, the cadence boundary matrix, mixed routing, independent reload,
resume and refresh, malformed or zero cadence inputs, unknown profiles, invalid roles/providers,
missing provider files, and atomic-write recovery. All expected outcomes were observed. Failed
resolutions produced no fallback state.

Both journeys were re-walked through comprehension, recovery, trust, speed, accessibility, and
language lenses. The resolver's forced permission failure emits a Python traceback, but the prior
snapshot remains intact and the installed skill names the exact recovery; this did not violate a
specified observable. No product defect was confirmed.

Cleanup removed both disposable targets. Source residue consists only of planned durable QA Plan
and QA Execute artifacts; raw evidence remains under the ignored evidence path.

## Final gate

| Gate | Result |
| --- | --- |
| `validate_spec.py` | PASS — 0 errors, 0 warnings |
| `validate_tasks.py` | PASS — 0 errors, 0 warnings |
| `python3 tools/test_workflow_config.py` | PASS — 8 passed, 0 failed |
| `python3 scripts/test_adopt.py` | PASS — `ok` |
| `npm test` | PASS — 6 files, 61 tests |
| `npm run knowledge` | PASS — 0 errors, 5 non-blocking warnings |

**Cycle verdict:** PASS — 5 scenario rows passed, 0 failed, 0 untested, 0 blocked, 0 bugs.
