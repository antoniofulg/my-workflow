# AI Memory Handoff Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Codex finalizes once | A fake interactive `codex` exits normally through the sourced helper | Fake `ai-memory finalize-session` is invoked exactly once |
| UT-002 | Codex status is preserved | A fake `codex` exits with status `42` | Wrapped command returns status `42` after finalization |
| UT-003 | Finalization failure is visible | Fake `ai-memory finalize-session` exits non-zero | Helper writes the documented failure message to stderr and keeps the Codex status |
| UT-004 | Arguments remain literal | Wrapper receives arguments containing spaces and shell metacharacters | Fake Codex receives the same argument vector and no argument is executed by the shell |
| UT-005 | Manual fallback finalizes directly | A fake `ai-memory finalize-session` exits with status `23` and `handoff()` is called directly | Fake `ai-memory` is invoked exactly once and `handoff()` returns status `23` |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Workflow adoption remains independent | Run `python3 scripts/test_adopt.py` without ai-memory installed or running | Existing adoption scenarios pass and create no ai-memory runtime files |
| IT-002 | Decision index remains canonical | Run the AD index generator/check after recording the integration decision | `AD-008` appears once and index verification exits 0 |
| IT-003 | Repository gate remains green | Run the repository's full offline gate | Command exits 0 with no failed or skipped tests |

## End-to-end

No automated end-to-end case. Agent lifecycle stores and provider quotas are not deterministic test
fixtures. A fresh Verifier performs the documented manual journey on the configured workstation.

## Security

| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | Shell argument injection | Pass command substitution, separators, whitespace, and glob characters as Codex arguments | Values reach Codex literally; no injected command executes |
| SEC-002 | Secret capture expands silently | Review setup defaults and capture exclusions | Server remains loopback-only, no cloud provider is configured, and exclusions plus DLP residual are explicit |
