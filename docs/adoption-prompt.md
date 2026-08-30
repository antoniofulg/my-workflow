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

Before writing, run `python3 /path/to/my-workflow/scripts/adopt.py plan /path/to/target-project --layers core --json` and review its actions. Report the managed paths and every target path that could be replaced. Preserve
product-owned product, architecture, design, and stack documentation. For a new project, replace
the AGENTS.md product stencil and create product docs only as the product earns them. For an
existing project, use `--skip-agents` when the product paragraph is filled; it preserves `AGENTS.md`
and `CLAUDE.md`, so merge workflow instruction changes manually. Preserve an existing local
`.my-workflow.toml` byte-for-byte. Install missing `.my-workflow.toml.example` and
`templates/agents/`, then run `--sync-agents` to generate the ignored provider runtime packets
from the tracked templates and local config; sync may overwrite those generated packets.

Read the pack's `CHANGELOG.md` from the target's adopted version to the current package version
before an update. Run `python3 /path/to/my-workflow/scripts/adopt.py apply /path/to/target-project --layers core` only
after the review. Add `parallel`, `quality`, or `extras` explicitly as needed; `full` selects all four.
For a filled product paragraph, pass `--skip-agents`. Adoption also runs the
target's explicit `--sync-agents` command after installing missing example/templates.

If `docs/qa/README.md` is absent, create it when `quality` is selected. If it exists, merge only newly discovered facts into
the existing profile; never overwrite existing content. Record the discovered interfaces, existing
runner or manual adapter, start and health authority, authentication, fixtures, cleanup, and
limitations. Keep command facts in the target's executable manifests or CI and link to them from
the profile.

Apply is additive and has no removal mode. It unions requested layers with installed layers. A
managed-file drift, unowned differing destination, malformed manifest, or unsafe symlink aborts
before any target write and lists every conflict. Use `status` afterwards; exit 0 means clean, 1
means drift, and 2 means invalid invocation or state.

Review the complete diff, managed-path overwrites, and the target's declared full gate. Record the
exact gate command and result. If the change exposes a user-visible UI, API, CLI, mobile, public
configuration, adoption, or docs-as-interface promise, send the existing Verifier a fresh
`qa-plan` packet followed by a separate `qa-execute` packet. For a purely internal refactor,
record `no user-visible change` and do not run QA. Activate `workflow-spec-driven`. At the start of
workflow work, activate `ponytail` at `full`; `AGENTS.md` carries the full-cycle session rule and
the explicit stop commands.
```
