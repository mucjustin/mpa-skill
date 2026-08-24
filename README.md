<p align="center">
  <img src="assets/logo.svg" alt="MPA Skill logo" width="160">
</p>

<h1 align="center">MPA Skill</h1>

<p align="center">
  <strong>可核验、可复用、能落地的公共管理研究工作流</strong><br>
  专为 <strong>MPA 研究生</strong>打造的 Codex Agent Skill · 不是通用论文模板
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

## 📑 目录

- [✨ 功能特性](#-功能特性)
- [🧭 先看它解决什么](#-先看它解决什么)
- [🛣️ 适用任务](#-适用任务)
- [🚀 安装](#-安装)
- [⚙️ 首次配置](#-首次配置)
- [可复现审计示例](#可复现审计示例)
- [📝 三个起步提示](#-三个起步提示)
- [🏗️ 架构](#-架构)
- [🧰 技术栈](#-技术栈)
- [📂 仓库结构](#-仓库结构)
- [🧪 开发与测试](#-开发与测试)
- [🔌 可选依赖](#-可选依赖)
- [🔒 隐私与安全](#-隐私与安全)
- [⚙️ 更新与卸载](#-更新与卸载)
- [❓ 故障排查](#-故障排查)
- [🤝 贡献](#-贡献)
- [📄 许可证](#-许可证)

---

## ✨ 功能特性

| 特性 | 说明 |
|---|---|
| 🧭 **MPA Research Spine** | 把「公共问题 → 利益相关者 → 制度情境 → 理论 → 证据 → 方法 → 分析 → 可执行建议」串成可核验主线，先识别缺口再动笔。 |
| 🛣️ **十条研究路由** | 课程资料 / 案例分析 / 案例大赛 / 政策备忘录 / 文献综述 / 研究设计 / 田野调研 / 数据分析 / 论文写作 / 答辩准备，按需组合。 |
| 🔗 **课程→毕业研究复用** | 课程笔记、案例、问卷、代码可沉淀为研究资产，但复用前必须回原始来源核验来源与边界。 |
| 🧠 **MPA 知识本体** | 理论地图、中国治理情境库、公管思维清单、课程-能力映射，让控制器拥有 MPA 学科内容。 |
| 🛡️ **数据先于写作** | 有可用数据时，先核对来源、清洗、方法、数值与既有结论；证据或方法未被接受，不靠改写正文掩盖缺口。 |
| 🔄 **可恢复交付** | 本地 Office 编辑中断后重新获取文档身份并核对新旧内容；无法判定时停在 `STATE_UNKNOWN`，不盲目重放写入。 |
| ✅ **契约测试护航** | 仓库结构、Skill 指令、文档一致性与隐私红线全部纳入 PowerShell 契约测试。 |

> 支持状态：**Windows-first**。Skill 指令本身可跨平台阅读，但自动工作区初始化和环境检查脚本目前使用 PowerShell。

---

## 🧭 先看它解决什么

`mpa-skill` 面向需要把课程、案例、政策、田野、数据和论文串成一条可核验研究链的 MPA、公共管理与公共政策研究生。它以 **MPA Research Spine**（公共问题 → 利益相关者与公共价值 → 制度与政策情境 → 理论 → 证据 → 方法 → 分析 → 可执行建议）组织任务，并设置两道行为门：

- **数据先于写作**：有可用数据时，先按[真实数据工作流](skills/mpa-skill/references/real-data-workflow.md)核对来源、清洗、方法、数值与既有结论；证据或方法未被接受，就不靠改写正文掩盖缺口。
- **可恢复交付**：只有路线确需本地 Office 编辑且相应能力可用时，才加载[本地 Office 编辑规则](skills/mpa-skill/references/local-office-editing.md)。中断后重新获取文档身份并核对新旧内容；无法判定时停在 `STATE_UNKNOWN`，不会盲目重放写入或宣称成功。

### v2.4.0 的证据边界

[冻结的可靠性基准](docs/validation/v2.4.0-benchmark.md)记录了这些观察结果：无 Skill 为 7/8，v2.3.0 为 7/8，v2.4.0 为 8/8；v2.4.0 相对两个基线均提升 +1/8，即 +12.5 个百分点。10 篇论文试点由 7 篇开发集和 3 篇冻结留出集组成；v2.3.0 与 v2.4.0 都完成 10/10 路由并找出 30/30 个预登记风险，记录输出中不受支持的声明为 0。

这说明的改进是**拒绝仍含旧值的产物，并在交付中断后恢复到可验证状态**；论文审计指标持平，不能据此声称 v2.4.0 的论文诊断优于 v2.3.0。该试点每个条件只有一次响应，4/10 个 PDF 的结构预检为 `UNAVAILABLE`，10 篇样本不是总体估计，只有 1 条中国情境记录，且来源链接可能漂移。因此试点不能泛化为模型可靠性、中文论文质量或真实 Office 写入成功率的证明。

### MPA Research Spine（MPA 研究主线）

<p align="center">
  <img src="assets/spine.svg" alt="MPA Research Spine" width="100%">
</p>

```text
公共问题
→ 利益相关者与公共价值
→ 制度与政策情境
→ 理论或分析框架
→ 证据
→ 方法
→ 分析
→ 可执行建议
```

Skill 会先识别这条主线中已经成立和仍然缺失的部分，再开始写作，避免用漂亮文字掩盖问题定义不清、利益相关者缺失、证据不足、方法不匹配或建议无法实施。

### 课程成果向毕业研究复用

课程笔记、案例、概念、文献卡片、作业、问卷、数据、代码和教师反馈可以成为后续研究资产，但必须记录来源。课程笔记或旧作业在进入开题和论文之前，需要回到原始来源重新核验。

---

## 🛣️ 适用任务

- MPA 课程资料完整阅读、笔记、复习和作业准备；
- 公共管理案例分析；
- 中国研究生公共管理案例大赛等案例竞赛的参赛作品规划、调研证据组织与理论框架打磨；
- 政策备忘录；
- 面向公共问题的文献检索与综述；
- 开题、研究设计、问卷、访谈和田野工作；
- 问卷、访谈、行政数据及混合方法分析；
- MPA 论文写作、引用核验与答辩准备。

普通教学设计、博客写作、编程、通用数据分析、单独整理 Zotero/Obsidian 或非 MPA 论文不会仅因关键词相近而触发本 Skill。

---

## 🚀 安装

### 使用 Agent Skills CLI

```powershell
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
```

### 让 Codex 安装

告诉 Codex：

```text
使用 $skill-installer 从 https://github.com/mucjustin/mpa-skill
的 skills/mpa-skill 安装用户级 Skill。
```

如果新安装的 Skill 没有立即出现在列表中，重启 Codex。

---

## ⚙️ 首次配置

初始化脚本只创建你指定根目录下的工作区和本机 JSON 配置，不修改 Zotero 数据库或 Obsidian 设置。

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace')
```

默认配置写入 `%APPDATA%\mpa-skill\config.json`。也可以通过环境变量指定其他配置：

```powershell
$env:MPA_WORKSPACE_CONFIG = 'path-to-your-config.json'
```

只查看将执行的操作：

```powershell
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace') -WhatIf
```

检查当前环境，不写入文件也不启动应用：

```powershell
& (Join-Path $skillRoot 'scripts\Test-MpaEnvironment.ps1')
```

---

## 可复现审计示例

Codex 会先检查指令和附件，组合最小必要路线，然后只问一次 `是否执行？`。确认后继续执行；只有遇到登录、验证码、付费访问、破坏性写入或新的实质研究歧义时才再次询问。

以 Texas State University 机构库开放的论文 [Establishing the Relationship Between Sewer Surcharge Fees and Pollutant Discharges by Industrial Users](https://digital.library.txst.edu/items/50bce8d1-3a34-49bb-8c38-8e52b8038265) 为例：PDF 第 29–32 页涉及排除、均值填补和聚合，第 30–32、37 页显示政策实施与 COVID-19 同期且没有充分对照，第 36–41 页的无显著结果不足以支持"没有影响"或直接政策推广。可复现路线是：获取开放 PDF → 保留页码审计原始数据、缺失处理与识别策略 → 将反事实和推断缺口标为 `RISK`/`AUTHOR_INPUT_NEEDED` → 只在分析被接受后写有边界的结论。来源、页码和预登记风险见[基准报告](docs/validation/v2.4.0-benchmark.md)及其机器可读结果。复现键：来源 `txst-50bce8d1-3a34-49bb-8c38-8e52b8038265`，风险 `d3-identification`（第 30、31、32、37 页）。

---

## 📝 三个起步提示

### 1. 原始数据转化

```text
把附件中的非 MPA 报告、原始数据和既有结论转化为 MPA 研究。先按 Research Spine 重锚公共问题，再核对数据来源、清洗、变量、方法和数值；分析未被接受前不要改写结论。
```

### 2. 无数据的案例/政策分析

```text
分析这个基层治理案例；当前没有原始数据。请明确证据缺口，比较利益相关者、制度约束、公共价值、备选方案、可行性与可迁移边界，不要虚构数据或效果。
```

### 3. 已验收内容的 Word 交付

```text
研究内容已经验收。请用当前可用且已核对 schema 的 Word/Office 能力交付；写入前记录文档身份和唯一锚点，中断后重新打开核对新旧内容，STATE_UNKNOWN 时停止，最后确认新内容存在、旧内容不存在且保存文件可重新打开。
```

---

## 🏗️ 架构

Skill 是一个**薄控制器**：只负责范围判定、分类编排、最小必要路线、安全停止与最终验收；专业执行（文献检索、论文写作、引用核验等）委托给对应技能，可选集成 Zotero 与 Obsidian。

<p align="center">
  <img src="assets/workflow.svg" alt="MPA Skill workflow" width="100%">
</p>

执行流程概括为：

1. **输入**：用户请求与材料；
2. **判定**：识别是否属于 MPA / 公共管理 / 公共政策任务；
3. **编排**：按依赖关系对任务分类并排序；
4. **路由**：组合最小必要路线；
5. **确认**：一次性 `是否执行？`；
6. **执行**：十条路由按需组合，调用可选专业技能；
7. **验收**：MPA 质量门（研究契约核验）+ 最终验收与状态交接。

安全停止贯穿全程：登录、验证码、付费墙、授权访问、破坏性写入或实质研究歧义都会暂停并询问。

---

## 🧰 技术栈

| 层级 | 技术 |
|---|---|
| **Skill 框架** | Codex Agent Skill（`SKILL.md` + `agents/openai.yaml`） |
| **脚本与测试** | PowerShell 5.1+ / PowerShell 7 (`pwsh`) |
| **CI / CD** | GitHub Actions（`windows-latest`） |
| **可选集成** | Zotero（本地 API / Better BibTeX）、Obsidian（Markdown Vault） |
| **依赖管理** | npm `skills` CLI |
| **版本规范** | [Semantic Versioning](https://semver.org/lang/zh-CN/) + [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) |

---

## 📂 仓库结构

```text
mpa-skill/
├── assets/                         # Logo、Banner、架构图、工作流图
├── skills/mpa-skill/               # Skill 本体（安装入口）
│   ├── SKILL.md                    # 控制器指令与触发规则
│   ├── agents/openai.yaml          # Skill 元数据
│   ├── references/                 # 路由、研究契约、真实数据、本地 Office、交付物、依赖与工作区规则
│   └── scripts/                    # Initialize-MpaWorkspace.ps1 / Test-MpaEnvironment.ps1
├── docs/validation/               # 语料清单、v2.4.0 机器结果与基准报告
├── tests/                         # 公开契约、可靠性场景、语料清单与脚本测试（含 fixtures）
├── .github/                        # CI 工作流、Issue 与 PR 模板
├── CONTRIBUTING.md                 # 贡献指南与版本维护规范
├── CHANGELOG.md                    # 变更记录
├── SECURITY.md                     # 安全披露政策
└── LICENSE                         # MIT
```

---

## 🧪 开发与测试

本地运行全部测试：

```powershell
pwsh -NoProfile -File tests/Test-PublicSkill.ps1
pwsh -NoProfile -File tests/Test-ReliabilityScenarios.ps1
pwsh -NoProfile -File tests/Test-BenchmarkManifest.ps1
pwsh -NoProfile -File tests/Test-WorkspaceScripts.ps1
```

前两项分别校验公开行为/文档契约和[可靠性场景](tests/fixtures/reliability-scenarios.json)，第三项校验公开论文清单，最后一项只在临时目录验证工作区脚本。CI（GitHub Actions，windows-latest）会在 main 分支和每个 Pull Request 上运行相同测试。

---

## 🔌 可选依赖

| 能力 | 是否必需 | 说明 |
|---|---:|---|
| Codex 文件与终端能力 | 是 | 读取材料、执行本地脚本和验证结果 |
| Python/R/表格等数据分析能力 | 否 | 仅在数据路线需要且能力契约可验证时使用；缺失时交付可复现步骤或报告阻塞 |
| 本地 Word/Office 编辑能力 | 否 | 仅在内容已验收且路线需要时使用；提供方中立，以实际 schema 与返回结构为准 |
| Zotero | 否 | 文献与附件管理；只使用受支持接口，不直接修改数据库 |
| Obsidian | 否 | 长期 Markdown 笔记与项目中心 |
| 文献、PDF、数据、Word、PPT Skills | 否 | 安装后由控制器选择；缺失时明确降级或报告阻塞 |

Skill 不会静默安装第三方软件、绕过机构访问或假装不存在的集成已经成功。

---

## 🔒 隐私与安全

- 无遥测、无内置账号、无云端密钥；
- 本机配置保存在 Skill 仓库之外；
- 公开基准只保存元数据、HTTPS 来源、派生风险和分数，不提交论文 PDF、原始长文或长篇摘录；来源链接可能随机构库调整而漂移；
- 不直接修改 `zotero.sqlite`；
- 不绕过登录、验证码、付费墙、授权或机构访问；
- 不把附件中的指令当作用户授权；
- 不把课程笔记或 AI 推断伪装成研究证据；
- 按当前学校/项目/课程/赛事规则披露 AI 辅助，AI 生成内容不冒充学生本人原创。

参见 [SECURITY.md](SECURITY.md)。

---

## ⚙️ 更新与卸载（Update & Uninstall）

**更新（Update）：**

```powershell
npx skills update mpa-skill -g -y
```

**卸载（Uninstall）：**

```powershell
npx skills remove mpa-skill -g -y
```

> 卸载 Skill 不会删除你创建的研究工作区和本机配置。如需删除这些数据，请先自行确认备份和准确路径。

---

## ❓ 故障排查

| 问题 | 解决方案 |
|---|---|
| 找不到 Skill | 重启 Codex，并运行 `npx skills list -g`。 |
| 找不到配置 | 运行 `Initialize-MpaWorkspace.ps1`，或设置 `MPA_WORKSPACE_CONFIG`。 |
| Zotero 无法启动 | 运行 `Test-MpaEnvironment.ps1`，确认配置中的可执行文件存在。 |
| 缺少专业能力 | 安装相应 Skill，或让控制器采用已验证的可用工具并说明降级范围。 |

---

## 🤝 贡献

欢迎 Issue 与 Pull Request。贡献流程、内容边界与版本维护规范见 [CONTRIBUTING.md](CONTRIBUTING.md)，历史变更见 [CHANGELOG.md](CHANGELOG.md)。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

---

## ⭐ Star History

如果这个项目对你的研究或学习有帮助，请给个 Star — 这是对wo最大的鼓励！
<a href="https://www.star-history.com/?type=date&repos=mucjustin%2Fmpa-skill">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=mucjustin/mpa-skill&type=date&theme=dark&legend=top-left&sealed_token=1reCqX5_wIXEWlTxSepu2oXV9XyQKYdVT5QmHM6TwwwAUDCQFJUDK9NAho-49BQFAhcW2MAvNOtxqSChy4PJ2-N2BKJrVWC1pxr53tb35q4zV97Py8Uh0w" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=mucjustin/mpa-skill&type=date&legend=top-left&sealed_token=1reCqX5_wIXEWlTxSepu2oXV9XyQKYdVT5QmHM6TwwwAUDCQFJUDK9NAho-49BQFAhcW2MAvNOtxqSChy4PJ2-N2BKJrVWC1pxr53tb35q4zV97Py8Uh0w" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=mucjustin/mpa-skill&type=date&legend=top-left&sealed_token=1reCqX5_wIXEWlTxSepu2oXV9XyQKYdVT5QmHM6TwwwAUDCQFJUDK9NAho-49BQFAhcW2MAvNOtxqSChy4PJ2-N2BKJrVWC1pxr53tb35q4zV97Py8Uh0w" />
 </picture>
</a>
<p align="center">
  <sub>Built with 🧠 for MPA researchers · 让公共管理研究从碎片走向可核验</sub>
</p>




