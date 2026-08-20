# explorer-agent Validation

**Date**: 2026-08-20  
**Spec**: Inline AC1–AC7 supplied in the verifier dispatch (no committed
`.specs/features/explorer-agent/spec.md` or `tasks.md` was present)  
**Diff range**: `e7c54ff..c70acbb`  
**HEAD**: `c70acbb4a1a1c59232eea908efcbce96c3c13147`  
**Verifier**: independent sub-agent (author ≠ verifier)

## Task Completion

| Work item | Status | Notes |
| --- | --- | --- |
| Explorer packets for Claude, Codex, Cursor | ✅ Done | Three final-named packets are present and parse/check successfully. |
| Planner delegation | ✅ Done | All three planner packets delegate product-tree searches/traces. |
| Fresh adoption | ✅ Done | `scripts/test_adopt.py:32-38` asserts all explorer packets. |
| Existing-directory readopt | ✅ Done | `scripts/test_adopt.py:58-66` covers pin preservation and packet restoration; an additional isolated all-provider probe passed. |
| Harness documentation, Codex configuration, and scope | ✅ Done | Four-role inventory and supported Codex configuration checks pass. |

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion/evidence | Result |
| --- | --- | --- | --- |
| AC1: Claude, Codex, and Cursor expose final-named `explorer` packets that are read-only search/trace roles and report concise path:line traces. | All three provider packets name `explorer`, prohibit edits/commits/mutating gates, and include a path:line report shape. | `.claude/agents/explorer.md:2,12,21,29`; `.codex/agents/explorer.toml:1,6-7,16,23`; `.cursor/agents/explorer.md:2,12,21,29`; consolidated provider assertions (`tomllib`, role text, and `[path:line]`) all passed. | ✅ PASS |
| AC2: Every planner delegates product-tree searches/traces to `explorer`. | Claude, Codex, and Cursor planner packets each instruct `spawn explorer` and prohibit parent product-tree search. | `.claude/agents/planner.md:33`; `.codex/agents/planner.toml:31`; `.cursor/agents/planner.md:33`; consolidated planner assertions passed. | ✅ PASS |
| AC3: `AGENTS.md`, `README.md`, and `docs/workflow/pack.md` describe the four-role harness, with no redundant `.cursor/rules`; Cursor implementer model remains unchanged. | Four roles are documented; `.cursor/rules` is absent; the Cursor implementer packet is byte-identical to `e7c54ff`. | `AGENTS.md:13-20`; `README.md:51-53,109-111`; `docs/workflow/pack.md:16-19`; `README.md:109-111` now names explorer in the packet inventory; `assert not Path('.cursor/rules').exists()` passed; `.cursor/agents/implementer.md:1-25` SHA-256 equals baseline `e7c54ff`. | ✅ PASS |
| AC4: Fresh adoption includes explorer packets. | A fresh destination contains Claude, Codex, and Cursor explorer packets. | `scripts/adopt.py:102-108,133-140`; `scripts/test_adopt.py:20-38` asserts `.cursor/agents/explorer.md`, `.claude/agents/explorer.md`, and `.codex/agents/explorer.toml`. | ✅ PASS |
| AC5: Re-adoption into existing agent directories copies missing packets while preserving every existing packet/model pin byte-for-byte. | Existing files remain unchanged; missing source packets are copied into existing provider directories. | `scripts/adopt.py:55-67,102-108`; `scripts/test_adopt.py:54-67` asserts a local planner pin survives and a missing explorer is restored; isolated all-provider probe asserted every existing packet/model-pinned file stayed byte-identical and every missing explorer was restored. | ✅ PASS |
| AC6: No Antclips product/auth artifacts or unrelated changes. | Diff contains only the 13 expected packet/docs/adoption files and introduces none of the excluded product/auth tokens. | `git diff --name-only e7c54ff..c70acbb` matched the allowlist; `git diff --unified=0 e7c54ff..c70acbb` token assertion found no `antclips`, `better-auth`, `hono`, `drizzle`, `tanstack`, `shadcn`, or `graphile`; `git diff --check` passed. | ✅ PASS |
| AC7: All Codex agent TOMLs use supported `developer_instructions`; verifier and explorer use the specified models/reasoning. | All four TOMLs have `developer_instructions` and no top-level `instructions`; verifier is `gpt-5.6-sol`/`medium`; explorer is `gpt-5.6-luna`/`medium`. | `.codex/agents/explorer.toml:1-6`; `.codex/agents/implementer.toml:1-5`; `.codex/agents/planner.toml:1-5`; `.codex/agents/verifier.toml:1-6`; TOML parse/assertion command passed for all four files and both model pins. | ✅ PASS |

