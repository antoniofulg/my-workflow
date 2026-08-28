# T14 task memory

- `MutationRunner.issue` is the single assisted dispatch/cleanup issue boundary. It writes an
  atomic `in_flight` record with attempt 1 before invoking a sink and restores the in-memory state
  when that pre-sink write fails.
- Git cleanup effects carry their owned worktree path; repository-root Git commands are reserved for
  declared effects. Pointer transport remains one-shot and sends only the persisted packet pointer.
- Existing `in_flight` and `unknown` records use the supplied bounded observer and never call a
  physical sink. State persistence and physical ledgers are independent test boundaries.
- T14 focused contract is 18/18. Generation 2 remains open under the authorized CP-S4 fingerprint;
  a fresh Technical Verifier must close it only after independent PASS.
