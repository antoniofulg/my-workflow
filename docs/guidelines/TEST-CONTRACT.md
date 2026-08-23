# Test Contract

**Read when:** writing or planning any test, or breaking a spec into tasks.

**Why this exists:** "All branches covered" cannot be audited. Named cases assigned to one task can.
A test that mirrors the implementation, or exists only to raise coverage, proves nothing.

## The artifact

Every feature large enough to have a `tasks.md` also has `.specs/features/<feature>/tests.md`. It is
written during Specify, immediately after acceptance criteria are settled, and it is the input to
task breakdown — not an output of it.

```markdown
# <Feature> Test Contract

## Unit
| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Rejects a record with a malformed email | `createRecord` with `email: "a@"` | throws `ValidationError`, no row written |

## Integration
| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Record survives a round trip | insert then read by id | every field equals what was written |

## End-to-end
| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| E2E-001 | Visitor completes the public form | fill, submit | confirmation visible; row present |

## Security
| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | Unauthenticated read of another account's records | `GET` the list route with no session | 401, no body leakage |
```

## Rules

1. **Derive, do not invent.** Every case maps to a spec acceptance criterion. Use components, error
   paths, boundaries, and journeys to find coverage gaps; if one reveals behavior absent from the
   spec, clarify the acceptance criterion before adding a case. Never create a case solely because a
   component or boundary exists. Security cases also follow `docs/guidelines/SECURITY.md` when its
   condition fires.
2. **Every case names an exact input, condition and expected result.** "Test the happy path" is not a
   case. "`POST` the create route with an unknown region returns 422 and no row" is.
3. **Every ID is assigned to exactly one task** — the task implementing the behaviour it verifies.
   Integration and e2e IDs go to the task that completes the flow they exercise.
4. **Audit before the breakdown is approved.** Every ID in `tests.md` appears in exactly one task's
   `## Tests` section. No orphans, no duplicates. An ID that fits no task means the breakdown is
   missing a slice — fix the breakdown, never drop the case.
5. **Tests ship inside the task that implements the behaviour.** Never a task dedicated to testing.
6. **A case is not done because a test exists.** It is done when the test asserts the contracted
   expected result. A test that exists without asserting the contracted behaviour is a hollow case and
   fails review.

## Choosing the layer

Pick the cheapest layer that can discriminate the behaviour.

| Layer | Use for | Cost |
| --- | --- | --- |
| Unit | Domain rules, validation, pure transformation, every error path | Cheapest |
| Integration | Anything crossing a boundary: repository, HTTP handler, queue | Moderate |
| End-to-end | A complete user journey through the real stack | Most expensive — deliberately scarce |

**e2e is a last resort, not a coverage tool.** If an integration test can discriminate the failure,
the e2e case is redundant.

Permanent e2e specs carry `@feature:<slug>` and `@journey:<slug>` tags, unique data with `finally`
cleanup, and residue-zero assertions. The `@feature:<slug>` tag is the selector the consuming
project's browser scoped gate uses to run only that feature's scenarios.

## Never add a test just to raise coverage

Before adding a test, name three things: the invariant it protects, the layer that owns it, and the
canonical suite it belongs to. Extend that suite. If no invariant exists, do not write the test.

Forbidden by default — allowed only when that artifact is the product contract and no stronger gate
already owns it:

- Tests asserting prose, copy or documentation content
- Snapshot tests standing in for behavioural assertions
- Tests over generated files, config shape, or CSS
- A second suite duplicating an existing one because the existing one was hard to find

## Where this differs from what tlc ships

`tlc-spec-driven` generates a Test Coverage Matrix during Tasks — a per-layer policy
(`Service → unit → all branches; 1:1 to spec ACs`). Keep it: it decides *which layer* and *which
command*. This contract adds *which cases*, so the matrix's promise becomes countable. Both exist;
the matrix sets the shape, `tests.md` enumerates the content.

The mutation sensor stays. Enumerated cases prove coverage exists; the sensor proves the coverage is
real. Neither substitutes for the other.
