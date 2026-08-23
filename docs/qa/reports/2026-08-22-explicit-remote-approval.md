# QA report — explicit remote approval — 2026-08-22

## Session

- **Adapter:** CLI/manual repository inspection plus disposable local adoption
- **Exact path:** `README.md` → canonical workflow sources → `scripts/adopt.py <temporary-target>`
  → installed `AGENTS.md` and `.agents/skills/autonomous/SKILL.md`
- **Environment:** macOS checkout-local shell; Node `v22.23.1`; no server, auth, or remote mutation
- **Scope:** Filed issue #25 — readiness evidence must not grant remote authority
- **Evidence:** `docs/qa/evidence/2026-08-22-explicit-remote-approval/session.md`
- **Preflight gate:** `npm test -- --run tools/shared/tests/remote-approval.test.ts` — 2/2 passed
- **Limitation:** No automated agent-execution harness exists. QA observes the installed contracts;
  live model compliance remains a manual observation.

## Matrix

| Charter | Scenario | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CH-remote-delivery-approval-2026-08-22` | `DOC-require-explicit-remote-action-approval` | pass | Source reload plus byte-identical adopted agent contracts | session.md |
| `CH-remote-delivery-approval-2026-08-22` | `DOC-read-explicit-workflow-provenance` | pass | README and lockfile read independently after adoption | session.md |

## Walk and probes

| Probe | Expected | Observed |
| --- | --- | --- |
| Canonical boundary | Every public workflow source separates readiness from authority | Present in all five canonical sources |
| Exact push authority | Push requires explicit current-session authorization | Present |
| Exact PR authority | Pull request creation requires separate authorization | Present |
| Exact merge authority | Merge requires separate authorization | Present |
| Autonomous invocation | Invoking `autonomous` alone grants no remote authority | Explicitly denied |
| Sequential authority | Authorization for one action does not imply the next | Explicitly denied; skill performs only that action, then re-checks |
| Unauthorized next action | Readiness stops and reports the action awaiting authorization | Present |
| Adopted bytes | Consumer receives the corrected contracts | `cmp` passed for `AGENTS.md` and autonomous skill |
| Provenance canary | Credits and external-skill boundary remain visible | Three credits and three separately pinned external skills confirmed |
| Neutrality canary | Package introduction names no consuming product or stack | Confirmed |

## Debrief

**pass.** Readiness and `autonomous` invocation stop before every unauthorized remote action. Push,
pull request creation, and merge each require an exact, current-session authorization, and one does
not authorize the next. The adopted consumer receives the same contract. Provenance, external-skill
separation, and product neutrality remain intact.

The first attempt expected source-only documentation in the adopted target; the clean retry then
used an overly broad lockfile predicate. These were adapter assumptions, not product defects. The
focused public reads completed every planned probe.

## Evidence and gates

- `npm test -- --run tools/shared/tests/remote-approval.test.ts` — 2/2 passed
- `python3 scripts/adopt.py <temporary-target>` plus `cmp` — adoption and reload passed
- Focused README/`skills-lock.json` inspection — five canary assertions passed
- `git diff --check` — passed before report close
- Full gate: `npm test` — 11/11 files and 142/142 tests passed
