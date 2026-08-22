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

## Task Breakdown

### T1: Foundation

**Depends on**: None
**Where**: `src/one.py`
**Tests**: unit
**Gate**: quick

### T2: Invalid foundation dependency

**Depends on**: T3
**Where**: `src/two.py`
**Tests**: unit
**Gate**: quick

### T3: Core

**Depends on**: None
**Where**: `src/three.py`
**Tests**: unit
**Gate**: quick
