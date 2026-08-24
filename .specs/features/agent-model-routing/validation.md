# Agent Model Routing Validation

**Verdict**: PASS
**Round**: User-authorized post-cap technical re-verification after cadence remediation
**Date**: 2026-08-24
**Spec**: `.specs/features/agent-model-routing/spec.md`
**Diff range**: `8368392..c02de27027fe93835a6af16207c53014c57c974b`
**Remediation under review**: `c02de27`
**Verifier**: fresh independent Verifier, author != verifier

## Task Completion

| Task | Recorded status | Verification status |
| --- | --- | --- |
| T1-T9 | complete | All 14 feature AC outcomes have direct assertions; both post-cap root causes are resolved and discriminating. |

## Prior-Finding Disposition

| Prior root cause | Current result |
| --- | --- |
| Frozen snapshot `agent_file` ownership was not discriminated. | RESOLVED. `tools/test_workflow_config.py:615-652` gives a wrong-role packet matching frozen metadata, distinguishes invalid ownership from a missing allowed path, and preserves snapshot bytes. Removing `.agents/skills/workflow-config/scripts/workflow_config.py:399-401` makes the ownership assertion fail at `tools/test_workflow_config.py:649`. |
| Configured cadence was tested only through `balanced_groups()`. | RESOLVED. `tools/test_workflow_config.py:551-576` varies `slice`, `feature`, `grouped.2`, and `grouped.4` through the public CLI and asserts exact CLI JSON plus persisted `workflow.json`. Forcing `.agents/skills/workflow-config/scripts/workflow_config.py:100-102` to return the default makes the test fail at `tools/test_workflow_config.py:574`. |

## Spec-Anchored Acceptance Criteria

### Configure every agent from one file

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | One model and effort for 3 providers x 5 roles. | `tools/test_workflow_config.py:109-117` asserts each parsed provider-role setting equals the matrix; `tools/shared/tests/qa-skills.test.ts:521-527` asserts exactly 15 configured settings. | PASS |
| 2 | Sync renders each configured value in provider-native syntax. | `tools/test_workflow_config.py:195-209` asserts exact Claude, Cursor, and Codex metadata; `tools/shared/tests/qa-skills.test.ts:529-544` compares every packet with the central matrix. | PASS |
| 3 | Sync preserves every non-model packet byte. | `tools/test_workflow_config.py:215-217,222-229` strips only generated metadata and byte-compares all 15 packets. | PASS |
| 4 | A second unchanged sync is byte-identical. | `tools/test_workflow_config.py:210-214` asserts no changed paths, all expected unchanged paths, and an unchanged tree digest. | PASS |
| 5 | Invalid matrix, effort, or packet metadata exits non-zero before writes. | `tools/test_workflow_config.py:122-168` asserts matrix and effort failures with exact paths; `tools/test_workflow_config.py:234-250,288-312` asserts malformed/duplicate metadata and invalid config preserve all packets; `tools/test_workflow_config.py:255-267` asserts public exit 2 and empty stdout. | PASS |
| 6 | Sync reports changed and already-current packet paths. | `tools/test_workflow_config.py:198-214` asserts exact 15-path `changed` and `unchanged` sets. | PASS |

### Freeze delegated execution settings

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | First resolve and refresh store model/effort for every delegated role. | `tools/test_workflow_config.py:317-331` asserts complete delegated records; `tools/test_workflow_config.py:352-356` asserts refreshed model and effort. | PASS |
| 2 | Resume returns frozen settings without reading config replacements. | `tools/test_workflow_config.py:361-371` changes config and resolution arguments, then asserts resumed snapshot equality. | PASS |
| 3 | Model or effort drift exits non-zero with sync and explicit-refresh guidance. | `tools/test_workflow_config.py:336-356,376-391` independently assert model and effort drift plus exact guidance. | PASS |
| 4 | Planner synchronizes but remains non-delegated. | `tools/test_workflow_config.py:317-331` asserts the delegated role set; `tools/test_workflow_config.py:462-477` rejects planner routing. | PASS |

### Adopt the centralized contract safely

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Fresh adoption installs v2 config and 15 matching packet settings. | `scripts/test_adopt.py:324-339` asserts version 2, packet existence, and every native setting against installed config. | PASS |
| 2 | Existing config and packet instructions remain byte-identical while metadata follows that config. | `scripts/test_adopt.py:364-394` byte-compares config and stripped packet bodies, then checks every packet setting against target config. | PASS |
| 3 | Unsynchronizable adoption exits non-zero and names the invalid packet. | `scripts/test_adopt.py:344-359` asserts exit 1, `verifier` in stderr, and malformed packet preservation. | PASS |
| 4 | Documentation names the central source and generated native fields. | `README.md:86-99` names the single editable source and generated fields; `docs/workflow/pack.md:51-57` states adoption synchronizes from `.my-workflow.toml`. | PASS |

**Spec-anchored result**: 14/14 acceptance criteria matched; 0 spec-precision gaps.

## Edge Cases

