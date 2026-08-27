# Two merge-alone slices

## Test Coverage Matrix

| Task | Tests |
| --- | --- |
| T1 | unit |

## Gate Check Commands

| Gate | Command |
| --- | --- |
| quick | `python3 -m unittest` |

## Execution Plan

### Phase 1: Foundation

```text
T1 -> T2 -> T3 -> T4
```

## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| A | The first capability works alone. | `python3 -m unittest capability_a` | yes | It has independent user value. |
| B | The second capability works alone. | `python3 -m unittest capability_b` | yes | It has independent user value. |

## Task Breakdown

### T1: Capability A setup

**Slice:** A
**Depends on:** None
**Where:** `src/capability_a.py`
**Tests:** unit
**Gate:** quick

### T2: Capability A behavior

**Slice:** A
**Depends on:** T1
**Where:** `src/capability_a_test.py`
**Tests:** unit
**Gate:** quick

### T3: Capability B setup

**Slice:** B
**Depends on:** None
**Where:** `src/capability_b.py`
**Tests:** unit
**Gate:** quick

### T4: Capability B behavior

**Slice:** B
**Depends on:** T3
**Where:** `src/capability_b_test.py`
**Tests:** unit
**Gate:** quick

### TDR1: Deep review remediation

**Depends on:** None
**Where:** `review.md`
**Tests:** unit
**Gate:** quick
