<p align="center">
  <img src="assets/logo.svg" alt="MPA Skill logo" width="160">
</p>

<h1 align="center">MPA Skill 🎓</h1>

<p align="center">
  <strong>From fragments to verifiable research</strong><br>
  A Codex Agent Skill for <strong>MPA graduate students</strong> — not a generic thesis template 🙅
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

## 🎯 What is this

A Codex Agent Skill that helps MPA graduate students connect coursework, cases, policy, fieldwork, data, and a thesis into **one verifiable research chain**.

At its core is the **MPA Research Spine**: public problem → stakeholders → institutional context → theory → evidence → method → analysis → actionable recommendations. Find the gaps first, then write ✏️

Two behavioral gates run throughout:

- 🛡️ **Data before writing**: when usable data exists, audit provenance, cleaning, methods, and numbers first. See the [execution handbook](skills/mpa-skill/references/execution.md).
- 🔄 **Recoverable delivery**: after Office interruption, reacquire document identity; stop at `STATE_UNKNOWN` when unsure.

> **Windows-first** · Instructions are platform-agnostic; automation scripts use PowerShell

---

## ✨ Features

| | Feature | One-liner |
|---|---|---|
| 🧭 | MPA Research Spine | Eight-step verifiable research thread |
| 🛣️ | Ten research routes | Course/case/policy/lit/design/fieldwork/data/thesis/defence |
| 🔗 | Course-to-capstone reuse | Notes, cases, code become assets; re-verify before reuse |
| 🧠 | MPA knowledge ontology | Theory map + China governance contexts + thinking checklist |
| 🛡️ | Data before writing | Audit first, write second, never mask gaps |
| 🔄 | Recoverable delivery | Interruptible; stops at `STATE_UNKNOWN` |
| 🧾 | AI-use disclosure | Generated only from actual tool use; see [disclosure workflow](skills/mpa-skill/references/aigc-disclosure.md) |
| ✅ | Contract tests | PowerShell tests cover structure, instructions, docs, and privacy |

---

## 🚀 Quick start

### Install

```powershell
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
```

