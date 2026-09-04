# QA Execute — w-entry-points — 2026-09-03

- **Charter:** [`CH-w-entry-points-2026-09-03`](../charters/CH-w-entry-points-2026-09-03.md)
- **Branch / HEAD:** `feat/w-entry-points` @ `0dc981af`. The charter froze code scope at
  `bb3d3656`; `0dc981af` is the QA plan itself, so no product code moved after the frozen scope.
- **Persona:** Workflow adopter (adjacent canary as Repository reader)
- **Adapter:** CLI/manual against checkout-owned disposable targets, as declared in
  [`docs/qa/README.md`](../README.md). No browser, API, or mobile surface exists.
- **Exact path:** `python3 scripts/adopt.py plan|apply|status <target> --layers core`, then
  `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents`,
  then filesystem inspection and frontmatter parse through `tools/shared/src/frontmatter.ts` via
  `bun -e`.
- **Targets:** `/Users/antoniofulg/Projects/.qa-w-entry-points-2026-09-03` (empty core adopt, then
  one re-apply over a consumer-owned skill). Removed after the walk.
- **Environment:** no network, no product runtime. `scripts/install_security_skills.py` not run, no
  remote fetched, no product code edited. Out of scope:
  [`BUG-20260903-cursor-route-bracket-effort-rejected`](../bugs/BUG-20260903-cursor-route-bracket-effort-rejected.md).
- **Opening gate:** `bun run test:all` → exit `0`, load averages `20.10 18.74 16.79` at start
  (1-minute load above 20; the known `tools/test_parallel_resource_lock.py` flake did not occur).
  Evidence `../evidence/2026-09-03-w-entry-points/01-opening-gate.log`.
- **Closing gate:** `bun run test:all` → exit `0`, load averages `14.47 16.21 16.90` at start.
  Evidence `../evidence/2026-09-03-w-entry-points/90-closing-gate.log`.
- **Evidence root:** `docs/qa/evidence/2026-09-03-w-entry-points/` (disposable, gitignored).

## Scenario matrix

| Scenario | Verdict | Evidence |
| --- | --- | --- |
| `ADP-install-review-and-qa-entries` | pass | `11-plan-core.json`; `12-target-after-plan.txt`; `13-apply-core.log`; `14-status.log`; `15-skill-links.txt`; `17-body-lines.txt` |
| `QAS-fork-w-skills` | pass | `16-frontmatter.json`; `16-frontmatter-assert.txt`; `17-body-lines.txt`; `21-implementer-template.txt`; `31-implementer-packets.txt` |
| `QAS-list-seven-w-entries` | pass | `16-frontmatter-assert.txt`; `70-doc-provenance-table.txt`; `70-doc-provenance.txt` |
| `ADP-install-phase-skills` | pass | `11-plan-core-extract.txt`; `13-apply-core.log`; `14-status.log`; `15-skill-links.txt`; `18-consumer-after.txt`; `19-reload-links.txt` |
| `QAS-resolve-phase-skill-procedures` | pass | `16-frontmatter-assert.txt`; `20-pointer-resolution.txt`; `20-pointer-fragment-note.txt` |
| `DOC-read-explicit-workflow-provenance` | pass | `70-doc-provenance.txt`; `70-doc-provenance-table.txt` |

No row is `fail`, `blocked-verify`, or pending. The live dual-`/wspecify` host return is an
untested limitation on `QAS-fork-w-skills`, not a scenario-level `untested`. No defect was found.

## Walk

### ADP-install-review-and-qa-entries

`plan --layers core --json` against the empty target exited `0` with `status: ready`,
`conflicts: []`, and 119 actions. The four new paths appear as managed actions:

- `.agents/skills/wreview/SKILL.md` (`add`)
- `.agents/skills/wqa/SKILL.md` (`add`)
- `.claude/skills/wreview` (`link`)
- `.claude/skills/wqa` (`link`)

The target's listing SHA-256 was identical before and after the plan
(`7d3c93e4e96cf29a516c8e2ca4ab583693f44b708bc0bdfa0afaa84e30b2019e`), so the read-only promise holds.

`apply --layers core` and `status` both exited `0`. Status reported `clean`, 73 `clean` + 17
`retained`, no conflicts. After apply, both `.agents/skills/wreview/SKILL.md` and
`.agents/skills/wqa/SKILL.md` exist; each `.claude/skills/w*` symlink points at
`../../.agents/skills/<name>` and opens the **same inode** as the canonical file. Line counts are
16 (`wreview`) and 14 (`wqa`), both under 40.

Independent re-read after status and after a second apply kept the same SHA-256 and inode pairs.
`wreview` names `.agents/skills/deep-review/SKILL.md` and refuses `--publish`. `wqa` binds
`$ARGUMENTS`, runs exactly one QA phase (`qa-plan` when the first argument is `plan`, else
`qa-execute`), and stops when no journey carries the flow tag.

### ADP-install-phase-skills

The same core plan lists all five phase directories as managed adds, including
`wspecify/references/discuss.md`. After apply, each `.agents/skills/w<phase>/SKILL.md` and
`.claude/skills/w<phase>/SKILL.md` share one inode. Re-adoption over a consumer-owned
`.agents/skills/consumer-thing/SKILL.md` exited `0` and left that file byte-identical
(SHA-256 `dadd3b098ceadb1a45c57f18cd3481f2fe763c6c5a3b4104bce4241f4bd16960` before and after).
Status after the second apply stayed `clean`; the consumer path is not a managed action.

