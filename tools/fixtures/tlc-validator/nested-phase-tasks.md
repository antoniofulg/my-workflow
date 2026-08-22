# Nested phase task layout

## Test Coverage Matrix

| Task | Tests |
| --- | --- |
| T1 | unit |
| T2 | unit |

## Gate Check Commands

| Gate | Command |
| --- | --- |
| quick | `python3 -m unittest` |

## Execution Plan

### Phase 1: Foundation

#### T1: Foundation task

### Phase 2: Core

#### T2: Core task

## Task Breakdown

### T1: Foundation task

**Depends on**: None
**Where**: `src/foundation.py`
**Tests**: unit
**Gate**: quick

### T2: Core task

**Depends on**: T1
**Where**: `src/core.py`
**Tests**: unit
**Gate**: quick
