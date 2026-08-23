# Adoption prompt

Paste this once to an agent, replacing the pack and target paths. It runs the read-only review that
must precede `adopt.py`, then the script, then the diff review.

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
record `no user-visible change` and do not run QA. Activate `tlc-spec-driven`. At the start of
workflow work, activate `ponytail` at `full`; `AGENTS.md` carries the full-cycle session rule and
the explicit stop commands.
```

For an update of an already-adopted project, replace the first paragraph with the target's current
pack version and ask the agent to read the pack's `CHANGELOG.md` between that version and `HEAD`
before writing.
