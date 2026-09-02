# Merge-Alone Slice Derivation — Technical Validation

**Result**: PASS

**Phase**: technical
**Feature**: `merge-alone-slices`
**Range**: `13b0d47..e0e97d5` (`50f3313`, `f7b3905`, `b1bec68`, `e0e97d5`)
**Branch**: `feat/merge-alone-slices`
**Date**: 2026-09-02
**Verifier**: independent session; did not author this code. Implementer transcript and operator
handoff were not loaded.
**Supersedes**: the stale validation.md from the dropped 2026-08-27 run (`AD-020`).

---

## 1. Acceptance criteria and test-contract coverage

Every `tests.md` row carries a labelled asserting test. Mapping re-derived by grep, not by trusting
`tasks.md`:

```
$ grep -rEn "MAS-(UT|IT)-[0-9]+" tools/ | sed 's/:.*\(MAS-[A-Z]*-[0-9]*\).*/ -> \1/' | sort -u
tools/test_tlc_validators.py           -> MAS-UT-001 .. MAS-UT-008   (8 rows, 8 refs)
tools/test_workflow_config.py          -> MAS-IT-001 .. MAS-IT-007   (7 rows, 10 refs)
tools/test_parallel_plan.py            -> MAS-IT-008
tools/shared/tests/workflow-config.test.ts -> MAS-IT-009
```

17 of 17 contract rows mapped, 0 unmapped.

| AC | Asserting test (`file`) | Asserts the spec outcome? |
| --- | --- | --- |
| MAS-01 | `test_praxis_migration_is_one_slice` (`tools/test_tlc_validators.py`) — asserts 3 `### Phase ` cohorts, 5 `TASK_RE` primaries, `slice_ids == ["A"]`, `check()` errors `[]` | yes — counts cohorts and primaries from the fixture text, not from parser internals |
| MAS-02 | `test_independent_capabilities_are_two_slices`; `test_initial_resolution_derives_two_independent_slices_from_tasks` (groups `[[1, 2]]`) | yes |
| MAS-03 | `test_rejects_incomplete_closure_fields` (4 subtests: empty outcome, empty gate, backtick-only gate, empty reason); `test_requires_exact_lowercase_merge_alone_yes` | yes — each subtest matches on a message naming `slice 'A'` and the field |
| MAS-04 | `test_rejects_inconsistent_primary_task_membership` (missing, wrong syntax, doubled, unknown slice); `test_rejects_duplicate_and_orphan_closure_rows` | yes — messages named per task/slice |
| MAS-05 | `test_slice_assertion_mismatch_fails_before_snapshot_write`, `test_non_positive_slice_assertions_fail_before_snapshot_write`, `test_refresh_slice_assertion_mismatch_preserves_snapshot_bytes` | yes — assert both the error text and snapshot absence / byte-identity |
| MAS-06 | `test_missing_tasks_defaults_to_one_slice_without_manual_count` (groups `[[1]]`) | yes |
| MAS-07 | `test_malformed_tasks_fails_before_snapshot_write`, `test_malformed_refresh_preserves_snapshot_bytes` | yes |
| MAS-08 | `test_resume_returns_frozen_snapshot_without_reading_changed_tasks` — passes `slice_count=8` and a changed/malformed `tasks.md`, asserts `resumed == first` and byte-identity | yes — the `8` is the discriminator: a resume that read tasks would raise |
| MAS-09 | `publishes the merge-alone slice planning contract` (`tools/shared/tests/workflow-config.test.ts`) — template ordering, one `**Slice:** [id]` per `T1..T4`, slice/phase-cohort/batch wording, README/SKILL text | yes |
| MAS-10 | `test_remediation_records_do_not_inflate_the_contract` — fixture carries `### T2R1:`, `### TDR1:` and a mis-tagged `**Slice:** B` under `TDR1`; asserts neither joins `task_slices` and `slice_ids` stays at 2 | yes |
| MAS-11 / MAS-12 | `test_resolved_snapshot_preserves_validator_slice_membership` (`tools/test_parallel_plan.py`) — resolves through `workflow_config.resolve`, then asserts `plan` lanes+blocked membership `== validated_slice_contract(...)["task_slices"]` and `source_git_head == snapshot["git_head"]` | yes — compares the planner to the validator's contract, not to a hard-coded literal |

