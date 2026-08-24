# Dependencies

All integrations are optional. Inspect installed Skills, plugins, applications, and tools before composing the route; never claim an integration exists from its name alone.

| Need | Preferred capability when installed | Graceful fallback |
|---|---|---|
| documents and PDFs | installed document/PDF readers and converters | read supported files directly; report unsupported formats |
| literature workflow | an end-to-end literature controller | use verified search, lawful acquisition, and source-card capabilities separately |
| one-paper reading | a paper-card or full-paper reader | extract a source-grounded structured reading note |
| research design | an academic research or proposal workflow | apply the MPA Research Contract directly |
| quantitative or qualitative data | installed analytics, spreadsheet, notebook, or statistics tools | audit the data and report the missing execution capability |
| citations | citation and reference-verification tools | verify identifiers and fields using available authoritative sources |
| Zotero | supported local API, connector, or linked-attachment helper | prepare a verified user-run handoff; never edit the database directly |
| Obsidian | local Markdown filesystem access or an Obsidian integration | write portable Markdown to the configured vault when authorized |
| Word or slides | installed document or presentation workflow | deliver accepted Markdown and a handoff specification |

When a preferred dependency is unavailable, choose the closest verified installed capability that preserves the requested evidence and safety boundaries. If no adequate capability exists, report the missing dependency before execution and keep completed read-only analysis separate from the blocked integration.

## Verified integration pitfalls

| Area | Verified behavior | Rule |
|---|---|---|
| local editor arguments | `key=value` parses values as JSON first; a lookup text like `0.571` becomes a number | pass string arguments via `--json` |
| local editor images | plain base64 without a `data:` prefix is rejected | use `file://`-prefixed local paths |
| local editor sessions | the service can stop mid-run and the file_id changes on reopen | re-read pool status, probe write state, rerun idempotently |
| local editor tables | `doc_insert_table` does not exist; region edits report `update_count`, not a message field | use `doc_insert_table_by_csv` or full-grid `doc_modify_table_region`; judge success by return shape |
| Zotero local API | read-only in verified setups (writes return 501) | write through the connector API; prepare a manual handoff for the remainder |
