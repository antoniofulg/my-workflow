# Domain and Architecture Modeling

**Read when:** a change creates or alters a bounded context, module boundary or dependency direction;
introduces, replaces or decouples an external provider; changes a port, adapter, queue or inter-module
message; or models an Entity, Value Object, Aggregate, Domain Service or Domain Event. Simple CRUD,
local bug fixes and boundary-preserving refactors do not.

This document owns how the domain is expressed in code. It does not own product language, domain
rules or architecture decisions. `docs/product/` owns the domain; the consuming project's architecture
docs own architecture invariants; `.specs/STATE.md` owns project decisions. Those sources win
whenever skill guidance conflicts.

## Design sequence

1. Ground the change in the canonical product and architecture sources. Use `knowledge/wiki/` only
   to follow connections or find contradictions; return to the cited source for the rule.
2. For boundaries, integrations or evolution, record ownership, public contract, port/adapter
   boundary, consistency model, failure semantics and evolution trigger in the feature design.
3. When a dependency crosses module or context boundaries, record its strength, distance and
   volatility, then decide whether to accept, relocate or decouple it.
4. For behaviour inside one bounded context, apply *Domain expression* below. Record the chosen
   building blocks, invariants, transaction boundary and domain events in the feature design without
   restating the product model.
5. When architectural and tactical modeling both apply, establish the bounded context and its
   contracts first, then model its internals.
6. Record a new lasting choice in the correct namespace: project decisions are `AD-NNN` entries in
   `.specs/STATE.md`; architecture invariants live in the consuming project's architecture docs.

For an auto-sized change without `design.md`, keep the same result in the inline design note.

## Domain expression

These rules fix how the model is written. A rule needing a concrete entity name to be understood
belongs in `docs/product/` instead.

### One aggregate, one module

An aggregate owns one folder, named for the aggregate. The folder holds the aggregate's behaviour,
its repository port and every adapter implementing that port, plus whatever else is specific to it.
Two aggregates in one folder is a folder that must split; one aggregate spread across two folders is
a boundary error.

Folders carrying no aggregate keep their own names: the HTTP surface, shared technical modules.

### One repository per aggregate root

Only an aggregate root gets a repository. Everything inside the aggregate is loaded and saved through
that root. The port takes and returns domain values. A persistence row never crosses it.

### Value Object or primitive field

A value becomes a Value Object when a rule must hold everywhere the value appears — a format, a range,
a normalization, a unit, or two fields only meaningful together. It stays a primitive when its only
rule is shape already enforced at the trust boundary.

The discriminator is where the value can enter from. A value that reaches the domain only through a
validated request needs no second guard. A value the domain derives itself, reads back from storage,
or receives from a job or a provider callback bypasses that boundary, so its rule has to travel with
it.

Identifiers stay opaque strings unless the project has decided otherwise.

### Where invariants are enforced

An invariant over one aggregate's own state is enforced inside that aggregate, in the method that
performs the transition, before the state changes. The method is named for the transition in the
product's language and refuses an illegal one rather than reporting it.

| Layer | Its job |
| --- | --- |
| HTTP / command boundary | Rejects malformed input and resolves authority before the command |
| Aggregate | Decides whether the transition is legal, then performs it |
| Repository adapter | Persists a decided outcome |
| Database constraint | Backstop proving the invariant held |

Authority is not an aggregate invariant. The command boundary resolves who may act; an aggregate
re-deriving it duplicates a rule whose inputs it cannot see.

A database constraint is never a rule's only statement. A rule living solely in SQL cannot be
exercised without the database and cannot explain its own refusal.

### Transaction boundary

One command mutates one aggregate in one transaction. The application layer opens the transaction and
the adapter runs inside it. An aggregate receives no handle to the transaction; it computes the next
state and returns it.

A rule spanning two aggregates resolves through events or jobs, never through a second aggregate
mutation in the same transaction, unless the architecture docs explicitly allow it.

### What the domain may import

A domain module imports the language standard library and other modules of the same aggregate.

**It does not import the web framework, the API framework, the persistence framework, a provider SDK,
or the public wire-contract package.** Each is a boundary the domain is meant to outlive. A domain
type matching a DTO field for field is still declared separately, because a wire contract and an
internal model change for different reasons.

The consuming project's boundary gate, if it has one, enumerates those module names. Moving business
rules out of persistence adapters is done as part of the next feature that touches a repository, not
as a migration of its own.

### Ports and adapters

The domain declares the port and names it for what the domain needs. The adapter conforms. A port
mirroring a library's API instead of the domain's need has the direction backwards.

A port earns its place when it isolates something the domain must outlive, or when it lets the domain
be exercised without infrastructure. A collaborator that is neither needs no port.

### Proportional intensity

Match the machinery to the rules a module actually has:

| What the module has | What it gets |
| --- | --- |
| Shape rules only | A contract schema, a repository and route handlers |
| One rule holding on every write | That rule, in one named function in the module |
| States with legal and illegal transitions, or fields that must agree | An aggregate owning those transitions |
| A rule spanning aggregates | A domain service, or the architecture doc's event path |

Model behaviour where a rule exists. Before adding an aggregate, name the invariant it protects; when
no name comes, the module has shape rules and the first row applies.

## Vendored skill scope

Vendored modeling skills are advisory. Their defaults do not become project rules merely because the
skill is installed. Do not edit a vendored skill to record a project exception. Record conventions
here after they are adopted.