No test observed asserting an implementation detail in place of the contracted outcome.

## 2. Gates — real exit codes (not read through a pipe)

```
$ python3 tools/test_tlc_validators.py > /tmp/tlc.log 2>&1; echo "EXIT_tlc=$?"
EXIT_tlc=0
Ran 17 tests in 0.553s
OK

$ python3 tools/test_workflow_config.py > /tmp/wc.log 2>&1; echo "EXIT_workflow_config=$?"
EXIT_workflow_config=0
55 passed, 0 failed

$ python3 tools/test_parallel_plan.py > /tmp/pp.log 2>&1; echo "EXIT_parallel_plan=$?"
EXIT_parallel_plan=0
27 passed, 0 failed

$ bun test tools/shared/tests/workflow-config.test.ts > /tmp/bunwc.log 2>&1; echo "EXIT_bun_wc=$?"
EXIT_bun_wc=0
 6 pass / 0 fail / 104 expect() calls

$ bun run test:all > /tmp/testall.log 2>&1; echo "EXIT_test_all=$?"
EXIT_test_all=0
  bun test: 124 pass, 0 fail, 1157 expect() calls, 124 tests across 8 files
  test:python: 13 / 10 / 15 / 17 / 55 / 5 passed, 0 failed
```

## 3. Discrimination sensor — 7 mutants, 7 killed

Each mutant injected alone, the named suite run, then `git checkout -- <file>`. Final
`git status --porcelain` is empty; no mutant survives in the tree.

| # | Mutant | Suite | Real exit | Failing test(s) |
| --- | --- | --- | --- | --- |
| a | `merge_alone != "yes"` → `merge_alone.casefold() != "yes"` (accept `Yes`) | `tools/test_tlc_validators.py` | 1 | `FAIL: test_requires_exact_lowercase_merge_alone_yes (value='Yes')` |
| b | delete the `repeats slice` duplicate loop in `_parse_closure_table` | `tools/test_tlc_validators.py` | 1 | `FAIL: test_rejects_duplicate_and_orphan_closure_rows` |
| c | delete the `closure row has no primary task` loop in `_slice_contract` | `tools/test_tlc_validators.py` | 1 | `FAIL: test_rejects_duplicate_and_orphan_closure_rows` |
| d | keep the `--slices` assertion but move it *after* `_write_snapshot` | `tools/test_workflow_config.py` (3 targeted) | 1 | `test_slice_assertion_mismatch_fails_before_snapshot_write`, `test_non_positive_slice_assertions_fail_before_snapshot_write`, `test_refresh_slice_assertion_mismatch_preserves_snapshot_bytes` — all on the `not workflow.json.exists()` / byte-identity assertion |
| e | resume branch calls `_derived_slice_count` and asserts `--slices` before returning the frozen snapshot | `tools/test_workflow_config.py` (targeted) | 1 | `FAIL test_resume_returns_frozen_snapshot_without_reading_changed_tasks: ConfigError: slice count assertion 8 does not match derived slice count 2` |
| f | `_derived_slice_count` returns `0` instead of `1` for missing `tasks.md` | `tools/test_workflow_config.py` (targeted) | 1 | `FAIL test_missing_tasks_defaults_to_one_slice_without_manual_count: ConfigError: slice count must be at least 1` |
| g | delete the `^#{1,6}\s+` → `current = None` reset in `parse_tasks` | `tools/test_tlc_validators.py` | 1 | `ERROR: test_remediation_records_do_not_inflate_the_contract`, `test_independent_capabilities_are_two_slices`, `test_slice_contract_json_is_deterministic_and_ordered` |

