# Optional Design Tools Validation

**Date**: 2026-08-23
**Spec**: inline acceptance contract supplied to the independent Verifier; no feature `spec.md` exists
**Diff range**: `7f3a462b74eab6de1c5a65e898d20e09faaa517c..7e14332c9394bb64b0cb2b2be5f2eadd76b9a6e6`
**Verifier**: independent sub-agent (author != verifier)

## Verdict

**PASS**

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| AC-1: optional, agnostic integrations | Graft and OpenDesign remain optional; adoption installs neither; absence or failure keeps honest repository fallbacks | `tools/shared/tests/qa-skills.test.ts:494` — stack/tool agnosticism; `:495-497` — both tools named and no mandatory adoption; `:501` — OpenDesign fallback. Existing Graft behavior is asserted by `tools/test_deep_review_token_metrics.py:425-429` and `:435-480`. | PASS |
| AC-2: repository-owned visual handoff | OpenDesign may iterate externally; repository owns the approved handoff; precedence is `spec.md` then `uiux.md`, approved artifact, tool/plugin output, legacy mockup | `tools/shared/tests/qa-skills.test.ts:498-501` — exact handoff, precedence, legacy order, and fallback assertions | PASS |
| AC-3: safe external filesystem writers | Isolate or explicitly allow directories; validate paths and symlinks before first write; preserve destination-only content; never delete automatically | `tools/shared/tests/qa-skills.test.ts:502-504` — exact isolation, validation, and no-delete assertions; policy at `docs/guidelines/SECURITY.md:17-21` | PASS |
| AC-4: operational details stay out | README/guidelines contain no concrete OpenDesign daemon address, port, CLI command, or version; README routes such details to the relevant skill | `README.md:145-146` — routing rule. Negative scan over `README.md`, `UI-UX.md`, and `SECURITY.md` found no concrete OpenDesign operational detail. | PASS |
| AC-5: durable decision and frozen route | AD-006 records the trade-off; index is current; prior decisions and Handoff are unchanged; frozen snapshot selects Codex Verifier | `tools/shared/tests/qa-skills.test.ts:505-508` — AD-006 and both recommendations; `.specs/AD-INDEX.md:15` — indexed decision; `.specs/features/optional-design-tools/workflow.json:10-29` — feature and Codex roles. `python3 tools/ad-index.py --check` passed, and a prefix comparison against `origin/main:.specs/STATE.md` proved prior state unchanged. | PASS |

**Status**: 5/5 criteria matched defined outcomes.

## Discrimination Sensor

One temporary worktree at `7e14332` held every mutation. Each mutation ran the canonical scoped Vitest suite independently, then was reversed before the next. The scratch was removed; real `git status --porcelain=v1` matched the captured baseline byte-for-byte.

| Mutation | Target | Fault | Result |
| --- | --- | --- | --- |
| M1 | `README.md:145` | Changed optional adoption to mandatory installation | KILLED — IT-023 failed at `tools/shared/tests/qa-skills.test.ts:497` |
| M2 | `docs/guidelines/UI-UX.md:17` | Swapped `spec.md` and `uiux.md` precedence | KILLED — IT-023 failed at `tools/shared/tests/qa-skills.test.ts:499` |
| M3 | `docs/guidelines/SECURITY.md:21` | Allowed automatic deletion | KILLED — IT-023 failed at `tools/shared/tests/qa-skills.test.ts:504` |

**Sensor depth**: lightweight, three contract-level mutations
**Result**: 3/3 killed — PASS

## Gate Check

| Command | Result |
| --- | --- |
| `npx vitest run tools/shared/tests/qa-skills.test.ts` | 23 passed, 0 failed, 0 skipped |
| `npm test` | 146 passed across 11 files, 0 failed, 0 skipped |
| `python3 tools/ad-index.py --check` | index current |
| `python3 tools/test_ad_index.py` | PASS (`ok`) |
| `python3 scripts/test_adopt.py` | PASS (`ok`) |
| `python3 tools/test_workflow_config.py` | 11 passed, 0 failed |
| `python3 tools/test_tlc_validators.py` | 9 passed, 0 failed |
| `python3 tools/test_deep_review_token_metrics.py` | 19 passed, 0 failed |
| `npm run knowledge` | 0 errors, 12 pre-existing/unharvested warnings including AD-006 |
| `git diff --check origin/main...HEAD` | PASS |

The scoped canonical suite grew from 22 tests on `origin/main` to 23 at HEAD; the branch adds one claimed test and removes none.

## Code and Documentation Quality

- Scope is seven files and one focused commit; no runtime dependency, installer, provider, product path, or synchronization implementation was added.
- README provides discovery; `UI-UX.md` owns visual handoff behavior; `SECURITY.md` owns generic writer safety; AD-006 owns rationale.
- Adoption remains stack-neutral and passed its source-pack test. `scripts/adopt.py:38-40` copies the complete guidelines tree, so consuming projects receive both policy changes without installing OpenDesign.
- Context-budget checks: `UI-UX.md` is 87 lines (rule target under 120); `SECURITY.md` is 158 lines (reference target under 160). All guidelines total 1,574 lines versus the 1,500-line target; the branch adds 13 guideline lines to a baseline already above that non-gating target. Added rules are conditional and live behind existing dispatch triggers.
- Concrete daemon, port, CLI, and version data remain outside README and guidelines. Naming those detail classes in the routing sentence is not operational configuration.
- `workflow.json.git_head` equals the frozen base `origin/main` commit, while its Verifier route is `.codex/agents/verifier.toml`; this is the expected pre-dispatch snapshot, not stale HEAD state.

## QA Routing

The diff changes docs-as-interface. This technical phase did not perform QA. Dispatch a fresh `qa-plan` Verifier, then a separate fresh `qa-execute` Verifier before PR readiness.

## Summary

**Overall**: PASS — technically ready for separate docs-as-interface QA.

**Ranked gaps**: none.
