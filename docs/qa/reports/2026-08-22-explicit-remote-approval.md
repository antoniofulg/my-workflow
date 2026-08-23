# QA report — explicit remote approval — 2026-08-22

## Session

- **Adapter:** Manual documentation inspection plus Vitest structural contract
- **Entry points:** `README.md`; `docs/workflow/pack.md`; `.agents/skills/autonomous/SKILL.md`
- **Scenario:** `DOC-read-explicit-workflow-provenance`
- **Scope:** Filed issue #25 — readiness evidence must not grant remote authority

## Walk

| Probe | Expected | Observed |
| --- | --- | --- |
| Canonical boundary | Every public workflow source says readiness is evidence, not authorization | Present in `AGENTS.md`, `README.md`, `docs/workflow/loop.md`, `docs/workflow/pack.md`, and `.agents/skills/autonomous/SKILL.md` |
| Action separation | Push, pull request, and merge require explicit authorization for that action | Present across all five sources |
| Autonomous behavior | Readiness without exact authorization stops and reports the next action | Present; implicit `gh pr merge` instruction removed |
| Regression contract | Cross-file assertions reject implicit merge authority | `remote-approval.test.ts` passed |

## Verdict

**pass.** The documentation and autonomous skill now stop at proven readiness when the current
session does not explicitly authorize the next remote action. A prior local approval or readiness
signal cannot authorize push, pull request creation, or merge.

## Evidence

- `npm test -- --run tools/shared/tests/remote-approval.test.ts` — pass
- `git diff --check` — pass
