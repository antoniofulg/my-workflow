# Decisions

Two namespaces, on purpose. Mixing them is how an architecture invariant becomes a reversible
project call, or a one-feature choice becomes “the way the system is”.

## Where a choice lives

| Kind | Id | Home | Lifetime |
| --- | --- | --- | --- |
| **Project decision** | `AD-NNN` (three digits) | `.specs/STATE.md`, append-only | The project. Supersede, never delete, never reuse an id |
| **Architecture invariant** | Whatever the consuming project uses | `docs/architecture/` | Holds regardless of feature. This pack does not invent those ids |
| **Feature-local** | Table in `decisions.md` | `.specs/features/<slug>/decisions.md` | Versioned with the feature; promote if it must outlive it |

Always cite **the file** with the label. The same letters in two files are not the same object.

Promote before the pull request, per [ARTIFACT-LIFECYCLE.md](../guidelines/ARTIFACT-LIFECYCLE.md):

- Must outlive the feature as a project call → `AD-NNN`
- Must outlive it as a product promise → `docs/qa/scenarios/`
- Must outlive it as an invariant → the architecture docs
- Must outlive it as an agent rule → `docs/guidelines/`

Feature workflow state (`spec.md`, `design.md`, `tasks.md`, and validation) stays under the versioned
`.specs/features/<slug>/` tree. Workflow memory remains disposable local state.

## Halt vs decide

An unattended run (`autonomous`) must **settle or stop** before building:

- If the documents already answer it, proceed.
- If evidence in the repo is enough, decide, record `AD-NNN` with reasoning, move on.
- If the remaining choice would **change what gets built**, halt. Write the report. Merge nothing.

A decision recorded with its reasoning is reversible in the morning. A decision made silently
inside an implementation is found months later.

Ambiguity that does **not** change what gets built is not a halt. Record it in `decisions.md` and
continue. A phase boundary is not a checkpoint.

## What a recorded decision must carry

For anything an unattended run chose while nobody was watching:

- what was chosen
- why
- alternatives rejected, and why
- cost to change now
- cost to the user today

Separate the human’s calls from the run’s. A reviewer in the morning needs to know whose they are.

Accepting a security risk is the same shape: explicit approval plus an append-only `AD-NNN`.
Silence is not acceptance.

## Knowledge

When two source documents disagree, the **source wins** and the wiki concept is wrong. The bundle
holds the graph and the contradiction; it does not override `docs/` or `.specs/STATE.md`.

Offer to record durable knowledge when it surfaces in conversation. Never write to `knowledge/`
without a yes. Never skip the offer.
