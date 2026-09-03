## Compact Chat Summary (returned in chat after validation)

The Verifier returns this block to the orchestrator after completing all checks:

```markdown
## Validation: [Feature] - [PASS ✅ | FAIL ❌]

**Spec-anchored check**: [N/N ACs matched spec outcome | M spec-precision gaps flagged]
**Gate**: [X passed, 0 failed]
**Sensor**: [N mutations injected, N killed, N survived]
**Report**: `.specs/features/[feature]/validation-[slice].md` for a slice Verifier, or `.specs/features/[feature]/validation.md` for the final integrated Verifier (versioned workflow state)

**Ranked gaps** (if FAIL):
1. [Gap description] - [AC or criterion] - [file:line or "no evidence"]
2. ...
```

---

## Validation Report Template (`.specs/features/[feature]/validation-[slice].md` for a slice; `validation.md` only for final integrated validation)

```markdown
# [Feature] Validation

**Date**: [YYYY-MM-DD]
**Spec**: `.specs/features/[feature]/spec.md`
**Diff range**: [commit range or branch..HEAD]
**Verifier**: independent sub-agent (author ≠ verifier)

---

## Task Completion

| Task | Status     | Notes   |
| ---- | ---------- | ------- |
| T1   | ✅ Done    | -       |
| T2   | ✅ Done    | -       |
| T3   | ⚠️ Partial | [Issue] |

---

## Spec-Anchored Acceptance Criteria

| Criterion (WHEN X THEN Y) | Spec-defined outcome | `file:line` + assertion | Result |
| ------------------------- | -------------------- | ----------------------- | ------ |
| WHEN X THEN Y             | [precise value/state from spec] | `path/to/test.ts:42` - `expect(result.field).toBe(expected)` | ✅ PASS |
| WHEN A THEN B             | [expected value]     | `path/to/test.ts:88` - `expect(res.status).toBe(400)` | ✅ PASS |
| WHEN C THEN D             | not precisely defined in spec | - | ⚠️ Spec-precision gap |

**Status**: ✅ All ACs covered / ❌ Gaps present / ⚠️ Spec-precision gaps flagged

---

## Discrimination Sensor

| Mutation | File:line | Description | Killed? |
| -------- | --------- | ----------- | ------- |
| 1        | `src/service.ts:42` | Flipped condition `x > 0` → `x >= 0` | ✅ Killed |
| 2        | `src/service.ts:88` | Changed return value `status: 'active'` → `status: 'inactive'` | ✅ Killed |
| 3        | `src/handler.ts:15` | Removed side-effect call to `notify()` | ❌ Survived → fix task created |

**Sensor depth**: [lightweight / P0-full]
**Result**: [N/N killed] - [PASS ✅ | FAIL ❌]

---

## Interactive UAT Results (if performed)

| #   | Test        | Result   | Details                                         |
| --- | ----------- | -------- | ----------------------------------------------- |
| 1   | [Test name] | ✅ Pass  | -                                               |
| 2   | [Test name] | ❌ Issue | [Verbatim user response] - Severity: [inferred] |
| 3   | [Test name] | ⏭️ Skip  | [Reason]                                        |

---

## Code Quality

| Principle        | Status |
| ---------------- | ------ |
| Minimum code     | ✅     |
| Surgical changes | ✅     |
| No scope creep   | ✅     |
| Matches patterns | ✅     |
| Spec-anchored outcome check (asserted values match spec) | ✅ |
| Per-layer Coverage Expectation met (domain 1:1 ACs; routes happy+edge+error) | ✅ |
| Every test maps to a spec requirement - no unclaimed tests | ✅ |
| Documented guidelines followed: [file(s) or "none - strong defaults applied"] | ✅ |

---

## Edge Cases

- [x] Edge case 1: Handled correctly
- [ ] Edge case 2: NOT handled - needs fix

---

## Gate Check

- **Gate command**: [Build gate command from `tasks.md` when present, or the inline execution plan's verify command]
- **Result**: [X] passed, [Y] failed, [Z] skipped
- **Test count before feature**: [N]
- **Test count after feature**: [M]
- **Delta**: [+(M - N) new tests]
- **Skipped tests**: [list with justification for each]
- **Failures**: [list with details]

---

## Fix Plans (if issues found)

### Fix 1: [Issue description]

- **Root cause**: [What's actually wrong]
- **Fix task**: [Task definition]
- **Priority**: [Blocker/Major/Minor/Cosmetic]

---

## Requirement Traceability Update

Update spec.md requirement statuses:

| Requirement | Previous Status | New Status   |
| ----------- | --------------- | ------------ |
| [FEAT]-01   | Implementing    | ✅ Verified  |
| [FEAT]-02   | Implementing    | ❌ Needs Fix |

---

## Summary

**Overall**: ✅ Ready | ⚠️ Issues | ❌ Not Ready

**Spec-anchored check**: [N/N ACs matched spec outcome | M spec-precision gaps]
**Sensor**: [N/N mutations killed]
**Gate**: [X passed]

**What works**: [List]

**Issues found**: [Issue 1: How to fix]

**Next steps**: [Action]
```
