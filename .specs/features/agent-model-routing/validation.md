# Agent Model Routing Validation

**Verdict**: PASS
**Date**: 2026-08-24
**Spec**: `.specs/features/agent-model-routing/spec.md`
**Diff range**: `059cbd050ca693beccad161b7301ace577387625..a9bb3225a8a5fa1000f712bfedf394474f5563df`
**Verifier**: fresh independent Verifier, author != verifier

## Ranked Gaps

None.

## Requirement Results

| Requirement | Result | Evidence |
| --- | --- | --- |
| AMR-01 | PASS | Complete 15-setting example and native values: `tools/shared/tests/qa-skills.test.ts:521-543`; exact `mixed` profile and routes: `tools/shared/tests/workflow-config.test.ts:87-132`. |
| AMR-02 | PASS | Missing config initializes and 15 runtimes generate: `tools/test_workflow_config.py:273-285`; every destination is preflighted before writes: `.agents/skills/workflow-config/scripts/workflow_config.py:452-494`. |
| AMR-03 | PASS | Native metadata plus unchanged template/non-model bytes: `tools/test_workflow_config.py:246-268,273-285,504-530`. |
| AMR-04 | PASS | Second sync has no changed paths, reports all paths unchanged, and preserves the tree digest: `tools/test_workflow_config.py:261-265`. |
| AMR-05 | PASS | Exact delegated snapshot objects and planner omission: `tools/test_workflow_config.py:758-772`. |
| AMR-06 | PASS | Frozen resume, model/effort drift rejection, and explicit refresh: `tools/test_workflow_config.py:777-832`. |
| AMR-07 | PASS | Fresh, invalid, malformed, and customized adoption: `scripts/test_adopt.py:327-466`; root/runtime/source symlink rejection and byte preservation: `tools/test_workflow_config.py:345-501`. |
| AMR-08 | PASS | Public tracked-source/ignored-state contract: `README.md:86-103,175-186,230-233`; `docs/workflow/pack.md:27-30,52-60`. |
| AMR-09 | PASS | Ignore ownership: `.gitignore:10-13`; package/source assertions: `tools/shared/tests/workflow-config.test.ts:53-85`; adoption preservation: `scripts/test_adopt.py:327-357,435-466`. |

**Requirement result**: 9/9 verified.

## Spec-Anchored Acceptance Criteria

### Configure every agent from one file

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Tracked example supplies every provider-role model/effort and exact `mixed` routing. | `tools/shared/tests/qa-skills.test.ts:521-543` — `expect(settings.size).toBe(15)` and exact native values; `tools/shared/tests/workflow-config.test.ts:87-132` — exact four mappings and resolved routes. | PASS |
| 2 | Missing local config initializes from the example and sync generates 15 native runtimes. | `tools/test_workflow_config.py:273-285` — exact config bytes, `len(result["changed"]) == 15`, and 15 packet paths. | PASS |
| 3 | Sync leaves tracked templates byte-identical. | `tools/test_workflow_config.py:278-285,504-518` — complete template map and targeted template bytes remain equal. | PASS |
| 4 | Repeated unchanged sync is byte-identical. | `tools/test_workflow_config.py:261-265` — empty changed list, complete unchanged set, equal digest. | PASS |
| 5 | Invalid config, model, effort, template, source, or destination fails before runtime writes. | `tools/test_workflow_config.py:173-241,290-452,535-699` — exact errors plus absent initialization and unchanged runtime/outside bytes. | PASS |
| 6 | Sync reports changed and already-current paths. | `tools/test_workflow_config.py:246-265` — exact first/second changed and unchanged path sets. | PASS |

