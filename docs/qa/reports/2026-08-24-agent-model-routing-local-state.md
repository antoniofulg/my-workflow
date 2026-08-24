# QA Execute — agent model routing local state

- **Date:** 2026-08-24
- **Charters:** [`CH-agent-model-routing-local-state-2026-08-24`](../charters/CH-agent-model-routing-local-state-2026-08-24.md); [`CH-agent-model-routing-adoption-boundary-2026-08-24`](../charters/CH-agent-model-routing-adoption-boundary-2026-08-24.md)
- **Persona:** Workflow adopter
- **Adapter:** CLI/manual through checkout-local disposable Git repositories, the documented `workflow_config.py` and `scripts/adopt.py` commands, plus independent filesystem/JSON/Git/package inspection
- **Environment:** macOS workstation; active checkout `/Users/antoniofulg/Projects/my-workflow-ai-memory-handoff`; branch `feat/agent-model-routing`; HEAD `255be335fd4ebd776161dfd11e92f324a543166c`; no server, browser, API, auth, live-model harness, or networked installer
- **Entry path:** `.my-workflow.toml.example` → local `.my-workflow.toml` → `.agents/skills/workflow-config/scripts/workflow_config.py --sync-agents` → feature resolve/resume/refresh; `README.md` → `scripts/adopt.py`
- **Preflight automated gate:** technical validation records `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py` at exit 0 with 110 Vitest + 18 adoption + 34 resolver = 162 passed, 0 failed, 0 skipped at `a9bb322`; `a9bb322..255be33` changes only the validation artifact
- **Final automated gate:** `npm test && python3 scripts/test_adopt.py && python3 tools/test_workflow_config.py` exited 0 at HEAD `255be335`: 110 Vitest + 18 registered adoption + 34 resolver = 162 passed, 0 failed, 0 skipped
- **Raw evidence:** `docs/qa/evidence/2026-08-24-agent-model-routing-local-state/`

## Matrix

| Scenario | Scope | Verdict | Independent confirmation | Evidence |
| --- | --- | --- | --- | --- |
| `CFG-centralize-agent-model-routing` | Complete matrix, exact mixed profile, sync, preservation, idempotence, invalid-input containment, CLI reporting | pass | Independent TOML/native parsing, template/body hashes, changed/current lists, reload, and pre/post failure hashes | [`summary.json`](../evidence/2026-08-24-agent-model-routing-local-state/summary.json) |
| `CFG-freeze-feature-workflow` | Resolve, frozen snapshot, stable resume, drift rejection, explicit refresh, planner exclusion | pass | Resolver stdout equalled reloaded `workflow.json`; unsynchronized config left resume stable; selected model and effort drift each failed until explicit refresh | [`session.log`](../evidence/2026-08-24-agent-model-routing-local-state/session.log) |
| `CFG-route-delegated-role-providers` | Override-over-profile-over-native routing with no fallback | pass | Exact route was Claude implementer, Cursor verifier/explorer, Codex deep reviewer; planner absent; CLI verifier override beat `mixed` profile | [`summary.json`](../evidence/2026-08-24-agent-model-routing-local-state/summary.json) |
| `CFG-resolve-deep-review-cadence` | v2 cadence and balanced consecutive groups | pass | `grouped.3` with seven slices independently reloaded as `[[1,2,3],[4,5],[6,7]]` | [`session.log`](../evidence/2026-08-24-agent-model-routing-local-state/session.log) |
| `CFG-keep-local-artifacts-out-of-git` | Git/package ownership, checkout isolation, clean-clone regeneration | pass | Git tracked 16 sources, ignored local/runtime state, package included sources and excluded runtime state, isolated checkouts stayed distinct, clean clone regenerated defaults | [`summary.json`](../evidence/2026-08-24-agent-model-routing-local-state/summary.json) |
| `ADP-adopt-workflow-safely` | Fresh/re-adoption, custom config, malformed input, consumer-byte preservation | pass | Fresh and repeated adoption, custom local/template/profile/tool/ignore preservation, regenerated metadata/bodies, and malformed/linked-source no-write recovery | [`session.log`](../evidence/2026-08-24-agent-model-routing-local-state/session.log) |

