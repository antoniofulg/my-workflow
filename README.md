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

The workflow references three external security skills:

- `security-best-practices` for secure-by-default language and framework guidance;
- `security-threat-model` for repository-grounded threat models;
- `security-review` for high-confidence residual vulnerability reviews.

They are not bundled in this pack. Their GitHub source, canonical path, reviewed commit, CLI
version (`1.5.23`), and content hash are authoritative in [`skills-lock.json`](skills-lock.json).
Adoption prints a
separate installer command; run it only after explicit authorization because it uses the network
and writes the consumer's `.agents/skills/` tree. It does not install `latest` or silently update
these dependencies.

## Adopt the workflow

Copy the loop, not the product. For a new project, replace the stencil paragraph under **What this
project is** in `AGENTS.md` and fill product documentation only as the product earns it. For an
existing project, preserve its filled product paragraph and product-owned documentation.

```bash
python3 scripts/adopt.py /path/to/target-project
```

For an existing project with a filled product paragraph, pass `--skip-agents` to preserve
`AGENTS.md` and `CLAUDE.md` byte-for-byte while installing the rest of the workflow:

```bash
python3 scripts/adopt.py --skip-agents /path/to/target-project
```

This is an explicit opt-in. It skips only the two agent instruction files; merge the workflow loop
into `AGENTS.md` and update `CLAUDE.md` manually later.

Prerequisites: the target directory must already exist, and `adopt.py` requires Python 3. Adoption
does not require a Git `HEAD`. Before running the workflow-config resolver, the target must be a Git
repository with at least one commit. Node.js and npm are needed only to validate this source pack's
gates, not to adopt it.

Feature planning under `.specs/features/` is ignored by default because these artifacts normally die
with the feature branch. If a project hands work off through Git worktrees, or a gate/CI job reads
the specs, version the relevant feature tree: remove the managed `.specs/features/` entry from the
target's `.gitignore` and commit those specs. Adoption does not detect or migrate this choice.

The workflow config is consumer-owned and optional. Copy
`.my-workflow.toml.example` to `.my-workflow.toml` when a project wants to make its cadence or
provider profile explicit. Adoption never creates or overwrites this file:

```bash
cp /path/to/my-workflow/.my-workflow.toml.example /path/to/target-project/.my-workflow.toml
```

The `cadence` controls the deep-review groups:

- `slice`: one group per slice (`1, 2, 3, 4` → `[1] [2] [3] [4]`).
- `feature`: one group for the whole feature (`1, 2, 3, 4` → `[1, 2, 3, 4]`).
- `grouped.N`: consecutive, balanced groups with at most `N` slices (`grouped.3` with four
  slices → `[1, 2] [3, 4]`).

The resolver uses the native provider for every role unless a named profile or role override is
selected. Precedence is `CLI override > profile > native provider`:

```bash
# Native route: all roles use Codex.
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-native --slices 4 \
  --native-provider codex

# Named profile: use the [profiles.mixed] routes from .my-workflow.toml.
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-profile --slices 4 \
  --native-provider codex --profile mixed

# Role overrides win over both the selected profile and the native provider.
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-override --slices 4 \
  --native-provider codex --profile mixed \
  --override deep_reviewer=cursor --override verifier=claude
```

The first resolution freezes the effective route and cadence in
`.specs/features/<feature>/workflow.json`. On resume, the snapshot is authoritative: changes to
`.my-workflow.toml` or resolver arguments are ignored. Run the resolver with `--refresh` only after
an explicit human request to resolve the feature again:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-refresh --slices 4 \
  --native-provider codex --refresh
```

The complete contract is in the
[workflow-config skill](.agents/skills/workflow-config/SKILL.md).

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
existing project, the default command refuses a filled product paragraph; use `--skip-agents` when
you want the rest of the workflow installed first, then merge the delivery loop into `AGENTS.md`
and update `CLAUDE.md` by hand. Preserve existing agent packets and model pins; add only missing
packets.

Run `python3 /path/to/my-workflow/scripts/adopt.py /path/to/target-project` only after that review.
For a filled product paragraph, use `--skip-agents` as described above.
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
QA profile only when the target does not already have one. By default it refuses to overwrite a
non-stencil `AGENTS.md` product paragraph. With `--skip-agents`, it leaves both `AGENTS.md` and
`CLAUDE.md` untouched. Always review the resulting diff before accepting managed-path replacements.
Adoption itself does not install external security skills. It prints the exact command for the
separate authorized step and leaves the security gate uncovered until that command succeeds.

## Skills

Canonical copies live in `.agents/skills/`. Claude Code gets symlinks in `.claude/skills/`. Cursor,
Codex and OpenCode consume `.agents`. Do not add `.cursor/skills` or other agent trees. The
project-owned `qa-plan` and `qa-execute` skills use the consuming project's profile in
`docs/qa/README.md`; they do not select a framework or replace the project's gate.

`adopt.py` installs and updates only the bundled TLC, Ponytail, Deep Review, QA, workflow-config,
and autonomous skills. Keep those canonical copies in `.agents/skills/` and the Claude Code
symlinks in `.claude/skills/`. The three external security skills are a separate authorized step:

```bash
python3 /path/to/my-workflow/scripts/install_security_skills.py \
  /path/to/target-project --yes
```

The installer uses only the reviewed refs and hashes in `skills-lock.json`; it does not resolve
`latest` or perform automatic updates. Review its printed plan and authorize the command before
running it. Until it succeeds, do not treat the security gate as covered.

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
