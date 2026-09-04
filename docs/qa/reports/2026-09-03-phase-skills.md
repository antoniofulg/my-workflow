# QA Execute — phase-skills — 2026-09-03

- **Charter:** [`CH-adopt-phase-skills-2026-09-03`](../charters/CH-adopt-phase-skills-2026-09-03.md)
- **Branch / HEAD:** `feat/phase-skills` @ `ef18f54c`. The charter froze code scope at `e4df550e`;
  `50ca157b` is the fix for the charter's known blocker and `ef18f54c` is the QA plan itself, so no
  product code moved after the frozen scope.
- **Persona:** Workflow adopter (adjacent canary as Repository reader)
- **Adapter:** CLI/manual against checkout-owned disposable targets, as declared in
  [`docs/qa/README.md`](../README.md). No browser, API, or mobile surface exists.
- **Exact path:** `python3 scripts/adopt.py plan|apply|status <target> --layers core|quality`, then
  `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents`,
  then filesystem inspection; `bun pm pack --dry-run` from the active checkout for `REL`.
- **Targets:** `/Users/antoniofulg/Projects/.qa-phase-skills-2026-09-03` plus two throwaway copies
  `.qa-phase-skills-neg-inline` and `.qa-phase-skills-neg-block` for the refusal cases. All removed.
- **Environment:** no network, no product runtime. `scripts/install_security_skills.py` not run, no
  remote fetched, no product code edited.
- **Opening gate:** `bun run test:all` → exit `0`, load average `15.92` at start.
  Evidence `../evidence/2026-09-03-phase-skills/01-opening-gate.log`. No load flake; the
  `tools/test_parallel_resource_lock.py` known flake did not occur.
- **Closing gate:** `bun run test:all` → exit `0` (see below).
- **Evidence root:** `docs/qa/evidence/2026-09-03-phase-skills/` (disposable, gitignored).

## Scenario matrix

| Scenario | Verdict | Evidence |
| --- | --- | --- |
| `ADP-install-phase-skills` | pass | `11-plan-core.json`; `12-target-after-plan.txt`; `13-apply-core.log`; `14-status.log`; `15-phase-skill-links.txt`; `18-consumer-after.txt` |
| `QAS-resolve-phase-skill-procedures` | pass | `20-pointer-resolution.txt`; `22-pointer-resolution-charter.txt`; `23-phase-frontmatter.txt` |
| `CFG-preload-agent-skills-in-packets` | pass | `31-claude-packet-diff.txt`; `34-perturbed-diff.txt`; `35-skills-lines.txt`; `41-neg-inline.log`; `41-neg-block.log`; `42-neg-inline-after.txt`; `42-neg-block-after.txt` |
| `ADP-adopt-workflow-safely` | pass | `13-apply-core.log`; `17-readopt.log`; `18-consumer-after.txt`; `53-status-quality.log` |
| `ADP-layered-workflow-adoption` | pass | `11-plan-core.json`; `52-apply-quality.log`; `53-status-quality.log`; `54-qa-layer-check.txt` |
| `CFG-centralize-agent-model-routing` | pass | `30-sync-agents.log`; `33-sync-perturbed.log`; `34-perturbed-diff.txt`; `35-skills-lines.txt` |
| `CFG-derive-merge-alone-slices` | pass | `60-merge-alone-contract.txt`; `63-resolver-derive.txt`; `64-slices-assertion.txt`; `65-merge-alone-authoring.txt` |
| `QAS-discover-independent-qa-skills` | pass | `51-qa-routing.txt`; `54-qa-layer-check.txt` |
| `DOC-read-explicit-workflow-provenance` | pass | `70-doc-provenance.txt` |
| `REL-report-current-workflow-release` | pass | `71-rel-readback.txt`; `72-pack-dry-run.txt`; `80-history-gate-retest.txt` |

No row is `fail`, `untested`, or `blocked-verify`. No defect was found.

## Walk

### ADP-install-phase-skills

