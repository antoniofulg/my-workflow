# Phase Skills — Slice S2 Validation

**Date**: 2026-09-03
**Spec**: `.specs/features/phase-skills/spec.md` — story PSK-03 (P1: Agents preload their skills), ACs 1–6 + Edge Cases
**Test contract**: `.specs/features/phase-skills/tests.md` — UT-005, UT-006, IT-001, IT-002
**Diff range**: `31c2bec..e8b9e50` (215a50c, d497023, 4a6a612, e8b9e50)
**Checkout**: `/Users/antoniofulg/Projects/my-workflow`, branch `feat/phase-skills`, clean before and after
**Verifier**: independent fresh session (author ≠ verifier)

**Verdict**: ✅ **PASS** with 1 ranked gap (Minor, non-blocking) and 1 procedural note.

> Procedural note: the `wverify` skill could not be invoked (`disable-model-invocation`, reserved for
> explicit user invocation). The phase was run from the Verifier role definition; the report shape
> follows `.agents/skills/wverify/references/validation-template.md`, which was read as a plain file.

---

## Task Completion

| Task | Commit | Status | Notes |
| --- | --- | --- | --- |
| T8 Preload skills in the Claude templates | 215a50c | ✅ Done | 5 templates, frontmatter only |
| T9 Rename load lines in the Codex templates | d497023 | ✅ Done | planner/implementer/verifier + explorer (see Deviation 2) |
| T10 Rename load lines in the Cursor templates | 4a6a612 | ✅ Done | same shape as T9 |
| T11 Reject unknown preload skills in sync | e8b9e50 | ✅ Done | check sits inside the plan loop, before any write |

---

## Spec-Anchored Acceptance Criteria

| Criterion | Spec-defined outcome | `file:line` + assertion | Result |
| --- | --- | --- | --- |
| **AC1** planner declares `skills: [workflow-spec-driven, wspecify, wtasks, ponytail]`, no `disallowedTools` | exact list, key absent | `templates/agents/claude/planner.md:7`. Asserted `tools/test_phase_skills.py:189` (`fields.get("skills") == "[" + ", ".join(expected) + "]"`, `CLAUDE_PRELOAD:41`) and `:195` (`assert "disallowedTools" not in fields`) | ✅ PASS |
| **AC2** implementer `skills: [wimplement, ponytail]` + `disallowedTools: Skill`; explorer + deep-reviewer `disallowedTools: Skill` with unchanged `tools`; verifier `skills: [wverify]`, no `disallowedTools` | exact values | `templates/agents/claude/implementer.md:7-8`, `explorer.md:9-10`, `deep-reviewer.md:7-8`, `verifier.md:7`. Asserted `tools/test_phase_skills.py:189,193,198` (`fields.get("tools") == READ_ONLY_TOOLS`, `:45`). Byte-check vs pre-slice: `git show 31c2bec:templates/agents/claude/explorer.md` line 9 and `deep-reviewer.md` line 7 are both `tools: Read, Grep, Glob, Bash` — identical to HEAD | ✅ PASS |
| **AC3** generated `.claude/agents/<role>.md` byte-identical to the template, only `model` / `effort` replaced | only those two lines differ | `diff templates/agents/claude/implementer.md .claude/agents/implementer.md` → `6c6 effort: medium` / `effort: high` only (`model:` resolves to the same `opus`). Asserted `tools/test_workflow_config.py:1738-1743` (`generated == template.replace("model: opus\neffort: medium\n", …)` — whole-file equality, plus the two-key survival check) | ✅ PASS |
| **AC4** a `skills:` name with no `.agents/skills/<name>/SKILL.md` ⇒ non-zero exit naming template and skill, nothing written | exit ≠ 0, both names in stderr, no packet files | `.agents/skills/workflow-config/scripts/workflow_config.py:575-580` (raise inside the plan loop, before `_write_bytes_atomic`). Asserted `tools/test_workflow_config.py:1767,1769-1770,1771-1773,1774` (`returncode != 0`; `"templates/agents/claude/implementer.md" in stderr`; `"nope" in stderr`; `not directory.exists()` per provider; `tree_state(root) == before`). Real-target proof below | ✅ PASS |
| **AC5** Cursor + Codex planner/implementer/verifier name the phase skills and name no reference file | phase-skill name present, reference tokens absent | `templates/agents/codex/planner.toml:9,19`; `codex/implementer.toml:23`; `codex/verifier.toml:15`; `cursor/planner.md:10,20`; `cursor/implementer.md:25`; `cursor/verifier.md:17`. Asserted `tools/test_phase_skills.py:212` (`removed not in text` over `REMOVED_REFERENCES:53`) and `:214` (`name in text` over `ROLE_PHASE_SKILLS:47`) | ✅ PASS |
| **AC6** every Load / Do-not-load line names a skill or a guideline path that exists | resolution, all 15 templates | `tools/test_phase_skills.py:216-221`: `assert token not in REFERENCE_FILENAMES`, `assert (ROOT / token).exists()`, `assert (SKILLS / name / "SKILL.md").is_file()`, driven by `load_lines():176-186` over `SCANNED_PROVIDERS:39` × `TEMPLATE_ROLES:37` | ✅ PASS |

