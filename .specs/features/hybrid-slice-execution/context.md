# Hybrid Slice Execution Context

**Gathered:** 2026-08-28
**Spec:** `.specs/features/hybrid-slice-execution/spec.md`
**Status:** Approved for design

## Feature Boundary

Replace the vendored TLC phase-batch workflow with one workflow-owned skill that dispatches safe
vertical slices through adaptive assisted execution. The feature owns context packets, configuration,
scheduling, worktree and Orca lifecycle, independent verification, adoption, and truthful QA evidence.
It does not modify Orca or publish the workflow.

## Human Decisions

### Workflow-owned skill

- The installed skill is named `workflow-spec-driven`.
- It is an adaptation of `tlc-spec-driven` 3.3.0 and retains CC BY 4.0 attribution in a `NOTICE.md`.
- The old `.agents/skills/tlc-spec-driven` path and all references are removed in the same change.
- No compatibility alias, fallback name, or dual-install period is allowed.

### Context contract

- Each implementation worker receives only its slice tasks, cited acceptance criteria, assigned test
  IDs, gate, needed design excerpt, and compact slice memory.
- Planning transcripts, complete project state, unrelated slices, and whole feature artifacts are not
  copied into a slice packet.
- Packet sizes are measured in bytes by an executable check and emitted as redacted JSON telemetry.

### Hybrid scheduling

- Planner, coordinator, Explorer, and read-only reviewers use the clean feature integration checkout.
- Only implementers that will write concurrently receive isolated worktrees.
- Tasks inside one slice run sequentially in one implementer session and checkout.
- Assisted execution is the default. `disabled` is the explicit serial override.
- Automatic concurrency starts with two lanes, adds at most one healthy lane per settle window, and
  stops at four. A project can supply a positive integer cap.
- Missing or invalid machine-health evidence prevents admission above two lanes.
- Heavy gates reuse the existing resource-provider lease protocol. No second lock service is added.

### Verification independence

- Every code-changing slice receives a fresh Technical Verifier after its commit and scoped gate.
- Deep Review runs on the integrated feature tree at the frozen review cadence.
- QA Plan and QA Execute use fresh Verifier sessions after Deep Review.
- The last implementer writes a handoff only. It never certifies its own work or performs final QA.

### Orca limitation

- The workflow is not an Orca patch.
- Long worker packets are stored on disk; Orca receives only a short pointer.
- Automated gates use a fake Orca and fake resource provider. They never require a live Orca run.
- The live-host journey remains truthfully `blocked-verify` until the upstream transport capability is
  available and a human schedules that external verification.

## Agent Discretion

- Exact internal Python function names and file decomposition, provided public CLI/config contracts
  and test outcomes remain unchanged.
- Health thresholds may use conservative platform-native signals, but the helper must use only the
  Python standard library and host commands already present.
- A worker session may be renewed after a slice checkpoint while its clean worktree remains reusable;
  only the compact checkpoint memory crosses into the replacement session.

## Deferred Ideas

- Shared model-memory or provider-level prompt-cache control across workers.
- New Orca APIs, idempotency keys, or transport fixes owned by the Orca team.
- More than four automatically admitted lanes.
- Remote execution, deployment, release, or package publication.
