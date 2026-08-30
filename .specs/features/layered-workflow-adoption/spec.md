# Layered Workflow Adoption Specification

## Problem Statement

The adopter installs the entire workflow as one destructive bundle. Existing projects cannot inspect a smaller adoption, add capabilities incrementally, or distinguish workflow-owned files from consumer changes. The feature introduces fixed, dependency-aware layers with read-only planning/status and conflict-safe application.

## Goals

- [ ] A project can inspect and apply only the workflow capabilities it wants.
- [ ] Re-adoption updates workflow-owned bytes without overwriting consumer changes.
- [ ] Existing project instructions survive adoption through managed blocks.
- [ ] The `full` profile preserves the capabilities of the current complete adoption.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Removing an installed layer | Deletion needs a separate ownership and recovery contract. |
| Selecting individual skills or files | Fixed layers keep dependencies valid and the surface small. |
| Modifying a consumer's `package.json` or `bun.lock` | Bun is a host prerequisite; product package ownership stays with the consumer. |
| External security-skill installation | `scripts/install_security_skills.py` remains a separate explicit operation. |
| A plugin framework or user-defined layer graph | Four fixed layers cover the observed adoption need. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Public command transition | Remove the positional legacy command; require `plan`, `apply`, or `status` | The workflow forbids compatibility aliases and updates all callers together. | y |
| Layer selection | `plan` and `apply` require `--layers`; `full` resolves all four layers | Explicit mutation scope is safer than a hidden default. | y |
| Re-applying a subset | Union requested layers with already installed layers; never remove omitted layers | v1 is additive/update-only. | y |
| Managed-file conflict | Abort the complete apply before the first write | Partial adoption and silent overwrite are both unsafe. | y |
| Existing identical file | Claim it as managed when its bytes equal the source | This supports projects that copied workflow files manually. | y |
| Existing differing workflow path | Report conflict and perform zero writes | Ownership is unknown until the human resolves it. | y |
| Consumer instruction files | Preserve prose and manage only delimited workflow blocks; `--skip-agents` touches neither `AGENTS.md` nor `CLAUDE.md` | Existing projects own their instructions. | y |
| Status exit codes | `0` clean, `1` drift/missing/conflict, `2` invalid invocation or manifest | Stable codes make status usable in CI. | y |
| Bun boundary | The consumer supplies Bun 1.4.x; adoption never edits product package metadata | All consuming projects already execute with Bun. | y |

**Open questions:** none.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Public adoption CLI and manifest schema | Fixed layer catalog, strict schema/version, deterministic output | LAY-01, LAY-02, LAY-11, LAY-15 |
| S6 | Target filesystem paths, hashes, instruction blocks | Root containment, no-follow symlink preflight, hash ownership, preflight-before-write | LAY-05, LAY-06, LAY-07, LAY-08, LAY-09 |
| S11 | Generated provider packets and checkout-local configuration | Synchronize only after a successful core apply; preserve consumer config | LAY-10, LAY-14 |

## User Stories

### P1: Inspect an adoption before changing a project

**User Story**: As a project maintainer, I want to plan selected workflow layers so that I can review every effect before applying it.

**Acceptance Criteria**:

1. The adopter SHALL expose exactly `core`, `parallel`, `quality`, and `extras`, with `full` as the profile resolving all four.
2. WHEN `plan TARGET --layers LIST` runs THEN the adopter SHALL emit deterministic resolved layers and per-path actions without changing the target.
3. WHERE `--json` is present the adopter SHALL emit one parseable JSON object on stdout and diagnostics only on stderr.
4. IF a requested layer is unknown or the fixed dependency graph is invalid THEN the adopter SHALL exit `2` before reading or writing target-owned content.

**Independent Test**: Snapshot a target, run text and JSON plans, and confirm an identical snapshot plus exact resolved layers/actions.

### P1: Apply workflow capabilities incrementally

**User Story**: As a maintainer of an existing project, I want to add workflow layers without losing project files or prose.

**Acceptance Criteria**:

1. WHEN a layer is applied THEN the adopter SHALL include `core` transitively and install only the cumulative union of requested and already installed layers.
2. WHEN apply succeeds THEN `.my-workflow/adoption.json` SHALL record schema version `1`, workflow version, sorted installed layers, and per-file source and installed SHA-256 ownership without timestamps.
3. WHEN a previously managed file still equals its recorded installed hash THEN apply SHALL update it to the current source bytes and hashes.
4. IF a managed file differs from its recorded installed hash, or an unowned destination differs from the source, THEN apply SHALL report every conflict and perform zero writes.
5. WHEN `AGENTS.md` or `CLAUDE.md` already contains consumer prose THEN apply SHALL preserve that prose byte-for-byte outside the selected managed blocks.
6. WHERE `--skip-agents` is present apply SHALL leave both instruction files byte-identical.
7. IF any selected destination or parent is a symlink, non-directory parent, or escapes the target THEN apply SHALL fail before any target or external mutation.
8. WHEN the same layers and source bytes are applied again THEN the target and manifest SHALL remain byte-identical.
9. WHEN an installed layer is omitted from a later request THEN apply SHALL retain it and SHALL NOT remove any recorded or consumer file.

