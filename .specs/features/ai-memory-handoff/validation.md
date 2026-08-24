# AI Memory Handoff Validation

**Verdict**: PASS
**Date**: 2026-08-24
**Spec**: `.specs/features/ai-memory-handoff/spec.md`
**Diff range**: `6675d55..88458a0`
**Verifier**: independent Verifier, author != verifier

## Task Completion

| Scope | Status | Evidence |
| --- | --- | --- |
| T1-T6 implementation and contract | Done | `scripts/ai-memory.zsh:3`, `docs/workflow/ai-memory.md:1` |
| T7 noninteractive Codex remediation | Done | `scripts/ai-memory.zsh:14`, `scripts/test_ai_memory.py:138` |
| T8 discrimination remediation | Done | `scripts/test_ai_memory.py:153`, `scripts/test_ai_memory.py:173`; all three required verifier mutants killed |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` evidence and assertion | Result |
| --- | --- | --- | --- |
| AIM-01 | Normal Claude Code or Cursor end creates one project/cwd-compatible pending handoff. | `docs/workflow/ai-memory.md:73` installs only lifecycle hooks for all three agents; `docs/workflow/ai-memory.md:78` enumerates `claude-code`, `codex`, and `cursor`; `docs/workflow/ai-memory.md:81` asserts `repo-root`. Live provider behavior remains owned by the existing QA scenario. | PASS |
| AIM-02 | Interactive Codex exit finalizes exactly once and preserves Codex status. | `scripts/test_ai_memory.py:90` — `assert result.returncode == 42`; `scripts/test_ai_memory.py:91` — `assert calls == ["finalize-session"]`; `scripts/test_ai_memory.py:173`-`184` asserts no-argument, prompt, `resume`, and `fork` preserve status/argv and finalize once. | PASS |
| AIM-03 | Failed automatic finalization emits a visible error and leaves a working fallback. | `scripts/test_ai_memory.py:97` — `assert result.returncode == 42`; `scripts/test_ai_memory.py:98` — exact error assertion; `scripts/test_ai_memory.py:99` — one finalization call; `scripts/test_ai_memory.py:134`-`135` asserts `handoff` returns ai-memory status and calls `finalize-session`. | PASS |
| AIM-04 | Compatible next agent receives at most one single-use handoff, never briefing or managed transcript. | `docs/workflow/ai-memory.md:55`-`56` disables startup briefing; `docs/workflow/ai-memory.md:66`-`69` excludes managed mode; `docs/workflow/ai-memory.md:143`-`147` defines zero-or-one delivery and single consumption. Live provider behavior remains owned by the existing QA scenario. | PASS |
| AIM-05 | Claude Code, Codex, and Cursor hooks use repo-root and sticky routing. | `docs/workflow/ai-memory.md:52`-`53` configures sticky routing; `docs/workflow/ai-memory.md:78`-`82` installs all three hooks with `--project-strategy repo-root`. | PASS |
| AIM-06 | Briefing, MCP, routing skills, managed workstreams, LLMs, embeddings, consolidation, and auto-improvement remain disabled. | `docs/workflow/ai-memory.md:48`-`64` omits providers and disables briefing/auto-improvement; `docs/workflow/ai-memory.md:66`-`69` excludes consolidation, embeddings, and managed mode; `docs/workflow/ai-memory.md:86`-`88` excludes MCP, instructions, and skills. | PASS |
| AIM-07 | Runtime data remains outside the repository; repository artifacts stay authoritative. | `docs/workflow/ai-memory.md:6`-`8` names repository authority and external runtime paths; `README.md:144`-`147` exposes the integration as optional and non-authoritative. | PASS |
| AIM-08 | Setup documents loopback, bounded capture, exclusions, and incomplete-DLP residual. | `docs/workflow/ai-memory.md:39`-`44` requires loopback; `docs/workflow/ai-memory.md:97`-`103` defines exclusions, bounded lexical behavior, and incomplete-DLP residual. | PASS |

**Spec-anchored status**: 8/8 technical outcomes matched; 0 spec-precision gaps. Provider lifecycle confirmation stays in separate QA Execute scope.

## Edge Cases

- Interrupted child/manual fallback: documented at `docs/workflow/ai-memory.md:123`-`129`; fallback behavior asserted at `scripts/test_ai_memory.py:132`-`135`.
- Multiple sessions: explicit `--session-id` path at `docs/workflow/ai-memory.md:131`-`135`.
- No pending handoff: zero startup payload contract at `docs/workflow/ai-memory.md:143`-`144`.
- Noninteractive/admin Codex invocations: bypass table at `scripts/test_ai_memory.py:153`-`170` asserts status, zero finalization, and exact argv.
- Interactive launch modes: `scripts/test_ai_memory.py:173`-`184` asserts no-argument, prompt, `resume`, and `fork` finalize once and preserve status/argv.

## Gate Check

- **Scoped**: `python3 scripts/test_ai_memory.py` — exit 0; 9 passed, 0 failed, 0 skipped.
- **Full Python/AD**: `python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check` — exit 0; 14 adoption test functions, 2 AD-index test functions, index current; 0 failed or skipped.
- **Build**: `npm_config_offline=true npm test && npm run knowledge && git diff --check` — exit 0; 8 Vitest files, 108 tests passed, 0 failed, 0 skipped; knowledge 0 errors and 16 warnings; diff check passed.
- **Before/after count**: base `6675d55` had 124 counted tests/functions; head has 133, delta +9. The branch adds the 9 helper tests and changes no pre-existing test suite.

## Discrimination Sensor

Three detached temporary worktrees at `88458a0`; real checkout porcelain was ` M .specs/features/ai-memory-handoff/validation.md` before and after cleanup.

| Mutation | File:line | Discriminating assertion | Result |
| --- | --- | --- | --- |
| Remove `mcp` from noninteractive bypass | `scripts/ai-memory.zsh:16` | `scripts/test_ai_memory.py:169` — `assert calls == []` | KILLED |
| Wrongly add `resume` to noninteractive bypass | `scripts/ai-memory.zsh:16` | `scripts/test_ai_memory.py:183` — `assert calls == ["finalize-session"]` | KILLED |
| On ai-memory failure, return its status instead of the nonzero Codex child status | `scripts/ai-memory.zsh:35` | `scripts/test_ai_memory.py:97` — `assert result.returncode == 42` | KILLED |

**Sensor depth**: lightweight, targeted at the remediated T7/T8 launch-mode and status branches.
**Sensor result**: 3/3 killed — PASS.

## Code Quality and Security

| Principle | Result |
| --- | --- |
| Minimum code; no speculative abstraction | PASS |
| Surgical helper and tests; no mandatory runtime dependency | PASS |
| Original argv and Codex status preserved | PASS |
| Failure visible and manual fallback preserved | PASS |
| Every documented wrapper launch class discriminated | PASS |
| Tests map to AIM-02/AIM-03 and the listed wrapper edge cases | PASS |

Argument safety remains asserted at `scripts/test_ai_memory.py:128`-`129`. Loopback, no-provider, capture exclusions, and incomplete-DLP residual remain documented at `docs/workflow/ai-memory.md:39`, `docs/workflow/ai-memory.md:48`, and `docs/workflow/ai-memory.md:97`-`103`.

## QA Disposition

Technical verdict remains PASS. Fresh QA Execute retested the provider lifecycle and the recorded
noninteractive-wrapper defect in
`docs/qa/reports/2026-08-24-ai-memory-handoff.md`. The scenario
`docs/qa/scenarios/WFL-ai-memory-handoff.md` is now `qa_status: pass`, with
`fix_status: fixed` and `retest_status: pass`. The original defect remains preserved as historical
bug evidence; this disposition does not expand or replace the technical verifier scope above.

## Summary

**Overall**: PASS — ready for fresh QA Execute.

- **Spec-anchored check**: 8/8 technical outcomes matched; 0 precision gaps.
- **Gate**: 133 counted tests/functions passed; 0 failed; 0 skipped.
- **Sensor**: 3/3 required mutants killed.
- **Ranked gaps**: none in technical scope.
