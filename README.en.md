<p align="center">
  <img src="assets/brand-lockup.svg" alt="Approved MPA Research Agent emblem with joined MP, teal A, gold dot and bilingual name" width="570">
</p>

<h1 align="center">MPA Research Agent</h1>

<p align="center">
  <strong>Evidence-grounded MPA and public policy research</strong><br>
  One portable Agent Skill for Codex and a WorkBuddy-compatible ZIP
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
    <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows%20%7C%20Linux-0078D4.svg" alt="Platform">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB.svg?logo=python&logoColor=white" alt="Python 3.10+">
  </a>
  <a href="#">
    <img src="https://img.shields.io/badge/Codex-Agent%20Skill-8A2BE2.svg" alt="Codex Agent Skill">
  </a>
</p>

<p align="center">
  <img src="assets/banner.svg" alt="MPA Research Agent banner" width="100%">
</p>

---

## 🎯 What is this

**MPA Research Agent** is an evidence-grounded public-management research Skill. AI organizes questions, lenses and uncertainty; the bundled offline Python/SQLite tool performs deterministic source-snapshot and quotation-location checks.

Match claims to evidence for the actual question. The **MPA Research Spine** (public problem, stakeholders and public value, institutional context, theory, evidence, method, analysis, recommendations) is a diagnostic checklist: use the relevant links and revise the question or method as evidence changes.

Two behavioral gates run throughout:

- 🛡️ **Data before writing**: when usable data exists, audit provenance, cleaning, methods, and numbers first. See the [execution handbook](skills/mpa-skill/references/execution.md).
- 🔄 **Recoverable delivery**: after Office interruption, reacquire document identity; stop at `STATE_UNKNOWN` when unsure.

> **Cross-platform**: since v2.3.0 the evidence tool and workspace setup are pure Python 3.10+ standard library and run on macOS, Windows and Linux. PowerShell is no longer required.

---

## ✨ Features

| | Feature | One-liner |
|---|---|---|
| 🧭 | MPA Research Spine | Diagnostic research checklist selected for the task |
| 🛣️ | Fourteen task routes | Course, case, policy, literature, design, fieldwork, data, thesis, defence, workplace topics, coaching, and related tasks |
| 🏢 | In-service research | Workplace problem → topic, insider-ethics checks, local de-identification, thesis and policy report from one evidence base |
| 🎓 | Coaching mode | Asks and diagnoses instead of drafting; draft self-check, method diagnosis, defence rehearsal, supervisor briefs |
| 🔗 | Course-to-capstone reuse | Notes, cases, code become assets; re-verify before reuse |
| 🧠 | MPA knowledge ontology | Theory map + China governance contexts + thinking checklist |
| 🛡️ | Data before writing | Audit first, write second, never mask gaps |
| 🔎 | Bundled evidence workbench | Offline hashes, exact quotations (incl. multi-line ranges and opt-in PDF-normalized matching), rival explanations, SQLite records, explicit human review |
| 🔄 | Recoverable delivery | Interruptible; stops at `STATE_UNKNOWN` |
| 🧾 | AI-use disclosure | Generated only from actual tool use; see [disclosure workflow](skills/mpa-skill/references/aigc-disclosure.md) |
| ✅ | Cross-platform tests | Python tests on macOS / Windows / Linux CI cover tools, safety red lines, docs and privacy |

---