Note on (d): the `tools/test_workflow_config.py` runner is `sorted(globals())` with no isolation and
stops at the first failure, so a whole-file run masks later failures behind alphabetically earlier
ones. The three (d)/(e)/(f) rows above were re-run by invoking the named test functions directly, on
a verified-green baseline (`10 PASS` before mutation), so each row names the test the mutant actually
kills rather than an incidental collateral failure.

## 4. Contract parity with `dx.md`

```
$ python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py \
    tools/fixtures/tlc-validator/merge-alone-two-slices.md --slice-contract-json ; echo EXIT=$?
{
  "task_slices": { "T1": "A", "T2": "A", "T3": "B", "T4": "B" },
  "slice_ids": [ "A", "B" ],
  "closures": {
    "A": { "outcome": "...", "gate": "python3 -m unittest capability_a", "merge_alone": true, "why": "..." },
    "B": { ... }
  }
}
EXIT=0
```

Shape, key order, and document ordering match `dx.md` exactly (`task_slices` → `slice_ids` →
`closures`; task ids `T1..T4` and slice ids `A, B` in document order). Determinism is separately
pinned by `test_slice_contract_json_is_deterministic_and_ordered`, which byte-compares two
subprocess runs.

`--slices` optional, `--feature` / `--native-provider` still required:

```
$ python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --native-provider codex
workflow-config: --feature and --native-provider are required unless --sync-agents is used
EXIT_nofeature=2
$ python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature merge-alone-slices
workflow-config: --feature and --native-provider are required unless --sync-agents is used
EXIT_noprovider=2
```

`argparse` declares `--slices` with no default, and `resolve(..., slice_count: int | None = None)`;
`main` no longer requires it. Error messages name the counts and the subject:

- `workflow-config: slice count assertion 2 does not match derived slice count 1` — supplied and derived
- `workflow-config: slice count must be at least 1` — non-positive assertion
- `workflow-config: tasks closure validation failed: ... Vertical Slice Closure ...` — validator detail relayed
- `Vertical Slice Closure slice 'A' has an empty independent gate`, `T1: exactly one non-empty Slice field is required`, `Z: primary tasks use a slice without a closure row` — slice/task named

`resolve()` orders the resume return, then derivation, then assertion, then `_write_snapshot`; the
mismatch cannot reach a write (mutant d confirms the ordering is load-bearing).

## 5. Frozen QA guard

```
$ git diff --name-only 13b0d47..e0e97d5 -- docs/qa/scenarios docs/qa/reports docs/qa/charters docs/qa/bugs docs/qa/evidence
docs/qa/scenarios/CFG-derive-merge-alone-slices.md
```

Exactly the one new scenario file; no existing scenario, report, charter, bug, or evidence file
touched. The only other `docs/qa` change is a one-line index entry in
`docs/qa/journeys/J-configure-feature-workflow.md` (`+1 -0`), outside the guarded set and consistent
with adding a scenario. The `historicalQaBaseline` guard in the bun suite passes.

## 6. Instruction budget

```
$ git diff --name-only 13b0d47..e0e97d5 -- AGENTS.md CLAUDE.md docs/guidelines
(no output)
```

`AGENTS.md` and every `docs/guidelines/*.md` are unchanged in the range. Prose additions land in
`README.md` (+13/-4), `CHANGELOG.md` (+4), `.agents/skills/workflow-config/SKILL.md` (+9/-2), and the
task template (+17) — none of which are per-turn instruction files.

## 7. Disclosed deviations (`memory/MEMORY.md`)

**(a) `parse_tasks` clears the current task on any heading — ACCEPTABLE.**
The reset is what makes MAS-10 true: without it, `**Slice:** B` under `### TDR1:` donates a second
slice value to the preceding primary task. Mutant (g) kills three tests, so the behaviour is pinned,
not incidental. No canonical document regresses: the task template's `T1..T4` bodies contain no
sub-headings, `nested-phase-tasks.md` still yields `{"T1": 1, "T2": 2}`, and this feature's own
`.specs/features/merge-alone-slices/tasks.md` validates at exit 0 (5 granularity warnings, 0 errors).
Residual filed as gap G4.

