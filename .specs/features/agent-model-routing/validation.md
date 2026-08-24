# Agent Model Routing Validation

**Verdict**: PASS
**Date**: 2026-08-24
**Spec**: `.specs/features/agent-model-routing/spec.md`
**Diff range**: `059cbd050ca693beccad161b7301ace577387625..3a7057051e19739e0562b27534aa08ea64412f2d`
**Verifier**: fresh independent Verifier, author != verifier

## Ranked Gaps

None.

## Requirement Results

| Requirement | Result | Evidence |
| --- | --- | --- |
| AMR-01 | PASS | Complete 15-setting matrix: `tools/shared/tests/qa-skills.test.ts:521-543`; exact `mixed` profile and delegated routes: `tools/shared/tests/workflow-config.test.ts:87-132`. |
| AMR-02 | PASS | Missing local config initializes and all runtime destinations are preflighted before writes: `tools/test_workflow_config.py:240-307`. |
| AMR-03 | PASS | Native metadata, template immutability, and non-model bytes: `tools/test_workflow_config.py:213-235,312-338`. |
| AMR-04 | PASS | Second sync reports no changes and preserves the complete tree digest: `tools/test_workflow_config.py:228-232`. |
| AMR-05 | PASS | Exact delegated snapshot objects and planner omission: `tools/test_workflow_config.py:566-580`. |
| AMR-06 | PASS | Frozen resume, model/effort drift rejection, and explicit refresh: `tools/test_workflow_config.py:585-640`. |
| AMR-07 | PASS | Fresh, invalid, malformed, and customized adoption: `scripts/test_adopt.py:327-466`; exact-once canonical registry: `scripts/test_adopt.py:646-687`. |
| AMR-08 | PASS | Tracked-source and ignored-state contract: `README.md:86-103,175-186,230-233`; `docs/workflow/pack.md:27-30,52-60`. |
| AMR-09 | PASS | Ignore ownership: `.gitignore:10-13`; package/source assertions: `tools/shared/tests/workflow-config.test.ts:53-84`; adoption ignore assertions: `scripts/test_adopt.py:327-357`. |

**Requirement result**: 9/9 requirements match current product behavior.

## Spec-Anchored Acceptance Criteria

### Configure every agent from one file

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Tracked example contains 15 model/effort pairs and exact `mixed` profile. | `tools/shared/tests/qa-skills.test.ts:521-543` — `expect(settings.size).toBe(15)` and exact native values; `tools/shared/tests/workflow-config.test.ts:87-132` — exact four mappings and resolved routes. | PASS |
| 2 | Missing local config initializes from the example and sync generates 15 native runtimes. | `tools/test_workflow_config.py:240-252` — exact config bytes, `len(result["changed"]) == 15`, and 15 runtime paths. | PASS |
| 3 | Sync leaves tracked templates byte-identical. | `tools/test_workflow_config.py:245-251,312-327` — complete and targeted template byte maps remain equal. | PASS |
| 4 | Repeated unchanged sync is byte-identical. | `tools/test_workflow_config.py:228-232` — empty changed list, complete unchanged set, and equal digest. | PASS |
| 5 | Invalid config/template or destination fails before runtime writes. | `tools/test_workflow_config.py:140-208,257-307,343-359` — exact invalid paths/errors, absent local initialization, and unchanged runtime state. | PASS |
| 6 | Sync reports changed and already-current paths. | `tools/test_workflow_config.py:217-232` — exact first/second changed and unchanged sets. | PASS |

### Freeze delegated execution settings

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Resolve/refresh stores provider, file, model, and effort for every delegated role. | `tools/test_workflow_config.py:566-580,601-605` — exact role objects and refreshed values. | PASS |
| 2 | Resume returns frozen settings without reading config replacements. | `tools/test_workflow_config.py:610-620` — config changes without sync, then `assert resumed == first`. | PASS |
| 3 | Runtime model/effort drift exits with sync/refresh guidance. | `tools/test_workflow_config.py:585-605,625-640` — model and effort drift paths assert actionable guidance. | PASS |
| 4 | Planner synchronizes but remains outside delegated routing. | `tools/test_workflow_config.py:240-252,566-580` — 15 packets and exact delegated-role set. | PASS |

### Adopt the centralized contract safely

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Fresh adoption installs tracked sources/local config and generates 15 matching ignored runtimes. | `scripts/test_adopt.py:327-357` — tracked source presence, ignore checks, all runtime files, and exact settings. | PASS |
| 2 | Existing config is byte-preserved and drives regenerated native values and instruction bytes. | `scripts/test_adopt.py:435-466` — exact config bytes, every native setting, and stripped metadata equality; `scripts/test_adopt.py:646-687` registers and executes the case. | PASS |
| 3 | Invalid local config/template exits non-zero, names the source, and makes no partial writes. | `scripts/test_adopt.py:362-430` — exact diagnostics plus complete config/source/runtime byte equality. | PASS |
| 4 | Published docs distinguish tracked sources from ignored operator state. | `README.md:86-103,175-186,230-233`; `docs/workflow/pack.md:27-30,52-60`. | PASS |

**Spec-anchored result**: 14/14 ACs match exact spec outcomes; 0 spec-precision gaps.

## T15-T22 Completion

