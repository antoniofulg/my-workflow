# Legacy Adoption Resolution Specification

## Problem Statement

Projects that copied older workflow files before the ownership manifest existed cannot adopt the
modular workflow. `plan` correctly reports divergent unowned destinations as conflicts, but the
maintainer has no safe public command for explicitly transferring those reviewed paths to workflow
ownership.

## Goals

- [ ] Resolve a legacy no-manifest adoption through explicit path-by-path authorization.
- [ ] Preserve the existing zero-write conflict contract until every current file conflict is authorized.
- [ ] Require a clean Git baseline so every replaced tracked byte remains recoverable.
- [ ] Reuse the existing staged publication, rollback, and manifest-last authority boundary.

## Out of Scope

| Feature | Reason |
| --- | --- |
| Automatic merge of project customizations | Only the project can decide where product-specific content belongs. |
| `--replace-all` or implicit takeover | Bulk authorization would recreate the silent overwrite risk. |
| Repairing drift after an adoption manifest exists | `status` and normal conflict resolution already own managed drift. |
| Historical hash inventory | Repository history recognized only 7/32 CRM conflicts and 21/40 Creatista conflicts. |
| Non-Git or dirty-target resolution | There is no complete recoverable baseline for destructive replacement. |
| Automatic managed-block repair | An altered instruction block cannot be separated safely from consumer prose. |

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Public command | `resolve` beside `plan`, `apply`, and `status` | Resolution is an explicit ownership transition, not a hidden apply mode. | User authorized recommended action |
| Authorization | Repeat `--replace PATH` for every current file conflict | Exact paths make destructive intent reviewable and auditable. | Agent default |
| Completeness | The confirmed set must equal the current replaceable conflict set | Partial publication would leave ambiguous ownership. | Agent default |
| Recovery | Require a Git repository with `HEAD` and an empty porcelain status | Replaced tracked bytes remain recoverable from the current commit. | Agent default |
| Existing manifest | Reject resolution when `.my-workflow/adoption.json` exists | The command is only a bootstrap for pre-manifest installations. | Agent default |
| Instruction files | Recommend `--skip-agents`; altered managed blocks remain manual conflicts | Product prose must never be taken over as a file conflict. | Agent default |
| Historical recognition | Do not ship hash history | It cannot resolve most observed conflicts and adds permanent inventory cost. | Agent default |
| Remaining dimensions | Authentication, rate limits, expiry, external providers, and long-lived persistence are N/A | This is a local one-shot Git and filesystem command. | Agent default |

**Open questions:** none - all resolved or logged above.

## Security Surfaces

| ID | Surface | Control | Requirements |
| --- | --- | --- | --- |
| S1 | Public CLI and ownership manifest | Separate verb, exact replacement set, deterministic result | LAR-01, LAR-02, LAR-03, LAR-08 |
| S6 | User-supplied filesystem paths | Catalog membership, normalized paths, existing no-follow preflight | LAR-04, SEC-001, SEC-002 |
| S11 | Git process and publication boundary | Direct argv, clean baseline, staged rollback, manifest last | LAR-05, LAR-06, LAR-07, SEC-003 |

## User Stories

### P1: Resolve reviewed legacy workflow conflicts

**User Story**: As a maintainer of a project that predates adoption manifests, I want to authorize
reviewed workflow paths explicitly so that modular adoption can replace obsolete copies without
silently taking product-owned content.

**Acceptance Criteria**:

1. The adopter SHALL expose `resolve TARGET --layers LIST --replace PATH...` as a separate command.
2. WHEN a clean Git target has no adoption manifest and the normalized replacement set equals every current replaceable file conflict THEN the adopter SHALL publish the selected workflow and schema-1 manifest through the existing staged transaction.
3. WHEN resolve succeeds THEN the adopter SHALL report every authorized path with action `replace` and SHALL make a subsequent `status` return clean.
4. IF one current replaceable conflict is not authorized THEN the adopter SHALL exit `1`, report the unresolved conflict, and perform zero target writes.
5. IF an authorization names a non-conflict, duplicate-unsafe, absolute, escaping, or managed-block path THEN the adopter SHALL exit `2` and perform zero target writes.
6. IF the target is not a Git repository with `HEAD`, has any porcelain status entry, or already has an adoption manifest THEN the adopter SHALL exit `2` and perform zero target writes.
7. WHERE `--skip-agents` is present the adopter SHALL leave `AGENTS.md` and `CLAUDE.md` byte-identical.
8. IF staging, synchronization, link publication, cleanup, or file publication fails THEN the adopter SHALL restore the clean baseline and SHALL NOT publish the adoption manifest.
9. The adopter SHALL invoke Git and every helper through direct argument vectors without shell interpolation.

**Independent Test**: A disposable legacy Git project starts with divergent tracked workflow files,
runs incomplete and invalid resolutions with byte-identical snapshots, then authorizes the exact
conflict set and reaches clean adopted status while preserving instruction files.

## Edge Cases

- IF resolve sees only identical claimable files and receives `--replace` THEN it SHALL reject the non-conflict authorization without writes.
- IF an altered managed instruction block remains THEN resolve SHALL report it as unresolved and SHALL NOT replace the instruction file.
- IF the target becomes dirty before publication THEN resolve SHALL fail before the first target write.
- WHEN the same resolved layers are later applied normally THEN apply SHALL remain byte-idempotent.

## Requirement Traceability

| Requirement ID | Story | Phase | Status |
| --- | --- | --- | --- |
| LAR-01 | Public resolve command | Specify | Implemented |
| LAR-02 | Exact complete authorization | Specify | Implemented |
| LAR-03 | Deterministic replace output and clean status | Specify | Implemented |
| LAR-04 | Reject incomplete or invalid authorization | Specify | Implemented |
| LAR-05 | Require clean Git baseline | Specify | Implemented |
| LAR-06 | Reuse staged rollback | Specify | Implemented |
| LAR-07 | Preserve instruction files | Specify | Implemented |
| LAR-08 | Reject manifest-backed targets | Specify | Implemented |
| SEC-001 | Reject unsafe replacement paths | Specify | Implemented |
| SEC-002 | Preserve no-follow containment | Specify | Implemented |
| SEC-003 | Avoid shell interpolation | Specify | Implemented |

**Coverage:** 11 total, 11 mapped to the test contract, 0 unmapped.

## Success Criteria

- [ ] The canonical adoption suite proves zero writes for every rejected resolution.
- [ ] A disposable pre-manifest project reaches clean modular adoption with exact reviewed paths.
- [ ] CRM and Creatista dry-run plans can produce explicit replacement lists without touching active checkouts.
- [ ] The full repository gate exits zero.