**(b) Two-slice fixture diagram / `Depends on` mismatch — GAP, not a blocker.**
Re-derived:

```
$ validate_tasks.check('tools/fixtures/tlc-validator/merge-alone-two-slices.md')
ERRORS: ['diagram shows T2 -> T3 but T3 has no matching `Depends on: T2`']
$ validate_tasks.check('tools/fixtures/tlc-validator/merge-alone-one-slice.md')
([], [])
```

No assertion is weakened — no test claims `check()` is clean on the two-slice fixture, and the
resolver path invokes only `--slice-contract-json`, which does not run `check()`. But the canonical
two-slice fixture backing five contract rows is a document the repository's own validator rejects.
Filed as gap G1.

**(c) Resolver tests rewritten to carry a derived `tasks.md` — ACCEPTABLE.**
Mechanically required by MAS-05: once the manual count stops owning the value, a test asserting
`--slices 4` must supply a `tasks.md` deriving 4. Each rewritten test keeps its original invariant.
Spot-checked `test_snapshot_write_failure_preserves_previous_snapshot`: only the refresh assertion
changed `3` → `2` to match the derived contract; the injected `os.replace` failure and the
"previous snapshot preserved" assertion are untouched. `write_derived_tasks` is a fixture helper, not
a weakening. No test was skipped, deleted, or loosened.

---

## Ranked gaps

None blocking. All five are follow-up items for the planner; nothing was fixed in this session.

| # | Sev | Gap |
| --- | --- | --- |
| G1 | medium | `tools/fixtures/tlc-validator/merge-alone-two-slices.md` fails full `check()` (`diagram shows T2 -> T3 but T3 has no matching Depends on: T2`). It backs MAS-UT-002/007/008 and MAS-IT-002/008. Latent trap: any later decision to run full `check()` in the resolver path breaks those five rows for a reason unrelated to the behaviour under test. Fix the fixture's diagram or its `Depends on` field. |
| G2 | low | `dx.md` promises "Present `tasks.md` is invalid → exit non-zero", but the resolver validates only the closure contract via `--slice-contract-json`; a `tasks.md` failing the diagram cross-check still resolves. Spec AC-07 and MAS-IT-005 both scope this to the closure contract, so the code matches the spec and the `dx.md` wording overstates it. Narrow the `dx.md` row. |
| G3 | low | `_parse_closure_table` terminates its scan on `^#{1,2}\s+` only. A `###` heading immediately after the closure table would leave the parser consuming pipe rows from later sections as closure rows. Unreachable under the canonical template ordering (`## Vertical Slice Closure` → `## Execution Plan`), and no test pins it. |
| G4 | low | The `parse_tasks` heading reset means a task body containing any sub-heading silently drops its trailing `Depends on` / `Tests` / `Gate` / `Slice` fields, surfacing as `exactly one non-empty Slice field is required` rather than naming the real cause. No test covers the sub-heading case. Consider resetting only on `#{1,4}` task-or-section-level headings, or documenting the constraint in the template. |
| G5 | nit | `_derived_slice_count` reaches the validator by `subprocess` + `Path(__file__).resolve().parents[2]`. A relocated validator degrades to the generic `tasks closure validation failed`. An in-process import of `validate_tasks.validated_slice_contract` (already importable — `tools/test_parallel_plan.py` does exactly that) would be shorter and fail more loudly. |

## Verdict

**PASS.** All 12 acceptance criteria and all 17 test-contract rows map to asserting tests that assert
the spec-defined outcome. All five named gates return exit code 0, including the full `bun run
test:all`. All seven required mutants were killed by the suite the packet named. The `dx.md` contract
shape, ordering, optionality, and error text match the implementation. The frozen QA scenario set and
the instruction-budget files are untouched. No mutant, edit, or fix was left in the tree
(`git status --porcelain` clean apart from the pre-existing untracked `.gate-cache/` and this file).
