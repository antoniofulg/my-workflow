# Bun tooling runtime — QA Execute

- **Date:** 2026-08-29
- **Reviewed HEAD:** `1f44ad358fb717b440cd5497f07dda115d55eba1`
- **Personas:** Repository reader; Workflow adopter
- **Adapter:** CLI/manual through documented Bun, adoption, package, knowledge, assisted-probe,
  and external-security entry points with independent filesystem readback
- **Environment:** active feature checkout plus checkout-owned disposable targets; Bun 1.4.x;
  network disabled by session boundary
- **Raw evidence:** `docs/qa/evidence/2026-08-29-bun-tooling-runtime/`
- **Live Orca:** not invoked

## Gate

Opening command:

```text
bun run test:all
```

Exit `1`. Bun reported 121 passes, 1 failure, and 1113 assertions across 8 suites. The failing
contract was `IT-006 keeps Bun as the active command authority while allowing historical evidence`:

```text
expected []
received [CH-adopt-bun-tooling-runtime-2026-08-29.md,
          CH-enable-bun-security-skills-2026-08-29.md,
          CH-review-bun-tooling-runtime-2026-08-29.md]
```

The Python leg did not run because the Bun leg failed. Raw output:
`docs/qa/evidence/2026-08-29-bun-tooling-runtime/opening-gate.txt`.

## Matrix

| Charter | Scenarios | Verdict | Independent readback |
| --- | --- | --- | --- |
| `CH-review-bun-tooling-runtime-2026-08-29` | `REL-report-current-workflow-release` | fail | Documented full gate failed before release/package readback |
| `CH-adopt-bun-tooling-runtime-2026-08-29` | `REL-report-current-workflow-release`; `ADP-adopt-workflow-safely` | untested | Stopped before adoption after opening product defect |
| `CH-enable-bun-security-skills-2026-08-29` | `REL-report-current-workflow-release`; `ADP-install-pinned-external-security-skills`; `ADP-preserve-security-install-target` | untested | Stopped before no-write/fail-closed walk; authorized success also lacks authority |

## Charter results

`CH-review-bun-tooling-runtime-2026-08-29` failed at its documented full-gate entry point. The
history guard compares all current QA artifacts with baseline `69914e831cb8`, then classifies paths
under `docs/qa/charters/` as historical even when those paths did not exist at the baseline. It
therefore rejects the current cycle's three immutable charters.

Filed
[`BUG-20260829-bun-history-gate-rejects-new-qa-charters`](../bugs/BUG-20260829-bun-history-gate-rejects-new-qa-charters.md).
Per QA fix-loop, execution stopped before adoption, package inspection, knowledge, probe-import, or
security-installer walks. Existing adjacent-canary verdicts remain historical and were not changed.

## Edge probes and experience lenses

No edge probe or experience-lens pass ran after the opening defect. No success was inferred from
technical validation.

## Limitations

Successful external-security installation is not authorized in this cycle. Its networked/write leg
will remain `untested`; no fake success will replace it. No browser, API, mobile, server, publish,
release, live Orca, or registry surface is in scope.

## Cleanup and closing gate

No disposable product target or worktree was created. Raw evidence is confined to the ignored
cycle directory. Source changes are the durable report, one bug record, and the failed release
scenario update. Closing gate was not repeated because the same unfixed deterministic defect would
produce the same result; the opening command is the terminal gate evidence for this session.

**Cycle verdict:** fail. Fresh QA Execute must rerun all three charters after an Implementer fixes
the history guard. Successful external-security installation remains separately `untested` without
network/write authorization.
