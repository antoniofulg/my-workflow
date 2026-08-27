# Workflow tour

Human-facing. Agents run [`AGENTS.md`](../../AGENTS.md) and load a guideline only when its
condition fires. This folder is the **why**: what each stage is for, what each guideline
protects, and which trade-off it encodes.

These pages do not restate the rules. The guidelines remain the source of truth for behaviour.

Cross-provider session continuation is owned by the host. Repository files, Git state, feature
artifacts, and explicit handoff prompts remain the durable semantic context.

Structural TypeScript checks for this source pack run on Bun 1.4 from the repository-local `./tools`
discovery root; npm remains the package and lockfile owner. Adopted consumers retain their own
runner and configuration.

## Walk this in order

1. [Purpose — delivery and reliability](purpose.md)
2. [The loop — stages from spec to merge](loop.md)
3. [Reviews — three questions, hard caps](reviews.md)
4. [Decisions — two namespaces, halt vs decide](decisions.md)
5. [Guidelines — why each file exists](guidelines.md)
6. [Skills, knowledge, adopt](pack.md)

## Map

| You want | Read |
| --- | --- |
| The thesis | [purpose.md](purpose.md) |
| Specify → slice → gate → PR | [loop.md](loop.md) |
| Verifier, QA, deep-review, filed issues | [reviews.md](reviews.md) |
| `AD-NNN` vs architecture invariants | [decisions.md](decisions.md) |
| One paragraph per guideline | [guidelines.md](guidelines.md) |
| What is vendored and what is not | [pack.md](pack.md) |
| The imperative rules | [`docs/guidelines/`](../guidelines/) |
| What agents load every turn | [`AGENTS.md`](../../AGENTS.md) |

## The loop at a glance

```
per slice    implement → scoped gate → atomic commit
             Verifier fingerprint cap  →  QA walk if user-visible
resolved     deep-review groups from workflow config, before QA

feature      QA session (no product code)
then         full gate → pull request
```

Public hierarchy: `Feature -> Vertical Slice -> Task`. Read
`.agents/skills/workflow-config/SKILL.md` before dispatch; it resolves cadence and delegated providers.

Repeated review blockers use the immutable fingerprint and independent counter in
[`REVIEW-ROUNDS.md`](../guidelines/REVIEW-ROUNDS.md); this guide does not duplicate that protocol.

A filed issue skips the ceremony: `implement → scoped gate → one commit`.
Credential-free declarative agent-tool configuration uses the local light path in
[`GATES.md`](../guidelines/GATES.md).