`plan --layers core --json` against an empty target exited `0` with `status: ready`, `conflicts: []`,
and 115 actions. All five phase directories appear as managed `add` actions with their references:
`wspecify` (3 paths, including `references/discuss.md`), `wdesign`, `wtasks`, `wimplement`, and
`wverify` (2 paths each). The target's file listing was byte-identical before and after the plan, so
the read-only promise holds.

`apply --layers core` and `status` both exited `0`; status reported 71 `clean`, 17 `retained`, one
`resolved`, and nothing modified or missing. For each phase, `.agents/skills/w<phase>/SKILL.md` and
`.claude/skills/w<phase>/SKILL.md` resolve to the **same inode**, with `.claude/skills/w<phase>` a
symlink to `../../.agents/skills/w<phase>`. Both read paths open one file, which is the observable
this scenario owns.

Re-adoption over a target carrying a consumer-owned `.agents/skills/consumer-thing/SKILL.md` and an
edited `templates/agents/claude/planner.md` exited `0` and left both byte-identical (SHA-256 compared
before and after). The consumer marker survived a second `apply` and the later `quality` apply.

### QAS-resolve-phase-skill-procedures

Every relative `references/*.md` path and every
`.agents/skills/workflow-spec-driven/scripts/*.py` citation inside the five phase `SKILL.md` files,
their reference files, and the router was extracted and resolved in the adopted target: **17
citations, 0 unresolved**. A separate markdown-link sweep across the same twelve files resolved 16
link targets with 0 unresolved.

The router links none of `references/{specify,design,tasks,implement,validate}.md`, and none of those
files exist. `discuss.md` sits at `wspecify/references/discuss.md` and no longer under the router,
whose `references/` now holds exactly `code-analysis.md`, `coding-principles.md`, `lessons.md`,
`memory.md`, `sub-agents.md`. The router names all five phase skills.

Frontmatter: each phase skill's `name` equals its directory, the only keys are `name` and
`description`, no `disable-model-invocation` key is present (known intent), and every `description`
names both its `/w<phase>` entry and its preloading agent — planner for `wspecify`/`wdesign`/`wtasks`,
implementer for `wimplement`, verifier for `wverify`.

### CFG-preload-agent-skills-in-packets and CFG-centralize-agent-model-routing

`--sync-agents` exited `0` and reported all fifteen provider packets unchanged after adoption had
already generated them. A template-versus-packet diff for the five Claude roles showed no differing
lines, which alone does not discriminate, because the tracked templates carry the same defaults as
`.my-workflow.toml`. So `.my-workflow.toml` was perturbed — planner to `haiku`/`low`, verifier to
`sonnet`/`low` — and the sync re-run. It reported exactly `.claude/agents/planner.md` and
`.claude/agents/verifier.md` as changed, and the diff against each template was exactly two lines,
`model` and `effort`. Implementer, explorer, and deep-reviewer stayed identical.

`skills:` and `disallowedTools:` are carried through byte for byte in all five roles:
planner `skills: [workflow-spec-driven, wspecify, wtasks, ponytail]`; implementer
`skills: [wimplement, ponytail]` plus `disallowedTools: Skill`; verifier `skills: [wverify]`;
explorer and deep-reviewer `disallowedTools: Skill`.

The refusal is the load-bearing half, and it holds in both frontmatter forms. On throwaway copies,
adding `wghost` to the planner template's `skills:` — once inline, once as a block list — made the
sync exit `2` with one line naming both the template and the skill:

```
workflow-config: templates/agents/claude/planner.md preloads unknown skill 'wghost'
```

Every destination file under `.claude/agents`, `.codex/agents`, and `.cursor/agents` was compared by
SHA-256 **and mtime** before and after each refusal, and both sets were identical: the sync writes
nothing when it refuses.

Provider prose was audited too. No packet, template, or skill anywhere under `templates/`,
`.agents/`, `.claude/agents`, `.cursor/agents`, or `.codex/agents` names a retired
`references/{specify,design,tasks,implement,validate}.md`. Every `docs/guidelines/*.md` path named by
a packet resolves (`FRONTEND`, `MODELING`, `QA-SCENARIOS`, `SECURITY`, `TEST-CONTRACT`), and every
skill named in packet prose is a bundled skill directory (`ponytail`, `workflow-spec-driven`,
`wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`). Cursor and Codex packets carry prose load
lines only, which is the recorded intent.

