# Merge-Alone Slice Derivation — Decisions (2026-09-02 re-port)

Everything this run chose while nobody was watching. Human-handed decisions first, then the ones the
run made on its own.

## Handed down by the human

| Decision | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- |
| Re-port merge-alone derivation as its own feature after the local/origin reconciliation, instead of inside the reconciliation merge | The 2026-08-27 implementation targeted the removed `tlc-spec-driven` skill and the pre-rewrite resolver; porting inside a 300-commit merge would have hidden any port error | Porting inside the merge commit | One branch and one pull request | None; the reconciled `main` shipped without derived counts for one day |
| Keep the existing spec, design, and test contract; re-plan only what the new base changed | The contract (closure table, `**Slice:**`, optional `--slices`, resume-first) was already approved and QA-walked | Rewriting the spec from scratch | Editing the spec again | None |

## Made by the run

### Planning

| Decision | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- |
| Drop the two snapshot-version acceptance criteria (old AC-12/13, `MAS-IT-010..012`) and fold planner acceptance into one AC-12 | The resolver already writes version 3 and every consumer already rejects other versions with tests; this feature adds no schema field | Re-asserting version checks that exist | Adding one AC back | None |
| One merge-alone slice, four sequential tasks | The validator, resolver, and published template are one usable outcome; none ships alone | Two slices (contract vs docs) | Re-freezing `workflow.json` | None |
| Mint a new QA scenario (`CFG-derive-merge-alone-slices`) instead of editing the frozen CFG scenarios | `IT-006` freezes every scenario present at the reconciliation merge | Editing `CFG-freeze-feature-workflow` and bumping the baseline again | Deleting one file | The derived-count promise is tracked on its own file rather than folded into the freeze scenario |

### Implementation (disclosed by the Implementer, judged by the Verifier)

| Decision | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- |
| Keep the current `TASK_RE` (`^#{2,4}\s+(T\d+)\s*:`) and reset the current task on every heading so `T2R1` records donate no fields | The current validator is the shipped authority; the reset is what makes remediation records inert (MAS-10) | Porting the old `###`-only heading rules and `_task_breakdown_syntax_errors` | Small validator change | A task body containing a sub-heading loses trailing fields with a misleading message (Verifier G4, unpinned) |
| Rewrite existing resolver tests that asserted `--slices > 1` to carry a matching derived `tasks.md` | `--slices` no longer owns the count (MAS-05); each test keeps its original invariant | Keeping manual counts alive for tests only | None | None |
| `_derived_slice_count` shells out to `validate_tasks.py --slice-contract-json` | The design chose the validator CLI as the one executable authority and the resolver already runs subprocesses | Importing `validated_slice_contract` directly (Verifier G5) | One function | One extra interpreter start per initial resolution or refresh |

### Follow-ups (not blocking; from the Technical Verifier)

- G3: `_parse_closure_table` stops only at `#`/`##`; a `###` after the table is unreachable under the template but unpinned.
- G4: sub-heading inside a task body drops trailing fields (see above).
- G5: subprocess vs direct import in `_derived_slice_count`.
- Every other `.specs/features/*/tasks.md` now fails `check()` for a missing closure section. Intentional hard cut recorded in `design.md` § Risks; normal resume never re-validates them.
