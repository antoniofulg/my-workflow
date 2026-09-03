# CH-adopt-phase-skills-2026-09-03

- **Date:** 2026-09-03
- **Scope:** `origin/main..e4df550e` on `feat/phase-skills` (merge-base `b5dc370`)
- **Time-box:** 45 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md), continuing into [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Followed-pointer tour — adopt the pack, then walk every path the installed files tell an agent to open
- **Public entry point:** `python3 scripts/adopt.py plan|apply|status <disposable target> --layers core`, then `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents`, then filesystem inspection of the installed skill tree and generated packets
- **Adapter candidate:** CLI/manual against a checkout-local disposable target, as declared in [`docs/qa/README.md`](../README.md). No network, no product runtime, no external security installer.
- **Scenarios:** `ADP-install-phase-skills`; `QAS-resolve-phase-skill-procedures`; `CFG-preload-agent-skills-in-packets`; reconfirm `ADP-adopt-workflow-safely`, `ADP-layered-workflow-adoption`, `CFG-centralize-agent-model-routing`, `CFG-derive-merge-alone-slices`, `QAS-discover-independent-qa-skills`, `DOC-read-explicit-workflow-provenance`, `REL-report-current-workflow-release`
- **Adjacent canary:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md) via `DOC-read-explicit-workflow-provenance`, `REL-report-current-workflow-release`
- **Known blocker at planning time:** [`BUG-20260903-history-gate-forbids-resetting-baseline-scenarios`](../bugs/BUG-20260903-history-gate-forbids-resetting-baseline-scenarios.md) — the documented full gate rejects this plan's scenario resets. Confirm it is fixed and the opening gate is green before walking, and record the opening-gate output as the first evidence artifact.

## Mission

The feature moved five phase procedures out of the router into skills of their own and made agents
preload them by name. Both halves fail quietly. A moved procedure leaves a path that still reads
like an instruction but resolves to nothing; a preloaded name that resolves to nothing produces an
agent with no procedure and no error. Walk the installed tree the way an agent reads it — follow
each pointer to a real file — and prove the sync refuses the hollow case instead of writing it.

## Expected observable

A core-layer adoption of an empty disposable target reports the five phase skill directories as
managed and leaves each `.agents/skills/w<phase>/SKILL.md` present, with `.claude/skills/w<phase>`
resolving to it. Every template, reference, and validator path named inside those five files and
inside the router opens. `--sync-agents` writes packets whose `skills:` and `disallowedTools:` lines
match their templates byte for byte, and a template naming an unresolvable skill stops the sync with
that template and skill in the message and no destination byte changed.

## Planned probes

- `plan --layers core --json` against an empty disposable target: require `.agents/skills/wspecify`,
  `wdesign`, `wtasks`, `wimplement`, `wverify` among the managed paths, and require the target to be
  byte-unchanged after the read-only plan.
- `apply --layers core`, then `status`: require clean managed status and, for each phase, that both
  `.agents/skills/w<phase>/SKILL.md` and the `.claude/skills/w<phase>` link open the same file.
- Re-adopt the applied target after adding a consumer-owned `.agents/skills/<consumer-skill>/` and
  an edited template body: require both to survive byte-for-byte and the diff to stay reviewable.
- Extract every relative `references/` path and every
  `.agents/skills/workflow-spec-driven/scripts/*.py` citation from the five phase SKILL.md files and
  the router, and resolve each in the adopted target. Require zero unresolved paths. Require the
  router to link no `references/{specify,design,tasks,implement,validate}.md`, and require
  `discuss.md` to sit under `wspecify/references/`.
- Read each phase skill's frontmatter: `name` equals its directory, no `disable-model-invocation`
  key, and the `description` names the preloading agent and the `/w<phase>` entry.
- `--sync-agents` on the adopted target: diff each generated `.claude/agents/<role>.md` against its
  template and require the only differing lines to be `model` and `effort`, with `skills:` and
  `disallowedTools:` carried through for planner, implementer, explorer, deep-reviewer, and verifier.
- Negative case, on a disposable copy only: add a `skills:` entry naming a skill with no
  `SKILL.md` — once inline, once in block list form — and require a non-zero exit naming the template
  and the skill, with every destination file's bytes and mtimes unchanged.
- Read the Cursor and Codex planner, implementer, and verifier packets: require their `## Load` and
  `## Do not load` lines to name only skills or guideline paths that exist, and to name no
  `implement.md` or `validate.md`.
- Reconfirm the reset promises against the new tree: layered `core` reporting
  (`ADP-layered-workflow-adoption`), model/effort rendering (`CFG-centralize-agent-model-routing`),
  the task template at its new `wtasks/references/tasks-template.md` path
  (`CFG-derive-merge-alone-slices`), and Verifier routing to `qa-plan`/`qa-execute` across all three
  providers (`QAS-discover-independent-qa-skills`).
- Adjacent canary: read `docs/workflow/pack.md`, `README.md`, and `docs/workflow/roadmap.md` and
  require the shipped capability list to match the installed skill tree with provenance intact
  (`DOC-read-explicit-workflow-provenance`).
- Remove only the checkout-owned disposable target and record source-checkout residue. Do not run
  `scripts/install_security_skills.py`, contact a network, or edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke the
canonical `qa-execute` skill, and use its declared CLI/manual adapter at HEAD `e4df550e`. Store raw
evidence under `docs/qa/evidence/2026-09-03-phase-skills/`, write the durable report to
`docs/qa/reports/2026-09-03-phase-skills.md`, and set each scenario's `qa_status`, `evidence`, and
`last_report` from that walk. Hand any product defect to an Implementer and require a fresh Verifier
after the fix; do not fix product code in the execute session.