- Missing provider, role, model, and effort: `tools/test_workflow_config.py:122-165`. PASS.
- Unknown matrix key: `tools/test_workflow_config.py:128-134,172-190`. PASS.
- Duplicate or missing packet metadata with validation before writes: `tools/test_workflow_config.py:234-250,288-312`. PASS.
- Wrong-role frozen path with matching metadata and missing allowed candidate: `tools/test_workflow_config.py:615-652`. PASS.
- Distinct checkout isolation: `tools/test_workflow_config.py:657-666`. PASS.
- Configured cadence ownership for `slice`, `feature`, `grouped.2`, and `grouped.4`: `tools/test_workflow_config.py:551-576`. PASS.

## Build Gate

- **Command at current HEAD**: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
- **Current result**: exit 0; 108 Vitest tests + 17 adoption test functions + 23 resolver test functions = 148 passed, 0 failed, 0 skipped.
- **Command at baseline `8368392`**: same Build command in a detached disposable worktree, with its `node_modules` linked to the active checkout dependency tree.
- **Baseline result**: exit 0; 108 Vitest tests + 14 adoption test functions + 11 resolver test functions = 133 passed, 0 failed, 0 skipped.
- **Count command**: `rg -c '^def test_' scripts/test_adopt.py tools/test_workflow_config.py`, plus the same files read from `git show 8368392:<path>`.
- **Delta**: +15 test functions/cases; no test-count decrease.
- **Other checks**: task validator exit 0 with 0 errors and 0 warnings; `git diff --check 8368392..HEAD` exit 0.
- **Warnings**: none from test runners. Adoption printed expected refusal and external-security instructions in smoke cases.

## Baseline Test Integrity

PASS. Baseline and current Build gates both pass. Vitest stayed at 108 tests; adoption grew from 14 to 17 test functions; resolver coverage grew from 11 to 23. No skip/disable mechanism occurs in the changed canonical suites. The prior baseline cadence chain at `8368392:tools/test_workflow_config.py:100-141` is restored at `tools/test_workflow_config.py:551-576` with exact public JSON and persisted snapshot assertions for all four required cadence values. Review of the renamed/split baseline resolver and adoption cases found no weakened outcome assertion.

## Discrimination Sensor

All mutations ran only in detached disposable worktrees removed after each run.

| # | Mutation | Scoped command | Result |
| --- | --- | --- | --- |
| 1 | Changed `_cadence()` at `workflow_config.py:100-102` to ignore configured values and return `CADENCE_DEFAULT`. | Direct call to `test_cli_loads_configured_cadence_into_json_and_snapshot` | KILLED, exit 1 at `tools/test_workflow_config.py:574`. |
| 2 | Removed provider-role ownership validation at `workflow_config.py:399-401`. | Direct call to `test_invalid_frozen_agent_paths_exit_two_without_snapshot_mutation` | KILLED, exit 1 at `tools/test_workflow_config.py:649`. |
| 3 | Removed resumed packet model/effort drift rejection at `workflow_config.py:410-415`. | Direct call to `test_resume_rejects_drift_and_refresh_freezes_new_settings` | KILLED, exit 1 at `tools/test_workflow_config.py:351`. |

**Sensor result**: 3/3 killed. Real-tree porcelain before and after each cleanup was identical: only `?? .specs/features/agent-model-routing/validation.md`.

## Code Quality

| Check | Result |
| --- | --- |
| Minimum implementation; no speculative abstraction | PASS |
| Surgical cadence remediation | PASS |
| All 14 feature ACs have exact outcome assertions | PASS |
| Config -> public CLI JSON -> persisted snapshot cadence discrimination | PASS |
| Frozen agent ownership discrimination | PASS |
| Baseline test integrity | PASS |
| Every in-scope test maps to a spec AC, listed edge case, or task done-when | PASS |
| Guidelines | PASS against `docs/guidelines/TEST-CONTRACT.md`, `docs/guidelines/GATES.md`, `docs/guidelines/VERIFICATION-EVIDENCE.md`, and `docs/guidelines/REVIEW-ROUNDS.md`. |

## Requirement Traceability

| Requirement | Verdict |
| --- | --- |
| AMR-01 through AMR-08 | Verified. |
| Post-cap frozen ownership remediation | Verified and discriminating. |
| Post-cap configured cadence remediation | Verified and discriminating. |
| Cross-cutting baseline integrity | Verified. |

## QA Disposition

The diff changes public CLI, configuration, adoption, documentation, and resume behavior. This session executed only the technical phase. QA Plan and QA Execute remain separate fresh Verifier phases under existing project QA artifacts.

## Summary

**Overall**: PASS, no new gaps.

All 14 ACs match spec outcomes. Build gate passes 148 checks. Baseline gate passes 133 checks with no count decrease. Configured cadence now crosses config -> public resolver JSON -> persisted snapshot for `slice`, `feature`, `grouped.2`, and `grouped.4`. Frozen ownership remains discriminated. All three fresh scratch mutants were killed.
