# AI Memory Handoff Threat Model

**Scope:** the optional local `ai-memory` handoff path and its sourceable Codex wrapper.

## Assumptions and deployment context

- The operator installs and runs the pinned upstream release on a workstation outside this checkout.
- The server binds to `127.0.0.1`; no cloud LLM, remote memory service, or managed workstream is used.
- Captured prompts and tool output can contain sensitive content. Secret-path exclusions reduce exposure,
  but free-form text and shell output are not a complete DLP boundary.

## Trust boundaries and assets

| Boundary | Untrusted side | Trusted decision point |
| --- | --- | --- |
| B1 | Agent prompts, tool output, and shell arguments | ai-memory's bounded capture and local operator configuration |
| B2 | External ai-memory process and lifecycle hooks | Loopback-only pinned installation and explicit disabled features |
| B3 | Codex wrapper arguments and exit status | `"$@"` forwarding and status preservation in `scripts/ai-memory.zsh` |

Assets are the operator's local handoff content, explicit reviewer packets, repository workflow
authority, shell process state, and provider credentials that must remain outside repository artifacts.

## Threats and controls

| ID | Threat and path | Control | Residual |
| --- | --- | --- | --- |
| TM-001 | Shell metacharacters in Codex arguments execute during handoff: B3 | Wrapper forwards `"$@"` to `command codex` and does not evaluate argument text. | A compromised `codex` executable remains outside this wrapper's control. |
| TM-002 | Finalization failure is hidden and loses the baton: B2 → B3 | Wrapper prints a fixed stderr message and leaves manual `handoff` available. | A killed shell or `kill -9` can still prevent automatic finalization. |
| TM-003 | Captured context leaves the local workstation or grows startup prompts: B1 → B2 | Loopback binding, no cloud features, single-use handoff, disabled briefing/MCP/routing/managed features. | The operator must configure path exclusions; free-form content remains outside complete DLP guarantees. |
| TM-004 | Runtime data becomes repository authority: B2 → workflow artifacts | Documentation names Git, `.specs/`, tasks, architecture docs, and `knowledge/` as canonical. | Operators can still manually copy stale content; review must preserve the stated boundary. |
| TM-005 | An internal Verifier or Deep Reviewer consumes Implementer handoff context and reviews with contaminated state: B2 → review process | Internal named subagents receive explicit role packets and do not consume Implementer handoff; top-level consumption is allowed only when no pending Implementer handoff exists. `drop_subagent_captures` is documented as storage/noise control, not role isolation. | Provider packet handling remains an operational boundary and requires independent review evidence. |

## Residual focus for review

Review wrapper argument forwarding, status preservation, visible failure handling, and documentation
defaults for loopback-only operation, bounded capture, exclusions, and disabled startup context.
