---
id: CFG-derive-merge-alone-slices
area: CFG
title: Derive the slice count from merge-alone outcomes
persona: Workflow adopter
journey: J-configure-feature-workflow
expected: The resolver derives the review cadence from the validated vertical-slice closure contract in `tasks.md`, uses one slice when Tasks was skipped, treats `--slices` as an assertion only, and returns the frozen snapshot on normal resume.
entry_points: python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --feature <slug> --native-provider <provider>; --slices <expected-count>; --refresh; python3 .agents/skills/workflow-spec-driven/scripts/validate_tasks.py <tasks.md> --slice-contract-json
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
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