**Status**: ✅ 6/6 ACs matched their spec-defined outcome.

---

## Real-target proof for AC4

Adopted a fresh target from the slice tree, then pointed its implementer template at a missing skill:

```
python3 scripts/adopt.py apply <target> --layers core      -> exit=0
python3 scripts/adopt.py apply <target> --layers parallel  -> exit=0
sed -i '' 's/skills: \[wimplement, ponytail\]/skills: [wimplement, nope]/' <target>/templates/agents/claude/implementer.md
python3 scripts/adopt.py apply <target> --layers parallel  -> exit=2
  stderr: workflow-config: templates/agents/claude/implementer.md preloads unknown skill 'nope'
python3 <target>/.agents/skills/workflow-config/scripts/workflow_config.py --root <target> --sync-agents -> exit=2
  stderr: workflow-config: templates/agents/claude/implementer.md preloads unknown skill 'nope'
```

AC4 fires through both the adopt path and direct sync in a real target.

---

## Discrimination Sensor

Injected in a detached worktree at `e8b9e50` (`git worktree add --detach`), never in the checkout.
Worktree removed afterwards; `git status --porcelain` empty.

| # | Mutation | File | Killed? | Killing assertion |
| --- | --- | --- | --- | --- |
| M1 | Drop `disallowedTools: Skill` | `templates/agents/claude/implementer.md:8` | ✅ Killed (exit 1) | `test_phase_skills.py:193` — `AssertionError: implementer: disallowedTools is None` |
| M2 | Drop `ponytail` from the planner `skills:` list | `templates/agents/claude/planner.md:7` | ✅ Killed (exit 1) | `test_phase_skills.py:189` — `planner: skills are '[workflow-spec-driven, wspecify, wtasks]'` |
| M3 | Restore `validate.md` in the Cursor verifier body | `templates/agents/cursor/verifier.md:20` | ✅ Killed (exit 1) | `test_phase_skills.py:212` — `cursor/verifier.md still names the removed reference validate.md` |
| M4 | Preload check `continue`s instead of raising | `workflow_config.py:577` | ✅ Killed (exit 1) | `test_workflow_config.py:1767` |
| M5 | Check `.agents/skills/<name>` **is_dir** instead of `SKILL.md` **is_file** | `workflow_config.py:576` | ❌ **Survived** | — see Gap 1 |
| M6 | Move the preload check after the write loop (validates, but only once packets are on disk) | `workflow_config.py:572-580` | ✅ Killed (exit 1) | `test_workflow_config.py:1771-1774` — the "nothing written" and `tree_state` assertions discriminate |
| M7 | Remove the template citation (`` `references/tasks-template.md` `` → "the tasks template") — **S1 surviving mutant 6** | `.agents/skills/wtasks/SKILL.md:165` | ✅ Killed (exit 1) | `test_phase_skills.py:146-148` — `wtasks/SKILL.md does not name references/tasks-template.md` |
| M8 | Break a validator path **inside a reference file**, not SKILL.md — **S1 gap 3** | `.agents/skills/wimplement/references/execution-template.md:156` | ✅ Killed (exit 1) | `test_phase_skills.py:149-152` via `phase_tree(name)` (`:79-81`) |
| M9 | Revert the T11 `.agents/skills` sync-input copy | `scripts/adopt.py:450` | ✅ Killed (exit 1) | `scripts/test_adopt.py:360` — `test_apply_is_cumulative_and_idempotent` |

**Sensor depth**: lightweight. **Result**: 9 injected, 8 killed, 1 survived.

Both S1 surviving/uncovered items (gap 2 = M7, gap 3 = M8) are now dead. S2 closed them as instructed.

---

## Implementer-reported deviations — adjudication

1. **`scripts/adopt.py:450` copies `.agents/skills` into the sync scratch root.**
   *Confirmed; root cause correct; no test weakened.* Reverting only that token makes
   `scripts/test_adopt.py:360` (`test_apply_is_cumulative_and_idempotent`) fail on
   `invoke(target, "apply", "--layers", "parallel").returncode == 0` — the scratch root has no
   `.agents/skills`, so the new T11 check rejects every preloaded name during `apply`. The change is
   one token in an existing tuple; `scripts/test_adopt.py` is untouched in this range
   (`git diff --numstat 31c2bec..e8b9e50` lists no entry for it). AC4 still fires in a real target —
   see the section above.
