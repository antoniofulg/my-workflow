# my-workflow

An operating system for agents. It ships the workflow-owned [`workflow-spec-driven`](.agents/skills/workflow-spec-driven/SKILL.md)
router and its five phase skills (`wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`)
with a capped delivery loop, countable tests and security surfaces, and a knowledge bundle. It is
not a product template and not a stack starter.

The design problem is the usual one: **ship, without lying about quality**. Unbounded review feels
responsible and never finishes. A green suite with no spec contract ships bugs. This pack picks a
middle: small vertical slices, cheap gates while building, a hard cap on review rounds, and a
human-owned merge.

## Quick start

Keep the immutable release checkout separate from the project receiving it. The target directory must
already exist. A Git repository is recommended so plans, conflicts, and workflow state remain
reviewable.

```bash
git clone --branch v0.10.0 --depth 1 https://github.com/antoniofulg/my-workflow.git /path/to/my-workflow-0.10.0
mkdir -p /path/to/target-project
python3 /path/to/my-workflow-0.10.0/scripts/adopt.py plan /path/to/target-project --layers core --json
python3 /path/to/my-workflow-0.10.0/scripts/adopt.py apply /path/to/target-project --layers core
python3 /path/to/my-workflow-0.10.0/scripts/adopt.py status /path/to/target-project
```

Use `core` for the operating loop and Bun tooling. Use `full` for parallel execution, quality and QA
skills, and optional Ponytail utilities; selected layers are cumulative, and every non-core layer
includes `core`. `full` installs capabilities but does not mandate every stage; the task classifier
selects the work. Adoption requires Python 3. Bun 1.4.x is needed only for source-pack tooling, not
adoption itself. Use the same target and `--layers` value with `plan` and `apply`; `status` reads
installed layers from the manifest and takes no layer selector.

After the first apply, immediately fill the consumer-owned `docs/product/AGENT-CONTEXT.md` with the
product identity, critical constraints, and routes to existing files or headings. Do not create empty
brand, design, or architecture files. Task-specific routes beat role defaults: visual polish reads
design/accessibility (for example, a button color), customer copy reads voice, a planner reads the
overview plus affected capabilities, and an implementer reads its approved task plus applicable
architecture/design. Narrow context never bypasses safety, permission, QA, or review requirements.

Start here: **[docs/workflow/](docs/workflow/)** — an index of every stage, guideline, and choice.

## Purpose

| Delivery | Reliability |
| --- | --- |
| Auto-sized planning (one line needs no spec) | Tests assert spec outcomes, not the implementation |
| Proportional scoped gate; full gate only when selected | Never weaken a test to go green |
| Nitpicks become filed issues, not extra rounds | Blocker and Major still hold the ship |
| `ponytail` at `full` — shortest code that works | Security surfaces declared and given `SEC-` ids |
| `autonomous` scopes remote delivery | Its invocation authorizes the feature-branch push, one pull request, and merge after readiness is rechecked; readiness is evidence, not authorization for deploy/release, production mutations, force-push, direct `main` push, or unrelated remote actions |

The loop, the caps, and the guidelines are the mechanism. The tour explains **why** each exists.
`AGENTS.md` is what agents run.

## Current workflow

Use plain intent in the request:

- “Visual polish / UI-only correction; I am doing manual QA” keeps adjustments to colors, spacing,
  typography, alignment, borders, and layout on the narrow inspect → implement → targeted check →
  commit path when behavior stays unchanged.
- “Feature” starts the smallest spec and slice route that fits the behavior. “Cross-feature” sets a
  broader mapping floor. A neutral Linear `issue` is classified from its concrete outcome, not its
  label.
- Documentation maintenance, agent-instruction changes, and mixed executable changes automatically
  use proportional checks from `GATES.md`. Named risk or changed public behavior selects stronger
  evidence. Confirmed deep-review defects are fixed inside their run; cosmetics become follow-up work.

The feature path is Specify → optional Design/Tasks → Execute. Each task uses its selected checks
and an atomic commit. Technical verification, deep review, QA, and the full gate are selected by
the changed behavior and concrete risk; installing their skills does not make every stage mandatory.

For UI work, Designer starts with constraints, reads selected references, and inspects existing
components read-only. A design tool or isolated prototype supports exploration when useful. Three
alternatives apply when a new screen or meaningful redesign leaves an actual design choice open;
existing patterns handle bounded compositions. One exploration and one refinement is the default.
Human visual acceptance is recorded only after the human confirms it.

The shared workflow stays in `AGENTS.md`. Keep the product index short and point to existing
documents, for example:

