# QA Execute — stall-based-halt — 2026-08-23

- **Branch / HEAD:** `feat/stall-based-halt` @ `c841207`
- **Phase:** `qa-execute` (fresh Verifier; neither the plan nor the code was written in this session)
- **Adapters:** CLI/manual — the `workflow-config` resolver against a checkout-local disposable Git
  repository; manual repository inspection for the documentation surfaces. Both are the adapters
  declared by `docs/qa/README.md`. No framework installed, no command invented.
- **Automated gate:** `npm test` → `vitest run --dir tools` → **8 files, 113 tests passed, exit 0**
  (run before the first charter).
- **Evidence:** `docs/qa/evidence/2026-08-23-stall-based-halt/` (gitignored, disposable)
- **Fixture:** `docs/qa/evidence/2026-08-23-stall-based-halt/fixture` — built to the
  `tools/test_workflow_config.py` `make_repo()` pattern, removed at close, residue asserted zero.

## Scenario matrix

| Scenario | Prior | Verdict | Evidence |
| --- | --- | --- | --- |
| `CFG-bound-remediation-stall-attempts` | untested | **pass** | `docs/qa/evidence/2026-08-23-stall-based-halt/resolver-session.md` |
| `CFG-freeze-feature-workflow` | untested (reset) | **pass** | `docs/qa/evidence/2026-08-23-stall-based-halt/resolver-session.md` |
| `DOC-halt-remediation-only-on-a-stall` | untested | **fail** — `BUG-20260823-workflow-tour-states-retired-halt-rule` | `docs/qa/evidence/2026-08-23-stall-based-halt/halt-rule-session.md` |
| `DOC-require-explicit-remote-action-approval` | pass | **pass** (canary reconfirmed) | `docs/qa/evidence/2026-08-23-stall-based-halt/halt-rule-session.md` |

**23 probes run, 22 passed, 1 failed.** No probe was skipped and none was left untested.

## CH-bound-remediation-stall-2026-08-23 — 15 probes, 15 pass

Journey `J-configure-feature-workflow`, persona Workflow adopter, entry point `.my-workflow.toml` →
the resolver CLI.

| # | Probe | Result |
| --- | --- | --- |
| 1 | Documented default agrees across the three surfaces | pass, with a divergence recorded below |
| 2 | Absent config → `3` | pass — exit 0, `"remediation": {"stall_attempts": 3}` |
| 3 | Absent `[remediation]` table → `3` | pass — exit 0, `3` |
| 4 | Empty `[remediation]` table → `3` | pass — exit 0, `3` |
| 5 | `stall_attempts = 5` | pass — exit 0, `5` |
| 6 | `stall_attempts = 0` unbounded | pass — exit 0, reported as `0`, neither rejected nor coerced |
| 7 | Non-integer rejected (`"3"`, then `true`) | pass — exit 1 both times, stderr names `remediation.stall_attempts`; the bool is rejected despite being an `int` subclass |
| 8 | Negative rejected | pass — exit 1, names `remediation.stall_attempts` |
| 9 | Unknown key rejected by name | pass — exit 1, `remediation contains unknown key 'attempts'` |
| 10 | Not frozen | pass — `p5/workflow.json` keys are `deep_review, feature, git_head, overrides, profile, roles, version`; no `remediation` |
| 11 | Resume inert to an unrelated invalid edit | pass — exit 0, snapshot fields byte-identical to baseline, threshold reported |
| 12 | Resume still fails closed on this table | pass — exit 1, names `remediation.stall_attempts` |
| 13 | Resume fails on unparseable TOML | pass — exit 1, `invalid .my-workflow.toml: Expected ']' …` |
| 14 | Threshold change reaches a resume | pass — `5` → `7` reported on resume, routing fields unchanged |
| 15 | Fresh resolve validates the whole config | pass — exit 1 naming `'bogus'`, and no `workflow.json` written |

Independent read path: every rejection was followed by a filesystem check confirming no snapshot was
created, and the frozen `p5/workflow.json` was re-read from disk after all four resume probes and
compared byte-for-byte against the baseline captured at probe 5.

**Divergence on probe 1 (non-blocking, no bug filed).** `README.md:101-108` and
`.agents/skills/workflow-config/SKILL.md:30-39` each state the key, the shrink rule, default `3` and
`0`-as-unbounded, and each cites `docs/guidelines/REVIEW-ROUNDS.md` as the definition.
`.my-workflow.toml.example:6-10` states the same four facts but carries no pointer to the guideline,
so a reader who stops there gets the summary "attempts that do not shrink the failing set" without
the running-minimum definition that distinguishes it from the formulation retired mid-feature. No
retired default appears on any of the three surfaces, so the scenario's promise holds; this is a
`Minor` documentation observation for the follow-up list, not a defect that blocks the journey.