### Freeze delegated execution settings

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Resolve/refresh stores provider, file, model, and effort for every delegated role. | `tools/test_workflow_config.py:758-797` — exact role objects and refreshed values. | PASS |
| 2 | Resume returns frozen settings without reading config replacements. | `tools/test_workflow_config.py:802-812` — config changes without sync, then `assert resumed == first`. | PASS |
| 3 | Runtime model/effort drift exits with sync/refresh guidance. | `tools/test_workflow_config.py:777-797,817-832` — model and effort drift assert the exact actionable guidance. | PASS |
| 4 | Planner synchronizes but remains outside delegated provider routing. | `tools/test_workflow_config.py:273-285,758-772` — 15 packets and exact delegated-role set. | PASS |

### Adopt the centralized contract safely

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Fresh adoption installs tracked sources/local config and generates 15 matching ignored runtimes. | `scripts/test_adopt.py:327-357` — sources, ignore rules, all runtime files, exact settings. | PASS |
| 2 | Existing config remains byte-identical and drives regenerated values/instructions. | `scripts/test_adopt.py:435-466` — exact config bytes, every native setting, stripped metadata equality; `scripts/test_adopt.py:646-687` registers and executes the case. | PASS |
| 3 | Invalid local config/template exits non-zero, names the source, and makes no partial writes. | `scripts/test_adopt.py:362-430` — exact diagnostics and complete config/source/runtime equality. | PASS |
| 4 | Documentation distinguishes tracked sources from ignored operator state. | `README.md:86-103,175-186,230-233`; `docs/workflow/pack.md:27-30,52-60`. | PASS |

**Spec-anchored result**: 14/14 ACs match exact spec outcomes; 0 spec-precision gaps.

## T15-T24 Completion

| Task | Result | Independent evidence |
| --- | --- | --- |
| T15 | PASS | `.my-workflow.toml.example` plus 15 templates are tracked; local config/runtimes are untracked and ignored at `.gitignore:10-13`; package assertions: `tools/shared/tests/workflow-config.test.ts:53-85`. |
| T16 | PASS | Initialization, generation, idempotence, immutable templates, invalid-before-write, and canonical snapshot paths: `tools/test_workflow_config.py:246-285,504-699,758-832,1038-1052`. |
| T17 | PASS | Fresh, repeated, customized, and invalid adoption: `scripts/test_adopt.py:295-466`. |
| T18 | PASS | Ownership docs and Git/package contract: `README.md:86-103,175-186,230-233`; `tools/shared/tests/workflow-config.test.ts:53-85`. |
| T19 | PASS | Exact mixed profile and malformed local-config preservation: `tools/shared/tests/workflow-config.test.ts:87-132`; `scripts/test_adopt.py:392-430`. |
| T20 | PASS | Early/late destination and parent collision preflight: `.agents/skills/workflow-config/scripts/workflow_config.py:413-494`; `tools/test_workflow_config.py:290-342`. |
| T21 | PASS | Customized config drives every native value and preserves non-model bytes: `scripts/test_adopt.py:435-466`; registered at `scripts/test_adopt.py:646-687`. |
| T22 | PASS | Registry deterministically rejects missing, duplicate, or unknown tests before running all 18: `scripts/test_adopt.py:646-687`. |
| T23 | PASS | Runtime parent/destination and local config/example/template links reject before writes, including dangling destination: `tools/test_workflow_config.py:345-452`; implementation guards: `.agents/skills/workflow-config/scripts/workflow_config.py:413-438,452-494`. |
| T24 | PASS | Existing and dangling `--root` links assert exit 2, empty stdout, exact diagnostic, and no target creation/change: `tools/test_workflow_config.py:455-501`; root guard: `.agents/skills/workflow-config/scripts/workflow_config.py:452-458`. |

## Build, Baseline, Git, and Package Evidence

