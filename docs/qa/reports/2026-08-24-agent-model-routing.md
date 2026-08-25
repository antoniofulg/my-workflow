# QA Execute — agent model routing

- **Date:** 2026-08-24
- **Charter:** [`CH-agent-model-routing-2026-08-24`](../charters/CH-agent-model-routing-2026-08-24.md)
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual through checkout-local disposable Git repositories, `workflow_config.py`, `scripts/adopt.py`, and independent filesystem/JSON inspection
- **Environment:** macOS workstation; active checkout `/Users/antoniofulg/Projects/my-workflow-ai-memory-handoff`; no server, browser, API, auth, or networked installer
- **Entry path:** `.my-workflow.toml` → `.agents/skills/workflow-config/scripts/workflow_config.py --sync-agents` → feature resolve/resume/refresh; `README.md` → `scripts/adopt.py`
- **Preflight automated gate:** technical validation records `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py` at exit 0 with 108 Vitest + 17 adoption + 28 resolver = 153 passed, 0 failed, 0 skipped
- **Final automated gate:** same exact command exited 0 with 108 Vitest + 17 adoption + 28 resolver = 153 passed, 0 failed, 0 skipped
- **Raw evidence:** `docs/qa/evidence/2026-08-24-agent-model-routing/`

## Matrix

| Scenario | Scope | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CFG-centralize-agent-model-routing` | Complete v2 matrix, sync, preservation, idempotence, invalid inputs, CLI reporting, docs | pass | Independent TOML/native parsing, metadata-stripped hashes, second-run tree hash, and docs reload | [`qa-execute-session.md`](../evidence/2026-08-24-agent-model-routing/qa-execute-session.md) |
| `CFG-freeze-feature-workflow` | Resolve, frozen snapshot, drift rejection, explicit refresh, planner exclusion | pass | CLI stdout matched reloaded `workflow.json`; model and effort drift each rejected before explicit refresh | [`qa-execute-session.md`](../evidence/2026-08-24-agent-model-routing/qa-execute-session.md) |
| `CFG-resolve-deep-review-cadence` | v2 cadence and balanced groups canary | pass | `grouped.2` with six slices reloaded as `[[1,2],[3,4],[5,6]]` | [`qa-execute-session.md`](../evidence/2026-08-24-agent-model-routing/qa-execute-session.md) |
| `ADP-adopt-workflow-safely` | Fresh, existing-config, malformed-packet, and residue canary | pass | Fresh target inspection, byte/hash comparison after re-adoption, Git visibility, and malformed-packet no-write check | [`qa-execute-session.md`](../evidence/2026-08-24-agent-model-routing/qa-execute-session.md) |

## Probe results

1. **PASS — central matrix and first sync.** One model/effort pair per provider was changed. Sync
   reported the exact three packet paths and twelve already-current paths. Independent parsing
   matched all fifteen packets to TOML, while metadata-stripped hashes proved all packet instructions
   were unchanged.
2. **PASS — idempotence.** Second sync reported zero changed and fifteen unchanged. Full packet-tree
   SHA-256 remained `489f9678900e8ea1b7dcbe19ee451cec1a9df294a06fce10d75595e2ffabd1eb`.
3. **PASS — six recovery edges.** Missing role, unknown role, invalid effort, duplicate metadata,
   missing metadata, and sync/resolution argument conflict each exited `2`, emitted one actionable
   diagnostic, wrote no stdout, and changed no packet bytes.
4. **PASS — frozen resolution and resume.** Resolution stdout equalled independently reloaded JSON.
   Four delegated roles included provider, agent file, model, and effort; planner remained absent.
   An unsynchronized config replacement did not alter resume output.
5. **PASS — drift and explicit refresh.** Synchronized model drift and effort drift each made ordinary
   resume exit `2` with sync/explicit-refresh guidance. Each explicit refresh persisted the new
   value and again matched reloaded JSON.
6. **PASS — cadence canary.** v2 `grouped.2` with six slices produced three consecutive balanced
   groups: `[[1,2],[3,4],[5,6]]`.
7. **PASS — fresh adoption.** Target received v2 config, resolver, `tools/ad-index.py`, workflow tour,
   and fifteen synchronized packets. Feature state remained visible to Git; source-only pack guide
   and unapproved external security skills stayed absent.
8. **PASS — pre-populated and malformed adoption.** Re-adoption preserved config and all fifteen
   non-model packet bodies byte-for-byte. A malformed verifier packet made adoption exit `1`, named
   the packet, and changed no packet bytes.
9. **PASS — docs-as-interface.** README, installed skill, and source pack state central ownership,
   generated metadata, explicit sync, frozen resume, explicit refresh, and adoption preservation.
   Two preliminary evidence checks were too phrase-exact across line wrapping; direct inspection and
   a corrected independent check passed, with no product divergence.
10. **PASS — cleanup and final gate.** All checkout-local disposable repositories were removed.
    Ignored raw evidence remained; source residue was limited to planned `docs/qa/` artifacts. The
    exact final gate exited `0` with 153 passed, 0 failed, 0 skipped.

## Debrief

Verdict: **PASS**. All four execution targets reached their expected public observables through the
declared CLI/manual adapter, every planned leg and six relevant recovery probes passed, and the
adjacent adoption canary remained green. No product defect was found.

Limitation: no live-model execution harness exists, so provider model availability and model/effort
compatibility remain provider-runtime concerns. This repository has no browser, API, mobile, auth,
server, or production-health surface. No networked installer or remote service was invoked.
