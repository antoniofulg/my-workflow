# QA Execute — ai-memory handoff

- **Date:** 2026-08-24
- **Charter:** [`CH-ai-memory-handoff-2026-08-24`](../charters/CH-ai-memory-handoff-2026-08-24.md)
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual; installed `ai-memory 1.31.0`, isolated zsh, provider lifecycle hooks, and `scripts/adopt.py`
- **Environment:** macOS workstation; active checkout `/Users/antoniofulg/Projects/my-workflow-ai-memory-handoff`; loopback service managed by LaunchAgent
- **Entry path:** `docs/workflow/ai-memory.md` → `scripts/ai-memory.zsh` → installed lifecycle hooks
- **Automated gate:** `npm_config_offline=true npm test && npm run knowledge && git diff --check` — exit 0; 8 files/108 tests passed; knowledge 0 errors/16 warnings
- **Raw evidence:** `docs/qa/evidence/2026-08-24-ai-memory-handoff/`

## Matrix

| Scenario | Scope | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `WFL-ai-memory-handoff` | AIM-01–AIM-08, including noninteractive wrapper risk | fail | External SQLite read showed the controlled session changed from open to ended after `codex --version` | [`session.md`](../evidence/2026-08-24-ai-memory-handoff/session.md) |
| `ADP-adopt-workflow-safely` | Adjacent fresh-adoption canary | not run | Fix-loop closed this Verifier immediately after the product defect; prior scenario verdict remains unchanged | limitation recorded here |

## Probe results

1. **PASS — preflight and setup boundary.** Full gate exited 0. The installed version is `1.31.0`;
   LaunchAgent and `lsof` show only `127.0.0.1:49374`; runtime data is external; LLM and embedding
   providers are disabled; routing is sticky; auto-improvement scheduler is disabled; the external
   marker and all three hook integrations use `repo-root`. Existing unrelated Claude Code and
   Cursor hooks remain present.
2. **FAIL — mandatory noninteractive wrapper risk.** A controlled Codex session was open before
   invoking `codex --version` through the sourced helper. The command created no agent session, but
   the helper finalized the latest open Codex session. Independent SQLite inspection showed
   `is_open` change from `1` to `0`. Filed
   [`BUG-20260824-noninteractive-codex-finalizes-open-session`](../bugs/BUG-20260824-noninteractive-codex-finalizes-open-session.md).
3. **NOT RUN — single-use/no-briefing, failure recovery, kill boundary, and adoption canary.** The
   charter requires stopping the affected path and the QA fix-loop requires closing this Verifier
   after a confirmed defect. No PASS is claimed for AIM-01, AIM-02, AIM-03, or AIM-04. The prior
   `ADP-adopt-workflow-safely` verdict remains unchanged rather than being reset without a regression.

## Debrief

Verdict: **FAIL**. Setup inspection supports AIM-05 through AIM-08, but public helper behavior breaks
the cross-provider workflow before independent single-use/no-briefing confirmation. The Implementer
must fix `BUG-20260824-noninteractive-codex-finalizes-open-session`; a fresh Verifier must rerun the
technical gate, resume this charter from the affected wrapper journey, and walk the adjacent adoption
canary.