- **Build command**: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`.
- **Current HEAD `a9bb322`**: exit 0; 110 Vitest + 18 registered adoption + 34 resolver = 162 executed, 0 failed, 0 skipped.
- **Baseline `059cbd0` detached worktree**: exit 0; 110 Vitest + 16 invoked adoption + 28 resolver = 154 executed, 0 failed, 0 skipped.
- **Executed delta**: +8 checks; no test-count decrease.
- `git ls-files`: exactly 16 tracked sources — `.my-workflow.toml.example` plus 15 templates; no local config/runtime packet tracked.
- `git check-ignore -v`: `.my-workflow.toml` and all three runtime roots match `.gitignore:10-13`.
- `npm pack --dry-run --json`: 277 entries; all 16 sources included; 0 local config/runtime entries.
- `validate_spec.py agent-model-routing`: 0 errors, 0 warnings.
- `validate_tasks.py agent-model-routing`: 0 errors; one expected T15 `Tests: none` artifact-layer warning.
- `check_commit.py`: all 12 commits in `059cbd0..a9bb322` pass Conventional Commit validation.
- `git diff --check 059cbd0..a9bb322`: exit 0.

## Discrimination Sensor

Mutations ran only in detached temporary worktrees at `a9bb322`; all scratch worktrees were removed and pruned.

| # | Mutation | Command / observation | Result |
| --- | --- | --- | --- |
| 1 | Removed root symlink rejection at `.agents/skills/workflow-config/scripts/workflow_config.py:455-456`. | `python3 tools/test_workflow_config.py` exited 1 at `tools/test_workflow_config.py:474`; existing root link no longer returned exit 2. The canonical dangling case was also replayed with its exact assertions and exited 1 because the mutant emitted `root is not a directory` instead of the required root-symlink diagnostic. | KILLED |
| 2 | Removed source-path symlink rejection at `.agents/skills/workflow-config/scripts/workflow_config.py:435-438`. | `python3 tools/test_workflow_config.py` exited 1 at `tools/test_workflow_config.py:446`, `AssertionError: local config`. | KILLED |
| 3 | Removed runtime-destination symlink rejection at `.agents/skills/workflow-config/scripts/workflow_config.py:424-425`. | `python3 tools/test_workflow_config.py` exited 1 at `tools/test_workflow_config.py:388`, `AssertionError: packet destination`. | KILLED |

**Sensor result**: 3/3 killed. Existing and dangling root-link contracts both discriminate the root guard.

## Edge Cases and Code Quality

- Existing symlinked runtime roots/agent parents, existing and dangling packet destinations, and symlinked local config/example/template sources assert exact diagnostics and unchanged local/outside state at `tools/test_workflow_config.py:345-452`.
- Existing and dangling root symlinks assert the canonical diagnostic and containment at `tools/test_workflow_config.py:455-501`.
- Distinct checkout configs remain isolated at `tools/test_workflow_config.py:1101-1113`.
- Missing/unknown matrix entries, malformed native metadata, idempotence, Git ownership, and package exclusion have exact assertions. No assertions were weakened from baseline.
- Every in-scope test maps to a spec AC, listed edge case, or T15-T24 done-when contract. No hollow or wrong-layer case remains.
- Diff is limited to centralized configuration, adoption, local/runtime ownership, public docs, and their tests/QA state. No compatibility fallback or unrelated abstraction found.

## Isolation

- Active checkout: `/Users/antoniofulg/Projects/my-workflow-ai-memory-handoff`, branch `feat/agent-model-routing`, HEAD `a9bb3225a8a5fa1000f712bfedf394474f5563df`.
- Real checkout was never stashed. No product, config, template, or runtime source was edited by verification.
- Pre-sensor and post-cleanup porcelain both contained only `.specs/features/agent-model-routing/validation.md`; its pre-sensor SHA-256 remained `e7b6f4692b7a48da8c9ee58565f96909506b03e2fc2cb8977fe651f2b45ed5ed` until this report was overwritten.
- Baseline and mutation worktrees, including the verifier-only baseline `node_modules` link, were removed and pruned. Pre-existing worktrees were untouched.

## Summary

**Overall**: PASS. All 9 requirements, 14 acceptance criteria, and T15-T24 have direct assertion evidence. Build, baseline comparison, Git/package ownership, validators, commit checks, and all three requested containment mutants pass. No gaps remain.
