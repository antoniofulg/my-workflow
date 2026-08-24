# Agent Model Routing Validation

**Verdict**: PASS
**Date**: 2026-08-24
**Spec**: `.specs/features/agent-model-routing/spec.md`
**Diff range**: `059cbd050ca693beccad161b7301ace577387625..8b06f5c1f91381a769d09b232f78f06ca2ca7a60`
**Re-verification fix**: `8b06f5c1f91381a769d09b232f78f06ca2ca7a60`
**Verifier**: fresh independent Verifier, author != verifier

## Ranked Gaps

None. The former shipped-`profiles.mixed` and malformed-local-config adoption gaps now have direct,
discriminating canonical assertions.

## Requirement Results

| Requirement | Result | Evidence |
| --- | --- | --- |
| AMR-01 | PASS | Complete 15-setting matrix: `tools/shared/tests/qa-skills.test.ts:521-543`; exact shipped `mixed` map and public resolution: `tools/shared/tests/workflow-config.test.ts:87-132`. |
| AMR-02 | PASS | Missing local config initialization and 15 generated runtimes: `tools/test_workflow_config.py:240-252`. |
| AMR-03 | PASS | Template-driven native rendering and byte preservation: `tools/test_workflow_config.py:213-235,257-283,475-506`. |
| AMR-04 | PASS | Second sync reports no changes and preserves the tree digest: `tools/test_workflow_config.py:228-232`. |
| AMR-05 | PASS | Snapshot stores exact delegated provider/file/model/effort and omits planner: `tools/test_workflow_config.py:511-525`. |
| AMR-06 | PASS | Frozen resume, model/effort drift rejection, and explicit refresh: `tools/test_workflow_config.py:530-585`. |
| AMR-07 | PASS | Fresh/preserved/template-invalid adoption: `scripts/test_adopt.py:295-387,435-466`; malformed local config, exact diagnostic, and full no-partial-write snapshot: `scripts/test_adopt.py:392-430`. |
| AMR-08 | PASS | Public ownership contract: `README.md:86-103,180-186,230-233` and `docs/workflow/pack.md:27-30,52-60`; Build gate green. |
| AMR-09 | PASS | Git/package assertions: `tools/shared/tests/workflow-config.test.ts:53-84`; fresh-adoption ignores: `scripts/test_adopt.py:327-357`. |

**Requirement result**: 9/9 verified.

## Spec-Anchored Acceptance Criteria

### Configure every agent from one file

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Tracked example has 15 model/effort pairs and exact `mixed` profile. | `tools/shared/tests/qa-skills.test.ts:521-543` asserts all 15 settings; `tools/shared/tests/workflow-config.test.ts:87-132` asserts the exact four shipped mappings and resolved providers; `tools/shared/tests/workflow-config.test.ts:53-84` asserts tracking/packaging. | PASS |
| 2 | Missing local config initializes from example; sync generates all 15 native runtimes. | `tools/test_workflow_config.py:240-252` asserts exact copied bytes, 15 changed paths, 15 runtime files, and unchanged templates. | PASS |
| 3 | Sync leaves every tracked template byte unchanged. | `tools/test_workflow_config.py:245-251,257-283` asserts complete template byte maps and individual template bytes remain identical. | PASS |
| 4 | Repeated unchanged sync is byte-identical. | `tools/test_workflow_config.py:228-232` asserts empty changed paths, complete unchanged paths, and equal tree digest. | PASS |
| 5 | Invalid local config, matrix, effort, or template fails before runtime writes. | `tools/test_workflow_config.py:140-185,288-305,309-321,342-371` asserts exact failures and unchanged runtime maps. | PASS |
| 6 | Sync reports changed and already-current packet paths. | `tools/test_workflow_config.py:217-232` asserts exact changed/unchanged path sets on first and second sync. | PASS |

### Freeze delegated execution settings

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Resolve/refresh stores selected model and effort for every delegated role. | `tools/test_workflow_config.py:511-525,530-550` asserts exact role objects and refreshed values. | PASS |
| 2 | Resume returns frozen settings without reading config replacements. | `tools/test_workflow_config.py:555-565` changes config without sync and asserts the resumed snapshot equals the original. | PASS |
| 3 | Runtime model/effort drift exits non-zero with sync/refresh guidance. | `tools/test_workflow_config.py:530-550,570-585` asserts both drift paths and exact actionable guidance. | PASS |
| 4 | Planner synchronizes but remains outside delegated routing. | `tools/test_workflow_config.py:240-252,511-525` asserts 15 packets and the exact delegated-role set. | PASS |

### Adopt the centralized contract safely

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Fresh adoption installs sources/local config and generates 15 matching ignored runtimes. | `scripts/test_adopt.py:327-357` asserts source presence, four ignored local paths, every runtime, and exact native settings. | PASS |
| 2 | Existing local config is byte-preserved; runtimes regenerate from preserved templates/config. | `scripts/test_adopt.py:295-322,435-466` asserts disposable runtime replacement, config/template preservation, and all-provider metadata/body parity. | PASS |
| 3 | Invalid local config or template exits non-zero, names the source, and makes no partial runtime writes. | Template: `scripts/test_adopt.py:362-387`; malformed local config: `scripts/test_adopt.py:392-430` asserts exit 1, empty stdout, exact source-bearing diagnostic, whole-tree equality, and config/source/runtime byte equality. | PASS |
| 4 | Published docs distinguish tracked sources from ignored operator state. | `README.md:86-103,180-186,230-233`; `docs/workflow/pack.md:27-30,52-60`. | PASS |

