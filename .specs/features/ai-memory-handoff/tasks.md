# AI Memory Handoff Tasks

## Execution Protocol

Use `tlc-spec-driven` through every task. Each task updates this file before its atomic Conventional
Commit. The last code-changing task is followed by a fresh Verifier.

**Design:** inline in `spec.md`; no separate design artifact.
**Status:** Approved

## Test Coverage Matrix

> Generated from `AGENTS.md`, `docs/guidelines/TEST-CONTRACT.md`, existing Python script tests, and the feature spec.

| Code Layer | Required Test Type | Coverage Expectation | Location Pattern | Run Command |
| --- | --- | --- | --- | --- |
| zsh shell helper | unit + security | Every wrapper branch and argument boundary; 1:1 to AIM-02/AIM-03 | `scripts/test_ai_memory.py` | `python3 scripts/test_ai_memory.py` |
| adoption boundary | integration | Existing adoption remains unchanged without external runtime | `scripts/test_adopt.py` | `python3 scripts/test_adopt.py` |
| decision index | integration | AD appears exactly once and generated index is current | `tools/test_ad_index.py` | `python3 tools/test_ad_index.py && python3 tools/ad-index.py --check` |
| documentation/config contract | none | Review and full build gate; prose assertions are forbidden | `docs/workflow/ai-memory.md`, `README.md` | build gate only |

## Gate Check Commands

| Gate Level | When to Use | Command |
| --- | --- | --- |
| Quick | Shell helper changes | `python3 scripts/test_ai_memory.py` |
| Full | Adoption/decision integration changes | `python3 scripts/test_ai_memory.py && python3 scripts/test_adopt.py && python3 tools/test_ad_index.py && python3 tools/ad-index.py --check` |
| Build | Phase completion | `npm_config_offline=true npm test && npm run knowledge && git diff --check` |

## Execution Plan

One vertical slice, executed sequentially:

```text
T1 → T2 → T3 → T4 → T5
```

## Task Breakdown

### T1: Add the opt-in Codex handoff helper

**Status:** complete
**What:** Add a sourceable zsh helper that wraps Codex finalization and exposes manual `handoff`, with its canonical behavioural tests.
**Where:** `scripts/ai-memory.zsh`
**Depends on:** None
**Reuses:** Existing standalone Python script-test pattern.
**Requirement:** AIM-02, AIM-03
**Tests:** UT-001, UT-002, UT-003, UT-004, SEC-001
**Gate:** Quick, then `git diff --check`.
**Commit:** `feat(workflow): automate codex handoff finalization`

### T2: Document the minimal ai-memory operating contract

**Status:** complete
**What:** Document pinned local installation, loopback service, three-agent hooks, repo-root/sticky routing, disabled features, capture exclusions, fallback, upgrade, and uninstall procedures.
**Where:** `docs/workflow/ai-memory.md`
**Depends on:** T1
**Reuses:** Optional-integration pattern in `README.md` and upstream ai-memory 1.31 documentation.
**Requirement:** AIM-01, AIM-04, AIM-05, AIM-06, AIM-07, AIM-08
**Tests:** SEC-002; documentation contract has no prose test.
**Gate:** Full and `git diff --check`.
**Commit:** `docs(workflow): define minimal ai-memory handoff`

### T3: Publish the optional integration entry point

**Status:** complete
**What:** Add the public optional-integration pointer without changing `scripts/adopt.py`.
**Where:** `README.md`
**Depends on:** T2
**Reuses:** Existing optional integrations and durable QA scenario conventions.
**Requirement:** AIM-05, AIM-06, AIM-07
**Tests:** IT-001, IT-003
**Gate:** Build and `git diff --check`.
**Commit:** `docs(readme): expose ai-memory handoff option`

### T4: Track the operator handoff journey

**Status:** complete
**What:** Add the durable QA scenario for Codex exit, finalization, and resume in another provider.
**Where:** `docs/qa/scenarios/WFL-ai-memory-handoff.md`
**Depends on:** T3
**Reuses:** Existing WFL area, workflow-adopter persona, and adoption journey.
**Requirement:** AIM-01, AIM-02, AIM-04
**Tests:** Manual QA scenario contract; no automated agent harness exists.
**Gate:** Build and scenario schema review.
**Commit:** `docs(qa): track cross-provider handoff journey`

### T5: Record the authority boundary

**Status:** complete
**What:** Record AD-008: ai-memory is optional transient transport, never project authority; regenerate the decision index.
**Where:** `.specs/STATE.md`
**Depends on:** T4
**Reuses:** AD-006 optional-integration boundary and `tools/ad-index.py`.
**Requirement:** AIM-07
**Tests:** IT-002
**Gate:** Full, Build, spec/tasks validators, and `git diff --check`.
**Commit:** `docs(decision): bound ai-memory to transient handoff`

## Diagram-Definition Cross-Check

| Task | Depends On | Diagram Shows | Status |
| --- | --- | --- | --- |
| T1 | None | Start | match |
| T2 | T1 | T1 → T2 | match |
| T3 | T2 | T2 → T3 | match |
| T4 | T3 | T3 → T4 | match |
| T5 | T4 | T4 → T5 | match |

## Test Co-location Validation

| Task | Layer | Matrix Requires | Task Says | Status |
| --- | --- | --- | --- | --- |
| T1 | zsh shell helper | unit + security | UT-001–UT-004, SEC-001 | match |
| T2 | documentation/config contract | none | SEC-002 manual review | match |
| T3 | adoption boundary | integration | IT-001, IT-003 | match |
| T4 | documentation/config contract | none | manual QA scenario contract | match |
| T5 | decision index | integration | IT-002 | match |
