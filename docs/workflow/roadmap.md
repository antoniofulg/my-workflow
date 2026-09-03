# Modular workflow roadmap

Shaping notes from 2026-09-03. Not a spec. Each slice below becomes its own feature through
`workflow-spec-driven`. Decisions here are provisional until an `AD-NNN` records them.

## Goal

Plan many features in one sitting, then let agents ship them one by one unattended, and let
user-filed Linear tickets be qualified and fixed with a human gate. Every role reads only the
skills it needs, and model or effort changes happen once, globally, for every provider.

## Decisions so far

- Phase skills: `workflow-spec-driven` (router: sizing, chain, resume), `wspecify`, `wdesign`,
  `wtasks`, `wimplement`, `wverify`, `qualify`. A phase SKILL.md carries its procedure
  under 200 lines, with templates and long examples underneath in its own `references/`. Validators and
  the shared references stay in the router and are cited by path. Critical rules live only in
  `AGENTS.md`.
- Scoping: agent frontmatter `skills:` preloads; agents without the `Skill` tool see only the
  preload. Phase skills set `disable-model-invocation: true`. Entry points `/specify`, `/design`,
  `/tasks`, `/implement`, `/verify`, `/qualify` use `context: fork` + `agent:`.
- `uiux.md` moves to Specify. It maps every screen, every user action, and every blocker that
  stops the user from completing the action. Design consumes it.
- Specify also writes an `## Impact` section in `spec.md`: shared entities the feature touches,
  every page, feature, job, or event that reads them, and the QA scenarios that cover them. Two
  explorers gather it (data and model dependencies; pages and journeys). Each affected feature gets
  a no-regression acceptance criterion, and the verifier reruns those scenarios. Example: a
  Publications feature touched People and Agenda; nobody tracked it.
- New agents: `designer` (fable; owns mockups from `uiux.md`, preloads design, UI-UX, FRONTEND,
  design-taste skills) and `qualifier` (haiku; classification only, no root cause).
- Gap hunt is a question at plan approval, not a mandatory step. Skipped for Small, asked for
  Medium and up, recommended for Complex. Two subagents: unhappy paths against current app
  behaviour and QA scenarios; domain and data gaps. Then frontier rounds of numbered questions
  with a recommended answer each, in the style of the installed `grilling` skill. Findings land as
  acceptance criteria or `context.md` decisions.
- Linear is the queue. No `queue.md`. Feature order is Linear priority and manual order in the
  Ready state. Spec frontmatter carries `ticket:`.
- Autofix never merges without the human gate. Reproduction raises confidence only.
- Root-cause hunting belongs to the implementer, not the qualifier.
- Runtime stays Python. Reason: 32k lines including 14k of tests already exist, macOS ships
  `python3`, `tomllib` is stdlib, no `node_modules` in consuming projects. Revisit only if the
  installed CLI ever needs to ship as a single binary.

## Linear model

States: Idea → Triage → Needs Info | Backlog | Ready for Fix → Approved → In Progress → In Review →
Done | Not a Bug | Rejected.

- Idea: human parking lot for things seen elsewhere. Human moves to Triage or Rejected.
- Triage: qualifier picks from here.
- Needs Info: could not reproduce or confidence below threshold; qualifier posts exact questions.
- Backlog: feature or non-bug, human decides, then `/specify TICKET`.
- Ready for Fix: qualified bug with packet. Human approves or denies.
- Approved: autofix consumer picks from here.

States and label groups are a pack-owned standard applied identically to every product, so one
qualifier prompt works everywhere. Label groups: kind (`bug`, `feature`, `idea`, `question`,
`duplicate`, `chore`, `tech-debt`); severity (`S1-blocker`, `S2-major`, `S3-minor`,
`S4-cosmetic`); source (`user`, `support`, `internal`, `market`); surface (`security`, `data`,
`payment`, `auth`, `ui`); route (`autofix`, `human`). Size maps to Linear estimate. Only area
labels are product-owned. The Linear module ships a script that creates missing states and labels
in a workspace, so setup is one command per product.

Qualifier packet, posted as a comment: kind, severity, size, expected behaviour with the product
doc or QA scenario it cites, key QA scenario id when one matches, reproduction steps, suspected
area, surfaces, confidence 0 to 1 from a fixed checklist, route.

## Unattended run

The runner is a shell script, not an agent, so no context accumulates:

```
for ticket in linear(state=Ready, order=priority):
    orca spawn claude -p "/autonomous TICKET" in fresh worktree
    wait; mark Done or Blocked; continue
```

Each feature gets a fresh agent. Within a feature, a `PreCompact` hook writes the Handoff, spawns
a successor through the Orca CLI in the same worktree, and the predecessor exits. A blocked
feature is skipped, not fatal; the morning report lists shipped and blocked with reasons.
Features run sequentially; slices inside a feature parallelize only when machine health passes.

