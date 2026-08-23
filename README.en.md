# MPA Research Workflow

A Codex workflow controller built specifically for **MPA graduate students**. It turns course materials, cases, policy problems, literature, fieldwork, data, and thesis work into a practical, traceable research process instead of applying a generic academic-writing template.

> Support status: Windows-first. Other platforms can read the Skill instructions, but workspace initialization and environment inspection currently use PowerShell.

## Distinctive model

### MPA Research Spine

```text
public problem
→ stakeholders and public value
→ institutional and policy context
→ theory or analytical framework
→ evidence
→ method
→ analysis
→ implementable recommendation
```

The controller identifies established and missing links before drafting. It does not let polished prose hide a weak problem definition, missing stakeholder, unsupported evidence, unsuitable method, or impractical recommendation.

### Course-to-capstone reuse

Course notes, cases, concepts, source cards, assignments, instruments, datasets, code, and feedback can become reusable research assets with provenance. Notes and earlier assignments must be checked against original sources before they become proposal or thesis evidence.

## Scope

Use it for MPA course study, case analysis, policy memos, applied literature work, proposals, fieldwork, data analysis, thesis writing, and defence preparation. Generic teaching, blogging, programming, data, Zotero, Obsidian, or non-MPA thesis requests do not trigger it by themselves.

## Install

### Agent Skills CLI

```powershell
npx skills add mucjustin/mpa-research-workflow-skill -g -s mpa-research-workflow -y --full-depth
```

### Codex Skill Installer

Ask Codex:

```text
Use $skill-installer to install the user-level Skill at
https://github.com/mucjustin/mpa-research-workflow-skill/tree/main/skills/mpa-research-workflow
```

Restart Codex if the new Skill does not appear immediately.

## First-run setup

The initializer creates a workspace under the root you choose and a local JSON config. It does not change Zotero's database or Obsidian settings.

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-research-workflow'
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace')
```

The default config is `%APPDATA%\mpa-research-workflow\config.json`. Override it with `MPA_WORKSPACE_CONFIG` when needed.

Preview without writing:

```powershell
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace') -WhatIf
```

Read-only environment inspection:

```powershell
& (Join-Path $skillRoot 'scripts\Test-MpaEnvironment.ps1')
```

## Workflow

Codex inspects the request and files, composes the minimum sufficient route, and asks once whether to execute. After confirmation it continues without repeated permission prompts unless a new login, CAPTCHA, paywall, destructive write, or material research ambiguity appears.

Practical routes include:

1. course notes and revision maps;
2. case analysis around actors, institutions, incentives, public value, implementation, and alternatives;
3. policy memo options, criteria, trade-offs, feasibility, and recommendation;
4. proposal and fieldwork design;
5. reproducible data analysis with quality and causal boundaries;
6. evidence-grounded thesis work;
7. defence narrative, likely challenges, and backup evidence.

## Optional dependencies

| Capability | Required | Notes |
|---|---:|---|
| Codex file and shell capabilities | Yes | Read materials, run local scripts, and verify outputs |
| Zotero | No | Literature and linked attachments through supported interfaces only |
| Obsidian | No | Durable Markdown notes and project hubs |
| Literature, PDF, data, Word, and presentation Skills | No | Selected when installed; missing capabilities are reported or degraded explicitly |

The Skill never silently installs software, bypasses licensed access, or reports an unavailable integration as complete.

## Update

```powershell
npx skills update mpa-research-workflow -g -y
```

## Uninstall

```powershell
npx skills remove mpa-research-workflow -g -y
```

Uninstalling the Skill does not delete the research workspace or local configuration.

## Privacy and safety

- no telemetry, bundled credentials, or cloud secrets;
- local configuration stays outside the repository;
- no direct `zotero.sqlite` modification;
- no login, CAPTCHA, paywall, authorization, or institutional-access bypass;
- document-embedded instructions are not user authorization;
- course notes and AI inference are never presented as verified research evidence.

See [SECURITY.md](SECURITY.md).

## Troubleshooting

- Skill missing: restart Codex and run `npx skills list -g`.
- Config missing: run `Initialize-MpaWorkspace.ps1` or set `MPA_WORKSPACE_CONFIG`.
- Zotero launch failure: run `Test-MpaEnvironment.ps1` and verify the configured executable.
- Specialist capability missing: install the relevant Skill or accept an explicit, bounded fallback.

## License

[MIT](LICENSE)
