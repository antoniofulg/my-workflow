# Merge-Alone Slice Derivation — Technical Validation

**Result**: PASS

**Feature**: `merge-alone-slices` · **Branch**: `feat/merge-alone-slices` · **Range**: `13b0d47..ee895c6`
**Verifier**: fresh session, author ≠ verifier. This session wrote no product code, fixed nothing, and
made no commit. The prior `validation.md` was discarded and overwritten, not used as evidence.
**Scope**: technical phase only. Re-derived from `spec.md`, `tests.md`, `dx.md`, the diff, and the code.

## 1. Acceptance criteria → asserting test

Every criterion has an assertion on the contracted outcome, not on the implementation shape.

| AC | Test ID | Asserting test at `file:line` | Asserted outcome |
| --- | --- | --- | --- |
| MAS-01 | MAS-UT-001 | `tools/test_tlc_validators.py:109` | 5 primary tasks, 3 cohorts, `slice_ids == ["A"]`, all membership `A` |
| MAS-01 | MAS-IT-001 | `tools/test_workflow_config.py:151` | `deep_review.groups == [[1]]` from the Praxis fixture |
| MAS-02 | MAS-UT-002 | `tools/test_tlc_validators.py:124` | `slice_ids == ["A","B"]`, `task_slices == {T1:A,T2:A,T3:B,T4:B}` |
| MAS-02 | MAS-IT-002 | `tools/test_workflow_config.py:163` | `deep_review.groups == [[1, 2]]` |
| MAS-03 | MAS-UT-003 | `tools/test_tlc_validators.py:135` | 4 subtests: empty outcome / empty gate / backtick-only gate / empty reason each raise naming `slice 'A'` |
| MAS-03 | MAS-UT-004 | `tools/test_tlc_validators.py:162` | `no`, ``, `Yes`, `true` all raise `slice 'A'.*exact lowercase yes` |
| MAS-04 | MAS-UT-005 | `tools/test_tlc_validators.py:175` | missing / mis-cased / duplicated / unknown-slice field each raise naming `T1` or `Z` |
| MAS-04 | MAS-UT-006 | `tools/test_tlc_validators.py:204` | `repeats slice 'A'` and `B: closure row has no primary task` |
| MAS-05 | MAS-IT-003 | `tools/test_workflow_config.py:175`, `:193`, `:212` | mismatch names supplied and derived counts; `0`/`-1` rejected; snapshot absent, or bytes identical on refresh |
| MAS-06 | MAS-IT-004 | `tools/test_workflow_config.py:238` | no `tasks.md` → `groups == [[1]]` |
| MAS-07 | MAS-IT-005 | `tools/test_workflow_config.py:248`, `:265` | error names `tasks closure validation failed` + `Vertical Slice Closure`; no snapshot written; refresh leaves bytes unchanged |
| MAS-08 | MAS-IT-006 | `tools/test_workflow_config.py:288` | tasks changed to 2 slices *and* made malformed; resume with `--slices 8` returns identical dict and identical bytes |
| MAS-09 | MAS-IT-009 | `tools/shared/tests/workflow-config.test.ts:70` | template carries `## Vertical Slice Closure`, `**Slice:** <slice-id>`, "merge-alone observable outcome", "A phase or cohort describes technical ordering", "a batch describes worker capacity"; skill and README show `--slices` as optional assertion only |
| MAS-10 | MAS-UT-007 | `tools/test_tlc_validators.py:214` | `T2R1` and `TDR1` (the latter carrying `**Slice:** B`) absent from `task_slices`; `len(slice_ids) == 2` |
| MAS-11 | MAS-IT-008 | `tools/test_parallel_plan.py:126` | `{lanes ∪ blocked} membership == validated_slice_contract(...)["task_slices"]` |
| MAS-12 | MAS-IT-008 | `tools/test_parallel_plan.py:126`, `:153` | planner consumes the resolver-written snapshot (`plan.source_git_head == snapshot.git_head`); a contract the validator rejects fails the plan closed with the validator's message |
| MAS-13 | MAS-IT-010 | `tools/test_parallel_plan.py:206` | a `### T2R1:` record carrying `**Status:** complete`, `**Resources:** db`, `**Depends on:** T3` leaves `T2`'s plan entry, `fallback`, and `reasons` byte-identical to the document without the record |

MAS-UT-008 (`tools/test_tlc_validators.py:226`) additionally asserts the `--slice-contract-json`
determinism and document-order contract that `dx.md:54` publishes: two subprocess runs produce
identical stdout, `list(task_slices) == ["T1","T2","T3","T4"]`, `slice_ids == ["A","B"]`.

**13 of 13 acceptance criteria, 8 of 8 MAS-UT, 10 of 10 MAS-IT covered by a named assertion.**