## Mockup fidelity

Port, do not reinterpret. The implementer starts from the mockup file and copies markup and
styles, then wires behaviour. Design tokens are extracted from the mockup once into the token
file; no colour or spacing is retyped. Any deviation is listed with a reason in the report. The
verifier runs a visual diff at the mockup viewport (Playwright screenshot against the mockup
render, pixel threshold) plus a DOM structure diff; the UI slice carries a fidelity TEST id in the
test contract. Other viewports follow the responsive rules in `uiux.md` and FRONTEND.md.

Reuse before create. `ponytail` already says "already in this codebase? reuse it", and it was not
enough. Three reinforcements: the implementer packet requires a component inventory step (grep the
shared components folder, name the component used for each element, and justify any new one in
one line); deep review flags a new component that duplicates an existing one; and a lint rule
bans raw `button`, `input`, `select`, and `a` outside the shared components folder, so the
half-featured button cannot compile. The lint is the part that actually holds.

## Global config

`~/.config/my-workflow/config.toml` is global across Claude, Codex, and Cursor. Per-checkout
`.my-workflow.toml` holds overrides only. `[defaults] effort = "high"` and
`[defaults.<provider>] model = "..."` cover every role; per-role tables override. The CLI walks
`git worktree list` and re-renders every checkout. Feature `workflow.json` snapshots keep freezing
resolved values, so a global change never alters a running feature. Claude roles may also use
`model: inherit`.

Freshness: a `PreToolUse` hook on the `Agent` tool (or `SubagentStart`) runs the idempotent sync,
so every spawn reads the current global config. Changing effort when a budget runs low is then one
command, for example `mw set defaults.effort medium`, and the next spawn in every worktree picks
it up. Confirmed in the Claude Code docs: agent files are live-watched and a frontmatter change
applies on the next spawn without restart (exceptions: first agent in a new scope, `--add-dir`
directories). `PreCompact` fires for auto and manual compaction, receives the trigger, and can
deny compaction with exit 2, so the successor handoff can replace compaction rather than race it.

Providers: the hook must be proven on Claude Code, Cursor, and Codex before slice 5 closes.
Claude is confirmed. Cursor and Codex hook events and whether they re-read agent definitions
mid-session are unverified; slice 5 opens with that research. Provider-independent fallback: the
runner script runs the sync before every spawn, and interactive sessions run it on start.

Distribution: keep the Python runtime and publish an npm wrapper package whose `bin` execs
`python3` on the bundled pack, so `npx my-workflow install` works. npm is a channel, not a
runtime. Also publish to PyPI for `uvx my-workflow`.

## Slices

1. Skill split, preload, materializer renders `skills:`. No behaviour change.
2. Slash entry points with `context: fork`.
3. `uiux.md` and impact map to Specify; gap-hunt question; designer agent.
4. Mockup fidelity rule, reuse inventory, lint on raw elements, token extraction, visual diff gate.
5. Global config file, defaults, worktree walker, spawn-time sync hook.
6. Qualifier role, `qualify` skill, bug spec template, shadow mode, manual `/qualify`.
7. Linear module: MCP config, standard states and labels with a setup script, ticket link, PR attach.
8. Autofix consumer on `autonomous`, PR only, human gate.
9. Runner script, PreCompact successor hook, morning report, agreement metric, kill switch.

## Deferred: deterministic installer

Adopting the pack into a project took a full day and was never fully verified. `scripts/adopt.py`
already has `plan`, `resolve`, `status`, `apply`; the pain is the agent-driven work around it.

Direction: split install into a deterministic part and an agent part.

1. Terminal UI: a stdin multi-select of modules (core, parallel, quality, linear, extras) with
   no new dependency. Prints the plan, conflicts, and asks once.
2. Deterministic apply: copies the selected layers, generates the ignored runtimes, writes a
   suggested `AGENTS.md` next to any existing one, and runs `doctor`: every agent renders, every
   skill path resolves, every guideline the agents cite exists, the toml validates, a sample spec
   passes its validator. Fails loudly with a list.
3. Prints a verify prompt to paste into an agent: reconcile the existing `AGENTS.md` with the
   suggested one, fill the product paragraph, confirm the declared gates exist, and nothing else.

A pack manifest with file hashes lets `upgrade` tell pack changes from local edits and do a
three-way merge instead of asking the agent to eyeball diffs.

`AGENTS.md` gets lighter: critical rules, this chat's role, and where truth lives. The load table
moves into the phase skills that need each guideline, and guidelines that apply to file areas
become path-scoped skills (`paths:` frontmatter), for example FRONTEND on UI globs. Open question:
whether `adopt.py` grows this or the global CLI absorbs it.