### ADP-adopt-workflow-safely and ADP-layered-workflow-adoption

Layering was walked incrementally: `core` first, then `quality` on the same target. Both applies and
both `status` runs exited `0`; after `quality` the status was 98 `clean`, 18 `retained`, one
`resolved`. `docs/qa/README.md` arrived with the quality layer, and the consumer-owned skill and
edited template survived the second layer untouched.

### QAS-discover-independent-qa-skills

`qa-plan` and `qa-execute` are the `quality` layer, not `core` — `QUALITY_PATHS` in
`scripts/adopt.py:50`. A core-only target therefore has verifier packets that route to `qa-plan` and
`qa-execute` before those skills exist. That is the layer contract working as designed, not a defect:
`DEPENDENCIES` makes `quality` depend on `core`, and an adopter who wants QA adopts the layer that
ships it. It is worth recording because the sync preflight validates `skills:` frontmatter only, so
prose routing to a not-yet-adopted skill is invisible to it by construction.

After `quality`, both skills are present, both `.claude/skills/qa-{plan,execute}` links resolve to
the same inode as their canonical file, and all three provider Verifier packets route the three
phases: `.claude/agents/verifier.md` (which also declares `skills: [wverify]`),
`.cursor/agents/verifier.md`, and `.codex/agents/verifier.toml` each state
`phase: exactly one of technical, qa-plan, or qa-execute` and instruct invoking the canonical
`qa-plan` / `qa-execute` skill.

### CFG-derive-merge-alone-slices

The installed template is at `.agents/skills/wtasks/references/tasks-template.md` (9437 bytes) and
the old `workflow-spec-driven/references/tasks-template.md` path is gone. The template still names
the three planning units apart — vertical slice, phase/cohort, batch — and the `workflow-config`
skill still presents `--slices` as an assertion rather than the source of truth.

`validate_tasks.py --slice-contract-json` on the tracked fixtures derived one slice from
`merge-alone-one-slice.md` (T1–T5 all in slice A) and two from `merge-alone-two-slices.md`, both exit
`0`. Resolving those as features in a disposable Git target produced deep-review groups `[[1]]` and
`[[1, 2]]`, matching the derived counts. A feature directory with no `tasks.md` resolved to one slice.

The assertion discriminates on the paths it owns: a first resolve with `--slices 5` against a derived
2 exited `2` with `slice count assertion 5 does not match derived slice count 2`, and `--refresh
--slices 3` against a derived 1 exited `2` with the same shape while leaving `workflow.json`
byte-identical. On a normal resume the assertion is not re-evaluated and the frozen snapshot comes
back — which is the documented contract in the `workflow-config` skill: `--slices` "remains an
optional assertion for initial resolution and refresh" and "normal resume returns the frozen snapshot
without reading current Tasks". Recorded as conforming, not as a finding.

### DOC-read-explicit-workflow-provenance — adjacent canary

`docs/workflow/pack.md` declares "eleven local capabilities" and its table has exactly eleven rows,
including all five phase skills and the router. The count claim and the table agree, and the table
agrees with the installed tree. `README.md` names the router and its five phase skills at lines 3–4
and again in the adoption section at 303–304. `docs/workflow/roadmap.md` is present.

Provenance is intact: `README.md` carries the credits section, and `qa-plan`/`qa-execute` each carry
an explicit `## Provenance` naming the author and the inspiring source. The external security skills
are still described as dependencies rather than bundled capabilities, with three pinned entries
(`security-best-practices`, `security-threat-model`, `security-review`) plus the pinned CLI version in
`skills-lock.json`. Nothing names a consuming product or stack.

The `workflow-config` skill directory is not in the capability table. That predates this feature —
`pack.md` at merge-base `b5dc370` claimed "six local capabilities" and also omitted it — so it is
outside this cycle's scope and is not raised as a defect here.

### REL-report-current-workflow-release — adjacent canary

