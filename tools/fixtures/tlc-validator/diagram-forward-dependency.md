# Diagram phase task layout with invalid dependency

## Test Coverage Matrix

| Task | Tests |
| --- | --- |
| T1 | unit |
| T2 | unit |
| T3 | unit |

## Gate Check Commands

| Gate | Command |
| --- | --- |
| quick | `python3 -m unittest` |

## Execution Plan

### Phase 1: Foundation

```text
T1 → T2
```

### Phase 2: Core

```text
T3
```

## Vertical Slice Closure

| Slice | Observable outcome | Independent gate | Merge if later slices are cancelled? | Why |
| --- | --- | --- | --- | --- |
| A | The task sequence completes. | `python3 -m unittest` | yes | Fixture contract. |

## Task Breakdown

### T1: Foundation

**Slice:** A
**Depends on**: None
**Where**: `src/one.py`
**Tests**: unit
**Gate**: quick

### T2: Invalid foundation dependency

**Slice:** A
**Depends on**: T3
**Where**: `src/two.py`
**Tests**: unit
**Gate**: quick

### T3: Core

**Slice:** A
**Depends on**: None
**Where**: `src/three.py`
**Tests**: unit
**Gate**: quick
