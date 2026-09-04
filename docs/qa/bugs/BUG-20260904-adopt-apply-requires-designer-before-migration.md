# BUG-20260904-adopt-apply-requires-designer-before-migration

- **Status:** open
- **Severity:** major
- **Scenario:** `REL-report-current-workflow-release`
- **Expected:** On a project adopted at 0.8.0, the 0.9.0 changelog Migration step 1
  (`adopt.py apply . --layers <installed layers> --skip-agents`) installs the seven `w*` skills,
  the router, and the `.claude/skills/` links. Designer tables are added only in step 3; packet
  sync is step 4.
- **Observed:** Apply exits `2` with `workflow-config: models.claude.designer is required`. The
  target is unchanged. `plan` for the same arguments exits `0` with `status: ready` and zero
  conflicts, so the preview does not show the apply failure.
- **Adapter:** CLI/manual against a checkout-owned disposable Git consumer
- **Exact path:** local clone of `v0.8.0` `scripts/adopt.py apply <target> --layers full --skip-agents`,
  then `v0.9.0` `scripts/adopt.py plan|apply <target> --layers full --skip-agents` while the
  0.8.0-generated `.my-workflow.toml` still lacks `[models.*.designer]`
- **Evidence:** `docs/qa/evidence/2026-09-04-release-0-9-0/53-090-apply.err`;
  `docs/qa/evidence/2026-09-04-release-0-9-0/52-090-plan.json`;
  `docs/qa/evidence/2026-09-04-release-0-9-0/55-notoml-090-apply.err`;
  `docs/qa/evidence/2026-09-04-release-0-9-0/56-apply-after-tables.out`

## Reproduction

1. Adopt a disposable Git consumer from tag `v0.8.0` with
   `python3 scripts/adopt.py apply <target> --layers full --skip-agents`. That write always
   creates `.my-workflow.toml` from the 0.8.0 example (no designer tables).
2. From tag `v0.9.0`, run
   `python3 scripts/adopt.py plan <target> --layers full --skip-agents --json`. Observe
   `status: ready`, `conflicts: []`, exit `0`, unchanged target hash.
3. Run the documented Migration step 1:
   `python3 scripts/adopt.py apply <target> --layers full --skip-agents`.
4. Observe exit `2`, stderr `workflow-config: models.claude.designer is required`, and an
   unchanged tree (no `w*` skills).

Hiding the local toml, or appending the three `[models.<provider>.designer]` tables from the
0.9.0 example *before* apply, both make apply exit `0`. Those are workarounds, not the
documented order.

## Impact

Every 0.8.0 adopted project has a local `.my-workflow.toml` without designer tables. The
published 0.9.0 Migration tells operators to apply first and add those tables later. Following
the note leaves the upgrade unapplied. `--skip-agents` only skips `AGENTS.md` / `CLAUDE.md`
blocks; apply still runs `_prepare_sync` and `sync_agents` against the consumer toml.

## Remediation recommendation

Make `--skip-agents` skip `_prepare_sync` so apply can install files without rendering runtime
packets, matching the changelog order (apply, copy templates, add designer tables, then
`workflow_config.py --root . --sync-agents`). Keep `plan` and `apply` consistent: a preview
that says `ready` must not be followed by an apply-time ConfigError.

Do not “fix” this by rewriting only the changelog if apply still cannot perform step 1 on a
real 0.8.0 consumer.

Regression check: a disposable 0.8.0-adopted target whose generated toml lacks designer tables
must accept `v0.9.0` `plan` and `apply --layers full --skip-agents` at exit `0` and then
contain the seven `w*` skills. Route to an Implementer; a fresh Verifier retests this journey
plus the adjacent adoption canary.
