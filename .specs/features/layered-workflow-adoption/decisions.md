# Layered Workflow Adoption Decisions

## Decisions provided by the human

| Decision | Why | Rejected alternatives | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Existing projects must be able to adopt the workflow incrementally. | Monolithic adoption is difficult to review and integrate safely. | Continuing the all-or-nothing copier. | Remove the layered CLI, manifest, managed blocks, and documentation. | Maintainers choose layers and review a plan before applying. |
| Parallel execution is the default when task division and machine conditions permit it. | The workflow should optimize delivery speed without forcing unsafe writers. | Always sequential or always creating worktrees. | Change the workflow route and parallel layer contract. | A feature with one shared writer still executes serially. |

## Decisions made during implementation

| Decision | Why | Rejected alternatives | Cost to change now | User cost today |
| --- | --- | --- | --- | --- |
| Ship four fixed layers: `core`, `parallel`, `quality`, and `extras`; `full` is a profile. | Fixed dependencies prevent invalid arbitrary skill combinations. | Plugin framework, user-defined graph, or individual-file selection. | Add a versioned layer/schema migration and expand every CLI/test contract. | `parallel`, `quality`, and `extras` include `core` automatically. |
| Make v1 additive and update-only; omitted installed layers are retained. | Automatic removal needs stronger recovery and ownership semantics. | Replacing the selected set or deleting omitted layers. | Design and verify a separate remove command. | Uninstalling a layer remains manual and unsupported. |
| Track per-file and managed-block ownership in `.my-workflow/adoption.json`. | Hash proof allows safe updates, drift status, and conflict detection with the standard library. | Whole-directory ownership, timestamps, or a database. | Introduce a new manifest schema and migration. | Consumer edits to managed content must be reconciled before apply. |
| Preserve consumer instructions through delimited managed blocks. | Existing AGENTS/CLAUDE prose belongs to the project. | Whole-file replacement or stencil-only adoption. | Migrate block markers and their hashes. | Broken or edited markers fail closed until repaired. |
| Hard-cut the positional CLI in favor of `plan`, `apply`, and `status`. | A public preview/status boundary is required for safe existing-project adoption. | Compatibility alias for `adopt.py TARGET`. | Reintroduce and maintain a second command path. | Callers must update to explicit subcommands and `--layers`. |
| Keep the adopter in one Python module and execute its shared-writer slice serially. | The boundary is cohesive and splitting it would add a framework while creating merge conflicts. | Multiple adopter modules solely to manufacture parallelism. | Extract modules if independent consumers or measurable maintenance pressure appear. | Implementation wall time was serial; review and QA still used fresh parallel roles. |

