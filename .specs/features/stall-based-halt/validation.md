# Technical Validation — stall-based-halt (whole feature)

**Verdict: PASS.** All six acceptance criteria (HALT-01 … HALT-06) carry `file:line` evidence and a
killing assertion. The discrimination sensor injected 21 mutants across both slices; **20 were killed and 1 is an
equivalent mutant** (S8 below — a defensive `or {}` that `tomllib` can never exercise). No mutant with
a behavioural difference survived. An honest reword of the whole `## Escalation` section — every contracted fact
preserved, every sentence rewritten — still passes, so the suite pins the contract, not the prose.
Two `Minor` findings and two advisories are recorded below; none block. Slice 1's `Major`
(`workflow-config/SKILL.md` contradicting itself about the snapshot) was remediated in `c0b8423` and
is now pinned by IT-026; it is closed.

- **Diff ranges:** slice 1 `943c0ef..8487001` (plus remediation `c0b8423`); slice 2 `c0b8423..bc5d77e`
  (`0e1be1f`, `bc5d77e`)
- **ACs:** HALT-01 … HALT-04 (slice 2), HALT-05 … HALT-06 (slice 1)
- **Test IDs:** UT-001 … UT-009, IT-026 (slice 1); IT-027 … IT-030 (slice 2, renumbered from
  IT-022 … IT-025 — verified collision: `tools/shared/tests/qa-skills.test.ts` already owned IT-022
  and IT-023 before this feature)
- **Decision consulted:** AD-007 (`.specs/STATE.md:3-18`). Its `Scope` line names
  `docs/guidelines/REVIEW-ROUNDS.md`, `.agents/skills/autonomous/SKILL.md`,
  `.agents/skills/workflow-config/`, `.my-workflow.toml.example` and `README.md` — every file the two
  slices touch is authorized; nothing outside that list was changed.

## Gate (re-run in this session)

| Command | Result |
| --- | --- |
| `npx vitest run --dir tools` | **8 files passed, 113 tests passed, 0 failed** (8.51s) |
| `python3 tools/test_workflow_config.py` | **14 passed, 0 failed** |

---

## Per-AC evidence — slice 2 (HALT-01 … HALT-04)

### HALT-01.1 — the escalation rule bounds by signature, not by review-round count — **covered**

- Contract: `docs/guidelines/REVIEW-ROUNDS.md:145-147` states the whole rule;
  `docs/guidelines/REVIEW-ROUNDS.md:66` rule 2 now ends `past the cap, escalation below bounds
  remediation by failure signature, not by an open blocker` — a pointer, not a second copy.
- Assertion: `tools/shared/tests/qa-skills.test.ts:790`
  `expect(normalize(reviewRounds)).not.toContain("blocker remains reproducible")` (whole-file, so the
  retired clause cannot reappear anywhere), plus the rule-2 anchors at `:305-306` and the ordering
  assertion at `:320-322`.
- No remaining sentence bounds *remediation* by round count. `:66` `do not start round 3` and `:147`
  `No new review round opens past a cap` bound **review**, which is what the spec's Out of Scope
  table preserves.

### HALT-01.2 — a differing signature continues without new human authorization — **covered, spec-precise**

- Contract: `docs/guidelines/REVIEW-ROUNDS.md:147` — "A signature that differs from the previous
  attempt's is progress: start the next attempt, with no new human authorization."
- Assertion: `tools/shared/tests/qa-skills.test.ts:784`
  `toMatch(/(?:with )?no new human authorization|without new human authorization/)`.
- Sensor: deleting `, with no new human authorization` (M12) kills IT-027.

### HALT-01.3 — scoped gate after each attempt, signature recorded; the signature definition — **covered, spec-precise**

- Contract: `docs/guidelines/REVIEW-ROUNDS.md:145` — failing gate command + sorted set of failing test
  identifiers + each one's first assertion message, "normalized to drop timings, absolute paths and
  line numbers", with the stated reason ("Line numbers shift on any edit, so keeping them would make
  every attempt read as progress and the bound would never fire").
