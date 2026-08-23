# CH-bound-remediation-stall-2026-08-23

- **Date:** 2026-08-23
- **Time-box:** 25 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Tour:** Configuration surface — the new key, its validation, and the snapshot boundary
- **Public entry point:** `.my-workflow.toml` → `python3 .agents/skills/workflow-config/scripts/workflow_config.py`
- **Adapter candidate:** CLI/manual, against a checkout-local disposable Git repository
- **Scenarios:** `CFG-bound-remediation-stall-attempts`, `CFG-freeze-feature-workflow`

## Mission

Adopt `[remediation] stall_attempts` as a project owner would: read the three surfaces that document
it, then drive the resolver through every value the documentation promises to accept and every one it
promises to reject by name. Then resume a frozen feature and confirm the threshold — and only the
threshold — moves.

## Expected observable

The resolver exits `0` and its JSON stdout reports the intended `remediation.stall_attempts` for a
declared value, an absent file, an absent table, an empty table, and `0`; it exits non-zero naming
`remediation.stall_attempts` or the unknown key for every malformed input, writing no snapshot on a
fresh resolve. `.specs/features/<slug>/workflow.json` never contains a `remediation` key, and a
resume echoes the frozen routing fields unchanged while reporting the current threshold.

## Fixture

Create the disposable target inside this checkout, following the pattern owned by
[`tools/test_workflow_config.py`](../../../tools/test_workflow_config.py): a temporary directory with
`.claude/agents/`, `.codex/agents/` and `.cursor/agents/` populated for every role, `git init`, a
seed commit. Remove it at the end of the session. Never resolve against the source checkout.

## Planned probes

1. **Documented default agrees across all three surfaces.** Read `README.md` (`[remediation]` block),
   `.agents/skills/workflow-config/SKILL.md` (`## Remediation stall bound`), and
   `.my-workflow.toml.example`. Each must state the key, the default `3`, `0` as unbounded, and the
   shrink rule, and must cite `docs/guidelines/REVIEW-ROUNDS.md` rather than restate the rule.
2. **Absent config → `3`.** Resolve a feature in the fixture with no `.my-workflow.toml`.
3. **Absent table → `3`.** Add a `.my-workflow.toml` carrying only `[deep_review]`, resolve a new
   feature slug.
4. **Empty table → `3`.** `[remediation]` with no keys.
5. **Declared value.** `stall_attempts = 5` → stdout reports `5`.
6. **Unbounded.** `stall_attempts = 0` → exit `0`, stdout reports `0` (not rejected, not coerced).
7. **Non-integer rejected.** `stall_attempts = "3"`, then `stall_attempts = true` → exit non-zero,
   stderr names `remediation.stall_attempts`. `true` matters: a bool is an `int` subclass.
8. **Negative rejected.** `stall_attempts = -1` → exit non-zero naming `remediation.stall_attempts`.
9. **Unknown key rejected by name.** `[remediation] attempts = 3` → exit non-zero naming `attempts`.
10. **Not frozen.** After a successful resolve with `stall_attempts = 5`, read
    `.specs/features/<slug>/workflow.json` — no `remediation` key present.
11. **Resume is inert to an unrelated edit.** Add an invalid top-level key to `.my-workflow.toml`,
    resume the already-frozen feature → exit `0`, snapshot fields echoed unchanged.
12. **Resume still fails closed on this table.** Set `[remediation] stall_attempts = -1`, resume →
    exit non-zero naming `remediation.stall_attempts`.
13. **Resume fails on unparseable TOML.** Corrupt the file so `tomllib` cannot parse it, resume →
    exit non-zero.
14. **Threshold reaches a resume.** Change a valid `5` to `7`, resume → stdout reports `7` while the
    routing fields are unchanged.
15. **Fresh resolve validates the whole config.** No snapshot, invalid top-level key → exit non-zero
    naming the key, and no `workflow.json` written.

Record each command, its exit code, and the relevant stdout/stderr line under
`docs/qa/evidence/2026-08-23-stall-based-halt/`. Confirm the source checkout's `git status` carries
only this cycle's durable QA artifacts and that the disposable target is gone.

End before any product fix, guideline edit, or remote action.