## 2. Gates — real exit codes

Load average read from `uptime` immediately before each batch. The documented flake threshold is ~20.

| Command | `status=` | Output excerpt |
| --- | --- | --- |
| `uptime` (before targeted batch) | — | `4:04 up 5 days, 17:07, 30 users, load averages: 14.68 19.88 24.51` |
| `python3 tools/test_tlc_validators.py` | `0` | `Ran 17 tests in 0.768s` / `OK` |
| `python3 tools/test_workflow_config.py` | `0` | `55 passed, 0 failed` |
| `python3 tools/test_parallel_plan.py` | `0` | `29 passed, 0 failed` |
| `python3 tools/test_qa_parallel_pilot.py` | `0` | `13 passed, 0 failed` |
| `python3 tools/test_parallel_executor.py` | `0` | `58 passed, 0 failed` |
| `bun test tools/shared/tests/workflow-config.test.ts` | `0` | `6 pass` / `0 fail` / `104 expect() calls` |
| `bun run test:all` | `FULLGATE_STATUS=0` | `124 pass` / `0 fail` / `Ran 124 tests across 8 files. [19.71s]`, then the full `test:python` loop to completion |

Full-gate load: `4:06 … load averages: 19.96 20.69 24.22` at start, `4:10 … load averages: 16.95 17.48 21.73`
at end — one-minute load stayed below the ~20 flake threshold for the run.

**Flaky suites**: no re-run was required, because neither flaked.
- `tools/shared/tests/security-skills-installation.test.ts` is inside the `bun test` default glob that
  reported `124 pass / 0 fail` across 8 files.
- `tools/test_parallel_resource_lock.py` is inside `test:python`
  (`git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | sort | while read test; do python3 "$test" || exit $?; done`).
  That loop is `|| exit $?`, so `FULLGATE_STATUS=0` is proof every listed Python suite exited `0`.

## 3. Discrimination sensor

Ten mutants, applied one at a time in the scratch worktree `/tmp/mas-mut` at `ee895c6` (`git worktree
add --detach`), each reverted with `git checkout -- .` before the next. **`__pycache__` is purged
between every mutant** — mutants (e)/(f) change `return 1` → `return 0`, which preserves file size and
let stale bytecode leak across runs on the first pass; every result below is from the purged re-run.
Each mutant was run against all three Python suites.

| # | Mutation | Killed | Killing test `file:line` and message |
| --- | --- | --- | --- |
| a | `merge_alone != "yes"` → `merge_alone.lower() != "yes"` (accept `Yes`) | yes | `tools/test_tlc_validators.py:162` — `(value='Yes') AssertionError: ValueError not raised` |
| b | delete the duplicate-slice-ID loop | yes | `tools/test_tlc_validators.py:204` — `assertRaisesRegex(ValueError, "repeats slice 'A'")` → `ValueError not raised` |
| c | delete the orphan-closure loop | yes | `tools/test_tlc_validators.py:204` — `"B: closure row has no primary task" does not match "A: primary tasks use a slice without a closure row"` |
| d | write the snapshot before the `--slices` mismatch check, check kept live | yes | `tools/test_workflow_config.py:175`, `:193`, `:212` — all three `AssertionError` (snapshot exists / bytes changed) |
| e | resume re-reads `tasks.md` instead of returning the frozen snapshot | yes | `tools/test_workflow_config.py:288` — `ConfigError: slice count assertion 8 does not match derived slice count 2` |
| f | missing `tasks.md` derives `0` instead of `1` | yes | `tools/test_workflow_config.py:238` — `ConfigError: slice count must be at least 1` |
| g | delete the `^#{1,6}\s+` reset in `validate_tasks.parse_tasks` | yes | `tools/test_tlc_validators.py:124` — `ValueError: T4: exactly one Slice field is required`; also kills `:214`, `:226`, and cascades into `tools/test_workflow_config.py:163` and `tools/test_parallel_plan.py:126` |
| h | planner falls back to its own `**Slice:**` when the validator raises | yes | `tools/test_parallel_plan.py:153` — `AssertionError: expected the validator to reject: T2: Slice field must use exactly` |
| i | planner prefers its own `**Slice:**` over the validator's (`fields.get("slice") or task_slices.get(task_id)`) | **survives** | no failure in any of the three suites — see the equivalence proof below |
| j | remove the `HEADING` reset added in `ee895c6` | yes | `tools/test_parallel_plan.py:206` — `StopIteration` in `entry_for`, then `assert entry_for(recorded,"T2") == entry_for(plain,"T2")` |

Mutant (h) — the mutant that survived the previous round — is now killed by
`tools/test_parallel_plan.py:153`, added in `f7676c2`.

