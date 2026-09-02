# QA report — merge-alone slice derivation — 2026-09-02

- **Cycle:** feature `merge-alone-slices`, branch `feat/merge-alone-slices`, HEAD `dfdf227`
- **Phase:** `qa-execute` (fresh Verifier; this session did not author the code and changed no product code)
- **Persona:** Workflow adopter
- **Journey:** [`J-configure-feature-workflow`](../journeys/J-configure-feature-workflow.md)
- **Scenario in scope:** [`CFG-derive-merge-alone-slices`](../scenarios/CFG-derive-merge-alone-slices.md)
- **Adapter:** CLI/manual, exactly as declared in [`docs/qa/README.md`](../README.md) — the public
  `workflow_config.py`, `validate_tasks.py --slice-contract-json`, and `parallel_plan.py`
  commands, run inside a disposable Git repository. No framework was installed and no command
  was invented.
- **Exact execution path:** `git archive dfdf227 | tar -x -C <target>` into
  `/Users/antoniofulg/Projects/.qa-merge-alone-2026-09-02` (checkout-owned sibling, the same
  disposable-target pattern the profile records for prior cycles), `git init` + baseline commit
  `6cd3027`, `workflow_config.py --sync-agents` to initialize the local config from
  `.my-workflow.toml.example`, then all probes against `<target>/.specs/features/qa-*`.
  The source checkout's `.specs/` was never resolved against. The target was removed at close.
- **Evidence:** `docs/qa/evidence/2026-09-02-merge-alone-slices/` (gitignored)
- **Report opened:** after the first two CH1 probes and before every remaining probe; the matrix
  rows for CH2–CH4 and all canaries were pending before their walks.

## Automated gate

| Item | Value |
| --- | --- |
| Command | `bun run test:all` |
| Result | `status=0` |
| Load average, before / after | `7.58` / `7.71` (well below the ~20 threshold this box flakes at) |
| Watched flaky suites | `tools/shared/tests/security-skills-installation.test.ts` and `tools/test_parallel_resource_lock.py` both passed in the single run; no isolated re-run was needed |
| Close-out re-run | `bun run test:all` → `status=0` (load `13.12` before / `11.69` after; no product code changed this cycle) |
| Evidence | `evidence/…/00-load-before-gate.txt`, `evidence/…/01-gate-test-all.log`, `evidence/…/91-gate-test-all-close.log` |

## Matrix

| # | Charter / canary | Verdict | Evidence |
| --- | --- | --- | --- |
| CH1 | `CH-derive-merge-alone-slice-count-2026-09-02` | **pass** | `10`–`18` |
| CH2 | `CH-refuse-invalid-slice-contracts-2026-09-02` | **pass** | `20`–`23` |
| CH3 | `CH-freeze-and-refresh-derived-slices-2026-09-02` | **pass** | `30`, `31` |
| CH4 | `CH-consume-derived-slice-membership-2026-09-02` | **pass** | `40`–`44` |
| C1 | canary `CFG-resolve-deep-review-cadence` | **holds** (frozen `pass` not contradicted) | `18-ch1-canary-cadence.log` |
| C2 | canary `CFG-freeze-feature-workflow` | **holds** (frozen `pass` not contradicted) | `31-ch3-canary-freeze.log` |
| C3 | canary `CFG-plan-parallel-slice-dispatch` | **holds** (frozen `pass` not contradicted) | `44-ch4-canary-planner.log` |
| S | scenario `CFG-derive-merge-alone-slices` | **pass** | all of the above |

Evidence file names are prefixed by the numbers above under
`docs/qa/evidence/2026-09-02-merge-alone-slices/`.

## CH1 — derived count and authoring surface

Walked as an adopter who never types `--slices`.

- The one-slice fixture (five primary tasks `T1`–`T5` across three technical phases, plus a `T2R1`
  remediation record) resolved with exit `0` and review groups `[[1]]` — technical organization did
  not inflate the count.
