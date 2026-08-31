# Release 0.8.0 Specification

## Problem Statement

The verified lock, legacy-adoption, and remediation changes exist only on local branches. The
current public release remains 0.7.0, so adopters cannot consume those changes from a stable tag.

## Goals

- Publish one integrated 0.8.0 source pack through the existing GitHub release channel.
- Keep package, changelog, canonical release test, and QA scenario on one version, with the Bun
  lockfile aligned to the root package and dependency graph.
- Preserve the package's private, non-npm distribution boundary.

## Out of Scope

| Capability | Reason |
| --- | --- |
| npm publication | `package.json` declares the package private and prior releases use GitHub. |
| Live Orca transport verification | The external host bug remains outside this release. |
| Additional PR #72 changes | Release scope is limited to the already verified candidate branches. |

## Assumptions & Open Questions

| Decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Version | `0.8.0` | Modular legacy adoption and configurable cross-project test locks are new public capabilities. | user requested |
| Distribution | GitHub tag and GitHub Release | Matches 0.7.0 and the private package contract. | repository evidence |
| Candidate branches | legacy adoption plus remediation | Their integrated tree already passed the full local gate. | recorded verification |

**Open questions:** none.

## User Stories

### P1: Consume the verified workflow as release 0.8.0

**User Story**: As a workflow adopter, I want one stable 0.8.0 release so that existing and new
projects can use modular adoption, shared test locks, and bounded remediation from one source pack.

**Acceptance Criteria**:

1. WHEN the release candidate is prepared THEN package metadata, the newest changelog heading, the canonical release test, and the current release scenario SHALL identify version `0.8.0`, while `bun.lock` SHALL identify the root package and dependency graph.
2. WHEN the source pack is inspected THEN it SHALL remain private, contain the adopted parallel tooling, and produce no publication residue.
3. WHEN release QA runs THEN it SHALL verify the full gate, package membership, disposable legacy adoption, first-use cross-project locking, and effect-free probe import.
4. IF live Orca transport is not verified THEN the release SHALL retain the `blocked-verify` boundary and SHALL NOT claim a successful live Orca run.
5. WHEN remote delivery completes THEN one pull request SHALL be merged and tag `v0.8.0` plus its GitHub Release SHALL point to the merged release commit.

**Independent Test**: Compare all version authorities and the Bun lockfile's root package and
dependency graph, run the complete mixed-language gate, inspect the dry-run package, adopt into
disposable legacy repositories, contend for a new machine-scoped lock, and import the installed
Orca probe with a fake executable that records zero calls.

## Edge Cases

- IF package dependencies and the Bun lockfile disagree THEN `bun install --frozen-lockfile` SHALL fail.
- IF any release QA leg is untested without an explicit `blocked-verify` boundary THEN remote
  publication SHALL stop.
- IF `origin/main` moves before merge THEN the release SHALL integrate it and rerun the full gate.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| RLS-01 | P1: consistent release identity | Specify | Verified |
| RLS-02 | P1: private source pack | Specify | Verified |
| RLS-03 | P1: independent release QA | Specify | Verified |
| RLS-04 | P1: honest Orca boundary | Specify | Verified |
| RLS-05 | P1: remote release identity | Specify | Planned |

**Coverage:** 5 total, 5 mapped to P1, 0 unmapped.

## Success Criteria

- [x] All release version authorities report 0.8.0, and the Bun lockfile reports the root package and dependency graph.
- [x] Full gate and independent release QA pass.
- [ ] The merged commit is tagged and published as GitHub Release v0.8.0.
