# Layered Workflow Adoption Test Contract

## Unit

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| UT-001 | Resolves fixed layers | duplicate/whitespace selections and `full` | deterministic dependency order; exact four-layer catalog |
| UT-002 | Rejects invalid layers | unknown layer or invalid graph | exit/exception before target access |
| UT-003 | Classifies managed actions | absent, identical, recorded-clean, recorded-drifted paths | add, claim, update, or conflict exactly |
| UT-004 | Validates manifests | malformed schema, duplicate JSON keys, non-normalized/escaping paths, unknown layer | rejected without target mutation |
| UT-005 | Parses managed blocks | valid, missing, duplicate, nested, edited markers | exact replace or conflict |

## Integration

| ID | Behaviour | Given / When | Expected |
| --- | --- | --- | --- |
| IT-001 | Plans without writes | text and JSON plan for `parallel,quality` | core included; stable actions/output; target byte-identical |
| IT-002 | Applies core to an existing project | consumer prose/config/package files exist | core files and blocks installed; consumer content preserved |
| IT-003 | Adds layers cumulatively | core, then parallel, then quality/extras | manifest union grows; omitted installed layers retained |
| IT-004 | Aborts conflicts atomically | managed drift and unowned differing destination | all conflicts reported; zero target writes |
| IT-005 | Preserves instruction ownership | AGENTS/CLAUDE prose, managed blocks, `--skip-agents` | outside prose byte-identical; skip leaves both files identical |
| IT-006 | Reports status drift | clean, missing, modified, retained records | exact state and exit 0/1; no writes or sync |
| IT-007 | Re-applies idempotently | same layers and source twice | byte-identical target and manifest |
| IT-008 | Preserves missing-only files | existing QA profile/config template destinations | consumer bytes preserved and ownership recorded |
| IT-009 | Preserves full capability set | full plan/apply | exact pre-feature path inventory plus sync and links |
| IT-012 | Publishes packets before authority marker | observe apply publication paths | generated packets are published before `.my-workflow/adoption.json`, which is last |
| IT-010 | Keeps Bun consumer boundary | adopted knowledge runtime in target with its own package metadata | direct Bun CLI passes; package files byte-identical; forbidden authorities absent |
| IT-011 | Rejects legacy CLI | positional target invocation | exit 2 with new-subcommand guidance; zero writes |
| IT-013 | Distinguishes fresh apply from installed status | fresh target with no manifest | apply succeeds; status exits 2 without writes |
| IT-014 | Rejects non-directory parent | selected `tools/` parent is a regular file | exit 2 before writes |

## End-to-end

| ID | Journey | Steps | Expected |
| --- | --- | --- | --- |
| E2E-001 | Existing project adopts incrementally | plan core; apply core; status; plan/apply parallel+quality+extras; status; run knowledge/import probe | reviewed actions match writes; final status clean; Bun CLI works; import calls Orca zero times |

## Security

| ID | Abuse case | Attempt | Expected |
| --- | --- | --- | --- |
| SEC-001 | Escape through target symlink | selected leaf or parent symlink points outside | exit non-zero before writes; external referent unchanged |
| SEC-002 | Escape through manifest path | `../`, absolute, duplicate JSON key, non-normalized, or symlinked managed path | manifest rejected; target and external paths unchanged |
| SEC-003 | Hide a managed-file conflict | alter one recorded file then apply several layers | all conflicts listed; no other selected file or manifest changes |
| SEC-004 | Corrupt instruction markers | duplicate/nest/remove a managed marker | conflict before writes; consumer prose unchanged |
| SEC-005 | Redirect through a non-directory parent | selected destination parent is a regular file | exit 2; target remains unchanged |
