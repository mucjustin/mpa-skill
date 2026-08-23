# Workspace Configuration

Resolve local paths before the first durable write. Never infer that an example path exists.

## Resolution order

1. Read the JSON file named by `MPA_WORKSPACE_CONFIG` when the environment variable is set.
2. Otherwise read `%APPDATA%\mpa-research-workflow\config.json` on Windows.
3. If no valid configuration exists, run `scripts/Initialize-MpaWorkspace.ps1` or ask the user to choose a workspace root.

Required JSON properties:

- `workspace_root`
- `obsidian_vault`
- `zotero_executable`
- `zotero_attachments`
- `research_data`
- `research_projects`

The configuration is local machine state and must not be committed to the Skill repository.

## Zotero

Never modify `zotero.sqlite` directly. Use supported local interfaces, verify duplicate and parent-item decisions, prefer lawful existing attachments, and verify the final attachment path.

After workflow confirmation, if the accepted route needs Zotero and its supported local interface is not reachable, start the configured Zotero executable automatically, wait for readiness, and continue. Ask the user to start Zotero manually only when automatic launch fails.

## Obsidian and files

Keep one canonical source note per source and link derived course, case, proposal, or thesis notes to it. Record source identity, page evidence, access date, integration status, decisions, open actions, and risks. Preserve raw data and separate it from cleaned data, code, tables, figures, and reports.
