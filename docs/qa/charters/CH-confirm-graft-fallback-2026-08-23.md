# CH-confirm-graft-fallback-2026-08-23

- **Date:** 2026-08-23
- **Time-box:** 10 minutes
- **Persona:** Workflow operator
- **Journey:** [`J-run-deep-review`](../journeys/J-run-deep-review.md)
- **Tour:** Adjacent optional-context canary
- **Public entry point:** `.agents/skills/deep-review/SKILL.md`
- **Adapter candidate:** Manual agent-file inspection
- **Scenarios:** `QAS-use-graft-context-with-plain-fallback`

## Mission

Re-read the existing Graft contract as the adjacent canary. Confirm the new general recommendation
does not make Graft mandatory or remove plain repository inspection when Graft is absent, fails,
becomes stale, or cannot cover selected paths.

## Expected observable

Deep Review still uses Graft only as optional orientation and always exposes an honest plain
repository-inspection fallback.

## Planned probes

- Compare README's optional-integration wording with the Deep Review skill.
- Confirm missing, failed, stale, and partial-coverage paths retain plain-inspection guidance.
- Confirm no adoption or tool-install step became mandatory.

End before running Deep Review or changing product files.