- The two-slice fixture resolved to `[[1, 2]]`, each ordinal once.
- `--slice-contract-json` reported `T1..T5 → A` and `T1,T2 → A; T3,T4 → B` in document order, with
  `slice_ids` and full `closures` rows. Repeated in a fresh process, both outputs were
  byte-identical (`cmp` clean).
- Appending a second remediation record (`### T4R1:` carrying its own `**Slice:** B`) left the
  contract byte-identical to the record-free run and the resolved groups at `[[1, 2]]`.
- The installed template
  `.agents/skills/workflow-spec-driven/references/tasks.md` names the three units apart at its
  `## Vertical Slice Closure` section — "A phase or cohort describes technical ordering; a batch
  describes worker capacity. Neither creates a vertical slice or owns its count." — shows
  `**Slice:** [id]` on every task stub, and prints the closure table with `yes` as the only value.
- Every published invocation in `README.md` (native, profile, override, refresh, `--sync-agents`)
  and in the `workflow-config` skill was copied verbatim (only `--root` pointed at the disposable
  target) and exited `0` with the documented role routing. Neither document presents `--slices` as
  the source of truth; both state the count is derived and the flag is an assertion.
- **Canary C1** in the same target: `grouped.3` over four derived slices produced the balanced
  `[[1, 2], [3, 4]]`; `remediation.stall_attempts` reported the default `3`, accepted `0`, and
  rejected `-2` with `remediation.stall_attempts must be an integer of at least 0` before any
  feature directory was created.

## CH2 — refusal and fail-closed

Every refusal was measured with a SHA-256 of `workflow.json` on both sides.

- `--slices 2` against the two-slice fixture succeeded. In fresh features, `--slices 1` and
  `--slices 3` exited `2` naming both numbers
  (`slice count assertion 1 does not match derived slice count 2`) and left the snapshot `ABSENT`.
- `--slices 0` and `--slices -1` exited `2` with `slice count must be at least 1`, snapshot
  `ABSENT`.
- Repeated with `--refresh` against a feature already holding a valid snapshot, all four mismatch
  and range refusals left the hash at `2621e23f…` on both sides.
- Twelve one-defect-at-a-time mutations each exited `2` naming the cause, with the snapshot absent
  (fresh feature) and, for four of them re-run with `--refresh` over an existing snapshot, the hash
  unchanged:

  | Mutation | Message |
  | --- | --- |
  | closure table dropped | `missing required section: ## Vertical Slice Closure; A/B: primary tasks use a slice without a closure row` |
  | blank observable outcome | `slice 'A' has an empty observable outcome` |
  | blank independent gate | `slice 'A' has an empty independent gate` |
  | merge-alone empty / `no` / `Yes` / `true` | `slice 'A' requires exact lowercase yes` |
  | duplicate slice id | `Vertical Slice Closure repeats slice 'B'` |
  | unreferenced closure row | `C: closure row has no primary task` |
  | task with no `**Slice:**` | `T3: exactly one non-empty Slice field is required` |
  | task with two `**Slice:**` | `T3: exactly one Slice field is required` |
  | task naming an undeclared slice | `Z: primary tasks use a slice without a closure row` |

- A feature directory containing no `tasks.md` resolved with exit `0` and groups `[[1]]`.
- **Canary C2 note:** the resume path (no `--refresh`) with a mismatching `--slices 3` exited `0`
  and left the frozen snapshot untouched, which is the documented resume contract, not a missed
  assertion.

**Non-blocking observation (not a defect, no bug filed):** the undeclared-slice failure names the
offending slice id (`Z`) but not the task that used it (`T3`), while the two membership-count
failures do name `T3`. The scenario's promise — exit non-zero naming the cause, snapshot untouched —
is met, so this is a diagnostic-quality nit for the planner to weigh, not a broken promise.

## CH3 — resume versus refresh

- A one-slice snapshot was frozen at hash `fdb78237…` with groups `[[1]]`.
- Replacing `tasks.md` with the two-slice fixture and resuming without `--refresh`: exit `0`, CLI
  and file both still `[[1]]`, hash unchanged.