### QAS-fork-w-skills

`readFrontmatter` from `tools/shared/src/frontmatter.ts` (via `bun -e`) parsed all seven adopted
`SKILL.md` files with `error: null`. Every file carries `context: fork`, `background: false`, an
`argument-hint`, and `agent:` planner / planner / planner / implementer / verifier / planner /
verifier. No `disable-model-invocation` key is present. The first instructional body line on the
five phase skills and `wqa` binds `$ARGUMENTS` and stops on a slash-empty argument; `wreview`
takes optional flags and rejects `--publish`.

The adopted Claude implementer template still lists `skills: [wimplement, ponytail]` and
`disallowedTools: Skill`, SHA-identical to the source checkout. After
`workflow_config.py --root <target> --sync-agents` (exit `0`, fifteen packets unchanged), the
generated `.claude/agents/implementer.md` repeats those two lines. Cursor and Codex packets keep
their prose load of `wimplement` (recorded intent from the prior cycle; this charter's canary is
the Claude template).

No host slash session was available. The live `/wspecify a` then `/wspecify b` return is
**untested**, not `blocked-verify`.

### QAS-list-seven-w-entries

The seven adopted descriptions start with Specify / Design / Tasks / Execute / Verify / Review /
QA and each contains `Argument:`. `docs/workflow/pack.md` claims thirteen local capabilities; its
skill table has 13 rows and includes all seven `w*` names. Roadmap slice 2 ends `(done)`. The
files a `/w` menu would read are those seven descriptions; a live host menu was not available and
is the same slash-session limitation as above.

### QAS-resolve-phase-skill-procedures

Each phase skill's `name` equals its directory. Relative `references/` paths and
`.agents/skills/workflow-spec-driven/scripts/*.py` citations in the five phase skills, their
reference files, and the router open in the adopted target. One markdown link in
`wspecify/references/discuss.md` uses a fragment
(`../SKILL.md#implicit-requirement-dimensions`); the destination file exists and the heading is
present. Retired `references/{specify,design,tasks,implement,validate}.md` are absent. The router
`references/` listing is `code-analysis.md`, `coding-principles.md`, `lessons.md`, `memory.md`,
`sub-agents.md`. The router names all five phase skills.

### DOC-read-explicit-workflow-provenance

Adjacent canary. README still has Credits and provenance, Antonio Fulgêncio, Tech Leads Club,
Pedro Nauck, the three external security skill names, and "not a product template and not a stack
starter". Both QA skills keep `## Provenance` as original project-owned adaptations inspired by
Pedro Nauck. `skills-lock.json` still pins the three security skills with refs, CLI `1.5.23`, and
hashes. `pack.md` thirteen matches its 13-row table and includes the seven `w*` rows; roadmap
slice 2 is `(done)`. No consuming product or stack name appears in README, pack, or the QA skills.
The adopted core target correctly omits source-only `pack.md` and `roadmap.md`.

## Probes and lenses

Eleven charter-aligned edge probes passed. Recorded in
`../evidence/2026-09-03-w-entry-points/80-probes-and-lenses.txt`.

Re-walked `J-adopt-workflow` and `J-review-workflow-release` with the six lenses:
comprehension, recovery, trust, speed, and language hold on the installed files. Accessibility
has no browser/UI surface here and is a limitation, not a fail.

## Findings

None. No product defect was observed, so no bug record was filed and no Implementer handoff is
required.

Two scanner notes that are not defects: a first pack.md row regex skipped `ponytail` (`full`)
because of inner backticks (recount is 13); a first pointer sweep treated a fragment link as a
missing file (the file and heading exist).

## Limitations

- The CLI/manual adapter observes exit codes, printed plans, target bytes, inodes, SHA-256, and
  installed links. A live `/w` host return is unreachable in this session; that leg stays
  `untested`.
- No network was used, `scripts/install_security_skills.py` was not run, and the three external
  security skills were verified only as pinned lock entries, not as installed trees.
- Accessibility has no product UI to walk.

## Cleanup and residue

The disposable sibling `/Users/antoniofulg/Projects/.qa-w-entry-points-2026-09-03` was removed;
none remains. The source checkout carries this report and the six updated scenario status fields
as the planned durable QA artifacts. `docs/qa/evidence/` is gitignored.

## Commands and exit codes

| Command | Exit |
| --- | --- |
| `uptime` (opening load 20.10 18.74 16.79) | 0 |
| `bun run test:all` (opening gate) | 0 |
| `python3 scripts/adopt.py plan <target> --layers core --json` | 0 |
| `python3 scripts/adopt.py apply <target> --layers core` | 0 |
| `python3 scripts/adopt.py status <target>` | 0 |
| `python3 scripts/adopt.py status <target> --json` | 0 |
| `bun -e` frontmatter parse of seven adopted `SKILL.md` | 0 |
| `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents` | 0 |
| `python3 scripts/adopt.py apply <target> --layers core` (re-adopt over consumer skill) | 0 |
| `python3 scripts/adopt.py status <target> --json` (after re-adopt) | 0 |
| `uptime` (closing load 14.47 16.21 16.90) | 0 |
| `bun run test:all` (closing gate) | 0 |
