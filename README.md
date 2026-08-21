# my-workflow

An operating system for agents. It increments [`tlc-spec-driven`](https://github.com/tech-leads-club/agent-skills/tree/main/skills/tlc-spec-driven)
with a capped delivery loop, countable tests and security surfaces, and a knowledge bundle. It is
not a product template and not a stack starter.

The design problem is the usual one: **ship, without lying about quality**. Unbounded review feels
responsible and never finishes. A green suite with no spec contract ships bugs. This pack picks a
middle: small vertical slices, cheap gates while building, a hard cap on review rounds, and a
human-owned merge.

Start here: **[docs/workflow/](docs/workflow/)** — an index of every stage, guideline, and choice.

## Purpose

| Delivery | Reliability |
| --- | --- |
| Auto-sized planning (one line needs no spec) | Tests assert spec outcomes, not the implementation |
| Scoped gate per slice; full gate once | Never weaken a test to go green |
| Nitpicks become filed issues, not extra rounds | Blocker and Major still hold the ship |
| `ponytail` at `full` — shortest code that works | Security surfaces declared and given `SEC-` ids |
| Human schedules merge | Approval is local-only; push and deploy need an explicit go-ahead |

The loop, the caps, and the guidelines are the mechanism. The tour explains **why** each exists.
`AGENTS.md` is what agents run.

## Credits and provenance

This workflow is maintained by Antonio Fulgêncio. The process builds on work from the following
authors and communities:

- Tech Leads Club: [`tlc-spec-driven`](https://github.com/tech-leads-club/agent-skills/tree/main/skills/tlc-spec-driven)
  and the security gate with its [security skills](https://github.com/tech-leads-club/agent-skills/tree/main/skills).
- Pedro Nauck: [`deep-review`](https://github.com/pedronauck/skills/tree/main/skills/mine/deep-review),
  whose review workflow is adapted here.
- The project-owned `qa-plan` and `qa-execute` skills are Antonio's adaptations, inspired by Pedro's
  [`qa-report`](https://github.com/pedronauck/skills/tree/main/skills/mine/qa-report) and
  [`qa-execution`](https://github.com/pedronauck/skills/tree/main/skills/mine/qa-execution).

The QA skills use their own wording and structure for this workflow; the links above identify the
inspiration and do not claim upstream authorship.

## Adopt the workflow

Copy the loop, not the product. For a new project, replace the stencil paragraph under **What this
project is** in `AGENTS.md` and fill product documentation only as the product earns it. For an
existing project, preserve its filled product paragraph and product-owned documentation.

```bash
python3 scripts/adopt.py /path/to/target-project
```

Paste this once to an agent, replacing the pack and target paths:

```
Adopt the agent OS from /path/to/my-workflow into /path/to/target-project.

First check `git status --short`; do not stash, reset, clean, or hide unrelated changes. Read the
pack's README.md, AGENTS.md, and adoption script. Inspect the target read-only: package and build
manifests, declared gates, CI jobs, production-parity start and health paths, public interfaces,
authentication, fixtures or seed data, cleanup and residue checks, and installed QA tooling. Never
invent a command or install a QA framework during adoption.

Before writing, report the managed paths and every target path that could be replaced. Preserve
product-owned product, architecture, design, and stack documentation. For a new project, replace
the AGENTS.md product stencil and create product docs only as the product earns them. For an
existing project, let the adoption script refuse a filled product paragraph and merge the delivery
loop by hand. Preserve existing agent packets and model pins; add only missing packets.

Run `python3 /path/to/my-workflow/scripts/adopt.py /path/to/target-project` only after that review.
If `docs/qa/README.md` is absent, create it. If it exists, merge only newly discovered facts into
the existing profile; never overwrite existing content. Record the discovered interfaces, existing
runner or manual adapter, start and health authority, authentication, fixtures, cleanup, and
limitations. Keep command facts in the target's executable manifests or CI and link to them from
the profile.

Review the complete diff, managed-path overwrites, and the target's declared full gate. Record the
exact gate command and result. If the change exposes a user-visible UI, API, CLI, mobile, public
configuration, adoption, or docs-as-interface promise, send the existing Verifier a fresh
`qa-plan` packet followed by a separate `qa-execute` packet. For a purely internal refactor,
record `no user-visible change` and do not run QA. Activate `tlc-spec-driven` and `ponytail` at full.
```

The script merges the workflow-owned ignore entries, copies missing agent packets, and creates the
QA profile only when the target does not already have one. It refuses to overwrite a non-stencil
`AGENTS.md` product paragraph. Always review the resulting diff before accepting managed-path
replacements.

## Skills

Canonical copies live in `.agents/skills/`. Claude Code gets symlinks in `.claude/skills/`. Cursor,
Codex and OpenCode consume `.agents`. Do not add `.cursor/skills` or other agent trees. The
project-owned `qa-plan` and `qa-execute` skills use the consuming project's profile in
`docs/qa/README.md`; they do not select a framework or replace the project's gate.

```bash
npx --yes @tech-leads-club/agent-skills install --skill tlc-spec-driven \
  --agent cursor --agent claude-code --agent codex --agent opencode --symlink --force
# Keep canonical in .agents/skills/tlc-spec-driven and only a .claude symlink.
# Delete any .cursor/skills, extra .codex/.opencode copies the installer creates.

npx --yes skills add dietrichgebert/ponytail \
  --agent claude-code --agent cursor --agent codex --agent opencode --yes
```

`autonomous` is vendored here. `CLAUDE.md` is the one line `@AGENTS.md` (not a symlink). Planner,
implementer, explorer and verifier packets live under `.cursor/agents/`, `.claude/agents/` and
`.codex/agents/`.

## Knowledge checker

```bash
npm install
npm test
npm run knowledge
```

The consuming project's full gate should not include this checker. Run it when writing to the
bundle.

## Out of scope

Product domains, product-owned documentation, architecture, infrastructure, and framework choices
belong to the consuming project. This pack is stack-agnostic on purpose and does not prescribe a
browser, API, CLI, mobile, or manual QA runner.

## Deliberately not included

- Any product, domain, architecture, or design *concepts* from a source project's wiki
- Dated `knowledge/raw/` observations
- Library and stack skills
- A product skeleton, Makefile, port scheme, or worktree-slot arithmetic
- Retired orchestration history
- Threat-model and security-review *skills* (the process stays in `docs/guidelines/SECURITY.md`)
