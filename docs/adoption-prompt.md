# Adoption prompt

Paste this once to an agent, replacing the pack and target paths. It runs the read-only review that
must precede `adopt.py`, then the adoption command and diff review.

```
Adopt selected layers of the agent OS from /path/to/my-workflow into /path/to/target-project.

First check `git status --short`; do not stash, reset, clean, or hide unrelated changes. Read the
pack's README.md, AGENTS.md, and adoption script. Inspect the target read-only: package and build
manifests, declared gates, CI jobs, production-parity start and health paths, public interfaces,
authentication, fixtures or seed data, cleanup and residue checks, and installed QA tooling. Never
invent a command or install a QA framework during adoption.

Before writing, set `<selected-layers>` to the requested fixed layers (`core`, `parallel`, `quality`,
`extras`, or `full`). Run `python3 /path/to/my-workflow/scripts/adopt.py plan /path/to/target-project --layers <selected-layers> --json` and review its actions. Report the managed paths and every target path that could be replaced. Preserve
product-owned product, architecture, design, and stack documentation. For a new project, adoption
initializes a neutral, consumer-owned `docs/product/AGENT-CONTEXT.md` index; fill it with product
identity and routes to existing docs only as the product earns them. For an existing project,
preserve its filled product paragraph. Before deliberately replacing a legacy `AGENTS.md`, extract
its product rules into that index and review the complete diff; adoption does not infer or perform
that migration. Use `--skip-agents` when the product paragraph is filled; it preserves `AGENTS.md`
and `CLAUDE.md`, so merge workflow instruction changes manually. Preserve an existing local
`.my-workflow.toml` byte-for-byte. Install missing `.my-workflow.toml.example` and
`templates/agents/`. Without `--skip-agents`, apply then runs `--sync-agents` to generate ignored
provider packets from tracked templates and local config; sync may overwrite generated packets.
With `--skip-agents`, local config initialization and packet sync are skipped; run explicit sync later.

If the plan reports conflicts and the target has no `.my-workflow/adoption.json`, review every
conflict and move product customizations into product-owned files. Commit that clean Git baseline,
then run `python3 /path/to/my-workflow/scripts/adopt.py resolve /path/to/target-project --layers <selected-layers> --replace <reviewed-file> [--replace <reviewed-file> ...]`, usually with
`--skip-agents` for an existing product paragraph. Use one `--replace` for every current file
conflict. There is no `--replace-all`; altered managed instruction blocks stay manual. Run
`status` after resolve. Once `.my-workflow/adoption.json` exists, use normal `status` and `apply`
plus manual resolution for managed-file drift.

Read the pack's `CHANGELOG.md` from the target's adopted version to the current package version
before an update. Run `python3 /path/to/my-workflow/scripts/adopt.py apply /path/to/target-project --layers <selected-layers>` only
after the review. Use the same `<selected-layers>` value in plan and apply; `full` selects all four.
For a filled product paragraph, pass `--skip-agents`; merge managed instructions and run the target's
explicit `--sync-agents` command later after installing or merging example/templates.

If `docs/qa/README.md` is absent, create it when `quality` is selected. If it exists, merge only newly discovered facts into
the existing profile; never overwrite existing content. Record the discovered interfaces, existing
runner or manual adapter, start and health authority, authentication, fixtures, cleanup, and
limitations. Keep command facts in the target's executable manifests or CI and link to them from
the profile.

Apply is additive and has no removal mode. It unions requested layers with installed layers. A
managed-file drift, unowned differing destination, malformed manifest, or unsafe symlink aborts
before any target write and lists every conflict. Use `status` afterwards; exit 0 means clean, 1
means drift, and 2 means invalid invocation or state.

Review the complete diff, managed-path overwrites, and the target's declared full gate as a candidate
check. Apply the proportional classifier in the adopted `docs/guidelines/GATES.md`: pure maintenance
uses accuracy/link/heading/whitespace checks, instruction changes use consistency plus existing
relevant contract checks, and mixed changes use canonical checks for changed executable behavior.
Record selected commands, results, and any named risk. Send fresh `qa-plan` and `qa-execute` packets
only when the classifier selects a public walk. For a purely internal refactor, record `no user-visible change` and do not run QA; otherwise record the narrow limitation. Preserve risk-based checks for
adoption, auth, data, and public interfaces. Activate `workflow-spec-driven`. At the start of
workflow work, activate `ponytail` at `full`; `AGENTS.md` carries the full-cycle session rule and the
explicit stop commands.
```