**Status**: ✅ All supplied ACs covered and verified.

### Remediation re-verification

`README.md:109-111` now says “Planner, implementer, explorer and verifier packets.” The
remediation commit `586f524` was verified in the final range; the four-role harness remains
documented at `README.md:51-53` and `docs/workflow/pack.md:16-19`.

## Discrimination Sensor

| Mutation | File:line | Description | Killed? |
| --- | --- | --- | --- |
| M1 | `scripts/adopt.py:65` | Changed `dest.exists() or dest.is_symlink()` to `dest.exists() and dest.is_symlink()`, allowing existing local packets to be overwritten. | ✅ Killed: isolated `python3 scripts/test_adopt.py` failed at `scripts/test_adopt.py:63`. |
| M2 | `scripts/adopt.py:58` | Changed `if not dest.exists()` to `if dest.exists()`, preventing fresh agent directories from being copied. | ✅ Killed: isolated `python3 scripts/test_adopt.py` failed at `scripts/test_adopt.py:32`. |

**Sensor depth**: lightweight, two targeted behavior mutations. The sensor evidence from the
prior verification was reused because `scripts/adopt.py` and `scripts/test_adopt.py` are
byte-identical to `ebf7053` (SHA-256 `ae9d363d361038a0becd2d8a32b281f4869c52168f8a1344da26c8da6bbcb50e`
and `a6e146fcf393f5b8350eeb13f7ce6d3041bb747eecc4827813fbb62f84bee2f2`, respectively), and
`git diff c974949..c70acbb -- scripts/adopt.py scripts/test_adopt.py` is empty.  
**Result**: 2/2 killed — PASS ✅ (reused, code unchanged)

The real worktree porcelain remained unchanged around this re-verification:
`git status --porcelain=v1`. The prior disposable worktree runs also ended with empty real-tree
porcelain.

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code and surgical changes | ✅ |
| No scope creep or unrelated edits | ✅ |
| Existing patterns/style retained | ✅ |
| Spec-anchored outcomes have file:line evidence | ✅ |
| Fresh and existing adoption behaviors have discriminating assertions | ✅ |
| Documented guidelines followed: `AGENTS.md`, validation protocol in `tlc-spec-driven/references/validate.md` | ✅ |

## Gate Check

- **Commands**: `npm test`; `python3 scripts/test_adopt.py`; TOML parse plus AC7 config assertions; `python3 -m compileall -q scripts`; `git diff --check e7c54ff..c70acbb`.
- **Current result**: Vitest 3 files / 38 passed / 0 failed; adoption self-check passed (`ok`); TOML parse, Python compile, and diff-check passed.
- **Baseline result** (`e7c54ff`, isolated worktree): Vitest 3 files / 38 passed / 0 failed; adoption self-check passed (`ok`).
- **Test-count delta**: Vitest `38 → 38` (0 delta); the adoption script still invokes 2 self-check functions and passes. No tests were removed.
- **Skipped tests**: none.
- **Failures**: none in the implementation gates; sensor failures were expected mutant kills.

## Requirement Traceability

| Requirement | Previous status | New status |
| --- | --- | --- |
| AC1 | Not recorded | ✅ Verified |
| AC2 | Not recorded | ✅ Verified |
| AC3 | Not recorded | ✅ Verified (README inventory remediation confirmed) |
| AC4 | Not recorded | ✅ Verified |
| AC5 | Not recorded | ✅ Verified |
| AC6 | Not recorded | ✅ Verified |
| AC7 | Not recorded | ✅ Verified |
