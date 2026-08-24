# Agent Model Routing Specification

## Problem Statement

Operators must edit provider-specific agent packets to change models or reasoning effort. The same
choice is duplicated across Claude, Codex, and Cursor syntax, which makes changes slow and lets the
runtime packets drift apart.

## Goals

- [ ] Make `.my-workflow.toml` the only manually edited source for every bundled agent model and effort.
- [ ] Materialize valid native metadata for Claude, Codex, and Cursor without changing packet instructions.
- [ ] Freeze delegated-role model and effort with each feature workflow snapshot.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Discovering provider model catalogs | Provider runtimes remain authoritative for model availability. |
| Selecting the top-level session model | The operator still starts Claude, Codex, or Cursor normally. |
| Model aliases shared across providers | Provider model identifiers have different semantics. |
| Concurrent sync commands in one checkout | Each checkout has one operator-owned workflow state. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Native packets still require model metadata | Generate metadata from `.my-workflow.toml` | All three runtimes consume native agent definitions. | yes |
| Sync timing | Explicit `--sync-agents`; adoption invokes it after installing packets | Resolution and resume remain read-only unless the operator requests refresh. | yes |
| Configuration coverage | Three providers and five roles, including planner | Every bundled packet becomes centrally configurable. | yes |
| Compatibility | Version 2 replaces version 1 with no fallback | Project policy requires hard cuts instead of compatibility layers. | yes |
| Snapshot scope | Freeze model and effort for delegated roles only | Planner is the current top-level session, not a delegated route. | yes |
| Effort validation | Validate the workflow effort vocabulary, then let runtimes enforce model compatibility | Availability varies by provider model and changes independently. | yes |
| Remaining implicit dimensions | Auth, rate limits, expiry, and external failures are N/A | The feature is a local deterministic file transformation with no network or identity boundary. | yes |

**Open questions:** none.

## User Stories

### P1: Configure every agent from one file ⭐ MVP

**User Story**: As a workflow operator, I want to change models and efforts in one TOML file so that
I do not edit three provider-specific packet trees.

**Why P1**: This is the requested capability and the only supported configuration path after the hard cut.

**Acceptance Criteria**:

1. The workflow SHALL define one model and one effort for each Claude, Codex, and Cursor combination of planner, implementer, verifier, explorer, and deep reviewer in `.my-workflow.toml`.
2. WHEN the operator runs `workflow_config.py --root <path> --sync-agents` THEN the workflow SHALL render each configured value in that provider's native packet syntax.
3. WHEN sync changes native metadata THEN the workflow SHALL preserve every non-model packet byte.
4. WHEN sync runs twice without a config change THEN the workflow SHALL leave every native packet byte-identical on the second run.
5. IF the model matrix, effort value, or native packet metadata is invalid THEN the workflow SHALL exit non-zero before changing any packet.
6. WHEN sync completes THEN the workflow SHALL report which packet paths changed and which were already current.

**Independent Test**: Change one entry for each provider in a disposable checkout, run sync twice,
and inspect native metadata plus unchanged packet bodies.

### P1: Freeze delegated execution settings

**User Story**: As a workflow operator, I want each feature snapshot to retain its delegated models
and efforts so that resume cannot silently use a newly synchronized setting.

**Why P1**: Provider routing is already frozen; model routing must obey the same resume contract.

**Acceptance Criteria**:

1. WHEN a feature workflow is first resolved or explicitly refreshed THEN the workflow SHALL store the selected provider's model and effort for every delegated role in `workflow.json`.
2. WHILE a feature workflow snapshot is resumed, the workflow SHALL return its frozen model and effort without reading replacements from `.my-workflow.toml`.
3. IF a resumed role packet's model or effort differs from its snapshot THEN the workflow SHALL exit non-zero with an instruction to synchronize and explicitly refresh.
4. The workflow SHALL synchronize planner packets without adding planner to delegated provider routing.

**Independent Test**: Resolve a feature, alter and synchronize a delegated model, observe resume
failure, then refresh and observe the new frozen values.

### P1: Adopt the centralized contract safely

**User Story**: As a consuming project maintainer, I want adoption to install a ready central config
without overwriting my existing choices or packet instructions.

**Why P1**: A central source is useful only when fresh and existing projects can adopt it predictably.

**Acceptance Criteria**:

1. WHEN adoption targets a project without `.my-workflow.toml` THEN the workflow SHALL install the bundled version 2 config and synchronize all installed agent packets.
2. WHEN adoption targets a project with `.my-workflow.toml` THEN the workflow SHALL preserve that file byte-for-byte and synchronize only model metadata in existing packets.
3. IF adoption cannot synchronize a consumer packet THEN the workflow SHALL exit non-zero and name the invalid packet.
4. The published workflow documentation SHALL describe `.my-workflow.toml` as the source of truth and the native model fields as generated metadata.

**Independent Test**: Adopt into empty and pre-populated disposable targets, compare config and
instruction bytes, and inspect all native model fields.

## Edge Cases

- IF a provider, role, model, or effort entry is missing THEN sync SHALL fail before packet writes.
- IF an unknown key exists in the model matrix THEN sync SHALL fail with its TOML path.
- IF a packet contains duplicate or missing model metadata THEN sync SHALL fail before packet writes.
- WHEN distinct checkouts use distinct configs THEN each checkout SHALL synchronize only its own packets.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| AMR-01 | Configure every agent | Tasks | In Tasks |
| AMR-02 | Configure every agent | Tasks | In Tasks |
| AMR-03 | Configure every agent | Tasks | In Tasks |
| AMR-04 | Configure every agent | Tasks | In Tasks |
| AMR-05 | Freeze execution settings | Tasks | In Tasks |
| AMR-06 | Freeze execution settings | Tasks | In Tasks |
| AMR-07 | Adopt centralized contract | Tasks | In Tasks |
| AMR-08 | Adopt centralized contract | Tasks | In Tasks |

**Coverage:** 8 total, 8 mapped to tasks, 0 unmapped.

## Success Criteria

- [ ] One TOML edit and one sync command update native settings for every provider.
- [ ] All provider packets match the central matrix after the full gate.
- [ ] Resume rejects model or effort drift until explicit refresh.
- [ ] Fresh and repeated adoption preserve the documented ownership boundaries.
