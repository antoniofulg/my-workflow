# Host-Owned Session Continuation Specification

## Problem Statement

The repository publishes an optional session-memory integration even though host-native continuation now covers its use case. The v0.6.0 breaking release removes that repository-owned subsystem while preserving durable repository context, independent review, historical release evidence, and external operator state.

## Goals

- [ ] Remove every active implementation, instruction, test, QA promise, and packaged artifact for the obsolete integration.
- [ ] Define host-owned continuation and fresh reviewer packets without adding a replacement runtime or host dependency.
- [ ] Prepare, validate, and document the local v0.6.0 release state without publishing it.
- [ ] Preserve historical v0.4.0/v0.5.0 evidence byte-for-byte.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Host continuation implementation | The host owns session continuation. |
| Orca dependency or generic Orca commands | The repository remains host-neutral; Orca belongs only in decision rationale. |
| External installation cleanup | External operator state is outside repository ownership. |
| Compatibility commands, stubs, wrappers, aliases, toggles, or migrations | The removal is intentionally breaking. |
| Push, pull request, merge, package publication, GitHub release, deploy, or operator-machine mutation | These actions need later explicit authorization. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Obsolete feature workflow state conflicts with the final reference allowlist | Delete `.specs/features/ai-memory-handoff/`; retain its Git history | Archiving would leave active repository matches outside the user-approved historical categories | y |
| v0.5.0 cleanup guidance | Link to the tagged v0.5.0 guide without executing its lifecycle commands | Prevents invented commands and external-state mutation | y |
| Release state | Prepare version `0.6.0` locally without releasing it | Another feature may join the release and publication remains human-authorized | y |
| Historical evidence scope | Preserve dated QA reports, charters, bugs, evidence, release certification, and historical changelog entries byte-for-byte | These records describe earlier releases rather than current promises | y |

**Open questions:** none - all resolved or logged above.

## User Stories

### P1: Remove the published integration

**User Story**: As a workflow maintainer, I want the obsolete repository-owned integration deleted so that current adoption and packaging expose no session-memory subsystem.

**Why P1**: This is the breaking product change.

**Acceptance Criteria**:

1. The repository SHALL contain none of the four deleted active paths named in the removal brief. (HSC-01)
2. WHEN adoption runs in a clean disposable fixture THEN the adopted checkout SHALL contain no integration script, guide, config, database, marker, source line, hook, handoff payload, or feature-specific test. (HSC-02)
3. WHEN adoption runs again in the same disposable fixture THEN the adopted checkout SHALL remain idempotent and SHALL not mutate shell startup files, Git hooks, or host settings. (HSC-03)
4. WHEN package contents are generated locally THEN the package manifest SHALL contain no removed integration artifact. (HSC-04)

**Independent Test**: Adopt into a disposable fixture twice, inspect repository and host-boundary sentinels, then inspect `npm pack --dry-run --json`.

### P1: Publish the host-owned continuation contract

**User Story**: As an operator, I want current guidance to assign continuation to the host while keeping repository artifacts authoritative so that I can resume across providers without a repository runtime.

**Why P1**: Removal needs one current, host-neutral replacement rule.

**Acceptance Criteria**:

1. The current README and workflow index SHALL state: “Cross-provider session continuation is owned by the host. Repository files, Git state, feature artifacts, and explicit handoff prompts remain the durable semantic context.” (HSC-05)
2. The repository SHALL provide no current instruction to install, enable, source, disable, re-enable, purge, isolate, detect, test, or use the removed integration. (HSC-06)
3. The reviewer contract SHALL require Verifier and Deep Reviewer to receive fresh role packets, exclude the Implementer transcript and operator handoff, and derive conclusions from the spec, diff, tests, and assigned evidence. (HSC-07)
4. The current generic guidance SHALL contain no Orca dependency or Orca command. (HSC-08)

**Independent Test**: Run the current-contract scan and inspect the reviewer rule.

### P1: Preserve history while updating current QA

**User Story**: As a release reviewer, I want current QA to describe v0.6.0 while older evidence remains unchanged so that current promises and historical facts do not conflict.

**Why P1**: QA documentation and adoption behavior are public interfaces.

**Acceptance Criteria**:

