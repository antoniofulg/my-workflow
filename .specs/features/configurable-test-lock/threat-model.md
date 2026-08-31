# Configurable Test Lock Threat Model

## Scope

Local CLI execution, temporary lock files, process inheritance, and adoption of the wrapper. The
feature handles no network traffic, credentials, product data, or privileged service.

## Assets

- Integrity of the wrapped command and its arguments.
- Exclusivity of each declared heavy-test resource.
- Integrity of filesystem paths under the private lock root.
- Confidentiality of command arguments and environment values.

## Trust Boundaries

- Consumer-provided CLI input enters the wrapper.
- A user-writable shared temporary parent contains the private lock root.
- Holder metadata crosses between local processes owned by the same user.
- The lock descriptor crosses from wrapper to child process.

## Attacker Assumptions

- An untrusted repository may supply malicious resource names or command arguments.
- Another local process may race to create or replace paths in the temporary parent.
- Processes owned by another OS user must not control the current user's lock files.
- Processes owned by the same OS user are assumed cooperative when using the wrapper; a hostile
  same-UID process can skip the wrapper or rewrite the lock namespace and is outside the guarantee.
- A same-user process can terminate its own wrapper; the surviving child must retain exclusivity.

## Threats and Controls

| Threat | Control | Test |
| --- | --- | --- |
| Shell injection through argv | Execute an argument vector directly with no shell | SEC-001 |
| Path traversal through resource names | Strict bounded identifier validation | SEC-002 |
| Symlink substitution of lock root or file | Stable no-follow directory FD, relative no-follow open, ownership checks, private mode | SEC-003 |
| Secret disclosure through holder reporting | Metadata allowlist excludes argv and environment | SEC-004 |
| Premature release after wrapper death | Child inherits the kernel lock descriptor | IT-006 |
| Indefinite resource denial | Configurable finite timeout, default 2,700 seconds | IT-005 |

## Residual Risk

- A malicious process running as the same OS user can intentionally hold the same resource until
  waiters time out. The finite timeout exposes the denial instead of bypassing exclusivity.
- Consumers can omit the wrapper or choose an overly broad resource name. Adoption remains inert by
  design; project gate configuration owns activation and granularity.
- A hostile same-UID process can unlink or replace a lock name, bypass the wrapper, or otherwise
  coordinate outside `flock`; the kernel lock protects cooperating clients and cannot provide an
  OS-level guarantee against the owner of the lock namespace.
