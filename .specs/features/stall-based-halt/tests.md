# Stall-Based Halt Test Contract

The instruction documents are this pack's product contract, so doc-content cases are the owning
layer here (`TEST-CONTRACT.md`, "allowed only when that artifact is the product contract"). The
resolver is ordinary code and gets ordinary unit cases.

## Unit

Canonical suite: `tools/test_workflow_config.py`. Invariant: the resolver accepts exactly the
configuration surface it documents, and rejects the rest by name.

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Absent config resolves the default | no `.my-workflow.toml`, resolve a feature | exit 0, resolved output reports `stall_attempts` 3 |
| UT-002 | Absent table resolves the default | `.my-workflow.toml` with `[deep_review]` only | exit 0, resolved output reports `stall_attempts` 3 |
| UT-003 | Empty table resolves the default | `[remediation]` with no keys | exit 0, resolved output reports `stall_attempts` 3 |
| UT-004 | A declared value is resolved | `[remediation] stall_attempts = 5` | exit 0, resolved output reports `stall_attempts` 5 |
| UT-005 | Zero resolves as unbounded | `[remediation] stall_attempts = 0` | exit 0, resolved output reports `stall_attempts` 0 |
| UT-006 | A non-integer is rejected | `stall_attempts = "3"` | exit non-zero, message contains `remediation.stall_attempts` |
| UT-007 | A negative value is rejected | `stall_attempts = -1` | exit non-zero, message contains `remediation.stall_attempts` |
| UT-008 | An unknown key is rejected by name | `[remediation] attempts = 3` | exit non-zero, message names `attempts` |
| UT-009 | The threshold is not frozen | resolve a feature with `[remediation] stall_attempts = 5` | `.specs/features/<feature>/workflow.json` contains no `remediation` key and still validates on resume |

## Integration

Canonical suite: `tools/shared/tests/qa-skills.test.ts`. Invariant: the halt rule stated in the
guideline and the halt rule stated in the `autonomous` skill are the same rule.

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-027 | The escalation rule bounds by progress, not by rounds | read `docs/guidelines/REVIEW-ROUNDS.md` `## Escalation` | states that a changed failure signature continues remediation without new authorization; no longer stops on an open blocker alone |
| IT-028 | The stall bound and its default are stated | read `docs/guidelines/REVIEW-ROUNDS.md` `## Escalation` | names `stall_attempts`, the default `3`, and `0` as unbounded |
| IT-029 | The autonomous halt condition matches the guideline | read `.agents/skills/autonomous/SKILL.md` halt conditions | the blocker condition is the stall condition and cites `docs/guidelines/REVIEW-ROUNDS.md` |
| IT-030 | Remote authorization is untouched | read `.agents/skills/autonomous/SKILL.md` halt conditions | the unauthorized-next-remote-action halt is still present and unchanged |
| IT-026 | The config surface is documented where it is read, and the snapshot is not confused with the output | read `.agents/skills/workflow-config/SKILL.md`, `.my-workflow.toml.example`, and `docs/qa/scenarios/CFG-freeze-feature-workflow.md` | the skill and the example both carry `[remediation] stall_attempts` with the default and the `0` meaning; the skill and the scenario both state the JSON output is the snapshot plus the resolved-now `remediation`, and neither equates the two artifacts |

## End-to-end

None. No user journey crosses this change: the product surface is instruction text and a resolver
exit code, and both are discriminated more cheaply above.

## Security

None. This feature declares no security surface — it changes when a local loop stops, and every
remote action keeps the authorization it already had (`SECURITY.md` does not fire on a change with
no new surface).

## Assignment

| Slice | Tasks own | IDs |
| --- | --- | --- |
| 1 — resolver learns `[remediation]` | resolver validation and resolved output | UT-001 … UT-009, IT-026 |
| 2 — the halt rule becomes a stall rule | guideline and skill wording | IT-027 … IT-030 |

Every ID appears in exactly one slice. No orphans.
