# Agent Model Routing Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Parses the complete matrix | Version 2 config with three providers and five roles | Every model and effort is returned unchanged. |
| UT-002 | Rejects invalid config | Missing role, unknown key, empty model, or invalid effort | Exit 2 with the exact TOML path; no packet bytes change. |
| UT-003 | Renders Claude metadata | Claude packet plus changed setting | Only YAML `model` and `effort` values change. |
| UT-004 | Renders Codex metadata | Codex packet plus changed setting | Only TOML `model` and `model_reasoning_effort` values change. |
| UT-005 | Renders Cursor metadata | Cursor packet plus changed setting | Only the embedded model/effort value changes. |
| UT-006 | Rejects malformed packets | Any packet missing or duplicating native metadata | Exit 2 names the packet; no packet bytes change. |
| UT-007 | Synchronizes idempotently | Two syncs with unchanged config | Second result has no changed paths and the tree digest is unchanged. |
| UT-008 | Freezes selected settings | New resolve after successful sync | Every delegated role contains provider, file, model, and effort. |
| UT-009 | Protects resume | Packet metadata differs from frozen snapshot | Resume exits 2 and instructs explicit sync plus refresh. |
| UT-010 | Refreshes settings | Synced config change followed by `--refresh` | Snapshot contains the new model and effort. |
| UT-011 | Keeps planner non-delegated | Complete synchronized matrix | Planner packets update but snapshot roles omit planner. |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Adopts into an empty target | Run adoption once | Target receives version 2 config and fifteen matching packet settings. |
| IT-002 | Re-adopts consumer configuration | Existing config and customized packet instructions | Config and instructions stay byte-identical; model metadata matches config. |
| IT-003 | Stops invalid adoption | Existing malformed packet | Adoption exits non-zero and identifies the packet. |

## End-to-end

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| E2E-001 | Operator changes delegated model | Edit central config, sync, resolve, inspect snapshot, resume | Native packet and snapshot match; resume succeeds without drift. |
| E2E-002 | Operator encounters frozen drift | Resolve, change config, sync, resume, refresh | Resume rejects drift; refresh accepts the deliberate change. |

## Security

No security cases. The feature reads local non-secret model identifiers and writes repository-owned
agent metadata without adding a network, identity, or privilege boundary.
