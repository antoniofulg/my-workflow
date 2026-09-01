# Gate Result Cache — Decisions

Everything this run chose while nobody was watching. Human-handed decisions first, then the ones the
run made on its own.

## Handed down by the human

| Decision | Why | Rejected | Cost to change now | Cost to the user today |
| --- | --- | --- | --- | --- |
| A passing cache record is evidence at **every** gate scope, readiness full gate included | The largest single re-run in the workflow is the full gate on a tree that already passed it; excluding it keeps most of the cost | Scoped-only caching, which would have left `autonomous` untouched and the contradiction dormant | One line in `autonomous/SKILL.md`, not yet written | Nothing yet: the rule is decided but unwired, so readiness still re-runs the full gate |
| Ship the tool, adopt it, and wire the documented gate steps | An unwired cache is never called; the guideline has promised this tooling since it was written | Tool-only, or tool-plus-adoption with wiring deferred to a later feature | Reverting three one-line edits | Agents must invoke the wrapper; a hand-typed bare gate silently loses the cache |

**Not recorded as an `AD-NNN`, deliberately.** `.agents/skills/autonomous/SKILL.md:135` still reads
"A cached or partial result is not evidence", and `docs/guidelines/GATES.md` already says the
opposite. Recording the decision while neither document moves would add a third voice to a repository
that already disagrees with itself. It is recorded here and lands with the wiring delivery.

## Made by the run

### Classification and depth

The work is a **feature** — `docs/guidelines/GATES.md` § "Cached evidence" contracts the behaviour
and no code delivers it. Not a direct correction: it opens a new public surface (a CLI verb, a
record schema, an ignored directory) and an implicit-requirement dimension (persistence).

Auto-sized **Medium**: spec required, Design and a formal `tasks.md` skipped, execution plan inline
in the implementer dispatch. The workflow resolver derived **one slice** with no `tasks.md`; an
asserted two-slice split was rejected because the tool alone changes no run and the wiring alone has
nothing to call — the mergeable unit is the pair. One slice means one Verifier and one deep-review
group. Cost to change: re-resolve with `--refresh`.

### Fingerprint material — `AD-018`

**Chosen:** `sha256(gate label, command argv, git tree object)`, where the tree object comes from
`git add -A` plus `git write-tree` against a temporary index seeded from `git rev-parse --git-path
index`.

**Why:** Git already answers "what is the exact content of this worktree" in one command, honours
`.gitignore`, changes on any edit, and does not change on a commit alone — which is precisely the
invalidation rule the guideline already states. The temp index is seeded from the real one so the
stat cache applies and only changed files are rehashed.