- This matches the spec's Assumptions table row *"What a 'failure signature' is"* field for field,
  **including the line-number drop and its rationale**.
- Assertion: `tools/shared/tests/qa-skills.test.ts:785-787` — the ordered three-part regex
  `/failing gate command.*failing test identifiers.*first assertion message/` and the explicit
  `timings, absolute paths(?:,)? and line numbers` alternation.
- Sensor: dropping line numbers from the normalization list (M9) kills IT-027.

### HALT-01.4 — no new review round opens post-cap; the caps are unchanged — **covered**

- Contract: `docs/guidelines/REVIEW-ROUNDS.md:147` — "No new review round opens past a cap — the caps
  stand."
- Caps verified unchanged by diff: `git diff c0b8423..bc5d77e -- docs/guidelines/REVIEW-ROUNDS.md`
  touches exactly two hunks (`:66` and `:143-147`). `:20` (`≤3 fix rounds`) and `:23` (`≤2 rounds`)
  are byte-identical to `c0b8423`.
- Assertion: `tools/shared/tests/qa-skills.test.ts:788` `toMatch(/no new review round/)`.
- Sensor: removing that sentence (M8) kills IT-027.

### HALT-02/03 — `stall_attempts` consecutive identical signatures halt; `0` unbounded; default `3` — **covered, spec-precise**

- Contract: `docs/guidelines/REVIEW-ROUNDS.md:147` — "Halt once `stall_attempts` consecutive attempts
  repeat one signature … `stall_attempts` is `.my-workflow.toml` `[remediation]`, default `3`; `0`
  never halts for a stall."
- Assertion: `tools/shared/tests/qa-skills.test.ts:802-807` — five independent assertions covering the
  key name, its source file, its table, the consecutive-identical semantics, the default `3`, and the
  `0` meaning.
- Sensor: changing the default `3`→`5` (M6) and deleting the `0` clause (M7) each kill IT-028.

### HALT-04 — the scoped gate cannot be made to run halts regardless of the stall count — **covered**

- Contract: `docs/guidelines/REVIEW-ROUNDS.md:147` ("or when the gate cannot be made to run") and
  `.agents/skills/autonomous/SKILL.md:177` ("or its gate cannot be made to run").
- Assertion: `tools/shared/tests/qa-skills.test.ts:821` `toMatch(/gate cannot be made to run/)` inside
  the `## Halt conditions` slice.

### HALT-04 — the autonomous halt condition is the stall condition and cites the guideline — **covered**

- Contract: `.agents/skills/autonomous/SKILL.md:177` — "Post-cap remediation stalls under
  `docs/guidelines/REVIEW-ROUNDS.md`, or its gate cannot be made to run". The retired wording ("leaves
  a blocker open") is gone.
- Assertion: `tools/shared/tests/qa-skills.test.ts:819-823`, including `not.toContain("leaves a
  blocker open")` and `not.toContain("stall_attempts")` — the second is the "cite, don't restate"
  pin required by `docs/guidelines/CONTEXT-BUDGET.md`.
- Sensor: reverting the bullet (M3), dropping the guideline citation (M10), and **restating** the
  threshold inline (M11) each kill IT-029.

---

## The IT-004 question — judged, not accepted

`IT-004` (`tools/shared/tests/qa-skills.test.ts:275`) lost three anchors (`escalate only`,
`post-fix gate fails`, `blocker remains reproducible`) and gained two
(`bounds remediation by failure signature`, `not by an open blocker`); the ordering assertion at
`:320-322` was retargeted at the new phrase rather than deleted.

**Verdict: not weakened.** Evidence, not reasoning:

- Anchor count went 12 → 11 in the loop, but the ordering chain (`without new human approval` →
  `scoped gate after each correction` → `corrected automatically in the same loop` →
  `do not start round 3` → the escalation pointer) is intact and still four links long, and the
  negative pin `not.toMatch(/ask(?: the human)? whether to fix/i)` at `:323` is untouched.
- Sensor M2 restored rule 2's **exact pre-`0e1be1f` clause** and left everything else at `bc5d77e`.
  It killed **IT-004 and IT-027**. The old wording is therefore still an actively rejected state, and
  IT-004 is one of the two tests rejecting it — it did not degrade into a test that passes on either
  wording.
