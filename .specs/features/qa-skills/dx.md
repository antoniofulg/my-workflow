# QA Skills Surface Contract

## Skills

### `qa-plan`

- **Trigger:** planning or refreshing durable QA coverage for a user-visible feature.
- **Inputs:** feature contract, diff/current behaviour, `QA-SCENARIOS.md`, operational profile.
- **Output:** journeys, scenarios, resets, and charters under `docs/qa/`.
- **Failure:** missing operational facts are reported and added to the profile before completion.

### `qa-execute`

- **Trigger:** executing planned real-user QA through a consuming product's public interface.
- **Inputs:** current QA plan, operational profile, runnable product.
- **Output:** durable report/status updates plus disposable evidence references.
- **Failure:** unreachable legs are `untested` or `blocked-verify`; product defects return to an
  Implementer.

## Operational profile

`docs/qa/README.md` exposes these fields to agents:

| Field | Contract |
| --- | --- |
| Public interfaces | One or more of browser, API, CLI, mobile, manual |
| Runner/adapter | Existing project authority or manual path |
| Start and health | Manifest/CI/doc reference used to run a production-parity target |
| Authentication | Test identity/session setup |
| Fixtures | Seed or setup source |
| Cleanup | Teardown and residue check |
| Limitations | Unavailable surfaces and external blockers |

## Removals

- The separate README prompts for new and existing projects are replaced by one branched prompt.
- Product-specific names and stacks are removed from the public README.
- Detailed QA planning/execution procedure is removed from `QA-EXECUTION.md` after moving to skills.
- Tracked `.specs/features/` artifacts and the per-commit `tasks.md` requirement are removed.