- Resuming again with `--slices 2` supplied: exit `0`, `[[1]]`, hash unchanged — the assertion is
  not applied on resume.
- Corrupting `tasks.md` (closure table removed) and resuming without `--refresh`: exit `0`, hash
  unchanged. A document that rots after the freeze cannot fail an in-flight resume.
- Restoring the valid two-slice document and running `--refresh`: exit `0`, groups `[[1, 2]]`, hash
  moved to `b396b717…`, snapshot `version` still `3`.
- Corrupting again and running `--refresh`: exit `2` naming the missing section, with the refreshed
  snapshot byte-for-byte intact at `b396b717…`.
- **Canary C2:** `remediation` never appears in `workflow.json` (`grep -c` = `0` before and after).
  Changing `stall_attempts` to `7` and resuming reported `{'stall_attempts': 7}` in the current CLI
  JSON while groups, roles, and the snapshot hash all stayed frozen.

## CH4 — downstream consumption

Read-only planning only: no worker dispatch, no worktree creation, no network.

- For the two-slice fixture carrying `**Status:**`/`**Resources:**` fields, the union of
  `lanes` + `blocked` was `{T1: A, T2: A, T3: B, T4: B}` — equal, field by field, to the validator's
  `task_slices`. `decision: concurrent-writers`, `fallback: false`, `reasons: []`.
- Planning the same feature twice in fresh processes produced byte-identical JSON.
- Inserting `### T2R1:` after `T2` with `**Status:** complete`, `**Resources:** db`, and
  `**Depends on:** T3` produced a plan equal to the record-free run in every key except the feature
  name; `T2`'s placement, reasons, and edges were identical, and the string `T2R1` appeared nowhere
  in the plan.
- Rewriting the primary headings as `## T1:`, `#### T2:`, `### t3:`, `### T4:` left both tools
  seeing four tasks with the same membership, `fallback: false`, `reasons: []`.
- Adding a `#### T1:` phase listing above the task's own definition did not double-count and did not
  fall back; the plan was identical to the base run.
- **Canary C3:** one candidate per slice, deterministic ready/blocked output, a decisive
  `serial-integration` fallback with per-task `invalid-status`/`missing-resources` reasons on a
  fixture lacking the dispatch fields, and the installed
  `.agents/skills/autonomous/references/parallelization.md` still requiring a fresh non-author
  technical Verifier per code-changing slice, integrated-head Deep Review, QA Plan, QA Execute, and
  final QA. Nothing contradicted the frozen `pass`.

## Limitations

- No browser, API, mobile, auth, server, or production health surface exists in this repository; the
  CLI/manual adapter is the only production-parity path, per the profile.
- Independent confirmation was done by re-reading `workflow.json` from disk and re-running each
  command in a fresh Python process rather than by a page reload; there is no reloadable surface.
- Hostile staged-file, concurrent-process, and interrupted-write behaviour around the atomic
  snapshot replacement remains a technical-verification surface, not a QA one.
- The disposable repository was built from `git archive dfdf227`, so it carries tracked files only;
  the local ignored `.my-workflow.toml` was regenerated from the tracked example rather than copied.

## Bugs

None filed. No product defect was confirmed, so no walk was stopped and no Implementer handoff is
required from this cycle.

## Residue

Source checkout after cleanup: one untracked file, this report. The disposable target
`/Users/antoniofulg/Projects/.qa-merge-alone-2026-09-02` was removed and no `.qa-*` sibling remains
(`evidence/…/90-residue-and-cleanup.log`). No product code was changed.

## Handoff

- `CFG-derive-merge-alone-slices` moves `untested → pass`.
- No frozen canary verdict was contradicted; `CFG-resolve-deep-review-cadence`,
  `CFG-freeze-feature-workflow`, and `CFG-plan-parallel-slice-dispatch` were walked read-only and
  left unedited, as `IT-006` requires.
- One optional follow-up for the planner: decide whether the undeclared-slice diagnostic should also
  name the task that referenced the missing closure row. No bug was filed for it.
