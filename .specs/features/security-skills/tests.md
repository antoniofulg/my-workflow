# External Security Skills Test Contract

## Unit / integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Plan-only boundary | Run installer without `--yes` | Status 2; no target mutation; exact plan printed |
| IT-002 | Authorized installation | Run with three valid staged trees | Three trees, Claude links and external lock entries match pins |
| IT-003 | Consumer preservation | Existing unrelated files and lock entries | Bytes and entries remain unchanged |
| IT-004 | Failure rollback | CLI unavailable, failing or divergent | Non-zero; pre-install state restored; gate unavailable message |
| IT-005 | Concurrent installation | Winner and failing contender share target | Transactions serialize; winner remains installed |
| IT-006 | Stale lock recovery | Dead owner lock exists | Installer safely recovers and completes |
| IT-007 | Target isolation | Caller exports `MY_WORKFLOW_TARGET` | Child process does not receive it |
| IT-008 | Adoption integration | Adopt a fresh target | No security tree copied; exact installer command printed |

## Security

| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | External symlink write | Managed directory or lock points outside target | Reject; referent bytes unchanged |
| SEC-002 | Provenance substitution | Change source type, repository, path, ref or CLI version | Reject before publication |
| SEC-003 | Content substitution | Installed tree hash differs from lock | Reject and restore target |
| SEC-004 | Moving dependency | Use `latest` or a non-40-character ref | Reject lock metadata |
| SEC-005 | Active toolchain boundary | Caller PATH supplies external npx/git candidates while target, staging and pack roots are untrusted | Validate candidate and resolved target outside those roots, execute the original validated shim, and pass only its validated parent directories plus fixed roots; scrub secrets and `MY_WORKFLOW_TARGET`; reject lexical or resolved root escapes |

## Manual QA

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| QAS-001 | Fresh adopter enables security skills | Adopt, inspect output, authorize printed command | Bundled skills remain bundled; three external skills install with exact pins and links |
