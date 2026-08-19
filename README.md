# my-workflow

Personal agent operating system. It increments `tlc-spec-driven` with slice caps, a knowledge
bundle, and an unattended-run skill. It is not a product template and not a stack starter.

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

## Adopt into an existing project

Copy the loop, not the product:

- `AGENTS.md` delivery loop and dispatch table (merge; never overwrite a filled **What this project
  is** paragraph)
- `docs/guidelines/`
- `.agents/skills/{tlc-spec-driven,ponytail*,autonomous}` plus a `.claude/skills/` symlink tree
- empty `knowledge/` machinery (`AGENTS.md`, `raw/README.md`, wiki indexes, `tools/knowledge`)

Do not overwrite the consuming product's product docs, architecture, design, or stack.

```bash
python3 scripts/adopt.py /path/to/existing-project
```

The script refuses to overwrite `AGENTS.md` when the target already has a non-stencil product
paragraph.

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

`autonomous` is vendored here. `CLAUDE.md` is a symlink to `AGENTS.md`.

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
