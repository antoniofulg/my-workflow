# QA Skills Decisions

## Decisions supplied by the human

| Choice | Why | Rejected alternatives | Cost to change later | Cost to the user today |
| --- | --- | --- | --- | --- |
| Reuse the existing Verifier | Keep one independent review role per provider | Add a QA reviewer agent | Update three provider packets and workflow docs | None; QA gets separate sessions |
| Make both QA skills Antonio's work with explicit Pedro Nauck credit | The workflow adaptation is original while its inspiration must remain visible | TLC ownership; silent fork | Rename metadata and public provenance | Attribution occupies a few lines |
| Let consuming projects choose Playwright, Cypress, or another adapter | Preserve stack independence | Mandate one browser framework | Change profile and skill adapter contract | Setup must discover capabilities |
| Ignore feature specs | Keep transient planning state out of repository history | Track on branches and delete before PR | Reverse ignore/rules and restore commit coupling | Fresh clones cannot resume local plans |
| Credit TLC and remove personal-project leakage from README | Make the public origin and scope accurate | Leave package URLs as implicit credit | README-only change | None |
| Version the delivery as `0.3.0` | Two public skills and a new adoption contract are a compatible feature increment | Patch release `0.2.3`; breaking `1.0.0` | Update package and lock versions | Consumers see a minor upgrade |

## Decisions made by the run

| Choice | Why | Rejected alternatives | Cost to change later | Cost to the user today |
| --- | --- | --- | --- | --- |
| Name the skills `qa-plan` and `qa-execute` | Match their workflow responsibilities and distinguish them from Pedro's originals | Reuse `qa-report`/`qa-execution` | Rename paths, pointers and tests | Two new names to learn |
| Use `docs/qa/README.md` as the stack profile | Stable location beside durable QA artifacts | Embed commands in skills; new root config | Move one pointer and template | One short project-owned document |
| Consolidate setup prompts into one branched prompt | Removes duplicated discovery and closeout instructions | Maintain two near-copies | Split README text again | Reader chooses a branch inside one prompt |
| Keep command strings in manifests/CI | Avoid stale documentation caches | Copy commands into QA profile | Relax profile contract | Agents must follow references |

## Durable decisions

- `AD-002`: independent QA skills use the existing Verifier and the consuming project's adapter.
- `AD-003`: feature planning trees are ignored local state.

## Halt report

**Status:** halted after Deep Review round 2. No push, pull request, or merge was performed.

T1 passed its Verifier and first remediation gate, but the second and final Deep Review round left
four blocking findings:

1. `.agents/skills/tlc-spec-driven/SKILL.md` still runs `validate_tasks.py` unconditionally before
   Execute even when Tasks was skipped.
2. Provider Implementer packets still require reading `tasks.md` rather than accepting the inline
   execution-plan/task payload when Tasks was skipped.
3. `AGENTS.md` resume still assumes local `tasks.md`; a skipped-Tasks session needs a Handoff + Git
   resume path that does not invent a missing file.
4. `scripts/adopt.py` appends child ignore rules but cannot re-include durable exceptions when the
   consuming project already ignores `.deep-review/` or `.specs/` at the parent directory.

Recommended next action: authorize one post-cap remediation batch for these four findings, followed
by a targeted closing review. Without that authorization, the feature remains local at commits
`1484c3b` and `9e75264`.
