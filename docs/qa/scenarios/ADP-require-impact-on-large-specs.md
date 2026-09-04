---
id: ADP-require-impact-on-large-specs
area: ADP
title: Require Impact on Large and Complex specs
persona: Workflow adopter
journey: J-adopt-workflow
expected: The adopted validate_spec CLI exits non-zero naming ## Impact for a Large or Complex spec that lacks that section, and does not require the section for Medium, Small, or a Large spec whose Impact is none.
entry_points: .agents/skills/workflow-spec-driven/scripts/validate_spec.py; tools/fixtures/tlc-validator/spec-size-large-no-impact.md; tools/fixtures/tlc-validator/spec-size-complex-no-impact.md; tools/fixtures/tlc-validator/spec-size-medium-no-impact.md; tools/fixtures/tlc-validator/spec-size-small-no-impact.md; tools/fixtures/tlc-validator/spec-size-large-impact-none.md
qa_status: untested
bug_ids:
fix_status:
retest_status:
fix_commits:
evidence:
last_report:
overlaps: ADP-validate-generated-feature-contracts
---

New promise from `specify-impact-designer`. Size on the spec header line gates the Impact
section. Copy the five size fixtures into a disposable target and run the adopted
`validate_spec.py` against those copies.

`ADP-validate-generated-feature-contracts` still owns TLC layouts and SHALL. This scenario
owns only the size-aware Impact rule.
