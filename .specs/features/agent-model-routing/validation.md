# Agent Model Routing Validation

**Verdict**: PASS
**Date**: 2026-08-24
**Spec**: `.specs/features/agent-model-routing/spec.md`
**Diff range**: `8368392..323a92018e2a69d7e741d43f7624ac0b9c8dce75`
**Verifier**: fresh independent Verifier, author != verifier

## Ranked Gaps

None.

## Task Completion

| Task | Independent result | Evidence |
| --- | --- | --- |
| T1 | PASS | Strict v2 matrix and model validation: `.agents/skills/workflow-config/scripts/workflow_config.py:134-209`; exact assertions: `tools/test_workflow_config.py:109-190`. |
| T2 | PASS | Fifteen native packets, output paths, byte preservation, and idempotence: `tools/test_workflow_config.py:195-229,365-451`. |
| T3 | PASS | Freeze, resume, drift, refresh, and planner omission: `tools/test_workflow_config.py:456-530`. |
| T4 | PASS | Fresh, invalid, and existing-config adoption paths: `scripts/test_adopt.py:324-394`. |
| T5 | PASS | Central ownership contract and fifteen-packet parity: `README.md:86-99`, `docs/workflow/pack.md:51-57`, `tools/shared/tests/qa-skills.test.ts:521-543`. |
| T6 | PASS | Resolver/adoption regression suites pass; invalid inputs assert no writes at `tools/test_workflow_config.py:234-400`. |
| T7 | PASS | Public CLI conflict, cadence, and frozen paths: `tools/test_workflow_config.py:255-283,535-571,664-715,720-793`. |
| T8 | PASS | Wrong-role ownership and missing-path outcomes: `tools/test_workflow_config.py:754-791`. |
| T9 | PASS | Configured cadence reaches exact CLI JSON and snapshot state: `tools/test_workflow_config.py:690-715`. |
| T10 | PASS | Identifier round trips, native headers, CRLF, and packet bodies: `tools/test_workflow_config.py:322-451`. |
| T11 | PASS | TOML multiline content cannot supply metadata: `tools/test_workflow_config.py:420-451`. |
| T12 | PASS | Body/after-boundary keys and backslash identifiers are rejected before writes: `tools/test_workflow_config.py:341-400`. |
| T13 | PASS | Triple-quote comment tokens remain data and inline comments remain bytes: `tools/test_workflow_config.py:426-451`. |
| T14 | PASS | Complete `tomllib` parse, unique top-level developer boundary, decoded assignments, and value-span rendering: `.agents/skills/workflow-config/scripts/workflow_config.py:248-358`; exact regression assertions: `tools/test_workflow_config.py:420-451`; both fresh mutants killed. |

## Spec-Anchored Acceptance Criteria

### Configure every agent from one file

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | One model and effort for 3 providers x 5 roles. | `tools/test_workflow_config.py:109-117` — every parsed setting equals the matrix; `tools/shared/tests/qa-skills.test.ts:521-543` — `settings.size` is 15 and every native value equals config. | PASS |
| 2 | `--sync-agents` renders every configured value in native syntax. | `tools/test_workflow_config.py:195-209` — exact Claude, Cursor, and Codex model/effort strings; `tools/test_workflow_config.py:420-448` — TOML-decoded escaped Codex value renders correctly. | PASS |
| 3 | Sync preserves every non-model packet byte. | `tools/test_workflow_config.py:215-229` — stripped metadata leaves identical bytes; `tools/test_workflow_config.py:403-451` — exact CRLF, multiline body, model comment, and effort comment bytes remain. | PASS |
| 4 | Second unchanged sync is byte-identical. | `tools/test_workflow_config.py:210-214` — empty changed paths, exact unchanged paths, unchanged tree digest. | PASS |
| 5 | Invalid matrix, effort, or packet metadata exits non-zero before writes. | `tools/test_workflow_config.py:122-190,234-400` — exact invalid classes and unchanged packet-byte maps. | PASS |
| 6 | Sync reports changed and already-current packet paths. | `tools/test_workflow_config.py:198-214` — exact fifteen-path changed and unchanged sets. | PASS |

### Freeze delegated execution settings

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Resolve and refresh store model/effort for every delegated role. | `tools/test_workflow_config.py:456-495` — exact four-role objects and refreshed values. | PASS |
| 2 | Resume returns frozen values without reading config replacements. | `tools/test_workflow_config.py:500-510` — config changes, then resumed snapshot equals the original exactly. | PASS |
| 3 | Model or effort drift exits non-zero with sync/refresh guidance. | `tools/test_workflow_config.py:475-495,515-530` — model and effort drift both assert exact guidance. | PASS |
| 4 | Planner synchronizes but remains outside delegated routing. | `tools/test_workflow_config.py:195-209,461-470` — fifteen packets sync while snapshot role set equals delegated roles only. | PASS |

### Adopt the centralized contract safely

| # | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| 1 | Fresh adoption installs v2 config and fifteen matching packets. | `scripts/test_adopt.py:324-339` — version 2, all packet files, and exact setting parity. | PASS |
| 2 | Existing config stays byte-identical and only metadata changes in packets. | `scripts/test_adopt.py:364-394` — exact config bytes, native parity, and stripped packet-byte equality; Codex suffix/CRLF precision at `tools/test_workflow_config.py:420-451`. | PASS |
| 3 | Unsynchronizable adoption exits non-zero and names the packet. | `scripts/test_adopt.py:344-359` — exit 1, `verifier` diagnostic, malformed packet retained. | PASS |
| 4 | Documentation names central source and generated native fields. | `README.md:86-99` and `docs/workflow/pack.md:51-57` state source ownership, generated metadata, sync, and adoption behavior. | PASS |

**Spec-anchored result**: 14/14 acceptance criteria matched; 0 spec-precision gaps.

## Codex TOML Surface Recheck

- Quoted `#` data and opposite triple-quote tokens: PASS at `tools/test_workflow_config.py:426-430,443-448`.
- Triple-double and triple-single tokens in comments: PASS at `tools/test_workflow_config.py:427-428,443-448`.
- Multiline values and model-like body lines: PASS at `tools/test_workflow_config.py:431-449`.
- Exactly one top-level `developer_instructions` boundary: implementation validates it at `.agents/skills/workflow-config/scripts/workflow_config.py:264-271`; a fresh four-case in-memory probe accepted one true boundary with a shadow assignment inside its multiline body, rejected a missing boundary, rejected an after-boundary-only model, and preserved the body bytes.
- After-boundary metadata cannot satisfy the header: PASS at `tools/test_workflow_config.py:385-400`; accepting it was killed by mutation 1.
- Escaped native model values decode through `tomllib`: PASS for `old\u002dmodel` at `tools/test_workflow_config.py:434,443-448`.
- Backslash config model values fail before writes: PASS at `tools/test_workflow_config.py:341-360`.
- Exact inline comments, CRLF, and non-model bytes: PASS at `tools/test_workflow_config.py:403-451`; deleting the effort comment was killed by mutation 2.

## Build Gate and Baseline Integrity

- **Build command**: `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py`
- **Current HEAD**: exit 0; 108 Vitest + 17 adoption + 28 resolver = 153 passed, 0 failed, 0 skipped.
- **Baseline `8368392`**: same command in a detached temporary worktree with checkout-local source and the active dependency tree linked; exit 0; 108 Vitest + 14 adoption + 11 resolver = 133 passed, 0 failed, 0 skipped.
- **Delta**: +20 checks; no test-count decrease.
- **Count commands**: `rg -c '^def test_' scripts/test_adopt.py tools/test_workflow_config.py` and `git show 8368392:<path> | rg -c '^def test_'`.
- `validate_spec.py`: 0 errors, 0 warnings.
- `validate_tasks.py`: 0 errors, 0 warnings.
- `git diff --check 8368392..323a920`: exit 0.
- Fresh direct Codex boundary/render probe: 4 passed, 0 failed.

## Discrimination Sensor

Mutations ran only in detached `/tmp/amr-mutant-323a920`; the worktree was removed afterward.

| # | Mutation | Canonical assertion | Result |
| --- | --- | --- | --- |
| 1 | Replaced the native boundary with `len(content)`, accepting a body/after-boundary Codex model key. | `tools/test_workflow_config.py:365-400` | KILLED: `test_sync_requires_native_header_metadata_for_every_provider` raised its expected-rejection assertion for `codex, duplicate=False`. |
| 2 | Removed the effort assignment suffix, deleting its inline comment while retaining the quoted value and newline. | `tools/test_workflow_config.py:448` | KILLED: exact `# effort comment\r\n` assertion failed. |

**Sensor result**: 2/2 killed — PASS. Active-checkout porcelain before and after matched exactly: only `.specs/features/agent-model-routing/validation.md` modified.

## Code Quality, Edge Cases, and QA Impact

| Check | Result |
| --- | --- |
| Minimum code / no new dependency | PASS: T14 deletes the hand-written lexer and uses Python 3.11 `tomllib`. |
| Surgical scope / no unrelated implementation | PASS: T14 changes resolver, canonical regression test, and task state only. |
| Every test maps to an AC, edge case, or task | PASS against `.specs/features/agent-model-routing/tests.md`. |
| Hollow-case check | PASS against `docs/guidelines/TEST-CONTRACT.md`: exact comments and bytes are asserted and both required mutants die. |
| Missing/unknown matrix entries | PASS at `tools/test_workflow_config.py:122-190`. |
| Duplicate/missing metadata and validation-before-write | PASS at `tools/test_workflow_config.py:234-400`. |
| Distinct checkout isolation | PASS at `tools/test_workflow_config.py:796-805`. |
| Public QA dispatch | Required: CLI, configuration, adoption, and docs-as-interface changed. Run fresh QA Plan, then fresh QA Execute; this technical packet performs neither. |

## Summary

**Overall**: PASS. All 14 ACs and T1-T14 are evidence-backed. Exact Build gate is green, baseline test count increased by 20, and both fresh high-risk Codex mutants were killed without changing the active implementation tree.

**Next step**: dispatch a fresh QA Plan Verifier for the public configuration, CLI, adoption, and documentation surfaces.
