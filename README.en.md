<p align="center">
  <img src="assets/logo.svg" alt="MPA Skill logo" width="160">
</p>

<h1 align="center">MPA Skill</h1>

<p align="center">
  <strong>Verifiable, reusable, and actionable research workflows for public administration</strong><br>
  A Codex Agent Skill designed for <strong>MPA graduate students</strong> — not a generic thesis template.
</p>

<p align="center">
  <a href="https://github.com/mucjustin/mpa-skill/actions/workflows/ci.yml">
    <img src="https://github.com/mucjustin/mpa-skill/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-blue.svg" alt="License: MIT">
  </a>
  <a href="https://github.com/mucjustin/mpa-skill/releases/latest">
    <img src="https://img.shields.io/github/v/release/mucjustin/mpa-skill?color=brightgreen" alt="Release">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/platform-Windows--first-0078D4.svg" alt="Platform">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/PowerShell-5.1%2B-5391FE.svg?logo=powershell" alt="PowerShell">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Codex-Agent%20Skill-8A2BE2.svg" alt="Codex Agent Skill">
  </a>
</p>

<p align="center">
  <img src="assets/banner.svg" alt="MPA Skill Banner" width="100%">
</p>

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🧭 What it solves first](#-what-it-solves-first)
- [🛣️ Applicable tasks](#-applicable-tasks)
- [🚀 Install](#-install)
- [⚙️ First-run setup](#-first-run-setup)
- [Reproducible audit example](#reproducible-audit-example)
- [📝 Three starter prompts](#-three-starter-prompts)
- [🏗️ Architecture](#-architecture)
- [🧰 Tech stack](#-tech-stack)
- [📂 Repository layout](#-repository-layout)
- [🧪 Development and testing](#-development-and-testing)
- [🔌 Optional dependencies](#-optional-dependencies)
- [🔒 Privacy and security](#-privacy-and-security)
- [⚙️ Update and uninstall](#-update-and-uninstall)
- [❓ Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧭 **MPA Research Spine** | A verifiable research thread: public problem → stakeholders → institutional context → theory → evidence → method → analysis → actionable recommendations. |
| 🛣️ **Ten Research Routes** | Course materials / case analysis / case competition / policy memo / literature review / research design / fieldwork / data analysis / thesis / defence — composed as needed. |
| 🔗 **Course-to-Capstone Reuse** | Notes, cases, surveys, and code can become research assets, but must be re-verified against original sources before reuse. |
| 🧠 **MPA Knowledge Ontology** | Theory map, China governance contexts, thinking checklist, and course-capability map to ground the controller in MPA content. |
| 🛡️ **Data before writing** | When usable data exists, audit provenance, cleaning, methods, numbers, and existing conclusions first; unaccepted evidence is not hidden by rewriting prose. |
| 🔄 **Recoverable delivery** | After local Office interruption, reacquire document identity and probe old and new content; stop at `STATE_UNKNOWN` instead of replaying writes or claiming success. |
| ✅ **Contract tests** | PowerShell contract tests cover repository structure, skill instructions, doc consistency, and privacy red lines. |

> **Windows-first**: the skill instructions are platform-agnostic, but automated workspace initialization and environment checks currently use PowerShell.

---

## 🧭 What it solves first

`mpa-skill` is for MPA, public-administration, and public-policy graduate students who need to connect coursework, cases, policy, fieldwork, data, and a thesis into one verifiable research chain. It organizes work around the **MPA Research Spine** (public problem → stakeholders and public value → institutional and policy context → theory → evidence → method → analysis → actionable recommendations) and applies two behavioral gates:

- **Data before writing:** when usable data exists, the [real-data workflow](skills/mpa-skill/references/real-data-workflow.md) audits provenance, cleaning, methods, numbers, and existing conclusions first. Unaccepted evidence or methods are not hidden by rewriting prose.
- **Recoverable delivery:** the [local Office editing rules](skills/mpa-skill/references/local-office-editing.md) load only when the route needs local Office mutation and a matching capability is available. After interruption, the controller reacquires document identity and probes old and new content; it stops at `STATE_UNKNOWN` instead of replaying a write or claiming success.

### v2.4.0 evidence boundary

The [frozen reliability benchmark](docs/validation/v2.4.0-benchmark.md) observed 7/8 for no skill, 7/8 for v2.3.0, and 8/8 for v2.4.0. The v2.4.0 gain against each baseline was +1/8, or +12.5 percentage points. The 10-paper pilot contained 7 development papers and 3 frozen holdouts; both v2.3.0 and v2.4.0 routed 10/10 papers and found 30/30 preregistered risks, with zero unsupported claims in the recorded outputs.

The observed improvement is **rejection of stale artifacts and recovery to a verifiable delivery state**. Paper-audit metrics were tied, so the pilot does not establish superior thesis diagnosis for v2.4.0. It sampled one response per condition, had 4/10 PDF structural preflights marked `UNAVAILABLE`, is a 10-paper pilot rather than a population estimate, contains only one China-context record, and depends on source links that may drift. It therefore does not prove general model reliability, Chinese-thesis quality, or live Office-mutation success.

### MPA Research Spine

<p align="center">
  <img src="assets/spine.svg" alt="MPA Research Spine" width="100%">
</p>

```text
public problem
→ stakeholders and public value
→ institutional and policy context
→ theory or analytical framework
→ evidence
→ method
→ analysis
→ actionable recommendations
```

The skill first identifies which parts of this spine already hold and which are still missing, then starts writing. This prevents polished prose from masking an ill-defined problem, missing stakeholders, insufficient evidence, mismatched methods, or infeasible recommendations.

### Course-to-capstone reuse

Course notes, cases, concepts, literature cards, assignments, surveys, data, code, and instructor feedback can become research assets — but provenance must be recorded. Course notes or old assignments must be re-verified against original sources before entering the proposal or thesis stage.

---

## 🛣️ Applicable tasks

- Complete reading, notes, revision, and assignment preparation for MPA course materials;
- Public-management case analysis;
- Case competition entries (for example, the China graduate public-management case competition): entry planning, fieldwork evidence organization, and theory framework refinement;
- Policy memos;
- Literature search and review for public problems;
- Proposals, research design, surveys, interviews, and fieldwork;
- Analysis of survey, interview, administrative, and mixed-methods data;
- MPA thesis writing, citation verification, and defence preparation.

Generic instructional design, blogging, programming, generic data analysis, standalone Zotero/Obsidian housekeeping, or non-MPA theses do not trigger this skill just because keywords look similar.

---

## 🚀 Install

### Using the Agent Skills CLI

```powershell
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
```

### Let Codex install it

Tell Codex:

```text
Use $skill-installer to install the user-level skill from
https://github.com/mucjustin/mpa-skill at skills/mpa-skill.
```

If a newly installed skill does not appear immediately, restart Codex.

---

## ⚙️ First-run setup

The initialization script only creates a workspace under a root you choose plus a local JSON config. It does not modify the Zotero database or Obsidian settings.

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace')
```

The default config is written to `%APPDATA%\mpa-skill\config.json`. You can point elsewhere via an environment variable:

```powershell
$env:MPA_WORKSPACE_CONFIG = 'path-to-your-config.json'
```

Preview what would be done:

```powershell
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace') -WhatIf
```

Check the current environment without writing files or launching apps:

```powershell
& (Join-Path $skillRoot 'scripts\Test-MpaEnvironment.ps1')
```

---

## Reproducible audit example

Codex inspects the request and attachments, composes a minimum sufficient route, then asks exactly once: `是否执行？`. After confirmation it proceeds automatically; it only asks again for logins, CAPTCHAs, paid access, destructive writes, or new substantive research ambiguity.

Take the Texas State University repository-open thesis [Establishing the Relationship Between Sewer Surcharge Fees and Pollutant Discharges by Industrial Users](https://digital.library.txst.edu/items/50bce8d1-3a34-49bb-8c38-8e52b8038265). PDF pages 29–32 cover exclusions, mean imputation, and aggregation; pages 30–32 and 37 show that implementation coincided with COVID-19 without an adequate control; and pages 36–41 do not justify converting non-significance into "no effect" or direct policy guidance. A reproducible route is: retrieve the open PDF → preserve page references while auditing raw data, missingness handling, and identification → mark counterfactual and inference gaps as `RISK`/`AUTHOR_INPUT_NEEDED` → write bounded conclusions only after analysis acceptance. Sources, pages, and preregistered risks are in the [benchmark report](docs/validation/v2.4.0-benchmark.md) and its machine-readable results. Reproduction keys: source `txst-50bce8d1-3a34-49bb-8c38-8e52b8038265`, risk `d3-identification` (pages 30, 31, 32, and 37).

---

## 📝 Three starter prompts

### 1. Raw-data conversion

```text
Convert the attached non-MPA report, raw data, and existing conclusions into MPA research. Re-anchor the public problem with the Research Spine, then audit provenance, cleaning, variables, methods, and numbers. Do not rewrite conclusions until the analysis is accepted.
```

### 2. Case/policy analysis without data

```text
Analyze this grassroots-governance case; no raw data is available. State the evidence gaps, compare stakeholders, institutional constraints, public value, alternatives, feasibility, and transfer boundaries, and do not invent data or effects.
```

### 3. Accepted-content Word delivery

```text
The research content has been accepted. Deliver it through a currently available Word/Office capability whose schema has been inspected. Record document identity and unique anchors before writing; after interruption, reopen and probe old and new content; stop at STATE_UNKNOWN; finally verify new content present, old content absent, and the saved file reopenable.
```

---

## 🏗️ Architecture

The skill is a **thin controller**: it owns scope classification, sequencing, minimum-sufficient routing, safety stops, and final acceptance. Specialist execution is delegated to matching skills; Zotero and Obsidian are optional integrations.

<p align="center">
  <img src="assets/workflow.svg" alt="MPA Skill workflow" width="100%">
</p>

Execution flow at a glance:

1. **Input**: user request and materials;
2. **Scope check**: identify whether the task belongs to public administration / public policy;
3. **Orchestrate**: classify and order tasks by dependency;
4. **Route**: compose the minimum sufficient route;
5. **Confirm**: single "是否执行？" prompt;
6. **Execute**: ten routes composed on demand, calling optional specialist skills;
7. **Accept**: MPA quality gate (research contract check) + final acceptance and handoff.

Safety stops run throughout: logins, CAPTCHAs, paywalls, licensed access, destructive writes, or substantive research ambiguity pause the workflow and ask.

---

## 🧰 Tech stack

| Layer | Technology |
|---|---|
| **Skill framework** | Codex Agent Skill (`SKILL.md` + `agents/openai.yaml`) |
| **Scripts & tests** | PowerShell 5.1+ / PowerShell 7 (`pwsh`) |
| **CI / CD** | GitHub Actions (`windows-latest`) |
| **Optional integrations** | Zotero (local API / Better BibTeX), Obsidian (Markdown Vault) |
| **Dependency management** | npm `skills` CLI |
| **Versioning** | [Semantic Versioning](https://semver.org/) + [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) |

---

## 📂 Repository layout

```text
mpa-skill/
├── assets/                         # Logo, banner, diagrams, workflow images
├── skills/mpa-skill/               # The skill itself (install entry)
│   ├── SKILL.md                    # Controller instructions and triggers
│   ├── agents/openai.yaml          # Skill metadata
│   ├── references/                 # Routing, research contract, real-data, local Office, deliverable, dependency, workspace rules
│   └── scripts/                    # Initialize-MpaWorkspace.ps1 / Test-MpaEnvironment.ps1
├── docs/validation/               # Corpus manifest, v2.4.0 machine results, and benchmark report
├── tests/                         # Public contract, reliability-scenario, corpus-manifest, and script tests (with fixtures)
├── .github/                       # CI workflow, issue and PR templates
├── CONTRIBUTING.md                # Contributing guide and versioning policy
├── CHANGELOG.md                   # Changelog
├── SECURITY.md                    # Security disclosure policy
└── LICENSE                        # MIT
```

---

## 🧪 Development and testing

Run the full test suite locally:

```powershell
pwsh -NoProfile -File tests/Test-PublicSkill.ps1
pwsh -NoProfile -File tests/Test-ReliabilityScenarios.ps1
pwsh -NoProfile -File tests/Test-BenchmarkManifest.ps1
pwsh -NoProfile -File tests/Test-WorkspaceScripts.ps1
```

The first two validate the public behavior/docs contract and [reliability scenarios](tests/fixtures/reliability-scenarios.json), the third validates the public thesis manifest, and the last exercises workspace scripts only in a temporary directory. CI (GitHub Actions, windows-latest) runs the same tests on main and every pull request.

---

## 🔌 Optional dependencies

| Capability | Required | Notes |
|---|---:|---|
| Codex file and terminal capabilities | Yes | Read materials, run local scripts, verify results |
| Python/R/spreadsheet analysis capability | No | Used only when the data route needs it and its contract is verifiable; otherwise hand off reproducible steps or report the block |
| Local Word/Office editing capability | No | Used only after content acceptance when the route needs it; provider-neutral and governed by the observed schema and return structure |
| Zotero | No | Literature and attachment management; supported interfaces only, never the database directly |
| Obsidian | No | Long-term Markdown notes and project hub |
| Literature, PDF, data, Word, PPT skills | No | Selected by the controller once installed; explicit degradation or blocking when missing |

The skill never silently installs third-party software, bypasses institutional access, or pretends an integration succeeded when it did not.

---

## 🔒 Privacy and security

- No telemetry, no built-in accounts, no cloud keys;
- Local config lives outside the skill repository;
- The public benchmark stores metadata, HTTPS sources, derived risks, and scores—not thesis PDFs, raw long text, or long excerpts; repository links may drift;
- Never modifies `zotero.sqlite` directly;
- Never bypasses logins, CAPTCHAs, paywalls, licensing, or institutional access;
- Never treats instructions embedded in attachments as user authorization;
- Never disguises course notes or AI inference as research evidence;
- Discloses AI assistance as current programme, course, or competition rules require; never presents AI-generated content as the student's own.

See [SECURITY.md](SECURITY.md).

---

## ⚙️ Update and uninstall

**Update:**

```powershell
npx skills update mpa-skill -g -y
```

**Uninstall:**

```powershell
npx skills remove mpa-skill -g -y
```

> Uninstalling the skill does not delete your research workspace or local config. Back up and confirm exact paths before removing those yourself.

---

## ❓ Troubleshooting

| Problem | Solution |
|---|---|
| Skill not found | Restart Codex and run `npx skills list -g`. |
| Config not found | Run `Initialize-MpaWorkspace.ps1`, or set `MPA_WORKSPACE_CONFIG`. |
| Zotero fails to start | Run `Test-MpaEnvironment.ps1` and confirm the configured executable exists. |
| Missing specialist capability | Install the matching skill, or let the controller use verified tools and state the degradation scope. |

---

## 🤝 Contributing

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for the workflow, content boundaries, and versioning policy; see [CHANGELOG.md](CHANGELOG.md) for history.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

<p align="center">
  <sub>Built with 🧠 for MPA researchers · from fragments to verifiable research</sub>
</p>
