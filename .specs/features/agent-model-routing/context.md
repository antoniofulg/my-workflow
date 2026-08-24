# Agent Model Routing Context

**Gathered:** 2026-08-24
**Spec:** `.specs/features/agent-model-routing/spec.md`
**Status:** Ready for design

## Feature Boundary

Move manual model and effort selection into `.my-workflow.toml`, materialize the native metadata
required by Claude, Codex, and Cursor, and freeze delegated settings in feature workflow snapshots.

## Implementation Decisions

### Source of truth

- `.my-workflow.toml` owns all model and effort choices.
- Native provider packets retain generated metadata because each runtime requires it.
- Packet instructions remain provider-owned content and are never generated from TOML.

### Roles

- Synchronize planner, implementer, verifier, explorer, and deep reviewer for every provider.
- Keep planner outside delegated-role provider routing.

### Agent's Discretion

- Command output shape and internal renderer structure.
- Exact test fixture organization.

### Declined / Undiscussed Gray Areas → Assumptions

- Automatic sync during ordinary resolution was not requested. Explicit sync avoids hidden tracked-file writes.
- Provider model discovery was not requested. Native runtimes validate model availability.

## Specific References

- The operator wants model and effort access in `.my-workflow.toml` instead of manual edits under
  `.claude`, `.codex`, and `.cursor`.
- The operator confirmed that native packets may retain generated runtime metadata.

## Deferred Ideas

- Named model presets and remote provider catalog discovery.
