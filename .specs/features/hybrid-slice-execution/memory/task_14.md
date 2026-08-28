# T14 task memory

- `MutationRunner.issue` is the single assisted dispatch/cleanup issue boundary. It writes an
  atomic `in_flight` record with attempt 1 before invoking a sink and restores the in-memory state
  when that pre-sink write fails.
- Git cleanup effects carry their owned worktree path; repository-root Git commands are reserved for
  declared effects. Pointer transport remains one-shot and sends only the persisted packet pointer.
- Existing `in_flight` and `unknown` records use the supplied bounded observer and never call a
  physical sink. State persistence and physical ledgers are independent test boundaries.
- Generation-2 remediation adds an AST reachable-lifecycle guard that classifies explicit mutating
  Git verbs and a PATH-backed cleanup ledger; the first post-effect `stop` failure is reconciled
  from persisted `unknown` state without reissuing the stop.
- T14 focused contract is 19/19 after remediation. Generation 2 remains open under the authorized
  CP-S4 fingerprint; a fresh Technical Verifier must close it only after independent PASS.