- The three retired anchors did not become unguarded: `blocker remains reproducible` is now forbidden
  **file-wide** by `:790`, a strictly stronger pin than IT-004's old positive substring check on one
  paragraph.
- The clause IT-004 lost was retired by AD-007 on purpose (`.specs/STATE.md:5-8`), and the behaviour
  it used to guard is re-pinned by IT-027/IT-028 with 14 assertions where there were 3.

Net: the contract IT-004 asserts is the same strength, and the feature's total discriminating power
against the pre-AD-007 rule went up.

---

## IT-030 — the safety trap bites

- Contract: `.agents/skills/autonomous/SKILL.md:180` (the halt condition) and `:136-141`
  (`## 4. Prove readiness, then respect the remote boundary`: "Readiness is evidence, not
  authorization … Each remote action needs its own explicit authorization in the current session …
  Never infer authorization for a later action from an earlier one").
- The two agree: a stall halt leaves blocking findings open, so `:123` ("No blocking findings remain")
  fails and readiness is never proven; and even a proven-ready tree still stops at `:180`. This
  matches the spec Edge Case "IF a blocker remains open and the run halts for a stall THEN the run
  SHALL NOT push, open a pull request, merge, or deploy."
- Assertion: `tools/shared/tests/qa-skills.test.ts:835-841` — the halt line verbatim inside the
  `## Halt conditions` slice, plus two whole-file pins on section 4's sentences.
- **Sensor, deleting the line (M4): kills `IT-030` and `does not turn autonomous readiness into an
  implicit merge`** — two independent tests. Weakening the line to a vague equivalent (M5) kills the
  same two. There is no reachable state in which a run at `bc5d77e` can be talked into pushing,
  opening a pull request, merging, or deploying without explicit per-action authorization, and no
  single-line edit that removes that guarantee survives the suite.

---

## Discrimination sensor

Isolated `git worktree` at `bc5d77e` (never `git stash`), full gate per mutant, worktree removed
afterwards; `git status --porcelain` restored to its pre-sensor baseline (`?? paralelizacao.md`,
`?? .specs/features/stall-based-halt/validation.md`).

### Slice 2 — 12 mutants, 12 killed, 0 survived

| # | Mutation | Result | Killed by |
| --- | --- | --- | --- |
| M1 | `## Escalation` reverted to its pre-`0e1be1f` wording | **killed** (2 failed / 111) | IT-027, IT-028 |
| M2 | rule 2's escalation clause reverted to `escalate only if the post-fix gate fails or the blocker remains reproducible` | **killed** (2 / 111) | IT-004, IT-027 |
| M3 | autonomous halt bullet reverted to `leaves a blocker open` | **killed** (1 / 112) | IT-029 |
| M4 | remote-authorization halt line **deleted** | **killed** (2 / 111) | IT-030, "does not turn autonomous readiness into an implicit merge" |
| M5 | remote-authorization halt line weakened to a vague equivalent | **killed** (2 / 111) | IT-030 + the same sibling |
| M6 | default `3` → `5` | **killed** (1 / 112) | IT-028 |
| M7 | `0` never halts for a stall removed | **killed** (1 / 112) | IT-028 |
| M8 | `No new review round opens past a cap` removed | **killed** (1 / 112) | IT-027 |
| M9 | line numbers kept in the signature normalization | **killed** (1 / 112) | IT-027 |
| M10 | guideline citation dropped from the autonomous bullet | **killed** (1 / 112) | IT-029 |
| M11 | `stall_attempts` restated inline in `autonomous/SKILL.md` | **killed** (1 / 112) | IT-029 |
| M12 | `with no new human authorization` removed | **killed** (1 / 112) | IT-027 |
| — | **HONEST REWORD**: `## Escalation` fully rewritten, every contracted fact preserved | **passed 113/113** | — (correct: the suite is not over-fitted to phrasing) |

### Slice 1 — 9 mutants, 8 killed, 1 equivalent

Re-derived in this session in a second worktree at `bc5d77e`, gate `python3 tools/test_workflow_config.py`.

| # | Mutation | Result | Failure |
| --- | --- | --- | --- |
| S1 | `remediation` removed from `CONFIG_KEYS` (`:28`) | **killed** | `AssertionError` |
| S2 | `STALL_ATTEMPTS_DEFAULT` `3` → `4` (`:31`) | **killed** | `AssertionError` |
| S3 | `attempts < 0` → `attempts <= 0` (`:140`) — rejects `0` | **killed** | `remediation.stall_attempts must be an integer of at least 0` |
| S4 | `type(attempts) is not int` → `not isinstance(...)` (`:140`) — lets TOML `true` through | **killed** | `AssertionError` |
| S5 | unknown-key message stops naming the key (`:138`) | **killed** | `AssertionError` |
| S6 | `remediation` dropped from the printed payload (`:358`) | **killed** | `KeyError: 'remediation'` |
| S7 | `remediation` persisted into `workflow.json` (`:336`) | **killed** | `existing snapshot has an incomplete schema` |
| S8 | `config.get("remediation") or {}` → `config.get("remediation", {})` (`:95`) | **equivalent — survived** | 14 passed |
| S9 | resume returns the frozen value instead of the resolved-now value (`:358`) | **killed** | `AssertionError` |

**S8 is an equivalent mutant, not a coverage gap.** `tomllib` never produces `None` for a table, so
`or {}` and `, {}` are the same function for every input a `.my-workflow.toml` can express; the same
dead guard appears again at `:131-132` (`if remediation is None`). No test can distinguish them, and
writing one would be a coverage-raising test that `AGENTS.md` forbids. See the advisory below.

---

## Per-AC evidence — slice 1 (HALT-05, HALT-06)

Unchanged from the slice-1 pass; restated here so this file speaks for the feature.

| AC | Production | Assertion |
| --- | --- | --- |
| HALT-05.1 — a declared value is resolved and reported | `workflow_config.py:94-96`, `:355-358` | `tools/test_workflow_config.py:467`, `:493`, `:495` |
| HALT-05.2 — no/empty table, absent file → `3` | `workflow_config.py:31`, `:95-96` | `tools/test_workflow_config.py:463-465` (`absent-config`, `absent-table`, `empty-table`) |
| Assumptions — `0` is valid and means unbounded | `workflow_config.py:140` (`attempts < 0`, so `0` passes) | `tools/test_workflow_config.py:468` (`unbounded` → `0`), `:493`, `:495` |
| HALT-05.3 — non-integer / negative exit non-zero naming `remediation.stall_attempts` | `workflow_config.py:140-141` (`type(...) is not int`, so TOML `true` is rejected — a `bool` is an `int` subclass) | `tools/test_workflow_config.py:509`, `:514`, `:519`, `:546` |
| HALT-05.4 — unknown key rejected **by name** | `workflow_config.py:137-138` | `tools/test_workflow_config.py:524` (literal `remediation contains unknown key 'attempts'`) |
| HALT-05 (enabling) — `[remediation]` is no longer a hard failure | `workflow_config.py:28` (`CONFIG_KEYS`) | covered transitively by every UT |
| HALT-06 — not written into `workflow.json` | `workflow_config.py:327-336` (the persisted snapshot has no `remediation` key), `:355-358` (added print-time only, after `_write_snapshot`) | `tools/test_workflow_config.py:581` |
| HALT-06 — a resume reports the **new** value, snapshot still validates | `workflow_config.py:305-312` (resume returns the snapshot verbatim), `:355-358` (re-reads the *current* config) | `tools/test_workflow_config.py:575`, `:581`, `:587`, `:589` (value changed `5`→`7`, resume reports `7`) |
| IT-026 — the surface is documented where it is read; snapshot ≠ output | `.agents/skills/workflow-config/SKILL.md:22-23`, `.my-workflow.toml.example`, `docs/qa/scenarios/CFG-freeze-feature-workflow.md` | `tools/shared/tests/qa-skills.test.ts:753-772` |

**Slice-1 `Major` — closed.** `SKILL.md:22-23` now reads "The JSON output is
`.specs/features/<feature-slug>/workflow.json` plus the resolved-now `remediation`. The snapshot is
the frozen routing state; never write the JSON output back to it." Fixed in `c0b8423` and pinned by
`tools/shared/tests/qa-skills.test.ts:769-771`.

---

## Findings

### 1. `Minor` — the halt report contract drops "the number of attempts"

- **Premise:** `docs/guidelines/REVIEW-ROUNDS.md:147` — the halt hands the human "what is still
  wrong, every fix tried, and the recommended call." Spec `## User Stories` → "P1: A stuck loop still
  stops", AC 3 requires the report to name *"the repeated failure signature, the number of attempts,
  and every fix that was tried."*
- **Path:** A run halts after 3 identical signatures and writes a report that names the failure and
  the fixes tried but not the attempt count — fully compliant with the shipped guideline, not
  compliant with the AC. The operator cannot tell from the report whether the loop hit the threshold
  or the gate refused to run, which are the two different halts at `.agents/skills/autonomous/SKILL.md:177`
  and want different responses. No assertion pins it: the honest-reword mutant *added* both the
  signature and the attempt count and the suite still passed, proving the fact is unguarded.
- **Verdict:** `Minor`, non-blocking. "What is still wrong" reasonably carries the repeated signature;
  only the attempt count is strictly absent, and no wrong action follows from its absence. Fix is one
  clause at `:147` plus one anchor in IT-028 — not a new test.

### 2. `Minor` — `REVIEW-ROUNDS.md` is 2 lines from its own asserted ceiling

- **Premise:** `docs/guidelines/REVIEW-ROUNDS.md` is now 158 lines; `tools/shared/tests/qa-skills.test.ts:291`
  (`expect(reviewGuideline.trimEnd().split(/\r?\n/).length).toBeLessThanOrEqual(160)`) asserts `≤ 160`. Slice 2's net change is `+4 −3` on this file and `+1 −1` on `autonomous/SKILL.md`,
  so the growth itself is justified — the new rule replaced the old one rather than being layered on
  top, and it is stated **once** (`:145-147`), pointed at from `:66`, and cited but not restated at
  `.agents/skills/autonomous/SKILL.md:177` (pinned by `:823`).
- **Path:** The next guideline edit that adds three lines fails IT-004 on the line cap rather than on
  a contract, which is a confusing failure mode for whoever hits it.
- **Verdict:** `Minor`, non-blocking, and **not** attributable to this feature — the file was already
  at 157. Recorded so the next author reaches for `CONTEXT-BUDGET.md` before adding prose here.

### Advisory — the round caps themselves are unasserted

`≤3 fix rounds` (`:20`) and `≤2 rounds` (`:23`) appear in no test (`grep -rn "≤3 fix rounds\|≤2 rounds"
tools/` → no match). This feature left them byte-identical, verified by diff, so there is no failure
path here — but "the caps are unchanged" is currently proven by review, not by the suite. Pre-existing;
add an anchor only if the caps are judged worth pinning, not to raise coverage.

### Advisory — integration test IDs have no registry

IT-022 and IT-023 already existed in `tools/shared/tests/qa-skills.test.ts` before this feature, which
is why `bc5d77e` renumbered IT-022…IT-025 to IT-027…IT-030. Nothing detected the collision
mechanically; `.specs/features/*/tests.md` carries no shared ID index. No failure path (the second
`it()` would simply have had a duplicate label), so this is advisory.

### Advisory — two dead `None` guards in the resolver

`.agents/skills/workflow-config/scripts/workflow_config.py:95` (`config.get("remediation") or {}`) and
`:131-132` (`if remediation is None: remediation = {}`) both defend against a `None` table.
`tomllib` cannot produce one — an empty `[remediation]` parses as `{}`. That is why sensor mutant S8
is equivalent. Two lines of unreachable defence, no failure path, and the same shape already exists
for `deep_review` at `:89`, so it is house style rather than this feature's debt. Delete both only as
part of a wider cleanup; do not add a test for them.

