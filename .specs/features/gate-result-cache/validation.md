# Gate Result Cache — technical verification

Branch `feat/gate-cache-tool`, HEAD `535ccd0`, range `origin/main..HEAD` (`d79587c`, `535ccd0`).
Independent Technical Verifier; this session did not write the code. Contract:
`.specs/features/gate-result-cache/spec.md`, P1 only, `GRC-01`..`GRC-05`. Fingerprint decision:
`AD-018` in `.specs/STATE.md:280`.

**Result**: PASS

One low-severity documentation gap is ranked below; it is outside the five criteria and is already
covered by a recorded deferral.

## Port scope

The feature was built on a base 158 commits behind `origin/main` and re-based onto the current tree.
Carried-over evidence is admissible only if the ported code is byte-identical apart from the
citation renumber, so that was re-derived first:

```
$ git diff feat/gate-result-cache-full-backup HEAD -- tools/gate_cache.py tools/test_gate_cache.py
 tools/gate_cache.py | 4 ++--
 1 file changed, 2 insertions(+), 2 deletions(-)
```

Both hunks renumber `AD-022` to `AD-018` in the module docstring (`tools/gate_cache.py:7`) and in the
`ponytail:` trade-off note (`tools/gate_cache.py:12`). `tools/test_gate_cache.py` is unchanged. No
executable statement differs, so the five prior technical rounds and two deep-review rounds on the
tool body remain admissible; behaviour on this base was still re-measured below rather than assumed.

## Acceptance criteria

Every criterion is asserted by a spec-anchored test, not by a mirror of the implementation.

| ID | Behaviour | Implementation | Assertion |
| --- | --- | --- | --- |
| `GRC-01` | A miss executes, streams to stdout and a log, exits the command's status, and records | `tools/gate_cache.py:158`, `tools/gate_cache.py:161`, `tools/gate_cache.py:162`, `tools/gate_cache.py:176`, `tools/gate_cache.py:98` | `tools/test_gate_cache.py:87`, `tools/test_gate_cache.py:128`, `tools/test_gate_cache.py:140` |
| `GRC-02` | A matching passing record exits 0 without executing | `tools/gate_cache.py:147`, `tools/gate_cache.py:149` | `tools/test_gate_cache.py:92`, `tools/test_gate_cache.py:295` |
| `GRC-03` | The key is tree object, gate label, and exact argv | `tools/gate_cache.py:53`, `tools/gate_cache.py:31` | `tools/test_gate_cache.py:97`, `tools/test_gate_cache.py:101`, `tools/test_gate_cache.py:105`, `tools/test_gate_cache.py:111`, `tools/test_gate_cache.py:114`, `tools/test_gate_cache.py:281` |
| `GRC-04` | A failing record is retained and never short-circuits | `tools/gate_cache.py:71`, `tools/gate_cache.py:170` | `tools/test_gate_cache.py:117` |
| `GRC-05` | No fingerprint means run the gate and store nothing | `tools/gate_cache.py:136`, `tools/gate_cache.py:139` | `tools/test_gate_cache.py:149` |

Numbered criteria behind those IDs, checked individually:

- AC1 miss executes and streams to both sinks — `tools/gate_cache.py:106` writes each chunk to
  `sys.stdout.buffer` and to the log handle; exit status is the command's at `tools/gate_cache.py:177`.
- AC2 hit exits 0 without executing — `tools/gate_cache.py:150` returns before `execute`; the run
  counter at `tools/test_gate_cache.py:95` proves non-execution rather than inferring it.
- AC3 record fields — all nine keys written at `tools/gate_cache.py:164`; each read back at
  `tools/test_gate_cache.py:136`.
- AC4 failing record retained and re-run — status is stored as `fail` at `tools/gate_cache.py:170`
  and rejected by `tools/gate_cache.py:71`; asserted at `tools/test_gate_cache.py:121`.
- AC5 tracked, staged, or untracked-unignored change invalidates — `git add -A` over the temporary
  index at `tools/gate_cache.py:47`; asserted at `tools/test_gate_cache.py:97`,
  `tools/test_gate_cache.py:101`, `tools/test_gate_cache.py:281`.
- AC6 commit alone does not invalidate — `write-tree` at `tools/gate_cache.py:50` never reads the
  commit graph; asserted at `tools/test_gate_cache.py:105`.
- AC7 gate label or command change differs — `tools/gate_cache.py:54`; asserted at
  `tools/test_gate_cache.py:111` and `tools/test_gate_cache.py:114`.