1. The current QA profile, journey, and scenarios SHALL contain no active continuity promise owned by the removed integration. (HSC-09)
2. WHEN v0.6.0 QA is planned and executed THEN the repository SHALL contain a new dated charter and execution report covering documentation, adoption, package contents, version parity, and the reference allowlist. (HSC-10)
3. The immutable historical evidence files identified by the removal plan SHALL remain byte-for-byte equal to their `v0.5.0` versions. (HSC-11)
4. WHEN the final reference scan runs THEN every remaining match SHALL belong to an explicit file allowlist classified as historical changelog, historical QA evidence, or the v0.6.0 removal note. (HSC-12)

**Independent Test**: Compare historical paths with `v0.5.0`, validate current QA state, and run the explicit-allowlist scan.

### P1: Prepare the breaking v0.6.0 state

**User Story**: As a maintainer, I want all release authorities aligned at v0.6.0 so that the combined release can be reviewed later without publishing it now.

**Why P1**: Version drift would make the release state invalid.

**Acceptance Criteria**:

1. The package manifest, lockfile, current QA release scenario, and every release-version assertion SHALL equal `0.6.0`. (HSC-13)
2. The v0.6.0 changelog entry SHALL record removal, host responsibility, durable semantic context, and the rule that adoption never removes external operator state. (HSC-14)
3. The v0.6.0 migration note SHALL link to the tagged v0.5.0 lifecycle guide and SHALL not invent or execute cleanup commands. (HSC-15)
4. The project decision `AD-011` SHALL supersede `AD-008`, name Orca only as rationale evidence, and establish the host-neutral ownership boundary. (HSC-16)
5. The prepared repository SHALL remain local-only with no tag, push, pull request, merge, publication, release, deploy, or operator-machine mutation performed by this feature. (HSC-17)

**Independent Test**: Run release parity, decision-index, Git-state, and local package checks.

## Edge Cases and Implicit-Requirement Sweep

| Dimension | Resolution |
| --- | --- |
| Input validation and bounds | The reference contract uses an explicit path allowlist; broad directory exclusions are invalid. |
| Failure and partial failure | Any non-zero required gate or QA verdict blocks completion; no test may be weakened or skipped. |
| Idempotency and retry | Re-adoption must leave repository output stable and host-boundary sentinels unchanged. |
| Auth boundaries and rate limits | N/A because this feature adds no authenticated or network surface. |
| Concurrency and ordering | N/A because work is local and sequential; unrelated concurrent changes must remain visible and untouched. |
| Data lifecycle and expiry | External runtime state is never removed; repository-owned obsolete paths are deleted. |
| Observability | Gate, QA, package, and final scan commands provide counted evidence. |
| External-dependency failure | The migration note links historical guidance; it does not invoke an external runtime. |
| State-transition integrity | `AD-008` becomes superseded only when `AD-011` is appended and the decision index is regenerated. |

## Security Surfaces

None. The feature removes a runtime and performs no shell startup, hook, external database, credential, network, or production mutation.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| HSC-01 | Remove the published integration | Tasks | Pending |
| HSC-02 | Remove the published integration | Tasks | Pending |
| HSC-03 | Remove the published integration | Tasks | Pending |
| HSC-04 | Remove the published integration | Tasks | Pending |
| HSC-05 | Publish host-owned continuation | Tasks | Pending |
| HSC-06 | Publish host-owned continuation | Tasks | Pending |
| HSC-07 | Publish host-owned continuation | Tasks | Pending |
| HSC-08 | Publish host-owned continuation | Tasks | Pending |
| HSC-09 | Preserve history and update QA | Tasks | Pending |
| HSC-10 | Preserve history and update QA | Tasks | Pending |
| HSC-11 | Preserve history and update QA | Tasks | Pending |
| HSC-12 | Preserve history and update QA | Tasks | Pending |
| HSC-13 | Prepare v0.6.0 | Tasks | Pending |
| HSC-14 | Prepare v0.6.0 | Tasks | Pending |
| HSC-15 | Prepare v0.6.0 | Tasks | Pending |
| HSC-16 | Prepare v0.6.0 | Tasks | Verified |
| HSC-17 | Prepare v0.6.0 | Tasks | Pending |

**Coverage:** 17 total, 17 mapped to tasks, 0 unmapped.

## Success Criteria

- [ ] All required gates pass with zero failures after the final mutation.
- [ ] The explicit reference scan reports only classified allowed matches.
- [ ] Historical evidence checks report zero changed protected files.
- [ ] Independent technical verification, QA plan, and QA execution pass.
- [ ] Local Git history contains atomic task commits and no remote action occurs.
