# BUG-20260824-noninteractive-codex-finalizes-open-session

- **Status:** fixed — retest passed
- **Severity:** major
- **Scenario:** `WFL-ai-memory-handoff`
- **Expected:** A noninteractive or informational Codex invocation through the sourced helper exits
  without finalizing another open Codex session; automatic finalization targets only the session
  created by the interactive child.
- **Observed:** `codex --version` printed its version, then the helper unconditionally ran
  `ai-memory finalize-session` and ended the latest controlled interactive Codex session in the
  project.
- **Adapter:** CLI/manual with installed `ai-memory 1.31.0`, external loopback service, isolated zsh,
  installed Codex lifecycle hook, and public `scripts/ai-memory.zsh`
- **Exact path:** create an open Codex lifecycle session in the checkout; run
  `zsh -fc 'source ./scripts/ai-memory.zsh; codex --version'`; inspect the session through the
  external ai-memory SQLite read path
- **Evidence:** `docs/qa/evidence/2026-08-24-ai-memory-handoff/session.md`
- **Fix commit:** `e30aae6`
- **Retest:** passed on 2026-08-24 after technical validation `55664f7`; real `codex --version` and the adjacent controlled `exec` dispatch both left pre-existing sessions open

## Reproduction

1. In a project with one open Codex session, source `scripts/ai-memory.zsh` in another shell.
2. Run `codex --version` (or another invocation that does not create an interactive agent session).
3. Observe that `ai-memory finalize-session` reports the existing session finalized.
4. Independently inspect that session and observe `ended_at` changed from null to non-null.

The controlled session id in this QA run was `fbcb4652-71b9-49e8-8b66-103cf159e5e5`.

## Smallest remediation

Make the wrapper finalize only the Codex session created by its interactive child. A child that
creates no agent session must not fall back to latest-session selection. If the installed hooks
cannot expose the child's exact session id to the wrapper, bypass finalization for every documented
noninteractive/informational/admin invocation and retain `handoff` as the explicit recovery path.

Add a regression assertion that a pre-existing open session remains open after at least
`codex --version` and `codex exec`; keep the existing exactly-once and child-status assertions for
interactive invocation.

## Retest

A fresh Verifier resumed the original report after fix `e30aae6` and technical validation
`55664f7`. The real public path printed `codex-cli 0.149.0`, returned `0`, and independent SQLite
inspection showed controlled session `11111111-1111-4111-8111-111111111111` remained open. The
adjacent `exec` dispatch also returned `0` without ending its controlled session. The rest of the
handoff charter and adoption canary then passed. See
`docs/qa/evidence/2026-08-24-ai-memory-handoff/session.md`.
