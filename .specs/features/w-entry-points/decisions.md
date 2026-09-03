# W Entry Points — decisions made while unattended

Human-handed decisions: delegated roles run on Cursor agents (implementer, verifier, explorer);
`/w` prefix names; merge by default once ready.

| Decision | Chosen | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- | --- |
| Spec approval | Approved as drafted under `$autonomous` | Human invoked autonomous at the approval question | Wait for a reply | none | none |
| Gap hunt | Skipped | Medium size; surface is seven skill files; the one risk (fork vs preload) is isolated to a probe | Two-subagent hunt plus a question round | none | none |
| Fork placement | On the phase skill itself | One name per phase in the menu; fewest files | Rename to hidden knowledge skills plus thin entries (kept as fallback) | one rename batch | none |
| `wreview` agent | `planner` | Needs the Agent tool to dispatch `deep-reviewer` jobs; deep-reviewer has read-only tools | A new orchestrator agent type | small | none |
| `wqa` shape | `wqa [plan] <flow>`, one QA phase per run | QA-EXECUTION requires one phase per fresh session | One command running both phases | small | one extra command for plan |
| Cursor model id | `<toml model>-<toml effort>` | `cursor-agent` rejects `[effort=]` and lists effort inside ids | Edit the toml ids | none | none |
| Orca route bug | Filed, not fixed | Out of scope; transport is `blocked-verify` | Fix `route_command` now | small | none for Claude routes |
| Dispatch transport for Cursor | Headless `cursor-agent --print --trust --workspace .` with a packet pointer | Works today (probe returned `OK`); repo's Orca route unverified | Orca assisted route | none | none |
| Model ids (human-handed, mid-run) | implementer `gemini-3.8-flash-high`; verifier and deep reviewer `cursor-grok-4.6-xhigh-fast`; all on Cursor | Human instruction | Keep the toml defaults | none | none |
| Cursor id composition | The local toml holds the exact `cursor-agent` model id; dispatch passes it verbatim and ignores the rendered `[effort=]` suffix | The CLI rejects the bracket form and encodes effort in the id | Compose `<model>-<effort>` at dispatch | none | none |
