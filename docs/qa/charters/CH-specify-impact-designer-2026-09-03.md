# CH-specify-impact-designer-2026-09-03

- **Date:** 2026-09-03
- **Scope:** `origin/main..0efc5d06` on `feat/specify-impact-designer` (merge-base `e1b61981`)
- **Time-box:** 45 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md), continuing into [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Followed-pointer plus CLI — adopt core, walk the new Specify/Design/Verify steps, run the size-aware validator on copied fixtures, sync designer, refuse a missing designer table
- **Public entry point:** `python3 scripts/adopt.py plan|apply|status <disposable target> --layers core`, then filesystem inspection of the installed skills and designer templates, then the adopted `validate_spec.py` against copies of the five size fixtures, then `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents`
- **Adapter candidate:** CLI/manual against a checkout-local disposable target, as declared in [`docs/qa/README.md`](../README.md). No network, no product runtime, no external security installer.
- **Scenarios:** `QAS-write-specify-impact-and-uiux`; `QAS-offer-gap-hunt-at-plan-approval`; `ADP-require-impact-on-large-specs`; reconfirm `QAS-resolve-phase-skill-procedures`, `CFG-centralize-agent-model-routing`, `CFG-preload-agent-skills-in-packets`, `ADP-adopt-workflow-safely`; adjacent canary `DOC-read-explicit-workflow-provenance`
- **Adjacent canary:** [`J-review-workflow-release`](../journeys/J-review-workflow-release.md) via `DOC-read-explicit-workflow-provenance` — read `AGENTS.md` for designer and `docs/workflow/pack.md` for five windows; do not reset provenance
- **Known blocker at planning time:** none. History-gate reset is fixed (`BUG-20260903-history-gate-forbids-resetting-baseline-scenarios`). Out of scope: [`BUG-20260903-cursor-route-bracket-effort-rejected`](../bugs/BUG-20260903-cursor-route-bracket-effort-rejected.md) — do not walk the Orca Cursor route.

## Mission

Specify now names blast radius and screens before stories freeze, offers a sized gap hunt at plan
approval, and ships a sixth matrix role for mockups. Both halves fail quietly. A Large spec without
Impact looks complete until the validator is the only check; a missing designer table leaves every
other role generating while the UI-bearing path has no packet. Walk the installed tree the way an
agent reads it, then prove the CLI refuses the hollow Large spec and the hollow designer table.

## Expected observable

A core-layer adoption of an empty disposable target installs `wspecify` with Impact, uiux.md, and
gap-hunt steps, `references/gap-hunt.md`, a spec template whose `## Impact` sits between Assumptions
and User Stories, `wdesign` that loads `uiux.md` and dispatches designer, and `wverify` that reruns
Impact scenario ids. The adopted `validate_spec.py` exits 1 naming `## Impact` for Large and Complex
fixtures that lack the section, and exits 0 for Medium, Small, and Large-with-`none`. `--sync-agents`
writes designer packets for all three providers; Claude designer carries `skills: [wdesign, ponytail]`
and no `disallowedTools`. A toml missing `[models.<provider>.designer]` stops the sync naming that
table and changes no destination byte. `AGENTS.md` names designer and has at most 134 lines;
`pack.md` names five windows.

## Planned probes

- `plan --layers core --json` against an empty disposable target: require
  `templates/agents/claude/designer.md`, `templates/agents/codex/designer.toml`, and
  `templates/agents/cursor/designer.md` among the managed paths, and require the target to be
  byte-unchanged after the read-only plan.
- `apply --layers core`, then `status`: require those three designer templates present, the five
  phase skills still installed, and `.agents/skills/wspecify/references/gap-hunt.md` open.
- Read installed `wspecify/SKILL.md`: Impact step after the dimensions sweep and before user
  stories; two explorers; ubiquitous AC per affected feature; uiux.md step after acceptance
  criteria and before the closure gate; gap-hunt step at plan approval citing `gap-hunt.md`
  (skip Small, ask Medium and Large, recommend Complex, autonomous only Complex with skip in
  `decisions.md`).
- Read installed `spec-template.md`: `## Impact` between Assumptions and User Stories.
- Read installed `docs/guidelines/UI-UX.md`: `uiux.md` is written in Specify.
- Read installed `wdesign/SKILL.md` step 1: load `uiux.md` when present and dispatch `designer`
  before internal design; planner keeps the architecture half of `design.md`.
- Read installed `wverify/SKILL.md`: rerun QA scenario ids named in `## Impact` as pass, fail, or
  untested; report no reruns when Impact is `none`.
- Read installed `gap-hunt.md`: two explorers, numbered frontier questions each with a recommended
  answer, settled findings become an acceptance criterion or a `context.md` decision, one-line
  proceed if nothing is found.
- Copy the five `tools/fixtures/tlc-validator/spec-size-*.md` files into the disposable target and
  run the adopted `validate_spec.py` on each copy. Require exit 1 and `missing required section:
  ## Impact` for Large-no-impact and Complex-no-impact; exit 0 for Medium-no-impact, Small-no-impact,
  and Large-impact-none.
- `--sync-agents` on the adopted target: require generated
  `.claude/agents/designer.md`, `.codex/agents/designer.toml`, and `.cursor/agents/designer.md`.
  Claude designer `skills:` and absent `disallowedTools` match the template; only `model` and
  `effort` differ. Example tables: Claude `inherit`/`high`, Codex `gpt-5.6-sol`/`high`, Cursor
  `claude-fable-5-1-thinking-high`/`high`.
- Designer template bodies: load `uiux.md`, `spec.md`, `UI-UX.md`, `FRONTEND.md`; write mockups
  under `docs/design/` and `uiux-review.md`; never write product code.
- Negative case, on a disposable copy only: remove one `[models.<provider>.designer]` table and
  require a non-zero exit naming that table, with every destination file's bytes and mtimes
  unchanged. On a second copy, remove one designer template and require a non-zero exit naming the
  template path, destinations unchanged.
- Re-adopt after adding a consumer-owned `.my-workflow.toml` sentinel: require the sentinel to
  survive byte-for-byte (`ADP-adopt-workflow-safely`).
- Adjacent canary: `AGENTS.md` names designer and `wc -l` is ≤134; `docs/workflow/pack.md` names
  five windows; provenance statements on README and the QA skills stay intact
  (`DOC-read-explicit-workflow-provenance`).
- Remove only the checkout-owned disposable target and record source-checkout residue. Do not run
  `scripts/install_security_skills.py`, contact a network, or edit product code.

## QA Execute handoff

Start a fresh Verifier session with `phase: qa-execute`. Read `docs/qa/README.md`, invoke the
canonical `qa-execute` skill, and use its declared CLI/manual adapter at HEAD `0efc5d06`. Store raw
evidence under `docs/qa/evidence/2026-09-03-specify-impact-designer/`, write the durable report to
`docs/qa/reports/2026-09-03-specify-impact-designer.md`, and set each scenario's `qa_status`,
`evidence`, and `last_report` from that walk. Hand any product defect to an Implementer and
require a fresh Verifier after the fix; do not fix product code in the execute session.
