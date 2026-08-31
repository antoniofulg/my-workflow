# Legacy Adoption Resolution Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Validates the complete replacement set | Current file conflicts plus missing, extra, duplicate, and block-key authorizations | Exact set accepted; every incomplete or invalid set rejected before publication |
| UT-002 | Validates the legacy Git boundary | Clean repository with HEAD, dirty repository, non-repository, and manifest-backed repository | Only the clean no-manifest repository is eligible |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Resolves a reviewed legacy project | Clean committed target with divergent managed files and no manifest; authorize every conflict | Each authorized action is `replace`; manifest is written last; subsequent status is clean |
| IT-002 | Rejects incomplete confirmation atomically | Omit one current file conflict | Exit 1; omitted conflict reported; target snapshot byte-identical |
| IT-003 | Rejects extra confirmation atomically | Name an identical, absent, or unmanaged path | Exit 2; zero target writes |
| IT-004 | Rejects unsafe target state | Dirty, non-Git, missing-HEAD, and manifest-backed targets | Exit 2 for each; zero target writes |
| IT-005 | Preserves project instructions | Resolve with `--skip-agents` and existing AGENTS/CLAUDE prose | Both files remain byte-identical |
| IT-006 | Preserves the publication transaction | Inject a failure before manifest publication | Original clean target restored; manifest absent |
| IT-007 | Keeps normal commands unchanged | Run existing plan/apply/status conflict and idempotence journeys | Existing outputs, codes, and write boundaries remain unchanged |

## End-to-end

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| E2E-001 | Existing project enters managed adoption | Plan parallel; review conflicts; resolve with exact paths and skip agents; status; re-apply parallel | Reviewed files replaced; instructions preserved; status clean; re-apply byte-idempotent |

## Security

| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | Escape through replacement path | Authorize `../x`, absolute path, separator tricks, or a block key | Exit 2 before target or external mutation |
| SEC-002 | Redirect through target symlink | Replaceable leaf, parent, or `.claude` parent becomes a symlink before resolve | Existing no-follow preflight exits 2; target and external referent remain unchanged |
| SEC-003 | Inject through Git, path, or resolver module arguments | Target/replacement names contain shell metacharacters or target contains a resolver module/package shadow | Direct argv treats values literally; synchronization executes only trusted source code; no extra process or file appears |
