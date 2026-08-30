# Configurable Test Lock Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Validates resource names | Safe names and traversal, separator, whitespace, empty, and 65-character inputs | Safe names accepted; every unsafe input rejected before command execution |
| UT-002 | Derives project identity | Two linked worktrees and one unrelated repository | Linked worktrees produce one key; unrelated repository produces another |
| UT-003 | Derives machine identity | Two unrelated repositories with the same resource | Both produce the same machine-scoped key |
| UT-004 | Validates timeout and command | Negative timeout and missing command | Parser exits non-zero before command execution |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Serializes one project resource | Two linked worktrees wrap the same resource | Second command starts after first releases |
| IT-002 | Serializes one machine resource | Two repositories wrap the same machine resource | Second command starts after first releases |
| IT-003 | Preserves unrelated concurrency | Two invocations wrap different resources | Both commands overlap |
| IT-004 | Preserves command result | Wrapped command exits with status 17 | Wrapper exits with status 17 |
| IT-005 | Times out without side effect | Holder owns a resource beyond the waiter's timeout | Waiter exits non-zero and its sentinel command never runs |
| IT-006 | Recovers after abnormal exit | Lock-owning wrapper is killed while its child holds the inherited descriptor, then the child exits | Next waiter remains blocked until child exit, then acquires without cleanup |
| IT-007 | Emits useful bounded diagnostics | Waiter observes an occupied resource | Diagnostic names resource, scope, PID, project identifier, and start time without command/environment payloads |
| IT-008 | Adoption installs only with parallel | Apply `core`, then apply `parallel`, into disposable targets | Core omits the tool; parallel installs and tracks it |

## End-to-end

None. The public interface is a local CLI and subprocess integration discriminates every journey.

## Security

| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | Shell injection through command arguments | Pass `$(...)`, semicolon, wildcard, and dollar arguments to a literal argv recorder | Recorder receives exact literals; no extra process or file appears |
| SEC-002 | Lock-path escape through resource input | Pass `../x`, `/tmp/x`, `a/b`, and whitespace | Wrapper rejects every value before filesystem or command mutation |
| SEC-003 | Shared-temp symlink substitution | Replace the expected private lock directory with a symlink | Wrapper fails closed without touching the referent |
| SEC-004 | Secret leakage in diagnostics | Wait on a command containing a sentinel secret in argv and environment | Diagnostics and metadata omit the sentinel |
