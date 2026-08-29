# T6 task memory

- Dispatch state persists repository, slice, task, operation, handle, route, commit, lease,
  packet, and log identities before the send mutation.
- A persisted `send_started`/`pointer_sent`/`settled` operation is never sent again; changed
  identity is rejected before packet or provider effects. `inspect` uses only bounded same-handle
  reads and records no raw provider payload.
- Focused probe contract: 8/8. Full offline gate is required before the T6 commit.