## CH-halt-on-stalled-remediation-2026-08-23 — 8 probes, 7 pass, 1 fail

Journey `J-run-deep-review`, persona Workflow operator, entry point `docs/guidelines/REVIEW-ROUNDS.md`
`## Escalation`. The charter's **Declared limitation** applies and was honoured: no agent-execution
harness exists, so no live unattended run was driven to the cap. The published surface for this
promise is the instruction text, which was walked in full; nothing is deferred to a session that
could do more, so no leg is `untested` or `blocked-verify` on that account.

| # | Probe | Result |
| --- | --- | --- |
| 1 | The rule is stated once, with the signature definition | pass |
| 2 | Progress is the running minimum, not the previous attempt | pass — same count, larger, and different-set-same-size are all named as stalls |
| 3 | The halt names what the operator needs | pass — `stall_attempts`, default `3`, `0` unbounded, unrunnable gate, and the four report contents |
| 4 | Round caps untouched | pass — ≤3 fix rounds, ≤2 deep-review rounds, "No new review round opens past a cap" |
| 5 | Rule 2 points, does not fork | pass — routes to the escalation section, states no second threshold |
| 6 | **The retired formulation survives nowhere** | **FAIL** — see below |
| 7 | The skill cites rather than restates | pass — `.agents/skills/autonomous/SKILL.md:176` names the stall and cites the guideline, carrying no copy of `stall_attempts` or the default |
| 8 | **Canary — the remote boundary** | pass — unchanged and intact |

### Probe 6 — defect

`docs/workflow/reviews.md:67`:

> Escalate only when the post-fix gate fails or a blocker remains reproducible at the cap.

This is the retired formulation, verbatim, on a surface `scripts/adopt.py` installs into every
consuming project. The word "only" positively excludes the stall rule this feature introduced, and
the file names neither `stall_attempts` nor the failure signature. `git diff --stat main...HEAD`
shows `docs/guidelines/REVIEW-ROUNDS.md` `## Escalation` was rewritten in this branch while
`docs/workflow/reviews.md` was not, so the two installed surfaces now state different halt
conditions for the same event. Filed as
`docs/qa/bugs/BUG-20260823-workflow-tour-states-retired-halt-rule.md`, severity `major`.

The existing negative guards (`tools/shared/tests/qa-skills.test.ts:805` and `:839`) assert only over
`docs/guidelines/REVIEW-ROUNDS.md` and the `autonomous` halt-conditions block; nothing in the gate
reads `docs/workflow/*`, which is where the drift landed. That gap is named in the bug's smallest
remediation.

`docs/workflow/purpose.md:38-39` was inspected and **not** filed: "Shipping past a cap with a
reproducible blocker is not [a result]" is a readiness statement matching
`.agents/skills/autonomous/SKILL.md:181`, not a halt condition. It is recorded in the evidence as
adjacent phrasing to re-read beside the fix.

### Probe 8 — the remote-boundary canary

`.agents/skills/autonomous/SKILL.md` still carries, unchanged: "Readiness is evidence, not
authorization"; "Each remote action needs its own explicit authorization in the current session";
"Never infer authorization for a later action from an earlier one"; and the halt condition "The tree
is ready but the current session does not explicitly authorize the next remote action".
`git diff main...HEAD` over `.agents/skills/autonomous/SKILL.md`, `docs/workflow/`, `AGENTS.md` and
`README.md`, filtered for `push|pull request|merge|deploy|authoriz|remote`, returns **no changed
line**. Nothing in this feature opened a path to a remote action without explicit per-action
authorization. `DOC-require-explicit-remote-action-approval` stays `pass`.

## Cleanup and residue

Disposable fixture removed. Source checkout `git status --porcelain` matches its session baseline
plus this cycle's durable QA artifacts; the pre-existing `?? paralelizacao.md` and
`?? .specs/features/stall-based-halt/validation.md` were present before this session and were not
touched.

## Disposition

**Delivery is blocked by one product defect.**

- `BUG-20260823-workflow-tour-states-retired-halt-rule` (`major`) goes to an **Implementer**. This
  Verifier session closes without touching product code, tests, or guidelines.
- After the fix: a **fresh Verifier** re-runs the technical gate, then resumes `J-run-deep-review`
  from probe 6 plus the probe 8 remote canary, and re-walks `DOC-halt-remediation-only-on-a-stall`.
- `CFG-bound-remediation-stall-attempts` and `CFG-freeze-feature-workflow` need no re-walk unless the
  fix touches the resolver or the configuration surfaces.
- Follow-up list (non-blocking): add the guideline pointer to `.my-workflow.toml.example`'s
  `[remediation]` comment.

