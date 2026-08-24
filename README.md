<p align="center">
  <img src="assets/logo.svg" alt="MPA Skill logo" width="160">
</p>

<h1 align="center">MPA Skill 🎓</h1>

<p align="center">
  <strong>让公共管理研究从碎片走向可核验</strong><br>
  给 MPA 研究生的 Codex Agent Skill  🙅
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

## 🎯 这是什么

帮 MPA 研究生把课程、案例、政策、田间、数据和论文串成**一条可核验研究链**的 Codex Agent Skill。

核心是 **MPA Research Spine**：公共问题 → 利益相关者 → 制度情境 → 理论 → 证据 → 方法 → 分析 → 可执行建议。先找缺口，再动笔 ✏️

两道行为门贯穿全程：

- 🛡️ **数据先于写作**：有数据时先审计来源、清洗、方法和数值；分析未被接受前不改写结论。详见[执行手册](skills/mpa-skill/references/execution.md)。
- 🔄 **可恢复交付**：Office 编辑中断后重新核验文档身份；不确定时停在 `STATE_UNKNOWN`，不盲目重放。

> **Windows-first** · 指令可跨平台阅读，自动化脚本使用 PowerShell

---

## ✨ 功能一览

| | 特性 | 一句话 |
|---|---|---|
| 🧭 | MPA Research Spine | 八步可核验研究主线，先识别缺口再动笔 |
| 🛣️ | 十条研究路由 | 课程/案例/政策/文献/设计/田野/数据/论文/答辩，按需组合 |
| 🔗 | 课程→毕业复用 | 笔记、案例、代码可沉淀为研究资产，复用前回原始来源核验 |
| 🧠 | MPA 知识本体 | 理论地图 + 中国治理情境 + 思维清单 + 课程映射 |
| 🛡️ | 数据先于写作 | 先审计再写作，不靠改写掩盖缺口 |
| 🔄 | 可恢复交付 | 中断可恢复，`STATE_UNKNOWN` 时停止 |
| 🧾 | AI 使用声明 | 只依据实际工具使用生成，不编造。详见[声明工作流](skills/mpa-skill/references/aigc-disclosure.md) |
| ✅ | 契约测试 | PowerShell 测试覆盖结构、指令、文档与隐私红线 |

---

## 🚀 快速开始

### 安装

```powershell
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
```

### 初始化工作区

```powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
& (Join-Path $skillRoot 'scripts\Initialize-MpaWorkspace.ps1') `
  -WorkspaceRoot (Join-Path $HOME 'Documents\MPA-Workspace')