### Mutant (i) is an equivalent mutant, not a gap

`slice_id = fields.get("slice") or task_slices.get(task_id)` cannot differ from
`task_slices.get(task_id)` under the current parsers, and this is evidence, not argument:

- Where both parsers recognise the heading (canonical `### T<n>:`), the planner's `fields["slice"]`
  and the validator's `task_slices[T<n>]` are read from the *same* `**Slice:**` line of the *same*
  section, and the validator (`.agents/skills/workflow-spec-driven/scripts/validate_tasks.py:250`,
  and its "exactly one non-empty Slice field" rule) rejects any document where that line is absent,
  duplicated, mis-cased, or names a slice without a closure row — so the plan never runs.
- Where the parsers disagree (item 4 below), the planner has *no section* for the task at all, so
  `fields` is never consulted and the mutated expression is unreachable.

I therefore raise no fix task for (i). **Kill rate on non-equivalent mutants: 9 / 9.**

## 4. Judging `ee895c6`

**Is the planner's task boundary now identical to the validator's? Partly — the end is, the start is not.**

- **End of task — now identical.** `validate_tasks.parse_tasks` ends a task on
  `re.match(r"^#{1,6}\s+", stripped)` at
  `.agents/skills/workflow-spec-driven/scripts/validate_tasks.py:117`. `ee895c6` gives the planner the
  same rule: `HEADING = re.compile(r"^#{1,6}\s+")` at
  `.agents/skills/workflow-config/scripts/parallel_plan.py:27`, applied at `:136-142`. A `### T2R1:`
  remediation record now terminates the preceding task in both, so it donates no field. This is
  exactly what AC-13 / MAS-IT-010 contract, and mutant (j) confirms the test discriminates it.
