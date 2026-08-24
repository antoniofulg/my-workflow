---
id: WFL-ai-memory-handoff
area: WFL
title: Resume work across providers with one ai-memory handoff
persona: Workflow adopter
journey: J-adopt-workflow
expected: A normal Codex exit or manual fallback leaves one project-scoped handoff that another supported agent consumes once without loading a recurring briefing or changing repository authority.
entry_points: docs/workflow/ai-memory.md; scripts/ai-memory.zsh; ai-memory install-hooks; codex; claude; cursor
qa_status: fail
bug_ids: BUG-20260824-noninteractive-codex-finalizes-open-session
fix_status: pending
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-08-24-ai-memory-handoff/session.md
last_report: docs/qa/reports/2026-08-24-ai-memory-handoff.md
overlaps:
---

Walk on a workstation where ai-memory `1.31.0` is installed outside the checkout:

1. Start the loopback server with the documented data and config paths. Confirm the service binds to
   `127.0.0.1` and uses no LLM, embedding, MCP, managed-workstream, or recurring-briefing feature.
2. Install lifecycle hooks for Claude Code, Codex, and Cursor with `repo-root` routing and inspect
   that existing unrelated agent configuration remains intact.
3. Source `scripts/ai-memory.zsh`, launch Codex from the repository, make a small disposable change,
   and exit normally. Confirm the wrapper calls `ai-memory finalize-session` once and returns Codex's
   exit status.
4. Start Claude Code or Cursor from the same repository (including a subdirectory or linked
   worktree). Confirm the pending handoff describes the next work and is consumed once.
5. Start another supported agent without creating a new handoff. Confirm no previous handoff or
   recurring briefing is injected again, and confirm Git plus `.specs/` remain the source of truth.
6. Repeat with an interrupted Codex process. Return to the repository, run `handoff`, and confirm the
   next supported agent receives the baton. If multiple Codex sessions are open, use the documented
   `--session-id` fallback.
7. Stop the server and inspect the repository. Confirm no ai-memory database, hook tree, marker, or
   handoff file was created in the checkout.

The repository has no automated harness for provider lifecycle behavior. Record command output and
screenshots or redacted agent-visible evidence under ignored `docs/qa/evidence/`, then update this
scenario's status and report fields in a dated QA report.

QA on 2026-08-24 stopped at the mandatory noninteractive-wrapper risk probe. A sourced helper ran
`finalize-session` after `codex --version` and ended the latest controlled interactive Codex session
even though the child created no session. See
`BUG-20260824-noninteractive-codex-finalizes-open-session`.