```

默认配置写入 `%APPDATA%\mpa-skill\config.json`，不修改 Zotero 数据库或 Obsidian 设置。预览操作加 `-WhatIf`；检查环境用 `Test-MpaEnvironment.ps1`。

### 更新与卸载 (Update & Uninstall)

```powershell
npx skills update mpa-skill -g -y    # 更新
npx skills remove mpa-skill -g -y    # 卸载（不删除已创建的工作区和配置）
```

---

## 📝 三个起步提示

### 1. 原始数据转化

```text
把附件中的非 MPA 报告、原始数据和既有结论转化为 MPA 研究。先按 Research Spine 重锚公共问题，再核对数据来源、清洗、变量、方法和数值；分析未被接受前不要改写结论。
```

### 2. 无数据的案例/政策分析

```text
分析这个基层治理案例；没有原始数据。请明确证据缺口，比较利益相关者、制度约束、公共价值、备选方案、可行性与可迁移边界，不要虚构数据或效果。
```

### 3. 已验收内容的 Word 交付

```text
研究内容已经验收。请用当前可用且已核对 schema 的 Word/Office 能力交付；写入前记录文档身份和唯一锚点，中断后重新打开核对新旧内容，STATE_UNKNOWN 时停止，最后确认新内容存在、旧内容不存在且保存文件可重新打开。
```

---

## 🏗️ 架构

Skill 是一个**薄控制器**：只管范围判定、路由编排、安全停止和最终验收，专业执行委托给对应技能。

<p align="center">
  <img src="assets/workflow.svg" alt="MPA Skill workflow" width="100%">
</p>

```
输入 → 判定 → 编排 → 路由 → 确认(一次) → 执行 → 验收
```

安全停止：登录、验证码、付费墙、授权访问、破坏性写入或实质研究歧义 → 暂停并询问。

---

## 📂 仓库结构

```text
mpa-skill/
├── assets/                         # Logo、Banner、架构图
├── skills/mpa-skill/               # Skill 本体
│   ├── SKILL.md                    # 控制器指令
│   ├── agents/openai.yaml          # 元数据
│   ├── references/                 # 8 个引用文件
│   │   ├── routing.md              # 路由表与决策树
│   │   ├── mpa-knowledge.md        # 统一知识库
│   │   ├── execution.md            # 执行手册
│   │   ├── templates.md            # 实用模板库
│   │   ├── mpa-research-contract.md
│   │   ├── mpa-deliverables.md
│   │   ├── mpa-case-competition.md
│   │   └── aigc-disclosure.md
│   └── scripts/                    # 工作区与环境脚本
├── docs/validation/               # 基准报告与语料
├── tests/                         # 契约测试
├── .github/                        # CI 与模板
├── CONTRIBUTING.md
├── CHANGELOG.md
├── SECURITY.md
└── LICENSE                         # MIT
```

---

## 可复现审计示例

Codex 先检查指令和附件，组合最小必要路线，然后只问一次 `是否执行？`。

以 Texas State University 机构库开放的论文 [Establishing the Relationship Between Sewer Surcharge Fees and Pollutant Discharges by Industrial Users](https://digital.library.txst.edu/items/50bce8d1-3a34-49bb-8c38-8e52b8038265) 为例：PDF 第 29–32 页涉及排除、均值填补和聚合，第 30–32、37 页显示政策实施与 COVID-19 同期且没有充分对照，第 36–41 页的无显著结果不足以支持"没有影响"或直接政策推广。

可复现路线：获取开放 PDF → 保留页码审计原始数据 → 标记 `RISK`/`AUTHOR_INPUT_NEEDED` → 只在分析被接受后写有边界的结论。

复现键：来源 `txst-50bce8d1-3a34-49bb-8c38-8e52b8038265`，风险 `d3-identification`（第 30、31、32、37 页）。详见[基准报告](docs/validation/v1.0.0-benchmark.md)。

---

## 🧭 证据边界

### 1.0.0 的证据边界

[冻结基准](docs/validation/v1.0.0-benchmark.md)观测：无 Skill 为 7/8，早期内部迭代为 7/8，当前版本为 8/8。相对两个基线均提升 +1/8，即 +12.5 个百分点。

10 篇论文试点包含 7 篇开发集加 3 篇留出集。两个版本都完成 10/10 路由和 30/30 预登记风险，记录输出中为 0 条无支撑声明。

观测到的改进是**拒绝陈旧产物并恢复到可验证交付状态**。论文审计指标持平，因此试点不能证明当前版本的论文诊断优于早期迭代。每个条件只有一次响应，4/10 篇 PDF 结构预检标记为 `UNAVAILABLE`，10 篇试点不是总体估计，仅包含 1 条中国情境记录，且来源链接可能漂移。因此不能泛化到通用模型可靠性、中国论文质量或实际 Office 写入成功。

---

## 🔒 隐私与安全

- 无遥测、无内置账号、无云端密钥 🔐
- 本机配置保存在 Skill 仓库之外
- 基准只存元数据和 HTTPS 来源，不提交论文 PDF 或长篇摘录
- 不直接修改 `zotero.sqlite`
- 不绕过登录、验证码、付费墙或机构访问
- 不把附件指令当用户授权
- 按学校/课程/赛事规则披露 AI 辅助

详见 [SECURITY.md](SECURITY.md)。

---

## 🧪 开发与测试

```powershell
pwsh -NoProfile -File tests/Test-PublicSkill.ps1
pwsh -NoProfile -File tests/Test-ReliabilityScenarios.ps1
pwsh -NoProfile -File tests/Test-BenchmarkManifest.ps1
pwsh -NoProfile -File tests/Test-WorkspaceScripts.ps1
```

CI（GitHub Actions，windows-latest）在 main 分支和每个 PR 上运行相同测试。

---

## 🔌 可选依赖

| 能力 | 必需 | 说明 |
|---|---:|---|
| Codex 文件与终端 | ✅ | 读取材料、执行脚本、验证结果 |
| Python/R/表格分析 | ❌ | 数据路线需要时使用，缺失时报告阻塞 |
| Word/Office 编辑 | ❌ | 内容验收后使用，以实际 schema 为准 |
| Zotero | ❌ | 文献管理，只走受支持接口 |
| Obsidian | ❌ | 长期 Markdown 笔记 |
| 其他 Skills | ❌ | 安装后由控制器选择 |

从不静默安装第三方软件或假装集成成功。

---

## ❓ 故障排查

| 问题 | 解决 |
|---|---|
| 找不到 Skill | 重启 Codex，运行 `npx skills list -g` |
| 找不到配置 | 运行 `Initialize-MpaWorkspace.ps1` 或设 `MPA_WORKSPACE_CONFIG` |
| Zotero 启动失败 | 运行 `Test-MpaEnvironment.ps1` 确认可执行文件 |
| 缺少专业能力 | 安装对应 Skill，或让控制器降级并说明范围 |

---

## 🤝 贡献

欢迎 Issue 与 PR 👋 流程见 [CONTRIBUTING.md](CONTRIBUTING.md)，变更见 [CHANGELOG.md](CHANGELOG.md)。

## 📄 许可证

[MIT License](LICENSE) · 开源共享 🎉

---

## ⭐ Star History

如果对你有帮助，给个 Star 吧~

<a href="https://github.com/mucjustin/mpa-skill">
  <img src="https://img.shields.io/github/stars/mucjustin/mpa-skill?style=social" alt="GitHub stars">
</a>

<p align="center">
  <a href="https://star-history.com/#mucjustin/mpa-skill&Date">
    <img src="https://api.star-history.com/svg?repos=mucjustin/mpa-skill&type=Date" alt="Star History" width="60%">
  </a>
</p>

<p align="center">
  <sub>Built with kyro🧠 for MPA researchers · 从碎片到可核验</sub>
</p>