## Probe results

1. **PASS — local initialization and template generation.** A tracked-only clone began without
   `.my-workflow.toml` or runtime packets. Documented sync initialized exact example bytes, generated
   fifteen native packets, matched every TOML model/effort value, preserved all template and
   non-model instruction bytes, and reported fifteen changed paths.
2. **PASS — overwrite and idempotence.** A disposable runtime edit was replaced from its tracked
   template and reported as the only changed path. Unchanged sync then reported zero changed and
   fifteen current paths; the complete runtime digest remained
   `d8b662763820dfceca972cd81edece83b3f5a1cde92be042b56b2a081c241570`.
3. **PASS — exact routing, cadence, snapshot, and reload.** `mixed` plus
   `--override verifier=cursor` resolved Claude implementer, Cursor verifier/explorer, and Codex deep
   reviewer. Planner was absent. Seven slices formed `[[1,2,3],[4,5],[6,7]]`; stdout equalled the
   independently reloaded snapshot.
4. **PASS — frozen resume and recovery.** Unsynchronized config replacement left resume output
   identical. Synchronized drift in the selected Claude model and selected Codex effort each made
   ordinary resume fail with sync/explicit-refresh guidance; each explicit refresh persisted and
   reloaded the new value.
5. **PASS — ten edge families.** Missing matrix role, unknown key, invalid effort, malformed TOML,
   duplicate template metadata, missing template metadata, runtime-parent collision, linked config,
   linked template, and linked runtime destination all exited non-zero with named stderr, empty
   success output, unchanged local bytes, and unchanged outside bytes. Existing and dangling
   `--root` symlinks also failed without target creation or changes.
6. **PASS — checkout, Git, package, and clean-clone ownership.** Two local configs produced distinct
   runtimes and changes in one checkout left the other digest unchanged. Git tracked the example and
   fifteen templates, ignored local config/runtimes, and remained clean after sync. Package dry-run
   had 280 members, included all sixteen sources, and excluded all local/runtime paths. A tracked-only
   clean clone contained no inherited local bytes and regenerated its own defaults.
7. **PASS — fresh and repeated adoption.** Fresh target received sources, initialized config,
   fifteen matching runtimes, `tools/ad-index.py`, and visible feature state. Source-only pack,
   ai-memory runtime, and three unapproved external security skills remained absent. Re-adoption was
   byte-idempotent and only printed the separate authorized installer command.
8. **PASS — custom and failing adoption.** Re-adoption preserved customized local config, three
   consumer template sentinels, QA profile, `tools/ad-index.py`, and unrelated ignore bytes while
   regenerating matching runtime metadata/bodies. Malformed config, malformed template, and linked
   template each failed, named the source, emitted no success output, and changed no local/outside
   bytes.
9. **PASS — docs and release canaries.** Reloaded README/skill described central ownership, explicit
   sync, tracked/ignored boundaries, frozen resume, and explicit refresh. Package and lock identity
   both reported `my-workflow@0.4.0`.
10. **PASS — cleanup and final Build.** Final QA summary records 145 passing independent checks,
    ten edge families, and 55 public/read-path commands. Disposable root was removed. Exact final
    Build passed 162 checks with no failures or skips.

## Debrief

Verdict: **PASS**. Both charters and all six scenarios reached their expected public observables.
No product defect found; no bug record or Implementer handoff required.

Limitations: no live-model harness exists, so provider model availability and model/effort
compatibility remain provider-runtime concerns. This repository has no browser, API, mobile, auth,
server, or production-health surface. No external security-skill installer, network service, or
remote fetch ran. Preliminary verifier-fixture stalls are recorded separately; all disposable roots
were removed and the clean final execution passed.
