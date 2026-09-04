# QA Execute — specify-impact-designer — 2026-09-03

- **Charter:** [`CH-specify-impact-designer-2026-09-03`](../charters/CH-specify-impact-designer-2026-09-03.md)
- **Branch / HEAD:** `feat/specify-impact-designer` @ `981649fc`. The charter froze code scope at
  `0efc5d06`; this walk used the integrated tree at HEAD as dispatched.
- **Persona:** Workflow adopter (adjacent canary as Repository reader)
- **Adapter:** CLI/manual against checkout-owned disposable targets, as declared in
  [`docs/qa/README.md`](../README.md). No browser, API, or mobile surface exists.
- **Exact path:** `python3 scripts/adopt.py plan|apply|status <target> --layers core`, then
  `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents`,
  then filesystem inspection; adopted `validate_spec.py` against copies of the five size fixtures.
- **Targets:** `/Users/antoniofulg/Projects/.qa-specify-impact-designer-2026-09-03` plus throwaway
  copies `.qa-specify-impact-designer-neg-table`, `.qa-specify-impact-designer-neg-template`,
  `.qa-specify-impact-designer-neg-ghost`, and `.qa-specify-impact-designer-perturb`. All removed.
- **Environment:** no network, no product runtime. `scripts/install_security_skills.py` was printed
  by adopt and not run. No remote fetched, no product code edited. Out of scope:
  [`BUG-20260903-cursor-route-bracket-effort-rejected`](../bugs/BUG-20260903-cursor-route-bracket-effort-rejected.md).
- **Opening gate:** `bun run test:all` → exit `0`, load averages `26.02 26.04 25.41` at start
  (1-minute load above 20; the known `tools/test_parallel_resource_lock.py` flake did not occur).
  Evidence `../evidence/2026-09-03-specify-impact-designer/01-opening-gate.log`.
- **Closing gate:** first `bun run test:all` → exit `1` at load `24.78 28.99 28.96` in
  `tools/test_deep_review_token_metrics.py`
  (`test_provider_block_finishes_active_jobs_and_resume_skips_valid_outputs`, leftover `job-3`).
  Not the known `test_parallel_resource_lock.py` flake. One clean retry after 1-minute load dropped
  to `19.17` → exit `0`. Evidence `90-closing-gate.log` and `91-closing-gate-retry.log`.
- **Evidence root:** `docs/qa/evidence/2026-09-03-specify-impact-designer/` (disposable, gitignored).

## Scenario matrix

| Scenario | Verdict | Evidence |
| --- | --- | --- |
| `QAS-write-specify-impact-and-uiux` | pass | `15-installed-tree.txt`; `16-wspecify-impact.txt`; `17-spec-template.txt`; `18-uiux-guideline.txt`; `19-wdesign.txt`; `20-wverify.txt` |
| `QAS-offer-gap-hunt-at-plan-approval` | pass | `16-wspecify-impact.txt`; `21-gap-hunt.txt` |
| `ADP-require-impact-on-large-specs` | pass | `22-validate-spec.log` |
| `QAS-resolve-phase-skill-procedures` | pass | `15-installed-tree.txt`; `60-pointer-resolution.txt`; `16-wspecify-impact.txt` |
| `CFG-centralize-agent-model-routing` | pass | `30-sync-agents.log`; `31-designer-packets.txt`; `33-example-tables.txt`; `33-sync-perturbed.log`; `34-perturbed-diff.txt`; `40-neg-missing-table.log`; `40-neg-table-cmp.txt` |
| `CFG-preload-agent-skills-in-packets` | pass | `31-designer-packets.txt`; `35-skills-lines.txt`; `42-neg-ghost.log`; `42-neg-ghost-cmp.txt` |
| `ADP-adopt-workflow-safely` | pass | `11-plan-core.json`; `12-plan-unchanged.txt`; `13-apply-core.log`; `14-status.log`; `15-installed-tree.txt`; `50-readopt.log`; `51-sentinel.txt` |
| `DOC-read-explicit-workflow-provenance` | pass | `70-doc-provenance.txt`; `70-doc-provenance-table.txt` |

No row is `fail`, `untested`, or `blocked-verify`. No defect was found.

## Walk

### ADP-adopt-workflow-safely

