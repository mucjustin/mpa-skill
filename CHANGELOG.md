# 📜 Changelog

<p align="center">
  <a href="https://github.com/mucjustin/mpa-skill/releases">
    <img src="https://img.shields.io/github/v/release/mucjustin/mpa-skill?color=brightgreen" alt="Release">
  </a>
  <a href="https://keepachangelog.com/zh-CN/1.1.0/">
    <img src="https://img.shields.io/badge/Keep%20a%20Changelog-1.1.0-4A90E2.svg" alt="Keep a Changelog">
  </a>
  <a href="https://semver.org/lang/zh-CN/">
    <img src="https://img.shields.io/badge/SemVer-2.0.0-6f42c1.svg" alt="Semantic Versioning">
  </a>
</p>

本项目所有显著变更均记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

---

## 📇 版本速览

| 版本 | 日期 | 主题 |
|---|---|---|
| [Unreleased](#unreleased) | — | 可靠性层合并：数据先于写作 + 可恢复交付 + 基准验证 |
| [2.5.1](#251---2026-08-24) | 2026-08-24 | README 视觉美化与文档体系升级 |
| [2.5.0](#250---2026-08-24) | 2026-08-24 | MPA 知识本体层上线（理论地图 / 中国情境 / 思维清单 / 课程映射） |
| [2.4.0](#240---2026-08-24) | 2026-08-24 | 本地 Office 编辑与真实数据工作流 |
| [2.3.0](#230---2026-08-24) | 2026-08-24 | 非 MPA → MPA 转化与工作区集成询问 |
| [2.2.1](#221---2026-08-24) | 2026-08-24 | 文字规范化与 Issue 模板补齐 |
| [2.2.0](#220---2026-08-24) | 2026-08-24 | 通用 AIGC 披露规则 |
| [2.1.1](#211---2026-08-24) | 2026-08-24 | 案例竞赛规则去特例化 |
| [2.1.0](#210---2026-08-24) | 2026-08-24 | 案例竞赛分支 |
| [2.0.0](#200---2026-08-24) | 2026-08-24 | 仓库与 Skill 重命名（破坏性变更） |
| [1.1.0](#110---2026-08-24) | 2026-08-24 | CI、Issue/PR 模板与文档体系 |
| [1.0.0](#100---2026-08-23) | 2026-08-23 | 首个公开版本 |

---

## [Unreleased]

### Added

- 合并可靠性层：数据先于写作路由（能力预检 → 来源/数据/数值审计 → 分析或证据缺口 → 内容 → 交付 → 验收）；STATE_UNKNOWN 写入状态分类与安全停止；Office 交付中断后重新获取文档身份并核对新旧内容；
- 新增 8 个可靠性场景测试（`tests/Test-ReliabilityScenarios.ps1` + `tests/fixtures/reliability-scenarios.json`）与论文清单测试（`tests/Test-BenchmarkManifest.ps1`）；
- 新增公开基准资产：`docs/validation/v2.4.0-benchmark.md`、`docs/validation/v2.4.0-results.json`、`docs/validation/mpa-thesis-corpus.json`；
- CI 新增可靠性场景与论文清单两步验证；
- 新增 AI 使用声明生成器（`skills/mpa-skill/references/aigc-disclosure.md`）：工具名称、版本、官方网址、使用用途、具体环节、参数设置、验证过程七字段仅取自实际发生的工具使用，未核实字段保留 `AUTHOR_INPUT_NEEDED`，不写入未执行的验证，且不代签、不代交声明；SKILL.md、routing.md、mpa-deliverables.md 与双语 README 同步挂载。

### Changed

- routing.md 合并交叉序列：保留 GitHub 版全部 12 条路由与 Theory grounding / China-context check 行，追加本地版数据先于写作段与四知识文件加载条件；
- local-office-editing.md 合并：以本地版结构（Capability preflight → Mutation transaction → Recovery → Conditional compatibility → Acceptance）为骨架，嵌入 GitHub 版 SDK 细节（`doc_insert_table_by_csv`、`file_id`、`is_dirty`、`--json`、`file://`、降序编辑、`inherit_styles`、550px/96DPI）；
- SKILL.md 合并：保留四知识文件指针与 thinking checklist 步骤，追加数据先于写作段与 Office 条件加载段，验收段补双向验证；
- Test-PublicSkill.ps1 合并：PS 5.1 兼容修复 + 本地版全部 benchmark 断言 + GitHub版四知识文件/SDK/路由断言；
- README 中英文版合并：以本地版 benchmark/证据边界/起步提示/审计示例为基底，叠加 GitHub 版视觉元素（logo、badge、TOC、特性表、SVG 图位、技术栈、页脚）。

### Validation

- 冻结候选在合成场景中为 8/8；无 Skill 与 v2.3.0 均为 7/8，差值均为 +1/8（+12.5 个百分点）；
- 真实论文验证为 7 篇开发集加 3 篇留出集。v2.3.0 与 v2.4.0 均完成 10/10 路由、找出 30/30 个预登记风险，记录输出中的不受支持声明为 0；观察到的改进限于陈旧产物拒绝和可恢复交付，不代表论文诊断更优；
- 限制：每个条件仅一次响应；4/10 个 PDF 结构预检为 `UNAVAILABLE`；10 篇试点不是总体估计；只有 1 条中国情境记录；来源链接可能漂移；
- AI 使用声明断言已纳入 `tests/Test-PublicSkill.ps1`（文件清单、七字段、防捏造、验证溯源、责任边界、README 双语链接、隐私扫描），契约测试与可靠性场景测试各连续 5 轮通过。

## [2.5.1] - 2026-08-24

### Changed

- README 中英文版视觉升级：居中 Logo 与 Banner SVG、徽章矩阵、目录导航、emoji 章节标题、特性表格、架构/工作流 SVG 图位、技术栈表格、故障排查表格、页脚；
- CHANGELOG 新增版本速览表与视觉徽章；
- 仓库结构说明补齐 `assets/` 与 `docs/validation/` 目录。

## [2.5.0] - 2026-08-24

### Added

- MPA 知识本体层（回应"skill 缺乏 MPA 学科内容"问题），新增 4 个 reference：
  - `mpa-theory-map.md`：理论地图（四主题分组：政策执行与基层 / 制度与激励 / 治理与制度主义 / 政策过程；含理论、核心命题、典型中国应用情境、适用论文类型、常见误用五列）；
  - `mpa-china-contexts.md`：中国治理情境库（情境、特征、典型政策工具、论文切入视角、代表案例五列）；
  - `mpa-thinking-checklist.md`：公管思维清单（13 项思维原则 + 自查问题 + 论文落地方式 + 反模式）；
  - `mpa-course-map.md`：课程-能力映射（MPA 核心课程、培养能力、支撑论文类型、论文落地点四列）；
- SKILL.md 四处指针：Start spine 步骤应用 thinking-checklist；MPA route ownership 的 case analysis 定位 china-contexts、thesis/defence 经 theory-map + thinking-checklist 锚定理论；deliverables 段补四文件读取时机；
- routing.md 新增 Theory grounding / China-context check 两行路由，跨路线顺序调整为先理论接地再文献证据，reference loading 追加四文件加载时机；
- 公开契约测试同步扩展四文件清单、内容断言（usage-note / coverage / table-rows）与 SKILL/routing 指针断言。

### Verified

- 公开契约测试 5 轮 + 工作区脚本测试 5 轮全 PASS；
- 隐私红线扫描 0 命中（个人路径、课题特例、机构线索全部清理）；
- 四文件与个人版去空白后内容一致（无脱敏差异）。

## [2.4.0] - 2026-08-24

### Added

- 新增真实数据工作流与条件式本地 Office 编辑规则：数据与数值先于写作接受；Office 交付在中断后重新获取文档身份、分类写入状态，并在 `STATE_UNKNOWN` 时停止；
- 新增 8 个可靠性场景、10 篇真实论文试点清单、逐案例机器可读结果与公开基准报告。

### Changed

- 转化、数据型论文与交付路线改为「能力预检 → 来源/数据/数值审计 → 分析或证据缺口 → 内容 → 交付 → 验收」；替换验收同时要求新值存在与旧值不存在；
- README 中英文版同步加入数据先于写作、可恢复 Office 交付、开放论文审计示例、三个起步提示及证据边界。

### Validation

- 冻结候选在合成场景中为 8/8；无 Skill 与 v2.3.0 均为 7/8，差值均为 +1/8（+12.5 个百分点）；
- 真实论文验证为 7 篇开发集加 3 篇留出集。v2.3.0 与 v2.4.0 均完成 10/10 路由、找出 30/30 个预登记风险，记录输出中的不受支持声明为 0；观察到的改进限于陈旧产物拒绝和可恢复交付，不代表论文诊断更优；
- 限制：每个条件仅一次响应；4/10 个 PDF 结构预检为 `UNAVAILABLE`；10 篇试点不是总体估计；只有 1 条中国情境记录；来源链接可能漂移。

## [2.3.0] - 2026-08-24

### Added

- 非 MPA → MPA 转化路由：明确「把非 MPA 材料改造为 MPA 工作」属于本控制器，按研究设计处理，改写前必须经 MPA Research Spine 重锚公共问题、利益相关者与理论；仅换措辞不算转化；
- 工作区集成主动询问：实质研究任务未说明 Zotero/Obsidian 偏好时，在路线确认中附带一次集成询问，确认前不写入；
- 契约测试新增 5 条断言。

## [2.2.1] - 2026-08-24

### Changed

- 文字表述规范化：SKILL.md 课程成果复用步骤改写、研究契约加载条件统一为 substantial research outputs；
- README（中英双语）架构图「五条分支」更正为当前十条路由；AIGC 披露条目排版修正；
- Issue 功能建议模板的 MPA 场景清单补齐（案例大赛、田野调研）。

## [2.2.0] - 2026-08-24

### Added

- 研究契约新增通用 AIGC 披露规则：按当前学校/项目/课程/赛事规则披露 AI 辅助；AI 生成的文字、数据、引用不得冒充学生本人原创（此前该规则仅覆盖案例竞赛场景）；
- 公开契约测试新增 AIGC 披露与课程笔记线索规则断言；
- README（中英双语）功能列表补充 AIGC 披露说明。

## [2.1.1] - 2026-08-24

### Changed

- 案例竞赛规则去特例化：移除源自个别获奖作品的示例与特定届数表述，保留对所有参赛课题通用的官方规则（三件套结构、字数上限、叙事弧、访谈证据、理论适用性、原创性与 AIGC 边界）；
- 全文按极简风格收紧措辞，规则数量不变。

## [2.1.0] - 2026-08-24

### Added

- 新增案例竞赛分支：`references/mpa-case-competition.md`，基于获奖参赛作品与官方通知提炼，涵盖三件套结构（案例正文/案例分析报告/调研报告与字数上限）、起承转合叙事、多主体访谈证据、理论适用性与框架耦合、原创性与 AIGC 边界；
- 路由表新增 case competition entry 路由；SKILL.md 触发描述与路由归属同步扩展；
- 研究契约指向案例大赛规则，明确当年官方通知优先；
- 公开契约测试新增案例竞赛文件、路由与内容断言，并将其纳入隐私扫描范围；
- README（中英双语）更新适用任务与仓库结构说明。

## [2.0.0] - 2026-08-24

### Changed

- 仓库由 `mpa-research-workflow-skill` 重命名为 [mpa-skill](https://github.com/mucjustin/mpa-skill)（GitHub 自动重定向旧地址）；
- Skill 名称与安装名由 `mpa-research-workflow` 改为 `mpa-skill`，安装命令更新为 `npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth`；
- 本机配置目录由 `%APPDATA%\mpa-research-workflow\` 改为 `%APPDATA%\mpa-skill\`。

### BREAKING

- 已按旧名安装的用户需卸载后以新名重装；旧配置目录需手动迁移到新路径。

## [1.1.0] - 2026-08-24

### Added

- GitHub Actions CI：在 windows-latest 上运行公开契约测试与工作区脚本测试；
- Issue 模板（缺陷报告、功能建议）与 Pull Request 模板；
- `CONTRIBUTING.md`：贡献流程、内容边界与版本维护规范；
- `CHANGELOG.md`：变更记录；
- README（中英双语）新增徽章、快速导航、Mermaid 架构图与仓库结构说明。

## [1.0.0] - 2026-08-23

### Added

- 首个公开版本：MPA Research Spine 研究主线与课程成果复用规则；
- 五条研究分支路由：课程资料、文献、研究设计、数据分析、论文与答辩；
- 工作区初始化与环境检查脚本（PowerShell，支持 WhatIf 预览）；
- 公开契约测试与工作区脚本测试；
- MIT 许可证与安全披露政策。