No commit, push, pull request, or merge was performed in this session.

## Retest — 2026-08-23

- **Range:** `c841207..a27543c`; fix commit `3dee592`
- **Session:** fresh Verifier, `qa-execute` (retest only). Neither the fix nor the walk above was
  written here. No product code, test, or guideline modified.
- **Scope:** per `docs/guidelines/REVIEW-ROUNDS.md`, only `reviewed_head..HEAD` and the affected
  scenario rows — probes 6, 7 and 8 from `CH-halt-on-stalled-remediation-2026-08-23`.
- **Evidence:** `docs/qa/evidence/2026-08-23-stall-based-halt/retest-session.md` (disposable)
- **Gate:** `npx vitest run --dir tools` → **8 files, 113 tests passed, exit 0**;
  `python3 tools/test_workflow_config.py` → **15 passed, 0 failed**

| # | Probe | Result |
| --- | --- | --- |
| 6 | The retired formulation survives nowhere | **pass** — re-derived, not accepted from the fix's report |
| 7 | The skill cites rather than restates | **pass** — `.agents/skills/autonomous/SKILL.md:177`, no `stall_attempts`, no default |
| 8 | Canary — the remote boundary | **pass** — nothing in the range opened a remote path |

**Probe 6.** The sweep was re-run from the repository root over the whole tree — not the files the
fix touched — and recursively, so the symlinked `.claude/skills/*` trees were read too. Patterns:
`blocker remains reproducible`, `leaves a blocker open`, `reproducible blocker`, `identical failure
signature`, `same failure signature`, `blocker is still`, `still reproducible`. Every hit is a
negative test guard, a QA record quoting the forbidden phrasing, or
`.specs/features/stall-based-halt/validation.md`. **No hit on an installed instruction surface
outside a record.** `docs/workflow/reviews.md:67-70` is now a pointer that names neither the
threshold nor `stall_attempts`. A second sweep for the rule's positive vocabulary (`stall`, `halt`,
`failure signature`) across the installed surfaces confirms the rule is stated once, at
`docs/guidelines/REVIEW-ROUNDS.md:145-147`, and cited elsewhere.

**The extended IT-026 sweep was verified by injection, not by reading.** In a detached
`git worktree` under the scratchpad — never `git stash`, never the real tree — a scratch tour page
`docs/workflow/zz-sensor.md` containing the retired sentence was created, a file named nowhere in
the suite. `npx vitest run --dir tools` returned **1 failed | 112 passed (113)**, failing at
`tools/shared/tests/qa-skills.test.ts:779` inside `IT-026`. The guard's
`readdirSync(join(repositoryRoot, "docs/workflow"))` really does read the directory from disk, so a
tour page added later is swept automatically. Scratch file and worktree removed, `worktree prune`
run.

**`docs/workflow/purpose.md:38-39` judged independently and left alone.** "Escalate is a result
after the required post-cap remediation and gate. Shipping past a cap with a reproducible blocker is
not." The subject is shipping and the predicate is "is not [a result]". It states no trigger, no
"only", and no threshold, and is the same statement as `.agents/skills/autonomous/SKILL.md:182-183`.
It is a readiness statement, not a halt condition. The original walk and the fix were both right to
leave it.

**CFG scenarios confirmed by diff, not re-walked.** `git diff c841207..a27543c` touches
`.my-workflow.toml.example` only as the two-line pointer comment this report's probe-1 divergence
asked for; `.agents/skills/workflow-config/` and its resolver are untouched in the range.
`CFG-bound-remediation-stall-attempts` and `CFG-freeze-feature-workflow` stay `pass`.

**Minor observation, not filed.** `docs/workflow/reviews.md` says "each attempt shrinks the
failing-test set" where the guideline says strictly smaller than the fewest seen so far in the loop.
It routes the reader to the owning section for the condition, so no surface carries a divergent
rule. Same class as the probe-1 observation already on the follow-up list. A second follow-up: the
scenario's `entry_points` does not list `docs/workflow/reviews.md`, the surface the drift actually
landed on — a `qa-plan` edit, not a `qa-execute` one.

### Retest disposition

**Delivery is no longer blocked.**

- `DOC-halt-remediation-only-on-a-stall` → `qa_status: pass`, `fix_status: fixed`,
  `retest_status: pass`, `fix_commits: 3dee592`.
- `BUG-20260823-workflow-tour-states-retired-halt-rule` — fix commit and retest recorded; closed.
- All four scenarios in this cycle's matrix are `pass`. None is `untested`, `fail`, or blocked.
- Non-blocking follow-ups: the `reviews.md` paraphrase above and the scenario `entry_points` gap.

No commit, push, pull request, or merge was performed in this retest session.
