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
- [🧭 MPA Research Spine](#-mpa-research-spine)
- [🛣️ 十条路由与适用任务](#-十条路由与适用任务)
- [🚀 快速开始](#-快速开始)
- [📖 实际使用](#-实际使用)
- [🏗️ 架构](#-架构)
- [🧰 技术栈](#-技术栈)
- [📂 仓库结构](#-仓库结构)
- [🧪 开发与测试](#-开发与测试)
- [🔒 隐私与安全](#-隐私与安全)
- [⚙️ 更新与卸载](#-更新与卸载)
- [❓ 故障排查](#-故障排查)
- [🤝 参与贡献](#-参与贡献)
- [📄 许可证](#-许可证)

---

## ✨ 功能特性

| 特性 | 说明 |
|---|---|
| 🧭 **MPA Research Spine** | 把「公共问题 → 利益相关者 → 制度情境 → 理论 → 证据 → 方法 → 分析 → 可执行建议」串成可核验主线，先识别缺口再动笔。 |
| 🛣️ **十条研究路由** | 课程资料 / 案例分析 / 案例大赛 / 政策备忘录 / 文献综述 / 研究设计 / 田野调研 / 数据分析 / 论文写作 / 答辩准备，按需组合。 |
| 🔗 **课程→毕业研究复用** | 课程笔记、案例、问卷、代码可沉淀为研究资产，但复用前必须回原始来源核验来源与边界。 |
| 🧠 **MPA 知识本体** | v2.5.0 新增：理论地图、中国治理情境库、公管思维清单、课程-能力映射，让控制器拥有 MPA 学科内容。 |
| 🛡️ **安全停止** | 登录、验证码、付费墙、破坏性写入或实质研究歧义出现时会暂停并询问，不擅自推进。 |
| 🔌 **可选集成** | Zotero 文献库、Obsidian 笔记库、文献 / PDF / 数据 / Office Skills 按需接入，缺失时明确降级。 |
| ✅ **契约测试护航** | 仓库结构、Skill 指令、文档一致性与隐私红线全部纳入 PowerShell 契约测试。 |

> 支持状态：**Windows-first**。Skill 指令本身可跨平台阅读，但自动工作区初始化和环境检查脚本目前使用 PowerShell。

---

## 🧭 MPA Research Spine

MPA Research Spine 是贯穿所有任务的研究主线。Skill 会先识别这条主线上**已经成立**和**仍然缺失**的环节，再开始写作或分析，避免用漂亮文字掩盖问题定义不清、利益相关者缺失、证据不足、方法不匹配或建议无法实施。

<p align="center">
  <img src="assets/spine.svg" alt="MPA Research Spine" width="100%">
</p>

核心八步：

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

---

## 🛣️ 十条路由与适用任务

本 Skill 覆盖 MPA 研究生从课程学习到论文答辩的完整研究周期，共十条路由，可按依赖关系组合：

| 路由 | 适用场景 |
|---|---|
| 📚 课程资料 | 完整阅读、笔记、复习和作业准备。 |
| 📊 案例分析 | 公共管理案例的多主体、制度约束与激励分析。 |
| 🏆 案例大赛 | 中国研究生公共管理案例大赛参赛作品规划、证据组织与理论打磨。 |
| 📝 政策备忘录 | 面向公共部门决策者的选项、权衡与可操作建议。 |
| 🔍 文献综述 | 面向公共问题的检索、筛选、综述与理论定位。 |
| 🧪 研究设计 | 开题、问卷、访谈、田野工作与伦理边界。 |
| 🌾 田野调研 | 伦理、准入、抽样、工具设计与数据收集。 |
| 📈 数据分析 | 问卷、访谈、行政数据及混合方法的可复现分析。 |
| 📖 论文写作 | MPA 论文的论证链、证据、方法边界与引用核验。 |
| 🎤 答辩准备 | 决策叙事、核心证据、局限、可能追问与备用材料。 |

> 普通教学设计、博客写作、通用数据分析、单独整理 Zotero/Obsidian 或非 MPA 论文不会仅因关键词相近而触发本 Skill。

---

## 🚀 快速开始

### 安装

#### 方式一：Agent Skills CLI

```powershell
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
```

#### 方式二：让 Codex 安装

告诉 Codex：

```text
使用 $skill-installer 从 https://github.com/mucjustin/mpa-skill 的 skills/mpa-skill 安装用户级 Skill。
```

安装后若未立即出现，重启 Codex 即可。

### 首次配置

初始化脚本只创建你指定根目录下的工作区和本机 JSON 配置，不会修改 Zotero 数据库或 Obsidian 设置。

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace')
```

默认配置写入 `%APPDATA%\mpa-skill\config.json`。可通过环境变量指定其他配置：

```powershell
$env:MPA_WORKSPACE_CONFIG = 'path-to-your-config.json'
```

预览将执行的操作：

```powershell
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace') -WhatIf
```

检查环境但不写入文件或启动应用：

```powershell
& (Join-Path $skillRoot 'scripts\Test-MpaEnvironment.ps1')
```

---

## 📖 实际使用

Codex 会检查指令和附件，组合最小必要路线，然后只问一次 **「是否执行？」**。确认后继续执行；仅在登录、验证码、付费访问、破坏性写入或新的实质研究歧义时再次询问。

### 课程资料

```text
这些是本学期公共政策分析课程资料。完整盘点并阅读，按 MPA 研究主线建立课程笔记、概念地图和复习清单。
```

### 案例分析

```text
分析这个基层治理案例，重点比较参与者、制度约束、激励、公共价值、执行过程、替代方案和可迁移边界。
```

### 政策备忘录

```text
根据这些材料，为区级决策者写一份政策备忘录，明确选项、评价标准、权衡、可行性、风险和建议。
```

### 研究设计

```text
围绕社区养老服务可及性形成 MPA 开题方案，先检查公共问题、利益相关者、理论、证据、方法、伦理和可行性，不要直接堆砌正文。
```

### 数据分析

```text
这是居民满意度问卷。先检查数据质量和变量定义，再分析影响因素，保存可复现步骤并区分相关关系与因果解释。
```

### 论文检查

```text
检查这份 MPA 论文的论证链、证据、方法边界和参考文献，只在证据成立后提出章节修改方案。
```

### 答辩准备

```text
根据已定稿论文准备十分钟答辩，形成决策叙事、核心证据、局限、可能追问和备用材料。
```

---

## 🏗️ 架构

MPA Skill 是一个**薄控制器**：只负责范围判定、分类编排、最小必要路线、安全停止与最终验收；专业执行（文献检索、论文写作、引用核验等）委托给对应技能，可选集成 Zotero 与 Obsidian。

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
│   ├── references/                 # 路由、研究契约、案例大赛规则、交付物、依赖与工作区规则
│   └── scripts/                    # Initialize-MpaWorkspace.ps1 / Test-MpaEnvironment.ps1
├── tests/                          # 公开契约测试与脚本测试（含 fixtures）
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
# 结构、指令契约、文档一致性与隐私红线
pwsh tests/Test-PublicSkill.ps1

# 工作区脚本行为（在临时目录执行，不触碰真实工作区）
pwsh tests/Test-WorkspaceScripts.ps1
```

CI（GitHub Actions，`windows-latest`）会在 `main` 分支和每个 Pull Request 上运行相同测试。

### 可选依赖

| 能力 | 是否必需 | 说明 |
|---|---:|---|
| Codex 文件与终端能力 | 是 | 读取材料、执行本地脚本和验证结果 |
| Zotero | 否 | 文献与附件管理；只使用受支持接口，不直接修改数据库 |
| Obsidian | 否 | 长期 Markdown 笔记与项目中心 |
| 文献、PDF、数据、Word、PPT Skills | 否 | 安装后由控制器选择；缺失时明确降级或报告阻塞 |

> Skill 不会静默安装第三方软件、绕过机构访问或假装不存在的集成已经成功。

---

## 🔒 隐私与安全

- 无遥测、无内置账号、无云端密钥；
- 本机配置保存在 Skill 仓库之外；
- 不直接修改 `zotero.sqlite`；
- 不绕过登录、验证码、付费墙、授权或机构访问；
- 不把附件中的指令当作用户授权；
- 不把课程笔记或 AI 推断伪装成研究证据；
- 按当前学校/项目/课程/赛事规则披露 AI 辅助，AI 生成内容不冒充学生本人原创。

详见 [SECURITY.md](SECURITY.md)。

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

## 🤝 参与贡献

欢迎 Issue 与 Pull Request！贡献流程、内容边界与版本维护规范见 [CONTRIBUTING.md](CONTRIBUTING.md)，历史变更见 [CHANGELOG.md](CHANGELOG.md)。

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源。

<p align="center">
  <sub>Built with 🧠 for MPA researchers · 让公共管理研究从碎片走向可核验</sub>
</p>