```markdown
## Critical constraints
- [Only the project constraints every task must see.]

## Role/task routes
| Role or task | Read only |
| --- | --- |
| Visual polish | docs/design/SYSTEM.md#tokens-and-accessibility |
| Customer-facing copy | docs/brand/VOICE.md |
| Feature planning | docs/product/OVERVIEW.md and affected journey references |
| Implementation | Assigned spec/task and the relevant architecture sections |
```

These paths are examples: replace them with real files and headings in your project. A visual-polish
task does not load the voice guide or all product journeys merely because those documents exist.
Project-specific operational rules, such as Linear routing and environment setup, can live in
separate references selected by the matching task.

## Credits and provenance

This workflow is maintained by Antonio Fulgêncio. The process builds on work from the following
authors and communities:

- Tech Leads Club: the adapted [`workflow-spec-driven`](.agents/skills/workflow-spec-driven/SKILL.md),
  based on [`tlc-spec-driven`](https://github.com/tech-leads-club/agent-skills/tree/main/skills/tlc-spec-driven),
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

Copy the loop, not the product. New projects use the shared `AGENTS.md` pointer and receive a neutral,
consumer-owned `docs/product/AGENT-CONTEXT.md` index; fill its identity and routes with existing
project references instead of copying this source pack's profile. Existing projects preserve their
filled product paragraph and product-owned documentation. For a legacy `AGENTS.md`, extract product
rules into that index before deliberately replacing older prose; adoption never infers or performs
that migration.

Choose a fixed capability layer. `core` contains the operating loop and Bun tooling, `parallel`
adds assisted slice execution, `quality` adds review and QA skills, and `extras` adds optional
Ponytail utilities. Selecting `parallel`, `quality`, or `extras` automatically includes `core`;
`full` resolves all four layers. Planning is read-only and should precede
every apply:

```bash
python3 scripts/adopt.py plan /path/to/target-project --layers core --json
python3 scripts/adopt.py apply /path/to/target-project --layers core
python3 scripts/adopt.py status /path/to/target-project
```

This release changes only this source pack's shared `AGENTS.md` and managed workflow files. Updating
an existing consumer remains a separate adoption step. Start that update from a clean dedicated
branch; adoption preserves unknown consumer files and aborts before writing when it finds conflicts.

Add capabilities later with another apply; installed layers are cumulative and omitted layers are
never removed. `--skip-agents` preserves both instruction files byte-for-byte and skips local-config
initialization and packet synchronization. Without it, adoption appends managed `core`, `parallel`,
and `quality` blocks while preserving consumer prose. A differing
managed file or unowned destination is reported as a conflict and causes zero writes.

### Resolve a legacy no-manifest conflict

For an existing project copied from an older workflow release, run `plan` first. If it reports
conflicts and the target has no `.my-workflow/adoption.json`, review each path and move any product
customization into the target's product-owned documentation or code. Commit that clean baseline,
then authorize every reviewed file conflict explicitly:

```bash
python3 /path/to/my-workflow/scripts/adopt.py resolve /path/to/target-project \
  --layers parallel \
  --replace tools/resource_lock.py \
  --replace tools/qa_parallel_pilot.py \
  --skip-agents
python3 /path/to/my-workflow/scripts/adopt.py status /path/to/target-project
```

Use one `--replace` for each reviewed file conflict, and usually pass `--skip-agents` when the
target has product-specific `AGENTS.md` or `CLAUDE.md` instructions. There is no `--replace-all`.
Altered managed instruction blocks remain manual conflicts. Once an adoption manifest exists,
resolve is no longer available: use `status`, `apply`, and manual resolution for managed-file
drift.

### Serialize only contested test resources

The `parallel` layer installs the dormant `tools/resource_lock.py` wrapper. Activation is explicit:
adoption does not rewrite a consumer command or gate. Wrap only a heavy command that shares a
browser, database, container runtime, or other declared resource; unit tests and other light gates
remain concurrent.

For worktrees of the same project, use the default project scope:

```bash
python3 tools/resource_lock.py run \
  --resource browser \
  -- python3 -m pytest tests/e2e
```

To serialize that resource across separate projects on one machine, opt into machine scope:

```bash
python3 tools/resource_lock.py run \
  --resource browser --scope machine \
  -- python3 -m pytest tests/e2e
```

The wrapper holds the named lock only for the wrapped command and passes its arguments directly.
Run `python3 tools/resource_lock.py run --help` for the authoritative flags, defaults, and result
codes.

The old positional `adopt.py TARGET` command is intentionally removed. `plan` and `apply` require
`--layers`; `status` reports clean state with exit 0, drift with exit 1, and invalid state or
invocation with exit 2.

Prerequisites: the target directory must already exist, and `adopt.py` requires Python 3. Adoption
does not require a Git `HEAD`. Before running the workflow-config resolver, the target must be a Git
repository with at least one commit. Bun 1.4.x is the JavaScript/TypeScript runtime for this pack;
it is needed only to validate the source pack's gates, not to adopt it.

Adoption is a review before it is a command. [`docs/adoption-prompt.md`](docs/adoption-prompt.md)
carries the prompt for the read-only inspection, adoption command, and diff review.

Feature workflow state follows the [artifact lifecycle](docs/guidelines/ARTIFACT-LIFECYCLE.md) and
remains visible to Git. Adoption removes only the exact legacy `.specs/features/` ignore line,
including duplicates, preserves consumer-owned lines and comments, and never stages or commits
files.

The tracked `.my-workflow.toml.example` documents the complete v3 matrix and `mixed` profile. Each
checkout owns an ignored `.my-workflow.toml`, initialized from that example by adoption without
`--skip-agents` or by explicit sync;
it is the single editable source for all Claude, Codex, and Cursor model and effort choices. The
tracked `templates/agents/` trees hold canonical instruction bodies, while sync generates the
ignored native runtime packets. Re-adoption preserves an existing local config byte-for-byte and
regenerates runtime packets from the templates and that config when `--skip-agents` is not used.
With `--skip-agents`, sync is an explicit later operator step.

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --sync-agents
```

Edit the `[models.<provider>.<role>]` tables in the local `.my-workflow.toml`, then run the explicit
sync command. If the local file is missing, sync validates and copies
`.my-workflow.toml.example` first. It reports changed and unchanged runtime packet paths and is
idempotent. Native `model`, `effort`, and `model_reasoning_effort` fields are generated output; do
not edit runtime packets manually. Runtime edits are disposable; edit tracked templates when
changing instruction bodies.

The `cadence` controls the deep-review groups:

- `slice`: one group per slice (`1, 2, 3, 4` → `[1] [2] [3] [4]`).
- `feature`: one group for the whole feature (`1, 2, 3, 4` → `[1, 2, 3, 4]`).
- `grouped.N`: consecutive, balanced groups with at most `N` slices (`grouped.3` with four
  slices → `[1, 2] [3, 4]`).

Post-cap remediation is bounded by `[remediation] stall_attempts`. It defaults to `3`; `0` means
unbounded. The threshold is read from the current local config on every attempt and is not stored
in the feature snapshot:

```toml
[remediation]
stall_attempts = 3
```

After each remediation attempt, the scoped gate produces a normalized, sorted failing-test
signature. A strictly smaller failing-test set resets the stall counter; an equal-size or larger
set increments it, including when membership changes. A reached nonzero threshold halts with the
signature, attempt count, and fixes tried. An unavailable gate halts immediately. The review cap
never opens a third deep-review round.

The resolver uses the native provider for every role unless a named profile or role override is
selected. Precedence is `CLI override > profile > native provider`:

When a feature has `tasks.md`, the resolver validates its vertical-slice closure table and derives
the slice count from merge-alone outcomes. A feature without `tasks.md` uses one slice. `--slices`
is an optional assertion against that derived count during initial resolution or refresh; it is not
the source of truth.

```bash
# Native route: all roles use Codex.
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-native \
  --native-provider codex

# Named profile: use the [profiles.mixed] routes from .my-workflow.toml.
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-profile \
  --native-provider codex --profile mixed

# Role overrides win over both the selected profile and the native provider.
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-override \
  --native-provider codex --profile mixed \
  --override deep_reviewer=cursor --override verifier=claude
```

The first resolution freezes the effective route and cadence in
`.specs/features/<feature>/workflow.json`, including model and effort for every delegated role.
Planner is synchronized but remains the top-level session, not a delegated snapshot role. On
resume, the snapshot is authoritative and packet metadata must still match its frozen model and
effort. If it differs, synchronize packets and explicitly refresh; ordinary resume will fail:

```bash
python3 .agents/skills/workflow-config/scripts/workflow_config.py \
  --root /path/to/target-project --feature register-user-refresh \
  --native-provider codex --refresh
```

The complete contract is in the
[workflow-config skill](.agents/skills/workflow-config/SKILL.md).

## Update an adopted project

Start from a clean tree and a dedicated update branch. Read the changelog since the version the
project adopted, plan the smallest layer update, then inspect the complete diff before committing:

```bash
cd /path/to/target-project
git status --short
git switch -c chore/update-my-workflow
python3 /path/to/my-workflow/scripts/adopt.py plan . --layers full
python3 /path/to/my-workflow/scripts/adopt.py apply . --layers full --skip-agents
git diff
```

Use `--skip-agents` when the target has product-specific instructions. It preserves `AGENTS.md` and
`CLAUDE.md`, skips local-config initialization and packet sync, and leaves managed instruction blocks
for manual merge. Read
[`CHANGELOG.md`](CHANGELOG.md) between the adopted version and the current package version before
accepting the update. Apply is additive: it does not remove an installed layer or consumer file.

Each release lists its upgrade steps under `### Migration` in the changelog; follow them in order
after `apply`. Templates install only when the directory is missing, so merge template changes by
hand while retaining customizations, then run the explicit sync command. Without `--skip-agents`,
apply performs normal sync; with it, local config and packets stay untouched until you sync later.
The roadmap's deterministic installer (`docs/workflow/roadmap.md`) is the planned replacement for
manual template merging.

## Managed paths

Review the managed paths and the plan's per-file actions. Adoption updates only workflow-owned files, preserves unknown
consumer files, creates missing `docs/qa/README.md`, `tools/ad-index.py`, `.my-workflow.toml.example`,
and `templates/agents/`, and records ownership in `.my-workflow/adoption.json`. It never removes an
installed layer or consumer file. Product documentation, `.specs/`, `package.json`, `bun.lock`, and
an existing local `.my-workflow.toml` remain consumer-owned.

The local config is the source for generated provider packets. Adoption preserves an existing
`.my-workflow.toml` and installs tracked templates when missing. Without `--skip-agents`, apply runs
`--sync-agents`; sync creates the local config when absent and regenerates or overwrites the ignored `.claude/agents/`,
`.codex/agents/`, and `.cursor/agents/` packets from the templates and config. Edit the config or
tracked templates, not generated runtime packets.

## Troubleshooting

**`conflict` in a plan or apply.** Review every listed path. Restore an owned file to its recorded
hash or resolve an unowned collision, then run the plan again. Apply is all-preflight: no selected
file or manifest is written while any conflict remains.

**`refusing adoption: Makefile:N uses machine-global workflow skill path`** Point the target's gate at
the vendored `.agents/skills/workflow-spec-driven/scripts/...` path.

**Claude skill symlinks point nowhere.** Re-run `apply --layers ...`; it recreates the `.claude/skills/`
links into `.agents/skills/`.

**A runtime packet has the wrong model or effort.** Edit the local `.my-workflow.toml`, then run
the documented `workflow_config.py --sync-agents` command. Runtime packets are generated output.

## Optional integrations

The workflow stays stack- and tool-agnostic. Optional capabilities can improve a stage when
available:

- **Graft** can enrich deep-review context; absence or failure falls back to repository inspection.
- **OpenDesign** can support visual iteration; the repository stores only the approved handoff, and
  absence or failure falls back to normal repository artifacts.

No integration is mandatory or installed by adoption. Keep daemon, port, CLI and version details in
the relevant integration documentation.

The adopter merges workflow-owned ignore entries, copies missing example/templates, generates
local runtime packets, and records per-file ownership in `.my-workflow/adoption.json`. It preserves
consumer prose through managed blocks, never removes an installed layer, and leaves package
metadata, local config, and unknown files untouched. Always review the plan and resulting diff
before accepting managed-path updates.
Adoption itself does not install external security skills. It prints the exact command for the
separate authorized step and leaves the security gate uncovered until that command succeeds.

## Skills

Canonical copies live in `.agents/skills/`. Claude Code gets symlinks in `.claude/skills/`. Cursor,
Codex and OpenCode consume `.agents`. Do not add `.cursor/skills` or other agent trees. The
project-owned `qa-plan` and `qa-execute` skills use the consuming project's profile in
`docs/qa/README.md`; they do not select a framework or replace the project's gate.

`adopt.py` installs and updates only the workflow-owned `workflow-spec-driven` router, its five
phase skills (`wspecify`, `wdesign`, `wtasks`, `wimplement`, `wverify`), Ponytail, Deep
Review, QA, workflow-config, and autonomous skills. Keep those canonical copies in
`.agents/skills/` and the Claude Code
symlinks in `.claude/skills/`. The three external security skills are a separate authorized step:

```bash
python3 /path/to/my-workflow/scripts/install_security_skills.py \
  /path/to/target-project --yes
```

The installer uses only the reviewed refs and hashes in `skills-lock.json`; it does not resolve
`latest` or perform automatic updates. Review its printed plan and authorize the command before
running it. Until it succeeds, do not treat the security gate as covered.

`autonomous` is vendored here. `CLAUDE.md` is the one line `@AGENTS.md` (not a symlink). Canonical
packet templates live under `templates/agents/{cursor,claude,codex}/`; generated implementer,
explorer and verifier runtimes live under the ignored `.cursor/agents/`, `.claude/agents/` and
`.codex/agents/` directories.

## Knowledge checker

These are optional source-pack maintainer checks, not adoption or consumer task gates.

```bash
bun install --frozen-lockfile
bun run test:all
bun run knowledge
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
