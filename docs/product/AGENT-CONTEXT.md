# Agent context

This repository is the my-workflow source pack for a stack-agnostic agent operating system. Product identity
belongs in consuming projects; this index routes source-pack work without loading product history.

## Critical constraints

- Keep shared workflow instructions product-neutral and preserve consumer-owned product context.
- Use the smallest role- and task-specific reference set; surface missing required context as a gap.
- Keep task classification, safety, QA, review, role separation, and permission boundaries intact.

## Role/task routes

| Role or task | Read only |
| --- | --- |
| Button color correction | `docs/guidelines/UI-UX.md`; `docs/guidelines/FRONTEND.md` |
| Customer-facing copy | [unset — source pack has no customer voice reference; consuming projects fill this route] |
| Boundary change | `docs/guidelines/MODELING.md`; `docs/guidelines/DX.md` |
| Planner, other feature | `README.md#purpose`; `docs/workflow/README.md`; affected capability/journey docs |
| Implementer | Approved slice; `AGENTS.md#critical-rules`; relevant architecture/design docs |
| Reviewer or verifier | `docs/guidelines/REVIEW-ROUNDS.md`; `docs/guidelines/VERIFICATION-EVIDENCE.md`; assigned spec/tests |
| Unknown scope or dependency | `docs/guidelines/CONTEXT-BUDGET.md`; add affected reference with an explicit reason |