2. **Codex and Cursor `explorer` packets renamed their `implement.md` load token.**
   *In scope — required by AC6, not AC5.* The line sits under `## Load`
   (`templates/agents/claude/explorer.md:15,18`; `cursor/explorer.md:13,16`;
   `codex/explorer.toml:13`) and `implement.md` no longer exists anywhere in the pack after S1. AC6
   binds *the templates* (all of them), on *every* Load or Do-not-load line, to a name that exists.
   Leaving explorer alone would have violated AC6. AC5's narrower planner/implementer/verifier list
   does not exclude it. Accepted.
3. **UT-008 widened to name-every-reference plus a `phase_tree(name)` walk.**
   *Confirmed; both S1 survivors now die* (M7, M8). The replaced block was strictly narrower — the
   diff removes the SKILL.md-only scan and reinstates every one of its assertions inside the
   `phase_tree` loop. No assertion lost.
4. **AC3 diff.** *Confirmed.* Only `effort:` differs; `model:` is `opus` on both sides.
5. **AC2 tool lines.** *Confirmed byte-identical* to `31c2bec` for explorer and deep-reviewer.

---

## Edge Cases

- [x] *Two templates disagree on a skill name* — `test_phase_skills.py:214,220` fails naming the
      offending file (`{label} does not name its phase skill …` / `loads unknown skill …`). M2 and M3
      exercise both halves.
- [x] *A phase SKILL.md over 200 lines* — S1 scope, still asserted (`test_phase_skill_line_cap`).
- [x] *`.claude/skills/<name>` a directory instead of a symlink* — S1 scope
      (`test_claude_symlinks_resolve`), unaffected by this slice.

---

## Code Quality

| Principle | Status |
| --- | --- |
| Minimum code | ✅ — 22 added lines in `workflow_config.py`, 1 changed token in `adopt.py` |
| Surgical changes | ✅ — frontmatter and prose only in 12 templates |
| No scope creep | ✅ — explorer rename adjudicated as AC6-mandated, not creep |
| Matches patterns | ✅ — `_preload_skills` mirrors the existing `_header` / regex-constant style |
| Spec-anchored outcome check | ✅ |
| Every test maps to a spec AC | ✅ — UT-005 → AC1–2, UT-006 → AC5–6, IT-001 → AC3, IT-002 → AC4 |
| No test weakened, skipped, or deleted | ✅ — verified against `git diff --numstat` and the full hunk text |

---

## Gate Check

| Command | Exit code |
| --- | --- |
| `python3 tools/test_phase_skills.py` | **0** — `11 passed, 0 failed` (9 → 11, +2) |
| `python3 tools/test_workflow_config.py` | **0** — `57 passed, 0 failed` (55 → 57, +2) |
| `python3 scripts/test_adopt.py` | **0** — `ok (84 tests)` |
| `bun run test:python` | **0** — full suite green |
| `python3 .agents/skills/workflow-config/scripts/workflow_config.py --root . --sync-agents` (1st) | **0** — `"changed": []`, 15 unchanged |
| `python3 … --sync-agents` (2nd) | **0** — `"changed": []`, 15 unchanged — idempotent |

**Delta**: +4 tests. **Skipped**: none. **Failures**: none. Working tree clean after every run.

---

## Ranked gaps

1. **Minor — AC4's `SKILL.md` half is not discriminated (mutant M5 survived).**
   `.agents/skills/workflow-config/scripts/workflow_config.py:576` checks
   `(root / ".agents" / "skills" / skill / "SKILL.md").is_file()`, which is exactly what AC4 says.
   But IT-002 (`tools/test_workflow_config.py:1758-1762`) only ever names `nope`, a skill with no
   directory at all, so relaxing the check to `.is_dir()` on the skill directory still passes the
   whole suite. A half-installed skill (directory present, `SKILL.md` missing) — the realistic
   failure this AC exists to catch — would sync silently under that relaxation.
   *Fix task (new Implementer session, not this one)*: extend
   `test_sync_rejects_an_unknown_preload_skill_before_any_write`, or add a sibling case, that creates
   `<root>/.agents/skills/hollow/` with no `SKILL.md`, sets the implementer template to
   `skills: [wimplement, hollow]`, and asserts the same non-zero exit / stderr / nothing-written
   contract. Priority: Minor — the shipped implementation is correct; only the sensor is blind.

No blocking gap. S2 is ready to integrate.
