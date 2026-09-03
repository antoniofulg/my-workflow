# CH-w-entry-points-2026-09-03

- **Date:** 2026-09-03
- **Scope:** `origin/main..bb3d3656` on `feat/w-entry-points` (merge-base `c3a72f70`)
- **Time-box:** 40 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Seven-entry inspect — adopt core, then read the seven `/w` files the way the menu and a forked agent read them
- **Public entry point:** `python3 scripts/adopt.py plan|apply|status <disposable target> --layers core`, then filesystem inspection of the seven `w*` skills, their `.claude/skills/` links, `docs/workflow/pack.md`, and `docs/workflow/roadmap.md`
- **Adapter candidate:** CLI/manual against a checkout-local disposable target, as declared in [`docs/qa/README.md`](../README.md). No network, no product runtime, no external security installer.
- **Scenarios:** `ADP-install-review-and-qa-entries`; `QAS-fork-w-skills`; `QAS-list-seven-w-entries`; reconfirm `ADP-install-phase-skills`, `QAS-resolve-phase-skill-procedures`; adjacent canary `DOC-read-explicit-workflow-provenance`
- **Adjacent canary:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md) via `DOC-read-explicit-workflow-provenance`
- **Known blocker at planning time:** none. History-gate reset is fixed (`BUG-20260903-history-gate-forbids-resetting-baseline-scenarios`). Out of scope: [`BUG-20260903-cursor-route-bracket-effort-rejected`](../bugs/BUG-20260903-cursor-route-bracket-effort-rejected.md) — do not walk the Orca Cursor route.

## Mission

The feature added fork keys to the five phase skills and two `/w` entries for review and QA.
Adoption now ships seven names. Walk the installed tree the way a human reads `/w` and the way an
agent follows the first body line — confirm the menu, the keys, and the two new core paths, and
reconfirm the five phase procedures still resolve.

## Expected observable

A core-layer adoption of an empty disposable target reports `.agents/skills/wreview`,
`.agents/skills/wqa`, `.claude/skills/wreview`, and `.claude/skills/wqa` as managed and leaves each
entry `SKILL.md` present with a `.claude/skills/` link that opens the same file. The original five
phase directories still install. All seven `w*` files carry `context: fork`, `background: false`,
the spec's `agent:`, and an `argument-hint`. Each `description` starts with the phase name and
contains `Argument:`. `pack.md` lists those seven rows among thirteen local capabilities; roadmap
slice 2 is `(done)`.

## Planned probes

- `plan --layers core --json` against an empty disposable target: require
  `.agents/skills/wreview/SKILL.md`, `.agents/skills/wqa/SKILL.md`, `.claude/skills/wreview`, and
  `.claude/skills/wqa` among the managed paths, and require the target to be byte-unchanged after
  the read-only plan.
- `apply --layers core`, then `status`: require the five phase skills and the two entry skills to
  be present, each `.claude/skills/w*` link resolving to the same file as `.agents/skills/w*/SKILL.md`.
- Read all seven frontmatters: `context: fork`, `background: false`, `argument-hint` present,
  `agent:` planner / planner / planner / implementer / verifier / planner / verifier, no
  `disable-model-invocation: true`, `description` starts with the phase name and contains
  `Argument:`. `wreview` and `wqa` stay under 40 lines.
- First body line: five phase skills and `wqa` bind `$ARGUMENTS` and stop on slash-empty;
  `wreview` names `.agents/skills/deep-review/SKILL.md` and refuses `--publish`; `wqa` runs
  exactly one QA phase and stops when no journey carries the flow tag.
- Claude implementer template still lists `skills: [wimplement, ponytail]` and
  `disallowedTools: Skill`.
- Reconfirm the five phase skills: `name` equals directory; every relative `references/` path and
  router-cited validator still opens in the adopted target.
- Adjacent canary: `docs/workflow/pack.md` capability count matches its table and includes the
  seven `w*` rows; `docs/workflow/roadmap.md` slice 2 ends `(done)`; provenance statements on
  README and the QA skills are intact.
- Remove only the checkout-owned disposable target and record source-checkout residue. Do not run
  `scripts/install_security_skills.py`, contact a network, or edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke the
canonical `qa-execute` skill, and use its declared CLI/manual adapter at HEAD `bb3d3656`. Store raw
evidence under `docs/qa/evidence/2026-09-03-w-entry-points/`, write the durable report to
`docs/qa/reports/2026-09-03-w-entry-points.md`, and set each scenario's `qa_status`, `evidence`,
and `last_report` from that walk. The live dual-`/wspecify` host return is a limitation: leave that
leg `untested` if no slash session is available. Hand any product defect to an Implementer and
require a fresh Verifier after the fix; do not fix product code in the execute session.
