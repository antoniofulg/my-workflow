# AI Memory Handoff Specification

## Problem Statement

When a weekly provider limit ends an agent session, the operator needs to continue in Claude Code,
Codex, or Cursor without manually reconstructing the work. The integration must transfer only the
next-session baton and must not become a second authority for tasks, decisions, rules, or project
knowledge.

## Goals

- Provide an opt-in, low-context handoff path across Claude Code, Codex, and Cursor.
- Automatically finalize an interactive Codex session when its process exits.
- Keep Git, `.specs/`, `tasks.md`, architecture docs, and `knowledge/` authoritative.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Managed workstreams via `ai-memory run` | They retain a portable event ledger beyond the requested single handoff. |
| MCP memory tools, routing skills, briefing, LLMs, embeddings, consolidation, and auto-improvement | They add durable recall, startup context, or provider work outside the requested baton transfer. |
| Automatic machine mutation from `scripts/adopt.py` | Agent hooks and shell configuration belong to the operator's machine, not the consuming checkout. |
| Replacing project workflow state | Repository artifacts remain the only project authority. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Deployment boundary | Single-user server bound to `127.0.0.1` | Keeps captured context local and avoids a remote auth/TLS surface. | yes |
| Project routing | Git `repo-root` with sticky mid-session routing | Prevents subdirectories from creating phantom projects while retaining cwd-aware handoff delivery. | yes |
| Startup context | One pending, single-use handoff only | Meets continuity need without recurring token load. | yes |
| Codex shutdown | A sourced zsh wrapper finalizes on process exit; `handoff` remains a manual fallback | Codex lacks a reliable true SessionEnd hook. | yes |
| Dependency release | Document and verify a pinned ai-memory release for workstation setup | The upstream project changes quickly; upgrades require deliberate revalidation. | yes |
| Remaining implicit-requirement dimensions | N/A for this local opt-in integration | No payments, public route, shared tenancy, or product data model changes are introduced. | yes |

**Open questions:** none.

## User Stories

### P1: Continue after provider exhaustion

As an operator, I want an ended agent session to leave one concise baton so I can continue the same
work in another installed agent after a provider limit is exhausted.

Acceptance criteria:

- **AIM-01:** WHEN Claude Code or Cursor ends a normal hooked session THEN ai-memory SHALL create one pending handoff scoped to that project and eligible cwd.
- **AIM-02:** WHEN an interactive Codex process exits THEN the shell helper SHALL call `ai-memory finalize-session` once and preserve the Codex exit status.
- **AIM-03:** IF automatic Codex finalization fails THEN the shell helper SHALL print a visible error and leave the `handoff` fallback available.
- **AIM-04:** WHEN another supported agent starts in the compatible project directory THEN ai-memory SHALL inject at most the pending single-use handoff rather than a project briefing or managed transcript.

Independent test: run a fake Codex process through the shell helper, verify one finalization call and
the original exit status, then inspect the documented live handoff journey across two agents.

### P1: Preserve workflow authority and privacy

As a workflow maintainer, I want ai-memory isolated as an optional transport so captured context does
not replace repository truth or silently broaden the startup prompt.

Acceptance criteria:

- **AIM-05:** WHERE ai-memory is adopted, the setup SHALL install lifecycle hooks for Claude Code, Codex, and Cursor with `repo-root` project resolution and sticky mid-session routing.
- **AIM-06:** WHERE ai-memory is adopted, the setup SHALL leave briefing, MCP registration, routing skills, managed workstreams, LLMs, embeddings, consolidation, and auto-improvement disabled.
- **AIM-07:** The workflow SHALL keep ai-memory runtime data outside the consuming repository and identify Git plus the documented workflow artifacts as authoritative.
- **AIM-08:** WHERE capture hooks are enabled, the setup SHALL document local-loopback operation, bounded capture, secret-path exclusions, and the residual that free-form prompts or shell output are not complete DLP boundaries.

Independent test: inspect the opt-in integration contract and run repository gates without an
ai-memory server; normal adoption remains unchanged and produces no ai-memory runtime state.

## Edge Cases

- IF Codex is terminated with `kill -9` or the shell itself dies THEN the integration SHALL require the explicit `handoff` fallback after the operator returns to the project directory.
- IF more than one Codex session is open in the same project THEN the operator SHALL use `ai-memory finalize-session --session-id <uuid>` instead of relying on latest-session selection.
- IF no handoff is pending THEN a new agent session SHALL receive no ai-memory startup payload.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Optional runtime dependency and local configuration | Explicit opt-in, pinned release, repository-independent setup | AIM-05, AIM-06, AIM-07 |
| S6 | zsh wrapper and filesystem capture | Argument-safe wrapper, bounded hooks, documented exclusions and residual | AIM-02, AIM-03, AIM-08 |
| S8 | User prompts and tool output may contain sensitive content | Loopback-only server, no cloud LLM, secret-path exclusions | AIM-06, AIM-08 |
| S9 | External ai-memory process and hooks | Fail-visible finalization; upstream kept outside package dependencies | AIM-03, AIM-05 |
| S11 | Persistent local server process | Loopback bind and explicit operator-managed lifecycle | AIM-05, AIM-08 |

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| AIM-01 | Continue after provider exhaustion | Specify | Complete |
| AIM-02 | Continue after provider exhaustion | Specify | Complete |
| AIM-03 | Continue after provider exhaustion | Specify | Complete |
| AIM-04 | Continue after provider exhaustion | Specify | Complete |
| AIM-05 | Preserve workflow authority and privacy | Specify | Complete |
| AIM-06 | Preserve workflow authority and privacy | Specify | Complete |
| AIM-07 | Preserve workflow authority and privacy | Specify | Complete |
| AIM-08 | Preserve workflow authority and privacy | Specify | Complete |

## Success Criteria

- A normal Codex exit invokes finalization exactly once while preserving its exit status.
- Claude Code, Codex, and Cursor can exchange one pending handoff without enabling recurring briefing.
- Repository adoption and full gates pass without ai-memory installed or running.
