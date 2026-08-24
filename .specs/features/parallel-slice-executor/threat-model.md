# Parallel Slice Executor Threat Model

## Scope

Slice A covers the local coordinator, its Git-common runtime receipts, subprocess boundary, and
consumer resource-provider lease protocol. Orca worker command details remain in Slice B.

## Trust boundaries and abuse paths

| Boundary | Abuse path | Required outcome | Control/evidence |
| --- | --- | --- | --- |
| Versioned feature state → local runtime state | Foreign, malformed, or torn JSON is replayed after restart | No adapter effect; named serial recovery | Strict schema/identity validation and atomic replacement; `tools/test_parallel_executor.py` |
| Coordinator → subprocess/provider | Feature, task, path, or provider input contains shell metacharacters | Exact argv only, bounded timeout, no shell expansion | `run_argv`, bounded provider path, SEC-003 tests |
| Coordinator → worktree path | Absolute escape, parent traversal, or unsafe symlink is supplied | Reject before adapter effect | `bounded_path` preflight and SEC-004 regression test |
| Provider → coordinator | Receipt is malformed, foreign, duplicate, unprepared, or contains secret values | Refuse worker dispatch; persist only redacted keys | Correlation/lease validation, serial fallback, redaction tests |
| Lane → cleanup | A lane releases another lane's lease or repeats destructive cleanup | Foreign release rejected; owned retry is idempotent | Ownership check and exact-once release tests |

## Attacker assumptions

- The operator may resume a repository with stale or copied local runtime state.
- A configured provider executable and its stdout are not trusted to identify the current lane
  unless the coordinator correlates every field.
- Paths and task identifiers may be untrusted strings even though the workflow is local.

## Residuals

Slice A does not claim runtime/database isolation beyond the provider receipt contract. Orca receipt
validation and worker transcript redaction are verified in Slice B. No credentials are stored in the
feature artifacts or test fixtures.
