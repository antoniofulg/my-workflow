# Host-Owned Session Continuation Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| CT-001 | Reject active references outside the allowlist | Scan every tracked repository file after removal | Zero non-allowlisted matches for all named forms and related commands/runtime wording |
| CT-002 | Preserve independent reviewer packets | Inspect current reviewer contract after wording removal | Fresh Verifier and Deep Reviewer packets; no Implementer transcript or operator handoff; conclusions use spec, diff, tests, and assigned evidence |
| CT-003 | Keep release authorities aligned | Read package, lockfile, current release scenario, and version assertions | Every current version equals `0.6.0` |
| CT-004 | Protect immutable history | Compare explicit historical files with `v0.5.0` | Zero byte differences |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| ADP-001 | Clean adoption installs no removed subsystem | Adopt into a disposable clean fixture | No config, database, marker, source line, hook, payload, script, guide, scenario, or feature test |
| ADP-002 | Re-adoption stays idempotent and host-neutral | Adopt twice with shell and hook sentinels outside managed output | Managed output is stable; sentinels and host settings are unchanged |
| REL-001 | Package excludes removed artifacts | Run `npm pack --dry-run --json` | Zero packaged paths belonging to the removed subsystem |

## End-to-end

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| QA-001 | Review v0.6.0 removal as an operator | Walk current docs, disposable adoption, package manifest, parity, and reference scan through declared CLI/manual adapters | New charter and report record PASS with exact commands and counted outputs |

## Security

No security case. The feature removes the external runtime surface and must not execute cleanup, edit shell startup files, modify Git hooks, access credentials, or mutate operator settings.