- AC8 fail-open — `tools/gate_cache.py:138` catches, runs with `log=None`, stores nothing; asserted
  at `tools/test_gate_cache.py:157`.
- AC9 one evidence line — `tools/gate_cache.py:118`; single-line uniqueness enforced by the field
  reader at `tools/test_gate_cache.py:52`.

Edge cases from `spec.md:69` are each covered: usage error `tools/test_gate_cache.py:161`; missing
log `tools/test_gate_cache.py:143`; unknown schema version `tools/test_gate_cache.py:200`; torn or
non-object record `tools/test_gate_cache.py:216`; interrupt writes no record
`tools/test_gate_cache.py:262`.

## Discovery contract

The Python half of the gate is a shell loop over `git ls-files`, pinned by string equality at
`tools/shared/tests/qa-skills.test.ts:1150` against `package.json`. Discovery is therefore
`git ls-files`, and the suite is genuinely selected by it:

```
$ git ls-files -- 'scripts/test_*.py' 'tools/test_*.py' | sort | while read test; do echo "DISCOVERED-AND-RUN: $test"; done | grep gate_cache
DISCOVERED-AND-RUN: tools/test_gate_cache.py
```

Adding `tools/test_gate_cache.py` to `expectedPythonSuites` at
`tools/shared/tests/qa-skills.test.ts:1126` is required wiring, not a weakened assertion. The list is
one side of an equality whose other side is derived live from `git ls-files` at
`tools/shared/tests/qa-skills.test.ts:1116` and compared at
`tools/shared/tests/qa-skills.test.ts:1149`. The list cannot drift from `git ls-files` without
failing in either direction: a new tracked suite that is not listed fails, and a listed path that is
untracked or deleted fails. The literal is a change-detector on the gate's own surface, and the
executing path is the pinned shell loop, so the edit widened neither.

## Discrimination sensor

Six mutants, each on a file copy outside the checkout, ten runs of the suite each. Command per run:
`python3 <copy>/test_gate_cache.py`.

| Mutant | Change | Killed | Killed by |
| --- | --- | --- | --- |
| M1 | drop the `isinstance(record, dict)` guard at `tools/gate_cache.py:69` | 10/10 | `test_a_partial_record_is_absent` (`tools/test_gate_cache.py:239`) |
| M2 | `cached_log()` ignores `status` (`tools/gate_cache.py:71`) | 10/10 | `test_independent_test_for_p1` (`tools/test_gate_cache.py:122`) |
| M3 | `shutil.copy2` to `shutil.copyfile` at `tools/gate_cache.py:45` | 10/10 | `test_a_same_second_same_size_edit_is_never_a_hit` (`tools/test_gate_cache.py:193`) |
| M4 | remove the per-fingerprint log bound at `tools/gate_cache.py:156` | 10/10 | `test_each_run_writes_its_own_log_and_leaves_one_behind` (`tools/test_gate_cache.py:257`) |
| M5 | revert to one log path per fingerprint (`tools/gate_cache.py:158`) | 10/10 | `test_each_run_writes_its_own_log_and_leaves_one_behind` (`tools/test_gate_cache.py:255`) |
| M6 | drop the schema-version check at `tools/gate_cache.py:69` | 10/10 | `test_an_unexpected_schema_version_is_absent` (`tools/test_gate_cache.py:211`) |

60 of 60 mutant runs killed; no survivor, so no fix task. M3 is the timing-sensitive one and was the
reason for ten runs rather than one: it held at 10/10 on the current interpreter and filesystem.
Baseline suite on unmutated source exits 0 in about 11.6s.

## Environment

Nothing on this base shells out to `rg`. `git grep` over tracked `.ts`, `.py`, `.json`, `.toml`,
`.sh` and `.zsh` sources finds the token only inside strings that are documentation copy —
`tools/ad-index.py:91` emits a `rg -A 20` recipe into a generated index, and
`templates/agents/codex/planner.toml:15` is prose in an agent packet. Neither is a spawn: there is no
`spawnSync`, `execFileSync`, or `subprocess` invocation naming `rg` anywhere in the tracked tree. The
machine confirms it negatively — no `rg` binary exists on this host (`/opt/homebrew/bin/rg` and
`/usr/local/bin/rg` are both absent; the shell's `rg` is an interactive function that never reaches a
subprocess), and the full gate below is green regardless. The ripgrep `PATH` shim the old branch
needed for every gate run is not part of any evidence here, and the pull request should not claim it.

## Local cruft

