# Local Office Editing

Read before multi-pass text, table, or image writes to a local document. Load only when the accepted route requires local Office mutation and a corresponding capability is actually available.

## Capability preflight

List actual tools and inspect their schemas. Treat names as hints and return structures as the contract. Record document identity, version, and save destination from current state. Confirm a tool exists before calling it: list, then schema. Table creation uses `doc_insert_table_by_csv` or a full-grid `doc_modify_table_region`; there is no `doc_insert_table`.

## Mutation transaction

Capture a structural or version snapshot. Find live anchors from the document and require a unique match. Apply positional edits in strictly descending document order. After each batch, verify the fields the tool actually returns and probe the resulting content.

## Call discipline

- Pass string arguments through `--json`. In `key=value` form the value is parsed as JSON first, so a lookup text like `0.571` silently becomes a number and the call fails.
- Image content carries the `file://` prefix for replacement, or an absolute local path for insertion; plain base64 without a `data:` prefix is rejected.
- Judge success by each tool's actual return shape: `update_count` and `version` for table region edits, `image_url` for image insertion. Do not assume a shared `message` field.
- Same-shape cell text updates: partial patch with `inherit_styles: true` and only the changed cells.
- Structure changes (row or column count, merges): full-grid cells payload; the service deletes and rebuilds the table.
- Insert figures at the placeholder paragraph start, then remove the placeholder text and keep the caption. Width near 550 px at 96 DPI fits the text body; set height from the aspect ratio.

## Recovery

After interruption or identity drift, reopen the document and reacquire identifiers. The editor service can stop mid-run, and volatile document handles such as `file_id` change on reopen. Recovery SOP:

1. Reopen the document through the preview entry point.
2. Take the fresh `file_id` from the editor pool status; never reuse a cached handle.
3. Probe one superseded text and one new text to learn whether earlier writes landed; an untouched file reports `is_dirty: false`.
4. Classify the mutation as not applied, applied, partially applied, or `STATE_UNKNOWN`.
5. Resume known states with idempotent operations. Descending order makes the rerun safe.
6. On `STATE_UNKNOWN`, stop immediately. Never continue a mutation or claim success from an unknown state.

## Conditional compatibility notes

| Observed interface | Apply only when observed |
|---|---|
| a CLI that coerces `key=value` scalars | pass document-search strings through its JSON argument modes |
| an image API that accepts URI content | use the URI form required by its schema, such as `file://` when explicitly documented or verified |
| volatile document handles such as `file_id` | reacquire the handle after reopen or service recovery |
| mutation results without a message field | decide success from documented fields such as version, update count, or returned object state |
| table APIs with separate CSV insertion and region mutation | select only from tools confirmed by list/schema inspection |

## Acceptance

Verify new content is present, old content is absent, the saved artifact reopens or renders, and the destination and returned version/update evidence agree. Report the counts.
