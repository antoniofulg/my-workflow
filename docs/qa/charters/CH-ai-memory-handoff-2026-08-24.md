# CH-ai-memory-handoff-2026-08-24

- **Date:** 2026-08-24
- **Time-box:** 35 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Setup boundary, Codex finalization, single-use provider handoff, and adoption canary
- **Public entry point:** `docs/workflow/ai-memory.md` → `scripts/ai-memory.zsh` → installed agent lifecycle hooks
- **Adapter candidate:** CLI/manual through the installed ai-memory `1.31.0`, an isolated zsh process, supported agent CLIs, and the public adoption script
- **Scenarios:** `WFL-ai-memory-handoff`, adjacent canary `ADP-adopt-workflow-safely`

## Mission

On the prepared workstation, confirm that the documented opt-in setup exposes one low-context baton
between Claude Code, Codex, and Cursor. Exercise automatic and manual Codex finalization, consume the
baton once in another provider, then prove that no recurring briefing or repository-owned runtime
state appears. Run adoption against a checkout-local disposable target as the adjacent canary.

## Starting state and boundaries

- ai-memory `1.31.0` is already installed, its server is already running on loopback, and lifecycle
  hooks are already installed for Claude Code, Codex, and Cursor.
- `scripts/ai-memory.zsh` has not been added to or sourced by the operator's persistent zsh startup
  configuration. Source it only in the QA shell; do not edit `~/.zshrc`.
- Use a disposable, non-secret baton and redact captured prompts or tool output. Do not add LLMs,
  embeddings, MCP registration, routing skills, managed workstreams, briefing, consolidation, or
  auto-improvement.
- Preserve existing unrelated agent configuration. Do not reinstall hooks unless inspection shows
  the prepared setup differs from the documented contract.
- Raw output and redacted agent-visible captures belong under
  `docs/qa/evidence/2026-08-24-ai-memory-handoff/`. Product defects return to an Implementer.

## Expected observable

The prepared setup reports the pinned local service and three project-routed hooks; an interactive
Codex exit finalizes exactly once without replacing its status; a compatible Claude Code or Cursor
session receives one concise project-scoped baton; the following supported session receives no old
baton or recurring briefing; and adoption plus repository inspection show no ai-memory runtime state
inside the target or source checkout.

## Criterion disposition

| Criterion | Disposition |
| --- | --- |
| AIM-01 | User-visible lifecycle promise; walk through `J-adopt-workflow` / `WFL-ai-memory-handoff` by ending one normal Claude Code or Cursor hooked session and observing one compatible pending baton. |
| AIM-02 | User-visible shell-helper promise; walk through `J-adopt-workflow` / `WFL-ai-memory-handoff` and observe one finalization plus the original Codex status. |
| AIM-03 | User-visible recovery promise; walk through `J-adopt-workflow` / `WFL-ai-memory-handoff` with fail-visible automatic finalization and the manual `handoff` fallback. |
| AIM-04 | User-visible startup-context promise; walk through `J-adopt-workflow` / `WFL-ai-memory-handoff` and observe zero-or-one delivery followed by no replay or briefing. |
| AIM-05 | Public setup/configuration promise; inspect the prepared `WFL-ai-memory-handoff` setup for all three hooks, `repo-root`, and sticky routing. |
| AIM-06 | Public setup/configuration promise; inspect `WFL-ai-memory-handoff` status and configuration for the explicitly disabled or absent capabilities. |
| AIM-07 | Public authority and filesystem promise; inspect `WFL-ai-memory-handoff` runtime paths and Git state, then confirm the adjacent `ADP-adopt-workflow-safely` canary. |
| AIM-08 | Public privacy-boundary promise; inspect the `WFL-ai-memory-handoff` loopback bind, bounded capture exclusions, and documented incomplete-DLP residual. |

## Planned probes

1. Capture the installed version and read-only service/configuration/hook status. Confirm `1.31.0`,
   `127.0.0.1:49374`, sticky routing, `repo-root` resolution for all three agents, external data and
   config paths, and preservation of unrelated hook configuration.
2. Inspect effective configuration and installed entries. Confirm startup briefing and
   auto-improvement are off and that no provider key, embedding, consolidation, MCP, routing skill,
   managed-workstream, or remote-server configuration participates in this setup. Confirm capture
   exclusions and the free-form prompt/shell-output DLP residual are visible in the public contract.
3. In an isolated zsh shell, source `scripts/ai-memory.zsh` without changing persistent shell files.
   Launch an interactive Codex session in this checkout, create a harmless disposable baton, exit
   normally, and record the child status, exactly one `finalize-session` call, and one pending
   project-compatible handoff.
4. Risk probe from Deep Review: run a noninteractive Codex command through the sourced helper and
   confirm it does not finalize an unrelated/latest interactive session. If it does, stop that path
   and register a product defect rather than consuming or repairing another session's handoff.
5. Exercise failure boundaries with controlled CLI state: finalization failure must print the
   documented error while preserving a nonzero Codex status; a killed Codex child with the wrapper
   still alive must finalize once; a dead wrapper/shell must remain recoverable through `handoff`.
   Use `--session-id <uuid>` instead of latest-session selection if sessions overlap.
6. Start Claude Code or Cursor from the same repository, a compatible subdirectory, or the linked
   worktree case documented by the scenario. Confirm the agent receives only the concise disposable
   baton and that repository files, not ai-memory, remain authoritative. Record redacted
   agent-visible evidence, consume the handoff, and keep that session open until the no-replay probe
   completes.
7. Start a second supported agent before ending the recipient session. Confirm the consumed baton is
   absent, no project briefing or managed transcript appears, and an empty pending state adds no
   ai-memory startup payload. Then create a second disposable baton in the still-open Claude Code or
   Cursor session, end it normally, and confirm the remaining provider receives exactly that new
   project/cwd-compatible handoff once.
8. Adjacent canary: run `scripts/adopt.py` against a checkout-local disposable target using the
   profile's existing CLI/manual adapter. Confirm ordinary adoption still succeeds and installs no
   ai-memory binary, runtime database, hook tree, marker, shell startup edit, or handoff file.
9. Stop only QA-owned transient activity and inspect source plus disposable target residue. The
   source checkout may contain only planned durable QA updates and ignored raw evidence; ai-memory
   runtime data must remain in the operator-owned external paths.

## Execution handoff

Use a fresh Verifier with the canonical `qa-execute` skill and the CLI/manual adapter declared in
`docs/qa/README.md`. Record a new dated report, update `WFL-ai-memory-handoff`, and confirm the
`ADP-adopt-workflow-safely` canary without resetting its existing verdict unless the observable
regresses. Do not install a framework or change product code during the walk.
