# Skills, knowledge, adopt

## Skills

Three families, nothing else:

| Skill | Role |
| --- | --- |
| `tlc-spec-driven` | Planner. Specify, Design, Tasks, Execute. Auto-sizes. |
| `ponytail` (`full`) | Shortest code that works. Stdlib before a dependency. |
| `autonomous` | Unattended run: classify feature vs filed issue, settle or halt, merge only when the full gate, blocking findings, and scenarios allow it. |

Canonical copies: `.agents/skills/`. Claude: symlinks in `.claude/skills/`. Cursor / Codex /
OpenCode consume `.agents`. Do not add `.cursor/skills`.

Planner / implementer / verifier are three windows. Packet text lives on the agent files; spawn
models live there too. Same `name` in `.cursor/agents/`, `.claude/agents/`, `.codex/agents/`. Real
files, no symlinks. `CLAUDE.md` is `@AGENTS.md`.

`autonomous` merge still needs: full gate 0 on the final tree, no Blocker/Major left, `main` not
moved underneath, flagged scenarios terminal (`untested` blocks; `blocked-verify` does not).

## Knowledge bundle

Empty on purpose. Machinery only: operating schema, `raw/` README, stub indexes, checker.

| Piece | Job |
| --- | --- |
| `knowledge/AGENTS.md` | OKF v0.2 schema (frontmatter, ingest, harvest, lint) |
| `knowledge/wiki/` | Concepts, when the consuming project earns them |
| `knowledge/raw/` | Immutable originals. Privacy surface — committed, so strip personal data |
| `npm run knowledge` | Conformance, drift, gaps. Run when writing to the bundle, not as the product gate |

## Adopt

`python3 scripts/adopt.py <target>` copies the loop into another repo and refuses to overwrite a
non-stencil **What this project is** paragraph. It writes `@AGENTS.md` as `CLAUDE.md`. Agent folders
copy only when the destination has none, so local model pins survive a re-adopt.

The consuming project owns product docs, architecture, design, stack, and `make check`.

## What was left out, and why

Stack skills, product wiki pages, a starter app, ports, and retired orchestration would make this
a clone of one product. The reliability rules are process; they travel. The domain does not.