### Initialize workspace

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace')
```

Default config goes to `%APPDATA%\mpa-skill\config.json`. Does not modify Zotero database or Obsidian settings. Add `-WhatIf` to preview; run `Test-MpaEnvironment.ps1` to check your setup.

### Update and uninstall

```powershell
npx skills update mpa-skill -g -y    # Update
npx skills remove mpa-skill -g -y    # Uninstall (keeps your workspace and config)
```

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

The skill is a **thin controller**: scope classification, routing, safety stops, and final acceptance. Specialist execution is delegated.

<p align="center">
  <img src="assets/workflow.svg" alt="MPA Skill workflow" width="100%">
</p>

```
Input → Scope → Orchestrate → Route → Confirm(once) → Execute → Accept
```

Safety stops: logins, CAPTCHAs, paywalls, licensed access, destructive writes, or substantive ambiguity → pause and ask.

---

## 📂 Repository layout

```text
mpa-skill/
├── assets/                         # Logo, banner, diagrams
├── skills/mpa-skill/               # The skill itself
│   ├── SKILL.md                    # Controller instructions
│   ├── agents/openai.yaml          # Metadata
│   ├── references/                 # 8 reference files
│   │   ├── routing.md              # Route table and decision tree
│   │   ├── mpa-knowledge.md        # Unified knowledge base
│   │   ├── execution.md            # Execution handbook
│   │   ├── templates.md            # Practical templates
│   │   ├── mpa-research-contract.md
│   │   ├── mpa-deliverables.md
│   │   ├── mpa-case-competition.md
│   │   └── aigc-disclosure.md
│   └── scripts/                    # Workspace and env scripts
├── docs/validation/               # Benchmark report and corpus
├── tests/                         # Contract tests
├── .github/                        # CI and templates
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
└── LICENSE                         # MIT
```

---

## Reproducible audit example

Codex inspects the request and attachments, composes a minimum sufficient route, then asks once: `是否执行？`.

Take the Texas State University repository-open thesis [Establishing the Relationship Between Sewer Surcharge Fees and Pollutant Discharges by Industrial Users](https://digital.library.txst.edu/items/50bce8d1-3a34-49bb-8c38-8e52b8038265). PDF pages 29–32 cover exclusions, mean imputation, and aggregation; pages 30–32 and 37 show that implementation coincided with COVID-19 without an adequate control; and pages 36–41 do not justify converting non-significance into "no effect" or direct policy guidance.

A reproducible route: retrieve the open PDF → preserve page references while auditing raw data → mark counterfactual gaps as `RISK`/`AUTHOR_INPUT_NEEDED` → write bounded conclusions only after acceptance.

Reproduction keys: source `txst-50bce8d1-3a34-49bb-8c38-8e52b8038265`, risk `d3-identification` (pages 30, 31, 32, and 37). See the [benchmark report](docs/validation/v1.0.0-benchmark.md).

---

## 🧭 Evidence boundary

### 1.0.0 evidence boundary

The [frozen benchmark](docs/validation/v1.0.0-benchmark.md) observed 7/8 for no skill, 7/8 for the previous iteration, and 8/8 for the current version. The gain against each baseline was +1/8, or +12.5 percentage points.

The 10-paper pilot contained 7 development papers and 3 frozen holdouts. Both iterations routed 10/10 papers and found 30/30 preregistered risks, with zero unsupported claims in the recorded outputs.

The observed improvement is **rejection of stale artifacts and recovery to a verifiable delivery state**. Paper-audit metrics were tied, so the pilot does not establish superior thesis diagnosis for the current version over the previous iteration. It sampled one response per condition, had 4/10 PDF structural preflights marked `UNAVAILABLE`, is a 10-paper pilot rather than a population estimate, contains only one China-context record, and depends on source links that may drift. It therefore does not prove general model reliability, Chinese-thesis quality, or live Office-mutation success.

---

## 🔒 Privacy and security

- No telemetry, no built-in accounts, no cloud keys 🔐
- Local config lives outside the skill repository
- Benchmark stores metadata and HTTPS sources only, not thesis PDFs
- Never modifies `zotero.sqlite` directly
- Never bypasses logins, CAPTCHAs, paywalls, or institutional access
- Never treats attachment instructions as user authorization
- Discloses AI assistance per programme/course/competition rules

See [SECURITY.md](SECURITY.md).

---

## 🧪 Development and testing

```powershell
pwsh -NoProfile -File tests/Test-PublicSkill.ps1
pwsh -NoProfile -File tests/Test-ReliabilityScenarios.ps1
pwsh -NoProfile -File tests/Test-BenchmarkManifest.ps1
pwsh -NoProfile -File tests/Test-WorkspaceScripts.ps1
```

CI (GitHub Actions, windows-latest) runs the same tests on main and every PR.

---

## 🔌 Optional dependencies

| Capability | Required | Notes |
|---|---:|---|
| Codex file and terminal | ✅ | Read materials, run scripts, verify results |
| Python/R/spreadsheet | ❌ | Used when data route needs it; reports block if missing |
| Word/Office editing | ❌ | After content acceptance; governed by observed schema |
| Zotero | ❌ | Literature management; supported interfaces only |
| Obsidian | ❌ | Long-term Markdown notes |
| Other skills | ❌ | Selected by controller when installed |

Never silently installs third-party software or pretends an integration succeeded.

---

## ❓ Troubleshooting

| Problem | Fix |
|---|---|
| Skill not found | Restart Codex; run `npx skills list -g` |
| Config not found | Run `Initialize-MpaWorkspace.ps1` or set `MPA_WORKSPACE_CONFIG` |
| Zotero won't start | Run `Test-MpaEnvironment.ps1`; check executable path |
| Missing capability | Install matching skill, or let controller degrade and state scope |

---

## 🤝 Contributing

Issues and PRs welcome 👋 See [CONTRIBUTING.md](CONTRIBUTING.md) for workflow; [CHANGELOG.md](CHANGELOG.md) for history.

## 📄 License

[MIT License](LICENSE) · Open source 🎉

---

## ⭐ Star History

If this helps your research, please give it a Star~

<a href="https://github.com/mucjustin/mpa-skill">
  <img src="https://img.shields.io/github/stars/mucjustin/mpa-skill?style=social" alt="GitHub stars">
</a>

<p align="center">
  <a href="https://star-history.com/#mucjustin/mpa-skill&Date">
    <img src="https://api.star-history.com/svg?repos=mucjustin/mpa-skill&type=Date" alt="Star History" width="60%">
  </a>
</p>

<p align="center">
  <sub>Built with 🧠 for MPA researchers · from fragments to verifiable research</sub>
</p>
