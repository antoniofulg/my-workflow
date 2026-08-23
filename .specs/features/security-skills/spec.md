# External Security Skills Specification

## Problem Statement

The workflow identifies security surfaces but does not install the security skills that act on them. Adoption must expose a reviewed, reproducible installation step without silently adding third-party code to a consuming project.

## Goals

- [ ] Install three reviewed upstream security skills only after explicit authorization.
- [ ] Preserve consumer files and restore the target exactly when installation fails.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Vendoring third-party security skills | Onboarding should consume reviewed upstream snapshots. |
| Installing `latest` or automatic updates | Provenance must remain reproducible and reviewable. |
| Changing the existing security gate | This feature supplies skills, not gate policy. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Installation authority | Require an explicit `--yes` invocation after adoption | Third-party code installation must not be implicit | yes |
| Upstream versions | Pin CLI version, 40-character refs and 64-character tree hashes | Reproducible provenance is safer than `latest` | yes |
| Failure behavior | Fail closed and restore the pre-install target | Partial publication can corrupt consumer state | yes |
| Existing workflow files | Preserve unrelated files and lock entries | Security onboarding owns only its three managed skills | yes |

**Open questions:** none.

## User Stories

### P1: Authorized installation

**User Story**: As a workflow adopter, I want a reviewed command that installs security skills so that agents can apply the security policy without hidden third-party writes.

**Acceptance Criteria**:

1. WHEN adoption completes THEN the system SHALL leave all three security skill trees absent and print the exact authorized installation command. <!-- SSK-01 -->
2. The system SHALL identify every external skill with a repository, allowlisted source type, immutable 40-character commit, skill path and 64-character expected tree hash. <!-- SSK-02 -->
3. WHEN the printed command is invoked with `--yes` THEN the system SHALL install exactly the three pinned trees under `.agents/skills/` and create their Claude skill links. <!-- SSK-03 -->
4. WHILE publishing managed skills, the system SHALL preserve consumer-owned files and unrelated `skills-lock.json` entries byte-for-byte. <!-- SSK-04 -->
5. IF the external CLI fails, is unavailable, changes managed paths or produces a mismatched tree THEN the system SHALL return non-zero, restore the pre-install target and report that the security gate remains unavailable. <!-- SSK-05 -->
6. The system SHALL keep reviewed refs, provenance and hashes authoritative in `skills-lock.json` and reject `latest` or unreviewed metadata. <!-- SSK-06 -->
7. WHEN users read onboarding output or README instructions THEN the system SHALL distinguish bundled workflow skills from separately authorized external security skills. <!-- SSK-07 -->

**Independent Test**: Adopt into a disposable Git project, verify absence, run the printed authorized command, then verify exact provenance, trees, links and preserved sentinels.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Runtime dependency and onboarding behavior | Explicit second step with immutable provenance | SSK-01, SSK-02, SSK-03, SSK-06 |
| S6 | Filesystem paths and subprocess environment | No-follow validation, staging and target isolation | SSK-04, SSK-05 |
| S9 | External Git repositories and CLI | Pinned refs, CLI version and tree hashes | SSK-02, SSK-05, SSK-06 |
| S11 | Concurrent processes and target publication | Per-target lock, atomic publication and rollback | SSK-04, SSK-05 |

## Edge Cases

- IF `--yes` is absent THEN the system SHALL print the plan, return status 2 and leave the target unchanged.
- IF a managed path or lock path resolves through a symlink outside the target THEN the system SHALL return non-zero without modifying the referent.
- IF two installers target the same project THEN the system SHALL serialize them so a failed installer cannot roll back a completed install.
- IF `MY_WORKFLOW_TARGET` exists in the caller environment THEN the system SHALL remove it before invoking the external CLI.
- IF the caller supplies active `npx` or `git` toolchain candidates THEN the system SHALL validate both the lexical candidate and its resolved target outside the consumer target, staging root, and workflow pack; execute the original validated candidate path so host shims retain dispatch semantics; and give the child only the validated tool parents plus fixed system roots in `PATH`, with secrets removed. <!-- SEC-005 -->

## Requirement Traceability

| Requirement ID | Story | Slice | Status |
| --- | --- | --- | --- |
| SSK-01 | Authorized installation | 2 | Done |
| SSK-02 | Authorized installation | 1 | Done |
| SSK-03 | Authorized installation | 1 | Done |
| SSK-04 | Authorized installation | 1 | Done |
| SSK-05 | Authorized installation | 1 | Done |
| SSK-06 | Authorized installation | 1 | Done |
| SSK-07 | Authorized installation | 2 | Done |

**Coverage:** 7 total, 7 mapped, 0 unmapped.

## Success Criteria

- [x] A fresh adopted project can install the three pinned skills through the documented public command.
- [x] All authorization, provenance, isolation, concurrency and rollback cases pass against current `main`.
