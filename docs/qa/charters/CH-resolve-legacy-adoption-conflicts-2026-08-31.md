# CH-resolve-legacy-adoption-conflicts-2026-08-31

- **Date:** 2026-08-31
- **Scope:** `3113066..ddcc3b889bad` for `legacy-adoption-resolution`
- **Time-box:** 35 minutes
- **Persona:** Workflow adopter
- **Journey:** [`J-adopt-workflow`](../journeys/J-adopt-workflow.md)
- **Tour:** Reviewed legacy ownership transfer with refusal and normal-command canaries
- **Public entry point:** `README.md` → Resolve a legacy no-manifest conflict → `scripts/adopt.py plan/resolve/status/apply`
- **Adapter candidate:** Existing CLI/manual disposable adoption path declared by [`docs/qa/README.md`](../README.md)
- **Scenario:** [`ADP-resolve-legacy-adoption-conflicts`](../scenarios/ADP-resolve-legacy-adoption-conflicts.md)
- **Adjacent canary:** [`ADP-layered-workflow-adoption`](../scenarios/ADP-layered-workflow-adoption.md)

## Mission

Start from a checkout-owned disposable Git project that contains divergent tracked workflow files
but no adoption manifest. Review the read-only plan, authorize the exact file-conflict set, and
confirm the project becomes cleanly managed without replacing its instruction prose.

## Expected observable

Incomplete or invalid replacement sets and unsafe target states exit with the documented code and
leave an independently reloaded tree unchanged. An exact replacement set reports every reviewed
path as `replace`, publishes a schema-1 manifest, preserves both instruction files, reaches clean
`status`, and remains byte-stable under normal re-apply.

## Criterion disposition

- `LAR-01`: public promise → primary scenario; invoke the separate documented `resolve` verb.
- `LAR-02`: public promise → primary scenario; only the exact complete conflict set publishes.
- `LAR-03`: public promise → primary scenario; output reports each replacement and status reloads clean.
- `LAR-04`: public promise → primary scenario; incomplete and invalid authorizations use exits `1`/`2` with zero writes.
- `LAR-05`: mixed disposition → primary scenario covers non-Git, missing-`HEAD`, and dirty targets; the exact pre-publication Git recheck remains technical verification because exercising that race needs internal control.
- `LAR-06`: mixed disposition → primary scenario observes manifest-last atomic success; injected publication-failure restoration remains technical verification because the public adapter has no fault-injection interface.
- `LAR-07`: public promise → primary scenario; `--skip-agents` preserves `AGENTS.md` and `CLAUDE.md` byte-for-byte.
- `LAR-08`: public promise → primary scenario; a manifest-backed target refuses unchanged.
- `SEC-001`: public trust promise → primary scenario; absolute, escaping, separator-trick, and managed-block replacement values refuse unchanged.
- `SEC-002`: public trust promise → primary scenario; disposable leaf and parent symlink probes cannot alter the target or external referent.
- `SEC-003`: internal disposition → direct argument-vector construction is an implementation mechanism covered by technical verification; QA checks only the public no-unexpected-process-or-file effect with literal metacharacter names.
- Existing `plan`/`apply`/`status` contract: adjacent canary → `ADP-layered-workflow-adoption`.

## Planned walk

1. Record source-checkout status. Create a separate checkout-owned disposable Git target with
   `HEAD`, divergent tracked catalog files, and consumer prose in both instruction files; record an
   independent byte, mode, symlink, and Git-state snapshot.
2. Enter through the README. Run text and JSON `plan` for the selected layers twice; require stable
   conflicts/actions, parseable JSON-only stdout, and a byte-identical target.
3. Attempt an incomplete replacement set; require exit `1`, every unresolved conflict in output,
   and the original snapshot. Attempt extra, duplicate, absolute, escaping, separator-trick, and
   managed-block values; require exit `2` and the same snapshot.
4. On separate disposable copies, attempt resolve against non-Git, missing-`HEAD`, dirty,
   manifest-backed, replaceable-leaf symlink, parent symlink, and `.claude` parent-symlink states;
   require exit `2`, unchanged target snapshots, and unchanged external referents.
5. Return to the clean committed target. Resolve the exact sorted conflict set with `--skip-agents`
   and JSON output; require exit `0`, every authorized action `replace`, empty conflicts, sorted
   replacements, and a schema-1 manifest after independently reloading the filesystem.
6. Require both instruction files byte-identical, `status` exit `0`, and no staging or transaction
   residue. A second `resolve` must exit `2` unchanged because the manifest now exists.
7. Run the adjacent normal-command canary: read-only `plan`, byte-stable `apply` of the same layers,
   clean `status`, then one reversible managed-file drift producing status exit `1` without writes.
8. Use literal shell metacharacters only inside checkout-owned target/path names; require no extra
   process marker or external file effect. Do not simulate internal publication failures.
9. Remove only disposable targets. Require source-checkout status to differ from preflight only by
   planned durable QA execution artifacts.

## QA Execute handoff

Use a fresh Verifier session with the canonical `qa-execute` skill. Read
[`docs/qa/README.md`](../README.md), this charter, both linked scenarios, and
`docs/guidelines/QA-SCENARIOS.md`. Use only the existing CLI/manual adapter via
`scripts/adopt.py` against separate checkout-owned disposable Git targets. Record raw evidence under
`docs/qa/evidence/2026-08-31-legacy-adoption-resolution/` and one durable dated report/status update.
Do not touch active CRM or Creatista checkouts, invoke live Orca, install packages or external
skills, use network access, or add a runner. Exact injected rollback, hostile process races, and
direct-argv implementation proofs remain technical-verification limitations.
