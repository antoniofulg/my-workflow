# QA Execute — ai-memory handoff

- **Date:** 2026-08-24
- **Charter:** [`CH-ai-memory-handoff-2026-08-24`](../charters/CH-ai-memory-handoff-2026-08-24.md)
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual; installed `ai-memory 1.31.0`, isolated zsh, provider lifecycle hooks, and `scripts/adopt.py`
- **Environment:** macOS workstation; active checkout `/Users/antoniofulg/Projects/my-workflow-ai-memory-handoff`; loopback service managed by LaunchAgent
- **Entry path:** `docs/workflow/ai-memory.md` → `scripts/ai-memory.zsh` → installed lifecycle hooks
- **Automated gate:** `rtk python3 scripts/test_ai_memory.py && rtk python3 scripts/test_adopt.py && rtk python3 tools/test_ad_index.py && rtk python3 tools/ad-index.py --check && npm_config_offline=true rtk npm test && rtk npm run knowledge && rtk git diff --check` — exit 0; 9 helper tests and 108 Vitest tests passed; adoption/AD checks passed; knowledge 0 errors/16 warnings
- **Raw evidence:** `docs/qa/evidence/2026-08-24-ai-memory-handoff/`

## Matrix

| Scenario | Scope | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `WFL-ai-memory-handoff` | AIM-01–AIM-08, including noninteractive wrapper risk | pass | Installed hooks plus external SQLite confirmed normal Claude finalization, one Cursor acceptance, no replay, wrapper recovery, and external-only runtime | [`session.md`](../evidence/2026-08-24-ai-memory-handoff/session.md) |
| `ADP-adopt-workflow-safely` | Adjacent fresh-adoption canary | pass | Fresh adoption and re-adoption returned the same target digest and created no ai-memory runtime artifact | [`session.md`](../evidence/2026-08-24-ai-memory-handoff/session.md) |

## Probe results

1. **PASS — preflight and setup boundary.** Full gate exited 0. The installed version is `1.31.0`;
   LaunchAgent and `lsof` show only `127.0.0.1:49374`; runtime data is external; LLM and embedding
   providers are disabled; routing is sticky; auto-improvement scheduler is disabled; the external
   marker and all three hook integrations use `repo-root`. Existing unrelated Claude Code and
   Cursor hooks remain present.
2. **PASS AFTER RETEST — mandatory noninteractive wrapper risk.** The original walk found that
   `codex --version` ended an unrelated open session and filed
   [`BUG-20260824-noninteractive-codex-finalizes-open-session`](../bugs/BUG-20260824-noninteractive-codex-finalizes-open-session.md).
   After fix `e30aae6`, the real `codex --version` returned `0` while the controlled session remained
   open. The adjacent `exec` dispatch also returned `0` without finalization.
3. **PASS — normal provider lifecycle and single-use delivery.** A real Claude Code CLI session
   ended normally and created one project-scoped handoff. The installed Cursor SessionStart hook
   emitted one agent-visible `additionalContext` payload and marked it accepted. A following Codex
   SessionStart returned `{}` with zero open handoffs.
4. **PASS — interactive Codex status and targeting.** A deterministic interactive child returned
   `42`; the sourced helper finalized the newest controlled session exactly once, preserved `42`,
   and left the older session open.
5. **PASS — fail-visible recovery.** A controlled finalizer failure printed the documented error,
   preserved child status `42`, and left the callable `handoff` fallback returning the finalizer's
   status `7`.
6. **PASS — killed child boundary.** A child killed with `SIGKILL` returned `137`; the surviving
   wrapper finalized its controlled session once.
7. **PASS — manual fallback and no replay.** `handoff` finalized one captured Codex session and
   returned `0`; Cursor received its disposable baton once; the next Codex SessionStart returned
   `{}` with zero open handoffs.
8. **PASS — adjacent adoption canary.** Fresh adoption and re-adoption exited `0`, retained digest
   `071616ea754a83a03faf93ac78016da9c9076c43`, and produced no ai-memory marker, binary, runtime DB,
   hook tree, or handoff file.
9. **PASS — residue and final gate.** QA-owned targets were removed, the exact external
   `projects/qa-runtime` test store was purged, and the full final gate exited `0` with 9 helper tests
   and 108 Vitest tests passing. Knowledge reported 0 errors and 16 warnings.

## Debrief

Verdict: **PASS after fix and fresh retest**. AIM-01–AIM-08 passed through the declared CLI/manual
adapter, and the adjacent adoption canary remained green. The original defect remains preserved in
this report's history and is now fixed with a passing retest. Cursor GUI behavior was not launched;
the exact installed Cursor lifecycle command and its agent-visible output were used as the supported
manual adapter. No browser, API, mobile, auth, server-application, or production-health surface exists
for this repository.