| Task | Independent result | Evidence |
| --- | --- | --- |
| T15 | PASS | `git ls-files` owns one example plus 15 templates and zero local/runtime files; `.gitignore:10-13`; package has 277 entries with all 16 tracked sources and zero local/runtime entries. |
| T16 | PASS | Initialization, generation, idempotence, immutable templates, invalid-before-write, and snapshot/resume: `tools/test_workflow_config.py:213-359,566-640`. |
| T17 | PASS | Fresh, repeated, customized, and invalid adoption: `scripts/test_adopt.py:327-466`; registry executes all 18 cases: `scripts/test_adopt.py:646-687`. |
| T18 | PASS | Ownership docs and Git/package contract: `README.md:86-103,175-186,230-233`; `tools/shared/tests/workflow-config.test.ts:53-84`. |
| T19 | PASS | Exact mixed profile and malformed local config: `tools/shared/tests/workflow-config.test.ts:87-132`; `scripts/test_adopt.py:392-430`. |
| T20 | PASS | Destination preflight and atomic collision coverage: `.agents/skills/workflow-config/scripts/workflow_config.py:413-473`; `tools/test_workflow_config.py:257-307`. |
| T21 | PASS | Customized local-config case asserts all native values/non-model bytes and is registered: `scripts/test_adopt.py:435-466,655`. |
| T22 | PASS | Registry rejects missing, duplicate, and unknown entries before deterministic execution: `scripts/test_adopt.py:646-687`; all three registry mutants were killed. |

## Build, Baseline, Git, and Package Evidence

- **Build command**: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`.
- **Current HEAD `3a70570`**: exit 0; 110 Vitest + 18 registered adoption + 31 resolver = 159 executed, 0 failed, 0 skipped.
- **Detached clean HEAD**: same Build passed; checkout started without `.my-workflow.toml` or provider runtime directories and remained Git-clean. `npm ci`: 95 packages, 0 vulnerabilities.
- **Baseline `059cbd0` detached worktree**: Build exit 0; 108 Vitest + 16 canonical adoption + 28 resolver = 152 executed, 0 failed, 0 skipped. `npm ci`: 95 packages, 0 vulnerabilities.
- **Executed delta**: +7 checks; no test-count decrease.
- `git ls-files`: exactly 16 tracked sources — `.my-workflow.toml.example` plus 15 templates; no local config/runtime packet is tracked.
- `git check-ignore -v --no-index`: `.my-workflow.toml` and all three runtime roots match `.gitignore:10-13`.
- `npm pack --dry-run --json`: 277 entries; example + 15 templates included; local config and runtime trees excluded.
- `validate_spec.py agent-model-routing`: 0 errors, 0 warnings.
- `validate_tasks.py agent-model-routing`: 0 errors, one expected warning for T15's declared `Tests: none` artifact layer.
- `check_commit.py`: all nine commits in the range pass Conventional Commit validation.
- `git diff --check 059cbd0..3a70570`: exit 0.

## Discrimination Sensor

Mutations ran only in detached temporary worktrees at `3a70570`; every worktree was removed and pruned.

| # | Mutation | Command/assertion | Result |
| --- | --- | --- | --- |
| 1 | Removed `test_existing_config_drives_all_native_values_and_preserves_non_model_bytes` from `TESTS` at `scripts/test_adopt.py:655`. | `python3 scripts/test_adopt.py` | KILLED — exit 1: `missing: test_existing_config_drives_all_native_values_and_preserves_non_model_bytes`. |
| 2 | Registered the customized case twice. | `python3 scripts/test_adopt.py` | KILLED — exit 1: `duplicate: test_existing_config_drives_all_native_values_and_preserves_non_model_bytes`. |
| 3 | Added unknown `test_registry_unknown_case`. | `python3 scripts/test_adopt.py` | KILLED — exit 1: `unknown: test_registry_unknown_case`. |
| 4 | Removed local-config and runtime `_preflight_destination` calls at `.agents/skills/workflow-config/scripts/workflow_config.py:440,458-459`. | `python3 tools/test_workflow_config.py` | KILLED — exit 1 at `tools/test_workflow_config.py:257-307` with `IsADirectoryError` on the early collision. |

**Sensor result**: 4/4 killed. PASS.

## Test Integrity and Code Quality

- Every in-scope test maps to a spec AC, edge case, or T15-T22 done-when contract; no hollow registry case remains (`docs/guidelines/TEST-CONTRACT.md:52-55,94-95`).
- Integration layer is the cheapest layer that discriminates adoption runner completeness (`docs/guidelines/TEST-CONTRACT.md:57-68`).
- No feature-scope regression, compatibility fallback, unrelated abstraction, or weakened assertion found in `059cbd0..3a70570`.
- All edge cases at `spec.md:94-100` have exact assertions or Git/package evidence.

## Isolation

- Active checkout: `/Users/antoniofulg/Projects/my-workflow-ai-memory-handoff`, branch `feat/agent-model-routing`, HEAD `3a70570`.
- Real checkout was never stashed and no product/config/runtime source was edited.
- Pre-sensor and post-cleanup porcelain match exactly: only `.specs/features/agent-model-routing/validation.md` is modified.
- Verifier-created worktrees were removed and pruned; pre-existing worktrees were untouched.

## Summary

**Overall**: PASS. 9/9 requirements and 14/14 ACs match the spec; T15-T22 are complete; Build and baseline are green; Git/package ownership holds; all four requested registry/preflight mutants are killed.
