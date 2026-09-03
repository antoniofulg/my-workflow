---
id: CFG-derive-merge-alone-slices
area: CFG
title: Derive the slice count from merge-alone outcomes
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver derives the slice count from the validated vertical-slice closure contract in `tasks.md` and groups those slices under the cadence configured in `.my-workflow.toml`; it uses one slice when Tasks was skipped, treats `--slices` as an assertion only, and returns the frozen snapshot on normal resume.
entry_points: python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider>; python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider> --slices <expected-count>; python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider> --refresh; python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py <tasks.md> --slice-contract-json; python3 .agents/skills/workflow-config/scripts/parallel_plan.py; .agents/skills/wtasks/references/tasks-template.md; .agents/skills/workflow-config/SKILL.md; README.md
qa_status: pass
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence: docs/qa/evidence/2026-09-02-merge-alone-slices/01-gate-test-all.log; docs/qa/evidence/2026-09-02-merge-alone-slices/22-ch2-mutations.log; docs/qa/evidence/2026-09-02-merge-alone-slices/30-ch3-freeze-refresh.log; docs/qa/evidence/2026-09-02-merge-alone-slices/43-ch4-equality.log
last_report: docs/qa/reports/2026-09-02-merge-alone-slices.md
overlaps: CFG-resolve-deep-review-cadence; CFG-freeze-feature-workflow
---

New promise from merge-alone slice derivation. The manual slice count is no longer a source of
truth: a present `tasks.md` declares one `**Slice:**` field per primary `T<number>` task and one
`## Vertical Slice Closure` row per used slice, with `yes` as the only accepted merge-alone value,
and the resolver derives its count from that validated contract.

What the walk has to distinguish is a count that is *derived* from one that is *supplied*. Five
primary tasks organized into three technical phases are still one slice when only the complete
migration would be merged; two capabilities that each ship alone are two. Review remediation records
such as `T2R1` are not mergeable outcomes and never raise the count, even when they carry a slice
field of their own.

The failure this scenario exists to catch is a resolver that writes a snapshot it should have
refused. A `--slices` value that disagrees with the derived count, a zero or negative value, and a
malformed closure contract must each exit non-zero naming the cause while leaving any existing
`workflow.json` byte-for-byte unchanged. A feature directory with no `tasks.md` resolves to exactly
one slice rather than failing.

Resume is the other half of the promise: while a valid snapshot exists and `--refresh` was not
requested, the resolver returns that frozen snapshot without reading current tasks, so a task
document that changed — or became malformed — after the freeze cannot move an in-flight feature's
cadence. Only explicit `--refresh` re-derives, and it replaces the snapshot atomically on the same
schema.

The authoring surface is part of the same promise. The installed task template is what an adopter
reads before writing a slice field, so it has to name the three planning units apart — a vertical
slice is a merge-alone outcome, a phase or cohort is technical ordering, a batch is worker capacity —
and neither `README.md` nor the `workflow-config` skill may still present `--slices` as the source of
truth. A copy-pasteable invocation that no longer matches the resolver is a broken promise even when
the resolver is correct.

Downstream consumption closes it. The parallel planner reads the resolver's snapshot and must report
the same primary-task membership the validator derived, over every heading shape the validator
accepts, and must ignore a review remediation record such as `T2R1` field-for-field, so the preceding
task's status, resources, and dependencies are what they would be with the record absent.

Walked 2026-09-02 through the CLI/manual adapter in a disposable repository built from `dfdf227`:
derived counts, twelve one-defect refusals with before/after snapshot hashes, resume-versus-refresh
freezing, and planner membership equality. See the report for the matrix and limitations.
