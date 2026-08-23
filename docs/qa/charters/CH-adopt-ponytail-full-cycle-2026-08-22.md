# CH-adopt-ponytail-full-cycle-2026-08-22

- **Date:** 2026-08-22
- **Time-box:** 10 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Ponytail full-cycle instruction and authority boundaries
- **Public entry point:** `README.md` → **Adopt the workflow** → `scripts/adopt.py`
- **Adapter candidate:** CLI/manual through the public adoption script and filesystem inspection
- **Scenarios:** `ADP-adopt-workflow-safely`, adjacent canary `DOC-read-explicit-workflow-provenance`

## Mission

Adopt into a checkout-local disposable target. Read the installed agent instructions as a workflow
operator would and confirm Ponytail starts before Specify, remains active through every workflow
phase and delegated prompt, and stops only on the two explicit human commands.

## Expected observable

The public adoption prompt activates Ponytail at workflow start, installed `AGENTS.md` owns the
full-cycle rule, the installed Ponytail skill owns persistence and stop commands, and the copied
workflow loop summarizes those authorities without replacing them.

## Planned probes

- Read the public adoption prompt and confirm it activates Ponytail at workflow start.
- Adopt into a fresh disposable target and inspect its installed `AGENTS.md`.
- Confirm the installed rule names Specify, Design, Tasks, Execute, subagent prompts, fixes, and
  reviews, with `stop ponytail` and `normal mode` as the only explicit exits.
- Inspect the installed Ponytail skill for the persistent `ACTIVE EVERY RESPONSE` contract.
- Inspect the copied workflow loop and confirm it points to `AGENTS.md` for activation/session scope
  and to the Ponytail skill for persistence/stop authority, without carrying a competing rule.
- Adjacent canary: confirm the public README still distinguishes the workflow's bundled local skills
  from separately authorized external security skills.

End before product remediation. A confirmed defect returns to an Implementer.
