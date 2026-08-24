# Local Office Editing

Batch synchronization rules for local Word documents through the installed document-editing capability. Read before multi-pass text, table, or image writes to a local document. These are verified behaviors of the local editor SDK; treat them as binding.

## Coordinate discipline

- Take every `begin` / `end` / `idx` from query tools (`doc_find`, structure-tree resolution, `doc_get_table_info`). Never hand-compute coordinates, and never reuse coordinates captured before an edit.
- Run batch text replacements in strictly descending document order. Descending order keeps unprocessed targets stable and makes a rerun idempotent after interruption.
- Verify uniqueness before each replacement: the probe text must match exactly once (`total == 1`). Skip and report otherwise.
- Snapshot the structure tree before a large multi-part edit; it is both the locator and the rollback reference.

## Call discipline

- Pass string arguments through `--json`. In `key=value` form the value is parsed as JSON first, so a lookup text like `0.571` silently becomes a number and the call fails.
- Image content carries the `file://` prefix for replacement, or an absolute local path for insertion; plain base64 without a `data:` prefix is rejected.
- Judge success by each tool's actual return shape: `update_count` and `version` for table region edits, `image_url` for image insertion. Do not assume a shared `message` field.
- Confirm a tool exists before calling it: `list`, then `schema <tool>`. Table creation uses `doc_insert_table_by_csv` or a full-grid `doc_modify_table_region`; there is no `doc_insert_table`.

## Table and image mechanics

- Same-shape cell text updates: partial patch with `inherit_styles: true` and only the changed cells.
- Structure changes (row or column count, merges): full-grid cells payload; the service deletes and rebuilds the table.
- Insert figures at the placeholder paragraph start, then remove the placeholder text and keep the caption. Width near 550 px at 96 DPI fits the text body; set height from the aspect ratio.

## Crash recovery

The editor service can stop mid-run, and the file_id changes on reopen. Recovery SOP:

1. Reopen the document through the preview entry point.
2. Take the fresh file_id from the editor pool status; never reuse a cached file_id.
3. Probe one superseded text and one new text to learn whether earlier writes landed; an untouched file reports `is_dirty: false`.
4. Rerun the batch; descending order makes the rerun safe.

## Two-way verification

After saving, verify numeric and wording updates in both directions: every new value is found, and every superseded value, stale label, and placeholder is absent. Report the counts.