The deleted `.agents/skills/tlc-spec-driven/` husk was untracked and contained only `__pycache__`
files. `git diff --diff-filter=D --name-only origin/main..HEAD` is empty and `git status --porcelain`
is clean, so nothing tracked was removed and no ignored-file deletion entered the range. The gate is
green for the right reason: `UT-001` asserts
`existsSync(join(repositoryRoot, ".agents/skills/tlc-spec-driven"))` is `false` at
`tools/shared/tests/qa-skills.test.ts:374`, whose invariant is that the renamed
`workflow-spec-driven` authority is installed exactly once and not shadowed by a stale copy under the
old name. A `__pycache__`-only directory at that path violated the invariant as written and as meant.
Removing it satisfies the assertion; the assertion itself was not touched.

## GATES.md

`docs/guidelines/GATES.md:44` through `docs/guidelines/GATES.md:58` reads correctly end to end after
`535ccd0`. "The rule:" at `docs/guidelines/GATES.md:49` now introduces four unconditional bullets,
which is right because the conditional it replaced was satisfied the moment the tool landed; the
section keeps its net length. The four bullets are accurate against the implementation: records key
on tree content and a commit alone does not invalidate one (`tools/gate_cache.py:50`), and scope
binds because the gate label is inside the key (`tools/gate_cache.py:54`), so a scoped record can
never be reached by a full-gate lookup.

The invocation line at `docs/guidelines/GATES.md:58` is accurate:
`python3 tools/gate_cache.py run --gate <scoped|full> -- <gate command>` matches the parser at
`tools/gate_cache.py:124` through `tools/gate_cache.py:127` and the usage string at
`tools/gate_cache.py:4`. `<scoped|full>` names this project's two scopes; the parser accepts any
label, which is wider than the doc and not a contradiction.

## Ranked gap

1. Low, documentation, outside `GRC-01`..`GRC-05`, no fix task required in this delivery.
   `docs/guidelines/GATES.md:51` says a matching passing record is fresh evidence to be cited instead
   of re-running, while `.agents/skills/autonomous/SKILL.md:135` still says "A cached or partial
   result is not evidence." The two documents disagree about whether a record may close a readiness
   claim. This is a declared deferral, not an undeclared contradiction: `AD-018` scopes itself to the
   tool and states that `.agents/skills/autonomous/SKILL.md` still refuses cached results and that
   this delivery does not change it (`.specs/STATE.md:291`), and the spec defers wiring to a separate
   redesign (`.specs/features/gate-result-cache/spec.md:29`). Worth carrying into the wiring feature
   so the two documents are reconciled in one change rather than drifting.

## Gate transcripts

Repository validator, `.agents/skills/workflow-spec-driven/scripts/validate_state.py`:

```
$ python3 /Users/antoniofulg/Projects/my-workflow/.agents/skills/workflow-spec-driven/scripts/validate_state.py gate-result-cache
validate_state: 0 error(s) across [gate-result-cache]
exit=0
```

Stale home install, `/Users/antoniofulg/.claude/skills/tlc-spec-driven/scripts/validate_state.py`:

```
$ python3 /Users/antoniofulg/.claude/skills/tlc-spec-driven/scripts/validate_state.py gate-result-cache
validate_state: 0 error(s) across [gate-result-cache]
exit=0
```

The two copies parse the verdict differently, so neither transcript alone supports a claim that "the
validator passes". The repository copy reads an explicit `Verdict` field first and falls back to a
bare `Result` line, then demands a `file:line` citation. The home copy joins every line matching a
validation heading or a `result:` pattern and calls the report unfilled if both status words appear
anywhere in that joined text. The single bare status line above is the only shape both accept.

Full gate through the tool:

```
$ python3 tools/gate_cache.py run --gate full -- bun run test:all
gate-cache MISS gate=full fingerprint=5244403ea6868a0ee15e2c958e2b996acc996c8dde34cbd2b2c563f97a84785a log=/Users/antoniofulg/Projects/my-workflow/.gate-cache/5244403ea6868a0ee15e2c958e2b996acc996c8dde34cbd2b2c563f97a84785a.i2lfx7y0.log status=pass
```

The record it wrote carries `"gate": "full"`, `"status": "pass"`, `"exit_code": 0`,
`"version": 1`, `"command": ["bun", "run", "test:all"]`, and a 754-line log, so the gate is green and
the tool recorded it. The Python half of that run reached `tools/test_gate_cache.py`, whose only
output is the bare `ok` at `tools/test_gate_cache.py:321`.
