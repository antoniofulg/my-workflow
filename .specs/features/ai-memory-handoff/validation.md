# AI Memory Handoff Validation

**Verdict**: PASS
**Date**: 2026-08-24
**Spec**: `.specs/features/ai-memory-handoff/spec.md`
**Feature diff range**: `6675d55..42d8ceb`
**T9 slice range**: `065f50a..42d8ceb`
**Verifier**: independent Technical Verifier, author != verifier

## Task Completion

| Scope | Status | Evidence |
| --- | --- | --- |
| T1-T8 implementation and prior remediation | Done | `scripts/ai-memory.zsh:3`, `scripts/test_ai_memory.py:88`, `docs/workflow/ai-memory.md:1` |
| T9 reviewer-isolation contract | Done | `docs/guidelines/REVIEW-ROUNDS.md:75`, `.specs/features/ai-memory-handoff/tasks.md:139` |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` evidence and assertion | Result |
| --- | --- | --- | --- |
| AIM-01 | Normal Claude Code or Cursor end creates one project/cwd-compatible pending handoff. | `docs/workflow/ai-memory.md:73` installs only lifecycle hooks for all three agents; `docs/workflow/ai-memory.md:78` enumerates `claude-code`, `codex`, and `cursor`; `docs/workflow/ai-memory.md:81` requires `repo-root`. Live provider behavior remains owned by the durable QA scenario. | PASS |
| AIM-02 | Interactive Codex exit finalizes exactly once and preserves Codex status. | `scripts/test_ai_memory.py:90` — `assert result.returncode == 42`; `scripts/test_ai_memory.py:91` — `assert calls == ["finalize-session"]`; `scripts/test_ai_memory.py:181`-`184` assert interactive launch modes preserve status/argv and finalize once. | PASS |
| AIM-03 | Failed automatic finalization emits a visible error and leaves a working fallback. | `scripts/test_ai_memory.py:97` — `assert result.returncode == 42`; `scripts/test_ai_memory.py:98` — exact error assertion; `scripts/test_ai_memory.py:134`-`135` assert `handoff` returns ai-memory status and calls `finalize-session`. | PASS |
| AIM-04 | Compatible next agent receives at most one single-use handoff, never briefing or managed transcript. | `docs/workflow/ai-memory.md:55`-`69` disables briefing and managed context; `docs/workflow/ai-memory.md:149`-`153` defines zero-or-one delivery and single consumption. Live provider behavior remains owned by the durable QA scenario. | PASS |
| AIM-05 | Claude Code, Codex, and Cursor hooks use repo-root and sticky routing. | `docs/workflow/ai-memory.md:52`-`53` configures sticky routing; `docs/workflow/ai-memory.md:78`-`82` installs all three hooks with `--project-strategy repo-root`. | PASS |
| AIM-06 | Briefing, MCP, routing skills, managed workstreams, LLMs, embeddings, consolidation, and auto-improvement remain disabled. | `docs/workflow/ai-memory.md:48`-`69` omits providers and disables briefing, auto-improvement, consolidation, embeddings, and managed mode; `docs/workflow/ai-memory.md:86`-`88` excludes MCP, instructions, and skills. | PASS |
| AIM-07 | Runtime data remains outside the repository; repository artifacts stay authoritative. | `docs/workflow/ai-memory.md:6`-`8` names repository authority and external runtime paths; `README.md:144`-`147` exposes the integration as optional and non-authoritative. | PASS |
| AIM-08 | Setup documents loopback, bounded capture, exclusions, and incomplete-DLP residual. | `docs/workflow/ai-memory.md:39`-`44` requires loopback; `docs/workflow/ai-memory.md:96`-`104` defines exclusions, bounded lexical behavior, and incomplete-DLP residual. | PASS |
| AIM-09 / S10 / SEC-003 | Internal named Verifier and Deep Reviewer receive explicit role packets and never consume an Implementer handoff; a top-level reviewer may consume only when no pending Implementer handoff can be consumed; capture dropping is not role isolation. | Canonical rule: `docs/guidelines/REVIEW-ROUNDS.md:75`-`80`. Explicit provider packets: `.claude/agents/verifier.md:9`-`19`, `.codex/agents/verifier.toml:7`-`17`, `.cursor/agents/verifier.md:9`-`19`; Deep Reviewer packets: `.claude/agents/deep-reviewer.md:10`-`22`, `.codex/agents/deep-reviewer.toml:7`-`20`, `.cursor/agents/deep-reviewer.md:9`-`21`. Storage/noise distinction and canonical pointer: `docs/workflow/ai-memory.md:107`-`110`. Exact abuse case: `.specs/features/ai-memory-handoff/tests.md:36`. | PASS |

**Spec-anchored status**: 9/9 outcomes matched; 0 spec-precision gaps.

## AIM-09 Contract and Security Parity

| Artifact | Required statement | Evidence | Result |
| --- | --- | --- | --- |
| Canonical instruction home | Reviewer role isolation is owned once by the reviewer-independence rule. | `docs/guidelines/REVIEW-ROUNDS.md:75`-`80`; exact imperative `must not consume an Implementer` occurs once in that guideline. | PASS |
| Integration guide | `drop_subagent_captures` controls storage/noise, not role isolation, and points to the canonical rule. | `docs/workflow/ai-memory.md:107`-`110` | PASS |
| Decision | Reviewer continuity is packet-defined; capture dropping does not protect top-level review. | `.specs/STATE.md:101`-`116` (AD-008) | PASS |
| Specification | AIM-09, S10, traceability, and success criterion agree. | `.specs/features/ai-memory-handoff/spec.md:66`, `:86`, `:100`, `:107` | PASS |
| Threat model | TM-005 carries the same control, top-level condition, capture distinction, and operational residual. | `.specs/features/ai-memory-handoff/threat-model.md:20`-`21`, `:31` | PASS |
| Security case | SEC-003 supplies exact attempt and expected result. | `.specs/features/ai-memory-handoff/tests.md:36` | PASS |

`docs/guidelines/TEST-CONTRACT.md:71`-`85` permits a prose assertion only when the artifact is the product contract and no stronger gate owns it. That exception applies here: reviewer dispatch is an agent-instruction contract, not repository runtime code. The permanent case is therefore a manual contract review; the discrimination sensor below executes the exact contract in a detached scratch. Provider packet handling remains the operational residual named at `.specs/features/ai-memory-handoff/threat-model.md:31`.

## Discrimination Sensor

Detached temporary worktree at `42d8ceb`; real checkout porcelain was empty before and after cleanup.
The sensor used an inline `python3` SEC-003 contract check over the canonical rule, integration guide,
spec, test contract, threat model, and AD-008.

| Mutation | File:line | Discriminating assertion | Result |
| --- | --- | --- | --- |
| Permit an internal named reviewer to consume an Implementer handoff. | `docs/guidelines/REVIEW-ROUNDS.md:79` | Required `explicit role packets and must not consume an Implementer`; check exited 1. | KILLED |
| Claim `drop_subagent_captures` provides reviewer role isolation. | `docs/workflow/ai-memory.md:107`-`109` | Required `optional storage and noise control` and `does not isolate reviewer roles`; check exited 1. | KILLED |
| Allow a top-level reviewer to consume while an Implementer handoff is pending. | `docs/guidelines/REVIEW-ROUNDS.md:80` | Required `only when no pending Implementer handoff can be consumed`; check exited 1. | KILLED |

**Sensor depth**: lightweight, three behavior-level contract mutations.
**Sensor result**: 3/3 killed — PASS.

## Gate Check

- **Structural validators**: `python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_spec.py .specs/features/ai-memory-handoff/spec.md && python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/tlc-spec-driven/scripts/validate_tasks.py .specs/features/ai-memory-handoff/tasks.md` — 0 errors, 0 warnings.
- **Guideline size**: `test "$(wc -l < docs/guidelines/REVIEW-ROUNDS.md | tr -d ' ')" -le 160` — exit 0; 160/160 lines.
- **Full Python/AD**: `python3 scripts/test_ai_memory.py && python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check` — exit 0; 9 helper tests, 14 adoption test functions, 2 AD-index test functions; index current; 0 failed or skipped.
- **Build**: `npm_config_offline=true npm test && npm run knowledge && git diff --check` — exit 0; 8 Vitest files, 108 tests passed, 0 failed, 0 skipped; knowledge 0 errors and 16 warnings; diff check passed.
- **Count command**: `rg -c '^def test_' scripts/test_ai_memory.py scripts/test_adopt.py tools/test_ad_index.py` plus Vitest summary — 133 counted tests/functions. T9 changes no test file, so the T9 before/after count is 133/133, delta 0.

## Code Quality and QA Disposition

| Principle | Result |
| --- | --- |
| Minimum change; no runtime/config implementation invented | PASS |
| One canonical instruction home; integration guide uses a pointer | PASS |
| No redundant guideline growth; hard 160-line cap remains green | PASS |
| AD/spec/test/threat contract parity | PASS |
| Tests map to acceptance criteria; manual SEC-003 uses the owning contract layer | PASS |
| T9 changes no public behavior through UI, API, CLI, mobile, public configuration, adoption, or docs-as-interface | PASS — Technical only; no QA dispatch |

Existing QA records and statuses were not changed. Prior provider-lifecycle QA remains recorded in
`docs/qa/reports/2026-08-24-ai-memory-handoff.md`; T9 is an internal reviewer-context rule and does
not invalidate that public journey.

## Summary

**Overall**: PASS.

- **Spec-anchored check**: 9/9 outcomes matched; 0 precision gaps.
- **Gate**: 133 counted tests/functions passed; 0 failed; 0 skipped.
- **Sensor**: 3/3 reviewer-isolation mutants killed.
- **Ranked gaps**: none.