`plan --layers core --json` against the empty git-seeded target exited `0` with `status: ready`,
`conflicts: []`, and 126 actions. The three designer templates and three designer runtime packets
appear as managed `add` actions, as do the five phase skills and `wspecify/references/gap-hunt.md`.
The target listing SHA-256 was identical before and after the plan
(`d6601f60e35c34b440683ac784cbae9e212638e9b691500797f6aa99ae00c0a3`), so the read-only promise holds.

`apply --layers core` and `status` both exited `0`. Status reported `clean` with 74 `clean` + 20
`retained` and no conflicts. After apply, the three designer templates, five phase `SKILL.md`
files, `gap-hunt.md`, `spec-template.md`, `validate_spec.py`, and all eighteen generated packets
are present. Each `.claude/skills/w<phase>` symlink points at `../../.agents/skills/<name>` and
opens the **same inode** as the canonical file.

Apply printed the external security installer command and did not invoke it. No security-skill
directory appeared in the target.

Re-adoption over a consumer-owned `# QA-SENTINEL-specify-impact-designer-2026-09-03` line in
`.my-workflow.toml` exited `0`. The file SHA-256 was
`7c8cc2ed502f66f5e64528ddf896411dfe0d2716739e9282998d37063362c877` before and after (1800 bytes).
Status after the second apply stayed `clean`. The Impact / gap-hunt / designer-dispatch headings
were still present on an independent re-read after that reload.

### QAS-write-specify-impact-and-uiux

Installed `wspecify/SKILL.md` orders the new steps after the dimensions sweep and before stories:

- `### 2. Map Impact` — two explorers, writes `## Impact`, one ubiquitous AC per affected feature
- `### 3. Capture User Stories with Priorities`
- `### 4. Write Acceptance Criteria`
- `### 5. UI/UX Surface Map (uiux.md)` — only when a screen is added or changed, after ACs and
  before the closure gate, following `docs/guidelines/UI-UX.md`
- `### 6. Requirement Closure Gate`
- `### 7. Plan Approval & Gap Hunt`

`spec-template.md` headings place `## Impact` between `## Assumptions & Open Questions` and
`## User Stories`. Installed `docs/guidelines/UI-UX.md` says `uiux.md` is written in Specify
before internal design. Installed `wdesign` step 1 loads `uiux.md` when present and dispatches
`designer` before internal design, while the planner keeps the architecture half of `design.md`.
Installed `wverify` `### 3.5` reruns the QA scenario ids named in `## Impact` as pass, fail, or
untested, and reports no reruns when Impact is `none`.

### QAS-offer-gap-hunt-at-plan-approval

The installed gap-hunt step cites `references/gap-hunt.md` and sizes the question: skip Small,
ask Medium and Large, recommend Complex; under autonomous, run only for Complex and record the
skip in `decisions.md`. Settled findings become acceptance criteria or `context.md` decisions;
if nothing is found, one line and proceed.

`gap-hunt.md` itself names two explorers (unhappy paths; domain and data gaps), numbered frontier
questions each with a recommended answer, the same settlement rule, and the one-line proceed.

### ADP-require-impact-on-large-specs

The five `tools/fixtures/tlc-validator/spec-size-*.md` files were copied into the disposable
target and checked with the adopted `validate_spec.py`:

| Fixture | Exit | Observed |
| --- | --- | --- |
| `spec-size-large-no-impact.md` | 1 | `missing required section: ## Impact` |
| `spec-size-complex-no-impact.md` | 1 | `missing required section: ## Impact` |
| `spec-size-medium-no-impact.md` | 0 | no errors |
| `spec-size-small-no-impact.md` | 0 | no errors |
| `spec-size-large-impact-none.md` | 0 | no errors |

A copy of this feature's own Large spec with `## Impact` also exited `0`.

### QAS-resolve-phase-skill-procedures

Every markdown link and `.agents/skills/workflow-spec-driven/scripts/*.py` citation in the five
phase skills, `gap-hunt.md`, `spec-template.md`, `discuss.md`, and the router resolved in the
adopted target: **29 citations, 0 unresolved**, including the new `references/gap-hunt.md` and
`validate_spec.py` pointers. The router names all five phase skills and links none of the retired
`references/{specify,design,tasks,implement,validate}.md` files; its `references/` holds
`code-analysis.md`, `coding-principles.md`, `lessons.md`, `memory.md`, `sub-agents.md`. Each
phase skill `name` equals its directory and no `disable-model-invocation` key is present.

