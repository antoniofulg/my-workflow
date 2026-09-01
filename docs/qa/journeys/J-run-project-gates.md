# J-run-project-gates

**Persona:** Workflow operator
**Goal:** Run a project gate once per tree, reuse its recorded result as evidence while the tree is
unchanged, and keep the cache from ever standing between the operator and a real gate result.
**Entry point:** `docs/guidelines/GATES.md` → `python3 tools/gate_cache.py run --gate <label> -- <command>`

## Before walking

- Walk in a **checkout-local disposable Git repository**, per the CLI/manual adapter in
  [`docs/qa/README.md`](../README.md). Every leg needs a repository whose worktree the walker can
  freely edit, commit, and break; the source checkout is not that.
- Use a **cheap, counting gate command** as the stand-in for a real suite — a command that appends a
  line to a file outside the fingerprinted tree and exits 0, so "did it execute" is read from the
  counter and not inferred from timing. Give it a failing variant for the refusal legs.
- This repository's own gate is `bun run test:all`. Nothing in it shells out to `rg`, and no `rg`
  binary exists on this host — an earlier revision of this journey required one, and that is no
  longer true. If a gate ever fails for a reason outside the cache, remember the tool **records that
  failure**, so clear `.gate-cache/` before reasoning about a later leg.
- The cache directory is `<root>/.gate-cache/`; records are `<fingerprint>.json` and logs are
  `<fingerprint>.*.log`. Read them directly — that is the independent read path for every leg.
- Reset between invalidation legs by reverting the edit, so each leg proves its own cause.

## Flow — reuse

1. Run the counting gate through the wrapper on a clean tree. Read the evidence line and confirm it
   names outcome, gate label, fingerprint and log path; confirm the counter advanced, the record
   exists with `status: "pass"`, and the log holds the command's output.
2. Run the identical invocation again with nothing changed. Confirm the evidence line reports a hit
   citing the same fingerprint, the exit status is 0, and the counter did **not** advance.
3. Invalidate once per leg, running the identical invocation after each and reverting before the
   next: (a) edit a tracked file; (b) stage a change without committing; (c) add an untracked,
   unignored file. Each must advance the counter and produce a different fingerprint.
4. Commit the current worktree content without changing any file. Run the identical invocation and
   confirm the fingerprint is unchanged and the counter did not advance.
5. Run the same command under a different `--gate` label, then the original label with a different
   command. Each must advance the counter and write its own record under its own fingerprint.
6. Read `docs/guidelines/GATES.md`, `.agents/skills/autonomous/SKILL.md`,
   `.agents/skills/tlc-spec-driven/references/implement.md` and `.agents/skills/qa-execute/SKILL.md`
   in the repository. Confirm each names the cached invocation an operator is told to run, and that
   `autonomous` admits a passing record only when gate scope **and** fingerprint match the claimed
   tree.
7. Scope binding: take the passing `scoped` record from step 1 and attempt to satisfy a `full`-gate
   claim with it. The observable is that `--gate full` on the same tree and command produces a
   different fingerprint and therefore executes — a `scoped` record can never be cited as a full-gate
   result.

## Flow — refusal

8. Make the gate command fail. Run it, confirm the wrapper exits with the command's own non-zero
   status and the record records a failure. Run the identical invocation again and confirm it
   executes rather than short-circuiting, and that the failing record's log is still readable.
9. Restore a passing record, then damage it by hand, one leg at a time, running the identical
   invocation after each: (a) truncate the JSON mid-object; (b) replace it with valid JSON that is
   **not** an object, such as `[]`; (c) change its schema version to an unexpected value; (d) leave
   the record intact but delete its log file. Every leg must execute the gate and exit with the
   command's status. A non-zero exit that is not the command's own, or any traceback, is a defect.
10. Make a tree object unobtainable — point `--root` at a directory that is not a Git repository, or
    run with `git` absent from `PATH`. Confirm the gate still runs, the exit status is the command's
    own, the evidence line reports no cache, and no record or log is written.
11. Invoke the tool with no command after `--`. Confirm it refuses with a usage error and writes
    nothing to the cache.

## Promises

- [`QAS-reuse-gate-result-for-unchanged-tree`](../scenarios/QAS-reuse-gate-result-for-unchanged-tree.md)
- [`QAS-run-the-gate-when-the-cache-cannot-vouch`](../scenarios/QAS-run-the-gate-when-the-cache-cannot-vouch.md)
- [`CFG-keep-the-gate-cache-out-of-git`](../scenarios/CFG-keep-the-gate-cache-out-of-git.md)

## Adjacent canary

[`CFG-keep-local-artifacts-out-of-git`](../scenarios/CFG-keep-local-artifacts-out-of-git.md) owns the
same Git-visibility promise for the runtimes that predate this directory. It is frozen historical
evidence, so read it for contrast and never reset it; `CFG-keep-the-gate-cache-out-of-git` carries
this cycle's verdict. Adoption is out of scope for this delivery — the tool is not in the adoption
payload yet, so no `ADP` row belongs to this journey.