- **Start of task — still divergent.** The validator matches
  `TASK_RE = ^#{2,4}\s+(T\d+)\s*:` case-insensitively on the *stripped* line
  (`validate_tasks.py:46`, `:103`); the planner matches
  `TASK_HEADING = ^###\s+(T\d+)\s*:` case-sensitively on the *raw* line
  (`parallel_plan.py:26`, `:130`). Direct probe on a validator-valid two-task document:

  ```
  heading form      validator task_slices              planner membership
  ### T2:           {'T1': 'A', 'T2': 'A'}             {'T1': 'A', 'T2': 'A'}
  ## T2:            {'T1': 'A', 'T2': 'A'}             {'T1': 'A'}
  #### T2:          {'T1': 'A', 'T2': 'A'}             {'T1': 'A'}
  ### t2:           {'T1': 'A', 'T2': 'A'}             {'T1': 'A'}
  (indented) ### T2:{'T1': 'A', 'T2': 'A'}             {'T1': 'A'}
  ```

  The task is dropped from the plan **silently** — no entry in `lanes`, none in `blocked`, and no
  `reasons` line. That contradicts the wording of AC-11 / AC-12 ("the same primary-task membership
  the validator derived") for those four heading forms. See gap G1.

**Is the divergence introduced by `ee895c6`? No.** The identical probe run against the planner at
`a872208` produces byte-identical output, so the start-boundary divergence predates the remediation.
`ee895c6` strictly improves the end boundary and changes nothing else in the planner.

**Did any pre-existing planner test lose an invariant? No.** `git show ee895c6 -- tools/test_parallel_plan.py`
is `+31 / -0`: one new test and one new helper, no test modified or deleted, and the pre-existing 29
planner assertions still pass (`29 passed, 0 failed`). Across the whole range the only planner-test
deletion is the `missing-slice:T1` reason case (removed in `f7676c2`); that invariant did not vanish,
it moved down a layer and is now asserted by `tools/test_parallel_plan.py:153`
(`T2: Slice field must use exactly`) and `tools/test_tlc_validators.py:175`, both of which mutant (h)
proves are load-bearing.

## 5. `dx.md` parity

| `dx.md` claim | Implementation `file:line` | Verdict |
| --- | --- | --- |
| CLI flags `--root --feature --native-provider --slices --profile --override --refresh` (`dx.md:8-16`) | `.agents/skills/workflow-config/scripts/workflow_config.py:893-901` | matches |
| Initial with `tasks.md` validates the closure contract and derives the count (`dx.md:18-19`) | `workflow_config.py:636-665`, invoked at `:832` | matches |
| Initial without `tasks.md` uses one slice (`dx.md:20`) | `workflow_config.py:639-640` (`if not tasks_path.is_file(): return 1`) | matches |
| `--slices` is an exact assertion that never owns the count (`dx.md:21-22`) | `workflow_config.py:833-840` — checked, then unconditionally overwritten by `slice_count = derived_count` | matches |
| Resume returns the existing snapshot without reading tasks or checking `--slices` (`dx.md:23-24`) | `workflow_config.py:822-830` — returns before `_derived_slice_count` at `:832` and before the `--slices` check | matches |
| Refresh validates and *atomically* replaces (`dx.md:25-26`) | `workflow_config.py:822` (`and not refresh`) + `_write_snapshot` at `:781-795` (`NamedTemporaryFile` + `fsync` + `os.replace`) | matches |
| Planner accepts the snapshot and reports the validator's membership (`dx.md:27-28`) | `parallel_plan.py:124` — membership sourced only from `validated_slice_contract` | matches, subject to G1 |
| `validate_tasks.py <tasks.md> --slice-contract-json` writes one JSON object with `task_slices` / `slice_ids` / `closures{outcome,gate,merge_alone,why}` (`dx.md:32-52`) | `validate_tasks.py:423`, `:433`; contract built at `:240-258` | matches |
| Task IDs and slice IDs in document order; output deterministic (`dx.md:54`) | asserted by `tools/test_tlc_validators.py:226` | matches |
| One `**Slice:**` per `### T<number>:`; each used slice once in the closure table (`dx.md:56-75`) | `validate_tasks.py:103-119`, `:186-211`, `:248-253` | matches |
| Failure table: invalid contract / mismatch / non-positive / invalid existing snapshot (`dx.md:79-84`) | `workflow_config.py:641`, `:837`, `:835`, `:667-673` | matches |
| Manual slice count removed with no alias or fallback (`dx.md:86-89`) | no `slice_count` source other than `derived_count` (`workflow_config.py:840`) | matches |

Informational, not a gap: `dx.md:37` says "writes one JSON object to stdout" while
`validate_tasks.py:433` emits it with `indent=2`. Still exactly one JSON object; the pretty-printing is
not a contract claim and MAS-UT-008 pins the byte-for-byte determinism that is.
`dx.md` also omits `--sync-agents` from the synopsis; that flag is outside this feature's surface and
is mutually exclusive with resolution, so the omission is correct scoping.

## 6. Frozen QA guard

```
$ git diff --name-only 13b0d47..ee895c6 -- docs/qa/scenarios docs/qa/reports docs/qa/charters docs/qa/bugs docs/qa/evidence
docs/qa/scenarios/CFG-derive-merge-alone-slices.md
```

Exactly one path, and it is the expected new scenario. No report, charter, bug, or evidence artifact
was touched.

## 7. `AGENTS.md` and `docs/guidelines/*.md`

```
$ git diff --name-only 13b0d47..ee895c6 -- AGENTS.md docs/guidelines/
(no output)
```

Both unchanged across the range.

## Ranked gaps

Only gaps re-observed in this session are listed. Nothing below was fixed here; each returns to a new
Implementer session.

**G1 — low, follow-up, non-blocking.** The planner silently drops a primary task whose heading the
validator accepts but the planner does not: `## T<n>:`, `#### T<n>:`, lowercase `### t<n>:`, or an
indented `### T<n>:`. Evidence: the probe table in item 4 — validator yields `{'T1':'A','T2':'A'}`, the
planner yields `{'T1':'A'}` with no `reasons` entry. Sites:
`.agents/skills/workflow-config/scripts/parallel_plan.py:26` (`^###\s+(T\d+)\s*:`, case-sensitive, raw
line) versus `.agents/skills/workflow-spec-driven/scripts/validate_tasks.py:46` (`^#{2,4}\s+(T\d+)\s*:`,
`re.IGNORECASE`) applied to `ln.strip()` at `:103`. This contradicts the wording of AC-11 and AC-12 for
those heading forms, and no test covers it. It is **not** a regression from `ee895c6` — the same probe
against the planner at `a872208` is byte-identical — and it does not affect any document written to the
published template, which mandates `### T<n>:`. Suggested remediation, for a separate Implementer:
reuse `validate_tasks.TASK_RE` in `parallel_plan._parse_tasks` (as the slice membership already reuses
`validated_slice_contract`) so the two parsers cannot disagree about where a task starts either, and
add a planner test asserting membership equality for a `## T<n>:` heading.

**No blocking gap.** All 13 acceptance criteria carry a discriminating assertion, all named gates and
the full gate exit `0`, and every non-equivalent mutant is killed.

## Method notes

- Scratch worktree `/tmp/mas-mut` (`git worktree add --detach ee895c6`); the active checkout was never
  mutated. Every mutant reverted with `git checkout -- .` plus a `__pycache__` purge.
- Baseline re-confirmed after the purge fix: `python3 tools/test_workflow_config.py` → `status=0`,
  `55 passed, 0 failed`.
- This session wrote only this file. No product code, test, fixture, or commit was created or amended.
