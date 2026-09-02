# BUG-20260827-assisted-pilot-batch-cli-drops-final-newline

- **Status:** closed — not reproducible on the current fixture; both halves of the required fix present and proven discriminating (Retest 12)
- **Severity:** major
- **Scenario:** `QAS-coordinate-assisted-orca-slices`
- **Expected:** The integrated mini CLI preserves newline-delimited output framing and passes grouped Deep Review before final persona QA.
- **Observed:** `python -m pilot.batch` receives stdin ending in `\n` but writes normalized records without the final delimiter; grouped Deep Review returned `FIX_BEFORE_SHIP` with this sole open Major.
- **Adapter:** Installed Orca `1.4.190` assisted CLI/manual flow with Luna-medium workers
- **Exact path:** conflict-free A/B implementation -> per-slice Technical Verification -> deterministic A-then-B integration -> grouped Deep Review
- **Evidence:** `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-8/deep-review-result.md`

## Impact

The inter-slice coordination flow reached and preserved every stage through deterministic
integration, but readiness correctly stopped before final persona QA. Newline-oriented downstream
consumers would observe changed record framing for a valid newline-terminated input.

## Required fix and retest

Preserve a final newline when stdin has one and add a focused subprocess assertion. An Implementer
must fix the disposable fixture behavior, then a fresh QA Verifier must resume grouped Deep Review,
final CLI persona QA, fixture full gate, and exact cleanup. This bug makes no automatic Orca
compatibility claim.

## Retest 9 — still open, not exercised

Retest 9 could not reach this defect. The disposable fixture only exists inside a live pilot run,
and that run stopped at the first worker turn: the `A_T1` packet was sent once with `ok=true`, but
the Codex agent reported an exhausted account quota resetting on Sep 1st, 2026, so no slice code was
ever written. No integrated fixture existed for the resumed grouped Deep Review, so the newline
framing contract was neither re-observed nor fixed.

This bug therefore stays **open** with no Resolution. The next fresh QA Verifier needs restored
Codex capacity, and must hand the fix to the Slice B Implementer on its own handle as one atomic
remediation commit, then re-run Deep Review on the new head. Evidence:
`docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-9/session.md`.

## Retest 10 — still open, not exercised

Retest 10 could not reach this defect either. The all-Claude snapshot's rendered route proof passed
on both slices and `A:T1` was delivered and honoured packet-exactly, but the `A_FINAL` and
`B_PARKED` packets were both silently truncated in transport
(`BUG-20260827-orca-terminal-send-truncates-claude-worker-packet`). No integrated fixture existed,
so grouped Deep Review, the fix loop, and the newline framing contract were neither re-observed nor
fixed.

This bug stays **open** with no Resolution. It cannot be reached until packet delivery to the worker
is provable; the transport defect blocks it. Evidence:
`docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-10/session.md`.

## Retest 12 — reached, re-derived, and closed

Retest 12 is the first cycle to actually reach this defect: the pointer-delivery contract carried all
four task packets, the fixture was implemented and integrated at `07540bc`, and grouped Deep Review
ran over it. The disposition was established by fresh measurement, **not** inherited from Retest 11
(whose run is recorded `invalid / not exercised`).

Every probe ran on a copy of `pilot/` proven byte-identical to the reviewed tree
(`diff -r <ground>/pilot <copy>/pilot --exclude=__pycache__` → identical). The reviewed tree was
never mutated.

| Check | Result |
| --- | --- |
| `printf 'Ada Lovelace\nGrace Hopper\n' \| python3 -m pilot.batch` | `b'ada-lovelace\ngrace-hopper\n'` — `ENDS_WITH_NEWLINE = True` |
| Recorded root cause present? | No — `pilot/batch.py:15-17` prints one record at a time and never writes a bare `"\n".join(...)` |
| Required focused subprocess assertion present? | Yes — `pilot/tests/test_batch.py:34-43`, `MainCLITest.test_stdin_stdout_normalizes_each_line`, asserting stdout is exactly `"john-smith\nmary-jane-watson\n"` |
| Does that assertion discriminate this bug? | Yes — injecting the exact recorded symptom gives `b'ada-lovelace\ngrace-hopper'` and `Ran 12 tests … FAILED (failures=1)`; clean before and after restore, `Ran 12 tests … OK` |
| Grouped Deep Review over the same tree | `SHIP`, **0 open Major** |
| Final CLI persona QA, newline-terminated stdin (E1) | framing preserved, exit `0`, zero stderr bytes |

Both halves of the required fix — preserve a final newline when stdin has one, plus a focused
subprocess assertion — are satisfied. **Nothing was remediated, because nothing was broken, and no
remediation batch was manufactured.**

The honest caveat: `pilot/` is a **disposable fixture the workers regenerate on every run**, so the
artifact this bug was filed against (Retest 8's `splitlines()` + join implementation) no longer
exists and cannot be re-observed. This record closes because the behaviour it protects is present
and discriminated on the current fixture, not because a specific line was edited. Should a future
run's worker reintroduce the symptom, that is a new observation against this same symptom id.

Evidence: `docs/qa/evidence/2026-08-27-assisted-orca-slices/retest-12/newline-disposition.md`;
`.../retest-12/persona-qa.txt`; `.../retest-12/deep-review-artifacts/state.json`;
`.../retest-12/session.md`.
