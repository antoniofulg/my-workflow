# Task 04 memory

- README now has one adoption prompt with new/existing project branches, clean-state and
  read-only capability discovery, managed-path review, diff/gate evidence, and user-visible QA
  routing.
- `docs/qa/README.md` is the stack-specific operational profile template. It records interfaces,
  adapters and their manifest/CI authority, start/health, auth, fixtures, cleanup/residue, raw
  evidence, and limitations without prescribing a framework or commands.
- `scripts/adopt.py` copies both project-owned QA skills and creates the profile only when absent;
  re-adoption preserves a consumer-owned profile. Adoption smoke checks cover skills, links,
  ignore merging, and profile preservation.
- README provenance credits Tech Leads Club for TLC Spec Driven/security skills and Pedro Nauck for
  Deep Review plus the `qa-report`/`qa-execution` inspirations. Product-specific names and stack
  leakage were removed.
- Package and lockfile root versions are `0.3.0`. The full offline suite passes 55/55.