Newest released changelog heading `## [0.8.0] - 2026-08-31` matches `package.json` version `0.8.0`
and `WORKFLOW_VERSION = "0.8.0"` in `scripts/adopt.py:21`; an `## [Unreleased]` section sits above it.
`bun.lock` identifies root package `my-workflow` and its dev-dependency graph. `bun pm pack
--dry-run` exited `0` for `my-workflow-0.8.0.tgz`, 608 files, 4.86 MB unpacked, with eleven
phase-skill file entries packed. No `.tgz` residue was left in the checkout.

The charter's known blocker,
[`BUG-20260903-history-gate-forbids-resetting-baseline-scenarios`](../bugs/BUG-20260903-history-gate-forbids-resetting-baseline-scenarios.md),
was retested rather than assumed. On the current tree, which carries five reset baseline scenarios,
`bun test tools/shared/tests/qa-skills.test.ts` exits `0`. The mutation sensor the fix was required to
preserve still bites: appending a line to the historical report
`docs/qa/reports/2026-08-31-release-0-8-0.md` made `IT-006` fail with exit `1`, and restoring the file
returned the gate to `0`. The fix is real and discriminating. Bug closed, `retest_status: pass`.

## Findings

None. No product defect was observed, so no bug record was filed and no Implementer handoff is
required.

Two observations recorded above are conforming behaviour, not defects: `qa-plan`/`qa-execute` belong
to the `quality` layer while the core-layer verifier packet's prose names them, and `--slices` is not
re-evaluated on a normal resume. Both match their written contracts.

## Limitations

- The CLI/manual adapter observes exit codes, printed refusals, target bytes, mtimes, inode identity,
  and installed links. Hostile staged-file, process-race, and exact-checkpoint-mutation controls
  remain technical-verification surfaces.
- The disposable target is not a consuming product, so slice resolution was walked against the
  tracked merge-alone fixtures rather than a real feature's `tasks.md`.
- No network was used, `scripts/install_security_skills.py` was not run, and the three external
  security skills were verified only as pinned lock entries, not as installed trees.

## Cleanup and residue

All three disposable siblings under `/Users/antoniofulg/Projects/` were removed; none remain. The
source checkout carries only this report as an untracked change. `docs/qa/evidence/` is gitignored.

## Commands and exit codes

| Command | Exit |
| --- | --- |
| `uptime` (load 15.92) | 0 |
| `bun run test:all` (opening gate) | 0 |
| `python3 scripts/adopt.py plan <target> --layers core --json` | 0 |
| `python3 scripts/adopt.py apply <target> --layers core` | 0 |
| `python3 scripts/adopt.py status <target>` | 0 |
| `python3 scripts/adopt.py apply <target> --layers core` (re-adopt over consumer state) | 0 |
| `python3 scripts/adopt.py apply <target> --layers quality` | 0 |
| `python3 scripts/adopt.py status <target>` (after quality) | 0 |
| `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents` | 0 |
| same, after perturbing `.my-workflow.toml` | 0 |
| same, on copy with inline `skills:` entry `wghost` | 2 |
| same, on copy with block-list `skills:` entry `wghost` | 2 |
| `python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py tools/fixtures/tlc-validator/merge-alone-one-slice.md --slice-contract-json` | 0 |
| `… merge-alone-two-slices.md --slice-contract-json` | 0 |
| `workflow_config.py --root <target> --feature qa-one --native-provider claude` | 0 |
| `… --feature qa-two --native-provider claude` | 0 |
| `… --feature qa-three --native-provider claude --slices 5` (derived 2) | 2 |
| `… --feature qa-four --native-provider claude --slices 2` | 0 |
| `… --feature qa-five --native-provider claude` (no `tasks.md`) | 0 |
| `… --feature qa-one --native-provider claude --refresh --slices 3` (derived 1) | 2 |
| `python3 .agents/skills/workflow-config/scripts/parallel_plan.py --help` | 0 |
| `bun pm pack --dry-run` | 0 |
| `bun test tools/shared/tests/qa-skills.test.ts` (reset scenarios) | 0 |
| `bun test tools/shared/tests/qa-skills.test.ts` (tampered historical report) | 1 |
| `bun test tools/shared/tests/qa-skills.test.ts` (report restored) | 0 |
| `bun run test:all` (closing gate) | 0 |