**Spec-anchored result**: 14/14 ACs matched; 0 spec-precision gaps.

## Edge Cases

| Edge case | Result | Evidence |
| --- | --- | --- |
| Missing provider/role/model/effort and unknown keys fail with paths | PASS | `tools/test_workflow_config.py:140-208`. |
| Missing/duplicate native metadata fails before writes | PASS | `tools/test_workflow_config.py:288-305,342-371,419-455`. |
| Distinct checkouts retain isolated local settings | PASS | `tools/test_workflow_config.py:854-866`. |
| Local config/runtime trees ignored; example/templates tracked and packaged | PASS | `tools/shared/tests/workflow-config.test.ts:53-84`; independent ownership commands below. |

## Task Completion

| Task | Independent result | Evidence |
| --- | --- | --- |
| T1-T14 | PASS | Existing canonical resolver/adoption assertions remain green in the Build gate; key branches cited in the AC and edge-case tables above. |
| T15 | PASS | Exact tracked set is one example plus 15 templates; local config/runtimes are ignored and excluded from the 277-file package. Assertions: `tools/shared/tests/workflow-config.test.ts:53-84`. |
| T16 | PASS | Initialization, 15-packet generation, immutable templates, idempotence, canonical paths, and invalid-before-write: `tools/test_workflow_config.py:213-371,775-805`. |
| T17 | PASS | Fresh/repeated/customized/invalid adoption and local ownership: `scripts/test_adopt.py:295-466`. |
| T18 | PASS | Contract/package tests cover exact mixed routing and ownership: `tools/shared/tests/workflow-config.test.ts:53-132`; published docs cited above; QA remains a separate phase. |
| T19 | PASS | Former gaps are directly asserted at `tools/shared/tests/workflow-config.test.ts:87-132` and `scripts/test_adopt.py:392-430`; both fresh mutants were killed. |

## Ownership and Packaging Evidence

- `git ls-files -- .my-workflow.toml .my-workflow.toml.example templates/agents .claude/agents .codex/agents .cursor/agents`: exactly 16 tracked sources (example + 15 templates); no local config/runtime packet tracked.
- `git check-ignore -v --no-index .my-workflow.toml .claude/agents/planner.md .codex/agents/planner.toml .cursor/agents/planner.md`: all four match `.gitignore:10-13`.
- `npm pack --dry-run --json`: exit 0, 277 entries; includes example and 15 templates; excludes local config and all three runtime trees.

## Build Gate and Baseline Integrity

- **Build command**: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
- **Current HEAD `8b06f5c`**: exit 0; 110 Vitest + 18 adoption + 30 resolver = 158 passed, 0 failed, 0 skipped.
- **Baseline `059cbd0`**: identical command in detached `/tmp/amr-baseline-*` with checkout-local source and linked dependency tree; exit 0; 108 Vitest + 17 adoption + 28 resolver = 153 passed, 0 failed, 0 skipped.
- **Delta**: +5 checks; no decrease.
- `validate_spec.py agent-model-routing`: 0 errors, 0 warnings.
- `validate_tasks.py agent-model-routing`: 0 errors, 1 expected warning (`T15` declares no tests; its matrix layer is `none` and independently verified above).
- `check_commit.py` against `8b06f5c` message: OK.
- `git diff --check 059cbd0..8b06f5c`: exit 0.

## Discrimination Sensor

Mutations ran only in detached `/tmp/amr-mutant-reverify-*`; baseline and mutant worktrees were removed afterward.

| # | Mutation | Canonical assertion | Result |
| --- | --- | --- | --- |
| 1 | Drifted shipped `profiles.mixed.verifier` from `codex` to `claude`. | `tools/shared/tests/workflow-config.test.ts:87-132` | KILLED: exact shipped-map assertion failed at line 89. |
| 2 | Made adoption ignore a non-zero resolver result, allowing malformed local config to continue. | `scripts/test_adopt.py:392-430` | KILLED: targeted test failed at line 418 with `expected malformed local config rejection`. |

**Sensor result**: 2/2 killed. Real checkout porcelain before and after remained exactly
` M .specs/features/agent-model-routing/validation.md`; no scratch worktree remains.

## Code Quality and QA Impact

| Check | Result |
| --- | --- |
| Minimum code / standard library | PASS: T19 adds assertions and fixtures only; no dependency or product abstraction. |
| Surgical remediation | PASS: fix commit changes only `tasks.md` and the two canonical suites. |
| Test layer | PASS: shipped config/public resolver contract is in the workflow-config contract suite; adoption behavior is in the adoption integration suite. |
| Test discrimination | PASS: both former gaps fail under their matching behavior-level mutations. |
| QA dispatch | Required because CLI, public configuration, adoption, and docs-as-interface changed. This technical packet did not execute QA. |

## Summary

**Overall**: PASS. All 9 requirements and 14 acceptance criteria have file:line evidence, the Build
gate and revised baseline comparison are green, ownership/package boundaries hold, and both former
coverage gaps now kill matching mutants.