**Independent Test**: Apply `core`, then `parallel`, then `quality,extras` to an existing disposable project; verify preserved consumer content, cumulative manifest, conflicts, idempotence, and zero external writes.

### P1: Inspect installed state

**User Story**: As a maintainer, I want a read-only status command so that I know whether workflow-owned files drifted.

**Acceptance Criteria**:

1. WHEN `status TARGET` reads a valid installation THEN it SHALL report each installed layer and every managed file as clean, missing, modified, or retained.
2. WHEN all recorded managed bytes and blocks match THEN status SHALL exit `0`; WHEN any are missing, modified, or conflicting THEN it SHALL exit `1` without writes.
3. IF the manifest is missing, malformed, has an unsupported schema, duplicate path, or path escaping the target THEN status and apply SHALL exit `2` without writes.

**Independent Test**: Apply a layer, mutate and remove recorded files one at a time, and assert exact status output/codes with an unchanged target snapshot.

### P1: Preserve complete and Bun-native adoption

**User Story**: As a current workflow user, I want the complete profile to retain today's capabilities while remaining Bun-native.

**Acceptance Criteria**:

1. WHEN `apply TARGET --layers full` succeeds THEN the installed capability set SHALL equal the prior complete adopter's core, parallel, quality, and extras paths, including missing-only ownership and agent synchronization.
2. WHEN a selected layer does not include `core` explicitly THEN dependency resolution SHALL still install core before dependent layer paths.
3. WHEN core is installed THEN provider packet synchronization SHALL run only after all selected writes and manifest replacement succeed.
4. WHEN adopted knowledge tooling is invoked THEN `bun tools/knowledge/src/cli.ts` SHALL run without npm, npx, tsx, package-lock, or changes to the consumer's package metadata.
5. WHEN the old positional `adopt.py TARGET` form is used THEN the adopter SHALL reject it with exit `2` and direct the caller to the new subcommands.

**Independent Test**: Compare full-profile paths with the pre-feature adoption inventory and run the installed knowledge CLI in a Bun consumer fixture.

## Edge Cases

- IF `--layers` contains duplicates or whitespace THEN the adopter SHALL normalize to a deterministic unique dependency order.
- IF a manifest records a layer no longer requested THEN status SHALL report it as installed and apply SHALL retain it.
- IF a managed block marker is missing, duplicated, nested, or altered THEN apply SHALL report a conflict and perform zero writes.
- IF a consumer-owned missing-only file already exists THEN apply SHALL preserve it and record consumer ownership without hashing the whole file as managed.
- IF synchronization fails after selected files were staged THEN apply SHALL leave the prior target and manifest unchanged.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| LAY-01 | Inspect | Design | In Design |
| LAY-02 | Inspect | Design | In Design |
| LAY-03 | Inspect | Design | In Design |
| LAY-04 | Inspect | Design | In Design |
| LAY-05 | Apply | Design | In Design |
| LAY-06 | Apply | Design | In Design |
| LAY-07 | Apply | Design | In Design |
| LAY-08 | Apply | Design | In Design |
| LAY-09 | Apply | Design | In Design |
| LAY-10 | Apply | Design | In Design |
| LAY-11 | Status | Design | In Design |
| LAY-12 | Status | Design | In Design |
| LAY-13 | Status | Design | In Design |
| LAY-14 | Complete/Bun | Design | In Design |
| LAY-15 | Complete/Bun | Design | In Design |
| LAY-16 | Complete/Bun | Design | In Design |
| LAY-17 | Complete/Bun | Design | In Design |
| LAY-18 | Complete/Bun | Design | In Design |

**Coverage:** 18 total, 18 mapped to the test contract, 0 unmapped.

## Success Criteria

- [ ] An existing project can adopt `core` without replacing consumer prose or package metadata.
- [ ] Adding `parallel` or `quality` changes only the resolved layer paths and managed instruction blocks.
- [ ] Every conflict and unsafe path fails before mutation.
- [ ] `full` retains the complete v0.7.0 capability set.

