# Stall-Based Halt Decisions

## Human decisions

| Choice | Why | Alternatives rejected | Change cost now | User cost today |
| --- | --- | --- | --- | --- |
| Halt on lack of progress instead of on an open blocker | An unattended run kept ending on a diagnosed blocker the operator would always have told to continue | Never halt on a blocker at all; a per-run `--no-halt-on-blocker` flag | Low | A stuck loop now runs longer before reporting |
| Put the threshold in `.my-workflow.toml`, not in the guideline | Projects differ in tolerance, and the resolver's key allowlist had to learn the table either way | Hard-code the default in `REVIEW-ROUNDS.md` | Low | One more consumer-owned key to document |
| Progress is a strictly smaller failing set, measured against the running minimum | Deep-review proved the signature comparison was defeatable by ordinary flaky output, in both directions | Widen the normalization drop-list; add an absolute attempt ceiling | Low | A fix that swaps which tests fail without reducing the count reads as a stall |
| Always branch and open a pull request; never commit to `main` | Stated this session | Local commits on `main` | Low | None |

## Run decisions

| Choice | Why | Alternatives rejected | Change cost now | User cost today |
| --- | --- | --- | --- | --- |
| Record `AD-007` and amend it twice rather than open `AD-008` | One decision changed shape under review; its history belongs in one entry | A new AD per revision | Low | The AD body carries three formulations, only the last active |
| Keep `stall_attempts` out of `workflow.json` | The snapshot freezes routing so a resumed feature stays stable; a halt threshold is an operator preference that should apply on the next attempt | Freeze it with the routing | Low | The resolver parses `.my-workflow.toml` twice on the CLI path |
| Split `_load_toml` / `_validate_remediation` out of `_read_config` | Reusing the full-validation helper regressed the documented resume contract for every in-flight feature | A `validate=False` parameter on `_read_config` | Low | Two small helpers where there was one |
| Cite the rule from `autonomous/SKILL.md` instead of restating it | The rule changed three times; the skill needed no edit on any of them | Restate the threshold where it is used | Low | A reader must follow one pointer |
| Extend `IT-026` to sweep `docs/workflow/*.md` read from disk | The same stale rule reached four surfaces; a hardcoded file list would miss the fifth | Fix the fourth occurrence only | Low | None |
| Did not re-dispatch a Verifier after the slice-1 doc remediation | Two reworded sentences, gate green, and the fix was pinned by a test proven to fail without it | A full verification round | Low | One remediation closed on the author's evidence plus a proven test |
| Left `paralelizacao.md` untracked | Unrelated to this feature and not ours to stage | Commit or delete it | Low | None |

## Known follow-ups, not fixed here

- `scripts/test_adopt.py:451` shells out to the `rg` binary. No document declares that prerequisite, so
  the suite cannot run on a machine without it. Reproduced on a clean clone of `main`, so it predates
  this feature.
- `docs/workflow/reviews.md` says "each attempt shrinks the failing-test set" where the guideline says
  strictly smaller than the fewest seen so far. It routes to the owning section, so no surface carries a
  divergent rule.
- `DOC-halt-remediation-only-on-a-stall`'s `entry_points` omits `docs/workflow/reviews.md`, the surface the
  drift landed on. A `qa-plan` edit.
- `_validate_remediation` runs twice on a fresh resolve, and `.my-workflow.toml` is parsed twice there.
- The round caps `≤3` and `≤2` are asserted by no test.
- Integration test IDs have no collision registry; this feature hit one and resolved it by hand.
- `REVIEW-ROUNDS.md` sits at 158 lines against an asserted ceiling of 160.
- Index-based heading slicing in `qa-skills.test.ts` breaks if a heading name is backtick-quoted in prose.
