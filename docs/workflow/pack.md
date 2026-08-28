# Skills, knowledge, adopt

## Skills

The workflow ships six local capabilities:

| Skill | Role |
| --- | --- |
| `tlc-spec-driven` | Planner. Specify, Design, Tasks, Execute. Auto-sizes. |
| `qa-plan` | Maps changed user-visible promises to durable QA journeys and charters. |
| `qa-execute` | Walks those journeys through the consuming project's existing adapter. |
| `ponytail` (`full`) | Shortest code that works. Stdlib before a dependency. |
| `autonomous` | Unattended run: classify work; credential-free configuration stays local, while eligible work may deliver one feature branch through one pull request. |
| `deep-review` | Multi-lane review orchestration, context assembly, findings, and rendered review artifacts. |

Canonical copies: `.agents/skills/`. Claude: symlinks in `.claude/skills/`. Cursor / Codex /
OpenCode consume `.agents`. Do not add `.cursor/skills`.

The security skills are external dependencies, not bundled capabilities. The pinned entries for
`security-best-practices`, `security-threat-model`, and `security-review` live in `skills-lock.json`.
The lock also pins the CLI version (`1.5.23`). Adoption prints a separate command for their
explicitly authorized installation into the same `.agents/skills/` tree. The command uses reviewed
commit refs and hashes; it does not install
`latest` or update dependencies automatically. Until it succeeds, the security gate remains
uncovered.

Planner / implementer / explorer / verifier are four windows. Canonical packet bodies live in
`templates/agents/{cursor,claude,codex}/`; sync generates ignored runtime files in
`.cursor/agents/`, `.claude/agents/`, and `.codex/agents/`. Spawn models live on those generated
files. `CLAUDE.md` is `@AGENTS.md`. Explorer is read-only and handles product-tree searches and
flow traces for the parent agent.

`autonomous` readiness still needs: full gate 0 on the final tree, no Blocker/Major left, `main` not
moved underneath, and flagged scenarios terminal (`untested` blocks; `blocked-verify` does not).
Invoking `autonomous` authorizes the feature-branch push, one pull request, and merge after readiness
is rechecked. Readiness is evidence, not authorization for deploy/release, production mutations,
force-push, direct push to `main`, or unrelated remote actions; those require explicit instruction.

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
non-stencil **What this project is** paragraph. It writes `@AGENTS.md` as `CLAUDE.md`, copies the
bundled skills (including `deep-review`) without shipping `__pycache__` or `*.pyc`, and creates
`docs/qa/README.md` only when the target has no profile. It copies missing
`.my-workflow.toml.example` and `templates/agents/`, preserves an existing local
`.my-workflow.toml`, and generates ignored runtime packets from those sources. Adoption rejects
Makefile references to machine-global `$(HOME)/.claude/...`,
`${HOME}/.claude/...`, `$HOME/.claude/...`, or `~/.claude/...`; point TLC gates at the adopted
`.agents/skills/tlc-spec-driven/scripts/...` path instead.

Adoption does not install the external security dependencies. After the bundled workflow is
adopted, it prints the exact project-local command to run with `--yes`. Review and authorize that
second step before allowing network access or writes to the consumer.

The consuming project owns product docs, architecture, design, stack, and `make check`.

## What was left out, and why

Stack skills, product wiki pages, a starter app, ports, and retired orchestration would make this
a clone of one product. The reliability rules are process; they travel. The domain does not.
