# CH-serialize-heavy-test-resources-2026-08-31

- **Date:** 2026-08-31
- **Scope:** `origin/main..8a7730b` on `feat/configurable-test-lock`
- **Time-box:** 35 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-execute-parallel-slices`](../journeys/J-execute-parallel-slices.md)
- **Tour:** Adoption, contention boundary, failure, privacy, and recovery tour
- **Public entry point:** `scripts/adopt.py plan|apply|status` -> `python3 tools/resource_lock.py run`
- **Adapter candidate:** CLI/manual with checkout-local disposable targets and Git repositories, as declared in [`docs/qa/README.md`](../README.md)
- **Scenario:** `QAS-serialize-heavy-test-resources`
- **Adjacent canary:** `CFG-plan-parallel-slice-dispatch`

## Mission

Experience the installed wrapper as an operator would: opt in only a declared heavy command, choose
project or machine contention, and observe that unsafe or expired requests never start the command.
Keep the existing resource-free planning path as the adjacent canary.

## Expected observable

Parallel adoption installs and tracks an otherwise inert wrapper. Same-resource commands start one
at a time at default project or explicit machine scope, different resources overlap, wrapped status
is preserved, refusal starts no command, diagnostics expose no command or environment secrets, and
the resource becomes available after its holder exits.

## Planned probes

- Plan and apply `core` and `parallel` into separate checkout-owned targets. Require core omission,
  parallel installation plus manifest ownership, no consumer-command rewrite, and clean `status`.
- In linked worktrees, omit `--scope` and use timestamped sentinels to require the second command to
  start only after the first ends.
- In unrelated disposable repositories, repeat with `--scope machine`; then use different resource
  names and require observable overlap.
- Return a distinctive child status and require the wrapper to preserve it. Occupy one resource,
  use a short timeout, and require status `75` with no child sentinel.
- Try invalid scope, resource, timeout, missing literal `--`, missing command, and project scope
  outside Git. Require nonzero refusal before any child or lock-path side effect.
- Pass shell metacharacters as literal arguments and use command/environment secrets while waiting.
  Require exact argv, one immediate bounded JSON diagnostic, required holder fields, and no secret.
- Terminate a holder and an independent waiting process in disposable fixtures. Require later
  acquisition without deleting a lock file and require the waiter not to disturb the holder.
- Adjacent canary: resolve a resource-free or disabled plan through
  `CFG-plan-parallel-slice-dispatch`; require its prior serial/zero-effect promise unchanged.
- Remove only checkout-owned targets and record source-checkout residue. Do not run live Orca,
  contact a network service, or mutate a real consumer repository.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke canonical
`qa-execute`, and use its CLI/manual adapter at HEAD `8a7730b`. Keep all fixtures under a disposable
directory owned by the active checkout. Walk the documented public commands only:

```bash
python3 scripts/adopt.py plan <core-target> --layers core --json
python3 scripts/adopt.py apply <core-target> --layers core
python3 scripts/adopt.py plan <parallel-target> --layers parallel --json
python3 scripts/adopt.py apply <parallel-target> --layers parallel
python3 tools/resource_lock.py run --resource browser -- <command> [argument ...]
python3 tools/resource_lock.py run --resource browser --scope machine -- <command> [argument ...]
```

Store raw evidence under `docs/qa/evidence/2026-08-31-configurable-test-lock/`, write a new report at
`docs/qa/reports/2026-08-31-configurable-test-lock.md`, then update scenario verdict fields only from
observed public-interface evidence. Do not probe the internal directory-replacement race; final
technical validation owns that security control. End before any product remediation.