**Current version: v2.3.1.** [GitHub Release and ZIP](https://github.com/mucjustin/mpa-skill/releases/latest) · [Changelog](CHANGELOG.md). Merging code alone does not create a GitHub Release.

## 🚀 Quick start

### Install

```bash
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
```

### WorkBuddy import (single Skill ZIP)

The Skill follows WorkBuddy's documented `SKILL.md`, `references/`, and `scripts/` layout with bilingual metadata and a ZIP packaging check.

```bash
python3 tools/package_skill.py --output dist/mpa-skill.zip
```

Import `dist/mpa-skill.zip` through WorkBuddy's Skills → Add Skill → Upload Skill, or download the named ZIP attachment from the [latest GitHub Release](https://github.com/mucjustin/mpa-skill/releases/latest). **ZIP compatibility is tested; in-app WorkBuddy import is not yet verified.** See [installation and compatibility](docs/install-and-compatibility.md).

### Initialize workspace (optional)

macOS / Linux:

```bash
SKILL_ROOT="$HOME/.agents/skills/mpa-skill"   # use your actual install location
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" workspace-init "$HOME/Documents/MPA-Workspace" --dry-run
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" workspace-init "$HOME/Documents/MPA-Workspace"
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" env-check
```

Windows:

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') workspace-init (Join-Path $HOME 'Documents\MPA-Workspace')
```

The config goes to `~/Library/Application Support/mpa-skill/config.json` (macOS), `%APPDATA%\mpa-skill\config.json` (Windows) or `~/.config/mpa-skill/config.json` (Linux), or wherever `--config` / `MPA_WORKSPACE_CONFIG` points. It never modifies the Zotero database or Obsidian settings, and stops rather than overwrite an existing config.

### Update and uninstall

```bash
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

## 🏢 Built for in-service MPA students (v2.3.0)

Most MPA students study while working, research their own organisation, and have fragmented time. v2.3.0 adds:

<p align="center"><img src="assets/in-service.svg" alt="In-service research path: workplace problem, topic comparison, insider check, de-identified evidence, thesis and policy report, plus the coaching loop" width="100%"></p>

- **Workplace problem → topic**: decompose a workplace frustration into phenomenon, public problem, research question and theory dialogue; compare 2–3 candidate topics on evidence access, feasibility, insider risk and confidentiality. See the [in-service research guide](skills/mpa-skill/references/in-service-research.md).
- **Insider-research checks**: role conflict, power relations in interviews, consent, material classification (classified material never enters the research), silent groups.
- **Local de-identification**: `redact` and `export --redact-terms` replace names, units and places from the student's own term list, with automatic fallbacks for ID numbers, phones, emails and official document numbers; fully offline.
- **Coaching mode**: when asked "coach me, don't write it", the Skill asks and diagnoses only, backed by `check-draft` (claim–evidence coverage, causal wording, overclaiming), method diagnosis, defence rehearsal and supervisor briefs. See [coaching mode](skills/mpa-skill/references/coaching-mode.md).
- **Resumable progress**: `progress` stores the status of the eight Research Spine links and the next task, so a 30-minute session can pick up where the last one stopped.
- **One study, two outputs**: thesis and policy report share one evidence base; every recommendation links back to evidence IDs.

These features pass synthetic unit and CLI tests; **they have not yet been evaluated with real students**.

## 🧩 Evidence-led Case Research Engine (v2.2.0)

For substantive public-management case studies and case competitions, an optional question-first workflow adds: choosing a lens based on evidence access and method fit; mapping actors' reported interests versus observed actions; planning verifiable materials; tracing events and rival mechanisms; and making uncertainty visible. The four lenses are examples, not a mandatory checklist. Short classroom questions remain short.

Read [case-research.md](skills/mpa-skill/references/case-research.md), [evidence-protocol.md](skills/mpa-skill/references/evidence-protocol.md), the [hypothetical example](docs/examples/case-research-starter.md), and the [evaluation protocol](docs/validation/case-research-evaluation.md). CI tests structural contracts; they **do not** demonstrate improved semantic research performance.

## 🔎 Offline Evidence Workbench (experimental)

Unlike the instruction protocols, the optional **Python + SQLite CLI** actually snapshots local UTF-8 TXT/Markdown, CSV, DOCX, and extractable-text PDF files (SHA-256), indexes source locators, links exact quotations to claims, records explicit human reviews, audits integrity, and exports Markdown/JSON. No uploads, model calls, or automatic verification claims. The CLI is now **bundled inside the installed Skill** as `scripts/mpa_evidence.py`, runnable with Python 3.10+ without a package installation for TXT/MD/CSV/DOCX. Run `python <skill-root>/scripts/mpa_evidence.py doctor` to check capabilities; `pypdf` is optional and requires separate user approval for PDF. See [the evidence workbench guide](docs/evidence-workbench.md). Local copied originals and extracted text are **not encrypted**. Automated CLI tests do not establish improved research outcome quality.

For the symbol rationale and monochrome variant, see [Visual Identity](docs/brand-identity.md).

## 🏗️ Architecture

**The Skill organizes research, deterministic code checks evidence, and a human researcher controls verification.** All new evidence starts `unverified`, never self-approved by the agent.

<p align="center"><img src="assets/spine.svg" alt="MPA Research Spine model" width="100%"></p>
<p align="center"><img src="assets/evidence-flow.svg" alt="Offline evidence workbench" width="100%"></p>

The Skill remains a **thin controller** for scope, routing, authorization and acceptance, with the evidence utility performing deterministic local operations.

<p align="center">
  <img src="assets/workflow.svg" alt="MPA Research Agent workflow" width="100%">
</p>

```
Research question → Evidence plan → Execute within authorization → Source audit → Human review of persisted evidence → Bounded delivery
```

Safety stops: logins, CAPTCHAs, paywalls, licensed access, destructive writes, or substantive ambiguity → pause and ask.

---

## 📂 Repository layout

```text
mpa-skill/
├── README.md / README.en.md
├── assets/                        # Logo, Research Spine, evidence flow (SVG)
├── skills/mpa-skill/
│   ├── SKILL.md                   # Cross-client controller and metadata
│   ├── agents/openai.yaml
│   ├── references/                # Research and source-integrity protocols
│   └── scripts/
│       ├── mpa_evidence.py        # Bundled CLI
│       └── evidence_workbench/    # Python / SQLite core, redaction, draft check, workspace config
├── tools/package_skill.py         # ZIP packaging
├── tests/                         # Tool, Skill contract, package, docs and workspace tests (all Python)
└── docs/                          # Installation, examples, historical benchmarks
```

---

## Reproducible audit example

Codex proceeds with read-only analysis within the request, asking only for missing authorization before external writes or source persistence. Existing authorization remains valid within its scope. For local libraries, use the [evidence-readiness checks](skills/mpa-skill/references/evidence-readiness.md) to reconcile catalog labels, source passages, reading scope and project data.

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

```bash
python3 -m unittest discover -s tests -v
python3 tools/check_release.py
python3 tools/package_skill.py --output dist/mpa-skill.zip
```

CI (GitHub Actions) runs the same suite on macOS, Windows and Linux with Python 3.10 and 3.13.

---

## 🔌 Optional dependencies

| Capability | Required | Notes |
|---|---:|---|
| Python 3.10+ with host file and terminal access | ✅ (for executable tools) | Without local execution rights, only the planning route is available |
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
| Config not found | Run `mpa_evidence.py workspace-init` or set `MPA_WORKSPACE_CONFIG` |
| Zotero won't start | Run `mpa_evidence.py env-check`; check path and connector |
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