**Rejected:** hashing a manual file walk (restates `.gitignore` badly and rehashes everything);
`git status --porcelain` (carries no content hashes, so two different edits to one file collide into
a false hit); `HEAD` sha (a dirty worktree would reuse a clean tree's result).

**Cost to change now:** the key format is internal; changing it invalidates existing records, which
is free — they are disposable.

**Cost to the user today:** a docs-only edit invalidates code gates. Conservative in the safe
direction, and the alternative is per-path scoping the guideline does not contract.

### Only passing records short-circuit

A failing record is written and kept — the guideline says a failing record starts diagnosis from its
log — but never skips a run. Rejected: caching red results, which would turn one broken run into a
permanently red tree until someone guessed to clear the cache. Cost to change: one condition. Cost
today: a red gate is always paid in full, which is correct.

### Fail open when the fingerprint is unavailable

No git, or git failing, means the command runs and nothing is read or written. Rejected: failing
closed, which would let a cache defect block a gate — the cache is an optimisation and must never
become a dependency of gating. Cost to change: one branch. Cost today: silent loss of caching in a
non-git checkout, surfaced by the `NOCACHE` evidence line.

### One verb instead of a protocol

`run --gate <label> -- <command>` wraps the gate. Rejected: a `fingerprint` / `check` / `record`
trio, which is three chances for an agent to record a pass it did not observe. Wrapping makes the
recorded status the observed exit status by construction. Cost to change: additive. Cost today: a
gate that must be invoked outside the wrapper gets no record.

### Deliberate ceilings

| Ceiling | Upgrade path |
| --- | --- |
| Interpreter, dependency binaries, and environment are outside the key | Delete `.gate-cache/` after a toolchain change |
| No eviction or size bound | Delete the directory; it is checkout-local and disposable |
| Records are never shared across checkouts or CI | Intentional — `docs/guidelines/BRANCHING.md` gives each checkout its own runtime, and a shared cache would let one checkout vouch for another |

### Scope left alone

`review_convergence.py` keeps its own fingerprint material. The two caches answer different
questions — one identifies a repeated blocker, the other identifies an unchanged tree — and merging
them would couple review convergence to worktree content.

## Decided during review

### Adoption ships the tool, not its self-check

The Verifier observed that `scripts/adopt.py` copies `tools/gate_cache.py` but not
`tools/test_gate_cache.py`, so a consuming project receives a copy it cannot verify. Left as is:
no tool in the adoption payload ships its self-check — `qa_parallel_pilot.py`,
`orca_assisted_probe.py` and `ad-index.py` all ship bare — and one exception is a worse contract
than the uniform gap. The self-check runs in this repository's `npm run test:python`, which is where
the tool is maintained. Cost to change: one `COPY_PATHS` entry, plus deciding the same for the other
three tools.

### Gate labels are a closed vocabulary: `scoped` and `full`

The label is fingerprint material, so drift in how the documented call sites spell it silently costs
every hit. The first wiring pass left three spellings (`<scope>`, `<level>`, and a literal `full`)
across `GATES.md`, `implement.md` and `qa-execute/SKILL.md`. Normalised to exactly two labels.
Cost to change: renaming a label invalidates existing records, which is free.

### The fix batch does not touch the tool

The Verifier found no product defect — every gap was a missing or non-discriminating test. The
remediation adds tests only. A batch that edits the code it is supposed to be pinning cannot show
the tests would have caught the original fault.

### Acceptance criterion 3 was amended mid-flight, not satisfied

Round-2 verification found the atomicity assertion unpinnable: the surviving mutant was a plain
`open(...,"w")` in place of the atomic replace, and the test could only observe corruption at rest,
never a torn write. The Verifier prescribed a reader racing two in-flight invocations. That was
rejected and the spec was amended instead.

**Why:** `hit()` catches `OSError` and `ValueError` and returns `False`, so a torn record is a cache
miss, never a false hit — losing atomicity costs a re-run, which is the fail-open behaviour this
design already accepts everywhere. A test needing a fabricated 500 ms window to see its property is
a flake generator in a suite that runs on every task gate. `AC3` and the overlap edge case now state
the falsifiable invariant: a record that does not parse completely is treated as absent, the gate
runs, and no hit is reported.

**What it cost, precisely.** `os.replace` stays in the code, and the suite would not notice its
removal — the Verifier measured a plain-write `write_record` surviving at 0/5. Two overlapping
invocations of one gate on one tree share a fingerprint and therefore one record path; a non-atomic
writer could in principle leave a syntactically valid record blending one run's `status` with
another's `exit_code`, which `hit()` would accept because it never reads `exit_code`. Nobody
constructed that interleave — it needs a same-tree pass/fail split and a byte-level race — and the
product prevents it today. The residual is that a future editor could delete the guard silently, so
the code carries a comment naming it load-bearing.

**Rejected alternatives:** the racing reader (flaky, pins the mechanism rather than the consequence);
adding an `exit_code == 0` clause to `hit()` (defensive code for a state the current writer cannot
produce). Cost to change: write the racing reader if `write_record` ever grows a second writer.

### Verification took three rounds

Round 1 FAIL — three mutants survived. Round 2 FAIL — two closed, atomicity did not reproduce the
claimed kill. Round 3 PASS. The tool was byte-identical to its first commit throughout: every round
corrected the test contract, never the code the tests were meant to pin. The Verifier withdrew its
round-2 prescription in round 3 on the reasoning above.


## The base was stale, and what that cost

This feature was planned, built, reviewed and QA-walked on a branch cut from a local `main` that was
**158 commits behind `origin/main`** — two releases, a Bun runtime migration, and a rewrite of
adoption into layers. Nobody fetched before branching. The readiness check caught it, which is where
the rule `main` has not moved underneath lives; it belongs at the start of a run, not the end.

**What survived:** the tool, its tests, the spec's P1, and the two scenarios that walk tool behaviour
only. The code is unchanged from what five verification rounds and two deep-review rounds examined,
apart from renumbering its `AD-022` citation to `AD-018` — the old branch's numbering collided with
decisions upstream had already taken.

**What was scrapped:** the `package.json` gate glob, because upstream already discovers `scripts/`
and does it better with `git ls-files` instead of `find`; the wiring in
`.agents/skills/tlc-spec-driven/references/implement.md`, because that file no longer exists;
the `scripts/adopt.py` payload entry and its tests, because adoption is now Bun-native layers; the
ripgrep prerequisite line in `README.md`, which belonged to the glob change; and the QA legs that
walked adoption. Deep Review round 1 spent roughly an hour on files that are gone.

**What it means for this delivery's scope:** P2 left the spec. The tool ships, `GATES.md` names its
invocation, and the wiring is a separate feature designed against the structure that exists now
rather than the one that existed in August.
