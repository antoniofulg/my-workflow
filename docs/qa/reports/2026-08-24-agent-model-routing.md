# QA report — centralized agent model routing

- **Date:** 2026-08-24
- **Persona:** Workflow adopter
- **Adapter:** Python CLI, Vitest, and disposable adoption targets
- **Entry path:** `.my-workflow.toml` → `workflow_config.py --sync-agents` → feature snapshot → `scripts/adopt.py`
- **Current verdict:** PASS
- **Raw evidence:** [`session.md`](../evidence/2026-08-24-agent-model-routing/session.md)

## Walked journeys

| Scenario | Verdict | Evidence |
| --- | --- | --- |
| `CFG-centralize-agent-model-routing` | pass | 15 packets synchronized; second sync reported zero changes; adoption tests preserved existing config and packet instructions |
| `CFG-freeze-feature-workflow` | pass | v2 snapshot contained four delegated model/effort pairs; synchronized packet drift rejected resume until `--refresh` |

## Commands

- `python3 tools/test_workflow_config.py` — 8 passed, 0 failed during T3; final implementation added no resolver regressions.
- `python3 scripts/test_adopt.py` — passed.
- `npm test` — 8 files, 108 tests, 0 failed.
- `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --sync-agents` — changed/unchanged JSON output; repeated run returned an empty `changed` array.

No browser, API, mobile, authentication, or production-health leg exists for this workflow pack.
