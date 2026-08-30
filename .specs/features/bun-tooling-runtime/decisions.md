# Bun Tooling Runtime Decisions

## Decisions provided by the human

| Decision | Why | Rejected alternatives | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Bun 1.4.x is the sole JavaScript/TypeScript tooling runtime. | Every consuming project already runs Bun. | Keeping npm/Vitest/tsx as parallel authorities. | Reintroduce a second lock, runner, commands, tests, and documentation. | Bun 1.4.x must be installed. |
| Do not remediate Orca itself. | Orca's team owns the transport fix; this workflow must remain functional meanwhile. | Patching or forking Orca. | Replace the temporary assisted boundary after upstream support lands. | Remote security-skill success and live Orca remain separately constrained. |
| Preserve historical evidence. | Past reports must continue to describe what actually ran. | Rewriting old npm/Vitest evidence to look current. | None; current authority is kept separate from history. | Historical documents retain old commands intentionally. |

## Decisions made during implementation

| Decision | Why | Rejected alternatives | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Use `bun:test`, `bun.lock`, direct Bun TypeScript execution, and `Bun.YAML`. | Native Bun covers the required runtime without extra dependencies. | Compatibility wrappers around Vitest, tsx, or yaml. | Restore dependencies and rewrite the structural contract. | YAML follows Bun's supported semantics. |
| Invoke the locked external CLI as `bunx --bun --no-install skills` after an exact version preflight. | A version-qualified package spec cannot resolve locally with `--no-install`. | Network resolution or a standalone `skills` executable on PATH. | Change the security installer and its fail-closed tests. | The pack-local dependency and lock must be present. |
| Adopt runtime sources but not repository-only TypeScript tests. | Consumers need the tooling, not this repository's validation suite. | Copying all `tools/` content. | Expand the adoption inventory and consumer prerequisites. | Consumer projects do not receive internal tests. |
| Keep active-command enforcement separate from immutable historical records. | Current instructions must be Bun-native without falsifying history. | Repository-wide blind replacement. | Update the explicit authority roots and historical boundary. | New active roots must be added to the scanner deliberately. |
