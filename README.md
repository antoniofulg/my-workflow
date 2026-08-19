# my-workflow

An operating system for agents. It increments [tlc-spec-driven](https://github.com/tech-leads-club)
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

## New project

1. Copy or clone this repository.
2. Replace the stencil paragraph under **What this project is** in `AGENTS.md` with one paragraph
   describing *your* product.
3. Fill `docs/product/`, `docs/architecture/`, and `docs/design/` as the product earns them.
4. Vendor the three skills (see below) if you started from a copy that omitted `.agents/`.
5. The consuming project owns `make check` (or whatever its full gate is). This pack does not.

```bash
python3 scripts/adopt.py /path/to/new-project
```

Paste this to an agent (replace the pack path):

```
This is a new product. Adopt the agent OS from /path/to/my-workflow into this repo.

Run `python3 /path/to/my-workflow/scripts/adopt.py` on this directory. Replace the stencil
under "What this project is" in AGENTS.md with one paragraph describing this product — not
the workflow, not the stack. Fill docs/product/, docs/architecture/, and docs/design/ only
as the product earns them. This repo owns the full gate (`make check` or equivalent); the
pack does not.

Keep CLAUDE.md as the one line `@AGENTS.md`. Spawn planner, implementer, and verifier; pin
models only on the agent files. Copy the loop, not a product skeleton, ports, or stack.
Activate tlc-spec-driven and ponytail at full.
```

## Adopt into an existing project

Copy the loop, not the product:

- `AGENTS.md` delivery loop and dispatch table (merge; never overwrite a filled **What this project
  is** paragraph)
- `docs/guidelines/` and `docs/workflow/`
- `.agents/skills/{tlc-spec-driven,ponytail*,autonomous}` plus a `.claude/skills/` symlink tree
- empty `knowledge/` machinery (`AGENTS.md`, `raw/README.md`, wiki indexes, `tools/knowledge`)

Do not overwrite the consuming product's product docs, architecture, design, or stack.

```bash
python3 scripts/adopt.py /path/to/existing-project
```

The script refuses to overwrite `AGENTS.md` when the target already has a non-stencil product
paragraph.

Paste this to an agent (replace the pack path):

```
Adopt the agent OS from /path/to/my-workflow into this existing project. Copy the loop, not
the product.

Run `python3 /path/to/my-workflow/scripts/adopt.py` on this directory. If it refuses to
overwrite AGENTS.md, merge the delivery loop and dispatch table by hand — never replace a
filled "What this project is" paragraph. Do not overwrite product docs, architecture, design,
or stack.

Keep CLAUDE.md as `@AGENTS.md`. If this repo already has `.cursor/agents/` (or Claude/Codex
equivalents), keep those model pins; adopt copies agent folders only when they are missing.
Decisions go through `.specs/AD-INDEX.md` (`python3 tools/ad-index.py`); do not Read all of
STATE.md. Activate tlc-spec-driven and ponytail at full. The delivery loop stays.
```

## Skills

Canonical copies live in `.agents/skills/`. Claude Code gets symlinks in `.claude/skills/`. Cursor,
Codex and OpenCode consume `.agents`. Do not add `.cursor/skills` or other agent trees.

```bash
npx --yes @tech-leads-club/agent-skills install --skill tlc-spec-driven \
  --agent cursor --agent claude-code --agent codex --agent opencode --symlink --force
# Keep canonical in .agents/skills/tlc-spec-driven and only a .claude symlink.
# Delete any .cursor/skills, extra .codex/.opencode copies the installer creates.

npx --yes skills add dietrichgebert/ponytail \
  --agent claude-code --agent cursor --agent codex --agent opencode --yes
```

`autonomous` is vendored here. `CLAUDE.md` is the one line `@AGENTS.md` (not a symlink). Planner,
implementer and verifier packets live under `.cursor/agents/`, `.claude/agents/` and `.codex/agents/`.

## Knowledge checker

```bash
npm install
npm test
npm run knowledge
```

The consuming project's full gate should not include this checker. Run it when writing to the
bundle.

## Out of scope

Creatista, antclips, and that product's tech stack (including hono, drizzle, tanstack, shadcn,
better-auth, graphile) were excluded. This pack is stack-agnostic on purpose.

## Deliberately not included

- Any product, domain, architecture, or design *concepts* from a source project's wiki
- Dated `knowledge/raw/` observations
- Library and stack skills
- A product skeleton, Makefile, port scheme, or worktree-slot arithmetic
- Retired orchestration history
- Threat-model and security-review *skills* (the process stays in `docs/guidelines/SECURITY.md`)
