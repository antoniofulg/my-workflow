# Verification Evidence

**Read when:** about to claim anything is done, or to commit.

**Why this exists:** Completion language without a fresh command is a false report. A green linter
does not mean the task is done; unit tests do not mean the feature is ready. Scope binds, and a
secret in a diff is an absolute stop.

## The rule

**No completion claim without fresh verification evidence.**

If the command proving the claim has not run since the last change, the result cannot be claimed.

## Scope binds

The verification must be at least as broad as the claim.

| Claim | Requires |
| --- | --- |
| "this test passes" | That test, run |
| "task complete" | The task's own tests and validation commands, plus the scoped gate |
| "feature complete" / "ready for a pull request" | The full gate |
| "bug fixed" | The original symptom reproduced failing, then passing |
| "regression test works" | Red before the fix, green after — both observed |

A narrow verification never supports a broad claim. Passing unit tests does not justify "task
complete"; a clean linter does not justify "ready to commit".

**Intermediate tasks in a multi-task feature are narrow claims by design.** The honest per-task claim
is *"task implemented, affected lanes green, full gate deferred to feature close"* — run the scoped
gate and say exactly that. See `docs/guidelines/GATES.md`.

## A green gate is not a met requirement

A passing pipeline proves the code compiles, lints and passes its tests. It does not prove the code
does what the spec said.

For any "complete" claim, additionally compare the deliverable against the canonical artifacts — the
acceptance criteria in `spec.md`, the cases in `tests.md`, and the `uiux.md` / `dx.md` contracts when
they exist. Field by field: names, types, defaults, required flags, shapes, behaviours. Paraphrase-level
similarity is not parity.

**Never reinterpret the contract to match what was built.** A mismatch fails the claim; fix the
deliverable and re-verify.

## Report shape

Cite actual command output. "I ran it and it passed" is not evidence — if the output is not shown, the
verification did not happen.

```
VERIFICATION
Claim:        <what is being claimed>
Command:      <exact command>
Executed:     <just now, after all changes | cached record for this tree>
Exit code:    <0 or non-zero>
Output:       <pass count, failure count, build result>
Warnings:     <any, or none>
Contract:     <artifacts compared, PASS or the mismatch; or n/a>
QA impact:    <scenario ids flagged or walked with verdicts; or "no user-visible change">
Verdict:      PASS | FAIL
```

On `FAIL`, do not use completion language. State what failed and what remains.

On `PASS`, only the specific claim the evidence supports may proceed.

## Before a commit

1. Run the scoped gate for a task, or the full gate for a feature — or cite a current cached record.
2. Confirm zero errors, zero failures.
3. Apply the QA flag rule from `docs/guidelines/QA-SCENARIOS.md`.
4. Produce the report above with verdict `PASS`.
5. Then commit.

Before a pull request, additionally review the diff for unrelated files and confirm it matches the
intended change.

## When verification fails

A scoped re-run — one test, one file, one `--grep` — is for diagnosis and for working through a
batch of failures. It never closes one.

1. **Read every failure before fixing any.** Which command, which test, which assertion. Quote the
   line, then cluster by cause — several failures usually have one.
2. **Re-run them untouched.** Passing with nothing changed means the defect is isolation, order or
   load, not the assertion. Fix that instead.
3. **Fix the cause, not the symptom.** One fix per cluster.
4. **Climb back to the gate that closes the claim.** The failing tests while iterating, then the
   scoped gate for the surface touched, then the declared gate for the level being claimed — whole
   and unfiltered, never a subset assembled by hand. `docs/guidelines/GATES.md` names which is which.
   If that gate cannot run, use the project's *declared* reduced target, whose scope is fixed in the
   build file; a scope picked to match what failed is the one that quietly drops a stage.
5. **Report that command, its exit code and its numbers**, in the shape above.

Some failures exist only in the whole run: a hook that fits its budget alone and times out on a busy
machine, a suite that mutates state another suite reads, a test that passes because an earlier one
left the right state. All three go green in isolation, so stopping at the subset ships them and
reports success — and the report is what everyone downstream trusts.

Between steps 1 and 4 the tree is known-red and the results are partial. That is deliberate: four
failures in a 500-test end-to-end suite at twenty minutes a run is eighty minutes to learn what one
run at the end tells you, and a fix is not more correct for having been measured alone. The
guarantee is not that every intermediate state was green — it is that **no claim rests on a subset.**

Never claim partial success, never blame the tooling without evidence of a false positive, and never
move to the next task while verification is failing.

## Stop and hand it back

Some situations are not verification failures to fix — they are reasons to stop and report. Record
what is blocking and the exact condition for resuming, then hand it to the human:

- Requirements contradict each other and no precedence rule resolves it
- A gate would only pass by weakening, skipping or deleting a test
- Blocking findings remain after the required post-cap remediation and gate in `docs/guidelines/REVIEW-ROUNDS.md`
- **Credentials, tokens or secrets appear** anywhere they should not — in a diff, a log, a fixture,
  a test artifact
- The action needed exceeds the authority the prompt gave: a push, a merge, a deploy, a production
  database change

The last two are absolute. Everything else on this list is a judgment call about whether continuing
is honest; those two are not, and no amount of progress justifies passing them.

## Words that signal the rule is being broken

"should work now" · "I'm confident" · "just this once" · "the linter passed" · "probably" · "seems to"
· expressing satisfaction before running anything · trusting another agent's success report.

Each of these is a claim standing in for a command. Run the command.
