# Configurable Test Lock Specification

## Problem Statement

Parallel worktrees can start heavy test commands that compete for the same browser, database,
container runtime, ports, CPU, or memory. Consumer projects need one portable command wrapper that
serializes only the declared resource while leaving implementation and unrelated tests concurrent.

## Goals

- [ ] Serialize a named heavy-test resource across worktrees of one project by default.
- [ ] Allow the same named resource to be serialized across projects on one machine.
- [ ] Install the dormant capability through the existing `parallel` adoption layer.
- [ ] Fail closed before the wrapped command when configuration or lock acquisition is unsafe.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Automatic classification of heavy tests | The consuming project owns its test topology. |
| Editing consumer `package.json` or `Makefile` commands during adoption | Those files are product-owned. |
| Lane-wide resource leases | The existing `resource_provider` contract already owns that lifecycle. |
| Windows support | The supported adoption environments are Unix-like and the proven locks use kernel file locks. |
| More adoption selectors | Runtime opt-in inside the existing `parallel` layer avoids a second catalog dimension. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Default scope | `project` | Independent projects should not block each other unless explicitly configured. | Yes |
| Cross-project scope | `machine` | The same resource name becomes one machine-wide lane when the consumer requests it. | Yes |
| Lock granularity | One named resource per wrapped command | The resource, not the whole test suite, is the contention boundary. | Yes |
| Activation | Explicit wrapper invocation | Installing `parallel` must not silently change consumer gates. | Yes |
| Timeout | 2,700 seconds by default; configurable per invocation | Matches the proven CRM ceiling while keeping waits bounded. | Agent default |
| Project identity | Resolved Git common directory | Linked worktrees share an identity while unrelated repositories remain independent. | Agent default |
| Remaining dimensions | Authentication, persistence, data expiry, and external providers are N/A | The feature is a local process and filesystem coordination tool. | Agent default |

**Open questions:** none - all resolved or logged above.

## User Stories

### P1: Serialize a heavy command by resource

**User Story**: As an agent working in parallel worktrees, I want a named test resource to admit one
command at a time so that heavy gates do not corrupt each other or exhaust the machine.

**Why P1**: Resource-safe concurrency is required for dependable parallel delivery.

**Acceptance Criteria**:

1. WHEN two project-scoped invocations from linked worktrees request the same resource THEN the system SHALL start the second wrapped command only after the first releases the lock.
2. WHEN two machine-scoped invocations from different repositories request the same resource THEN the system SHALL start the second wrapped command only after the first releases the lock.
3. WHEN two invocations request different resource names THEN the system SHALL allow both wrapped commands to run concurrently.
4. WHEN no scope is supplied THEN the system SHALL use `project` scope.
5. WHEN the wrapped command exits THEN the system SHALL return the wrapped command's exit status.
6. IF the acquisition timeout expires THEN the system SHALL exit non-zero without starting the wrapped command.
7. IF the lock holder terminates normally or abnormally THEN the system SHALL make the resource acquirable without manual lock-file cleanup.

**Independent Test**: Two subprocesses contend on one resource while timestamped sentinels prove
serialized start, then repeat with distinct resources and machine scope.

### P1: Configure and diagnose the lock safely

**User Story**: As a project maintainer, I want explicit scope, resource, and timeout controls so that
each heavy gate uses the smallest safe contention boundary.

**Why P1**: A global all-tests lock would discard useful parallelism.

**Acceptance Criteria**:

1. WHEN a maintainer invokes `run --resource <name> --scope <project|machine> --timeout-seconds <n> -- <command>` THEN the system SHALL apply those exact lock settings to that command.
2. WHILE an invocation waits for an occupied resource the system SHALL emit bounded diagnostics containing the resource, scope, holder PID, holder project identifier, and holder start time.
3. IF scope, resource, timeout, or command input is invalid THEN the system SHALL exit non-zero before executing the command.
4. The system SHALL pass command arguments directly without shell interpolation.
5. The system SHALL omit wrapped command arguments and environment values from lock metadata and diagnostics.

**Independent Test**: Contract tests invoke literal metacharacter arguments, invalid inputs, and an
occupied lock, then assert exact execution and diagnostics without secret payloads.

### P1: Adopt the capability without changing consumer behavior

**User Story**: As a workflow adopter, I want the lock tool installed with parallel tooling so that I
can opt heavy gates into it without receiving another adoption framework.

**Why P1**: Portability is the reason to centralize the capability.

**Acceptance Criteria**:

1. WHEN the `parallel` layer is applied THEN the system SHALL install `tools/test_resource_lock.py` and track it in the adoption manifest.
2. WHEN the `core` layer is applied without `parallel` THEN the system SHALL omit `tools/test_resource_lock.py`.
3. WHILE the installed wrapper is not invoked the system SHALL leave every consumer command and gate unchanged.

**Independent Test**: Existing adoption tests apply `core` and `parallel` into disposable projects
and assert the installed path and absence boundary.

## Edge Cases

- IF project scope runs outside a Git repository THEN the system SHALL fail before executing the command.
- IF a resource name contains traversal, separators, whitespace, or exceeds 64 characters THEN the system SHALL reject it before filesystem mutation.
- IF the private lock directory is a symlink or is owned by another user THEN the system SHALL fail before opening a lock file.
- WHEN a waiting process is interrupted THEN the system SHALL exit without disturbing the current holder.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Public CLI and adoption inventory | Exact argparse contract and manifest assertions | CTL-04, CTL-08, CTL-09 |
| S6 | Command arguments and temporary lock paths | Direct argv execution, validated resource names, private lock directory | CTL-08, SEC-001, SEC-002, SEC-003 |
| S11 | Concurrent local processes and inherited file descriptors | Kernel lock, bounded acquisition, holder-safe interruption | CTL-01, CTL-02, CTL-06, CTL-07 |

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| CTL-01 | Serialize project resource | Tasks | Verified by T1 |
| CTL-02 | Serialize machine resource | Tasks | Verified by T1 |
| CTL-03 | Preserve unrelated concurrency | Tasks | Verified by T1 |
| CTL-04 | Default project scope | Tasks | Verified by T1 |
| CTL-05 | Preserve command exit status | Tasks | Verified by T1 |
| CTL-06 | Bound acquisition timeout | Tasks | Verified by T1 |
| CTL-07 | Recover after holder exit | Tasks | Verified by T1 |
| CTL-08 | Validate CLI and execute direct argv | Tasks | Verified by T1 |
| CTL-09 | Install through parallel adoption | Tasks | In Tasks |
| SEC-001 | Prevent shell interpolation | Tasks | Verified by T1 |
| SEC-002 | Reject unsafe resource paths | Tasks | Verified by T1 |
| SEC-003 | Protect the lock directory | Tasks | Verified by T1 |
| SEC-004 | Keep command and environment secrets out of diagnostics | Tasks | Verified by T1 |

**Coverage:** 13 total, 13 mapped to tasks, 0 unmapped.

## Success Criteria

- [ ] The fake heavy-command contract proves same-resource serialization and different-resource concurrency.
- [ ] Both `project` and `machine` scopes behave as specified across disposable Git repositories and worktrees.
- [ ] Parallel adoption installs the dormant wrapper without modifying consumer-owned commands.
- [ ] The full repository gate exits zero.