### CFG-centralize-agent-model-routing and CFG-preload-agent-skills-in-packets

`--sync-agents` on the adopted target exited `0` twice with `changed: []` and all **eighteen**
packets listed unchanged, including the three designer packets. Destination SHA-256 sets were
identical before and after the first explicit sync (18 files).

Initialized `.my-workflow.toml` and the example carry the three designer tables: Claude
`inherit`/`high`, Codex `gpt-5.6-sol`/`high`, Cursor `claude-fable-5-1-thinking-high`/`high`.
Generated packets match those models. Claude designer `skills: [wdesign, ponytail]` and no
`disallowedTools`, matching its template; only `model` and `effort` are the replaceable lines.

A throwaway copy with Claude designer `effort` perturbed to `low` made sync exit `0` and report
exactly `.claude/agents/designer.md` changed. The packet-versus-template and packet-versus-original
diffs were the single `effort` line; the other seventeen destinations kept their SHA-256.

Missing `[models.cursor.designer]` on a copy made sync exit `2` with
`workflow-config: models.cursor.designer is required`. Destination SHA-256 **and mtimes** were
unchanged. Removing `templates/agents/claude/designer.md` on a second copy exited `2` naming
`templates/agents/claude/designer.md`, destinations unchanged.

Adding `wghost` to the Claude designer template `skills:` list exited `2` with
`workflow-config: templates/agents/claude/designer.md preloads unknown skill 'wghost'`.
Destinations unchanged. The other five Claude roles still carry their template `skills:` and
`disallowedTools:` byte-identical to the templates (planner preload intact, implementer /
explorer / deep-reviewer keep `disallowedTools: Skill`).

Designer template and packet bodies load `uiux.md`, `spec.md`, `UI-UX.md`, and `FRONTEND.md`,
write mockups under `docs/design/` and `uiux-review.md`, and say never write product code.

### DOC-read-explicit-workflow-provenance

Adjacent canary on the source checkout. `AGENTS.md` names designer among the spawn roles and is
**134** lines. `docs/workflow/pack.md` says the five windows are planner / implementer / explorer
/ verifier / designer. README still distinguishes bundled local adaptations from Tech Leads Club
and Pedro Nauck sources, names the three separately authorized external security skills
(`security-best-practices`, `security-threat-model`, `security-review`) pinned in
`skills-lock.json`, and stays stack-agnostic. Both QA skills keep their Antonio / Pedro
provenance statements. Provenance was not reset.

## Probes and lenses

Charter tour plus edges walked:

1. Read-only `plan --json` leaves the target byte-unchanged.
2. Designer templates and runtime packets are managed core paths.
3. Size-aware validator on all five copied fixtures, plus this feature's own Large spec.
4. Idempotent `--sync-agents` (eighteen packets, two runs).
5. Designer effort perturbation changes only that packet's `effort` line.
6. Missing designer table refuses by table name and writes nothing.
7. Missing designer template refuses by path and writes nothing.
8. Unknown preloaded skill refuses by template and skill and writes nothing.
9. Re-adopt preserves a consumer `.my-workflow.toml` sentinel byte-for-byte.
10. Security installer is printed and not run; no security-skill dirs appear.

Lenses on the two largest changed journeys (adopt + configure):

- **Comprehension:** Impact, uiux.md, gap-hunt, and designer-dispatch are numbered headings an
  agent can follow; `gap-hunt.md` is a cited sibling.
- **Recovery:** each refusal names the missing table, template, or skill.
- **Trust:** plan is read-only; refusals leave SHA-256 and mtimes unchanged; the sentinel survives
  re-apply.
- **Language:** skip / ask / recommend / autonomous-only-Complex wording is present in both the
  skill and `gap-hunt.md`.
- **Speed / accessibility:** no product runtime or UI exists; recorded as the profile limitation,
  not a failed lens.

## Closing

Disposable targets were removed. Source checkout residue is the planned durable report and
scenario status updates, plus the pre-existing untracked
`.specs/features/specify-impact-designer/validation-s1-r8.md`. Evidence stays gitignored.

Closing gate: first `bun run test:all` exited `1` under load `24.78` on an unrelated Deep Review
token-metrics assertion (`job-3` leftover). One clean retry after load dropped below 20 exited
`0`. No specify-impact-designer product defect. No new bug filed.

No row remains pending. Every walked scenario is `pass` with evidence on this report.
