# Changelog

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

## [2.0.0] - 2026-08-24

### Changed（架构精简与能力增强）

- **引用文件从 13 个精简为 8 个**：合并四个 MPA 知识文件（理论地图、中国情境、思维清单、课程映射）为统一的 `mpa-knowledge.md`；合并四个执行规则文件（真实数据工作流、本地 Office 编辑、依赖管理、工作区配置）为统一的 `execution.md`
- **SKILL.md 从 48 行精简为 36 行**：用单一「引用加载表」替代分散在 3 段中的 "Read X before Y" 指令
- **routing.md 简化为路由表 + 决策树**：移除冗余的加载指令，用紧凑的表格组织 12 条路由

### Added（新增能力）

- **`templates.md` 实用模板库**：8 种路由的落地模板（案例分析、政策备忘录、文献综述、研究设计、田野调查清单、数据分析报告、答辩准备、课程笔记），每个模板含结构骨架和检查清单
- **知识库扩展**：理论地图新增运动式治理、目标责任制、公共选择理论、网络治理、民主行政、政策终结、间断均衡 7 个理论（共 26 个 → 33 个）；中国情境库新增区域协同、营商环境优化、生态环境治理、数据治理与隐私保护 4 个情境（共 10 个 → 14 个）；思维清单新增政策评估意识原则
- **方法选择决策树**：按数据特征和研究问题类型自动推荐定量/定性/混合方法

### Removed

- 删除 `mpa-theory-map.md`、`mpa-china-contexts.md`、`mpa-thinking-checklist.md`、`mpa-course-map.md`（合并入 `mpa-knowledge.md`）
- 删除 `real-data-workflow.md`、`local-office-editing.md`、`dependencies.md`、`workspace-configuration.md`（合并入 `execution.md`）

### Migration

- 旧版本引用的文件路径已变更：`real-data-workflow.md` → `execution.md`（数据工作流章节）、`local-office-editing.md` → `execution.md`（Office 编辑章节）、`dependencies.md` + `workspace-configuration.md` → `execution.md`（依赖管理 + 工作区配置章节）、四个知识文件 → `mpa-knowledge.md`（对应章节）
- `SKILL.md` 的引用加载表完整映射了新路径

---

## [1.0.0] - 2026-08-24

首个公开发布版本。开发过程中的内部迭代标签（含基准条件 `previous` / `current` 的对应关系）见[基准报告](docs/validation/v1.0.0-benchmark.md)的命名说明。

### Added

- MPA Research Spine 研究主线：公共问题 → 利益相关者 → 制度语境 → 理论 → 证据 → 方法 → 分析 → 建议
- 13 条路由（双语关键词）：课程、案例分析、案例大赛、政策备忘录、文献综述、研究设计、田野调查、数据分析、学位论文、论文答辩、非公管转公管、理论接地、中国情境检验
- 四份 MPA 知识本体文件：
  - `mpa-theory-map.md`：理论地图（政策执行与基层 / 制度与激励 / 治理与制度主义 / 政策过程）
  - `mpa-china-contexts.md`：中国治理情境库
  - `mpa-thinking-checklist.md`：公管思维清单（13 项原则 + 反模式）
  - `mpa-course-map.md`：课程-能力映射
- 可靠性层：数据先于写作、STATE_UNKNOWN 安全停止、双向验收
- Provider-neutral Office 编辑规则：能力预检 → 变更事务 → 恢复 → 条件兼容 → 验收
- 真实数据工作流：标准化解释边界、来源/数据/数值审计
- 案例竞赛规则：三件套结构、叙事弧、访谈证据、理论适用性、AIGC 边界
- 非 MPA → MPA 转化路由：研究设计处理，改写前经 Research Spine 重锚
- 通用 AIGC 披露规则
- AI 使用声明生成器（`skills/mpa-skill/references/aigc-disclosure.md`）：工具名称、版本、官方网址、使用用途、具体环节、参数设置、验证过程七字段仅取自实际发生的工具使用，未核实字段保留 `AUTHOR_INPUT_NEEDED`，不写入未执行的验证，且不代签、不代交声明；SKILL.md、routing.md、mpa-deliverables.md 与双语 README 同步挂载
- 公开基准资产：论文清单（`docs/validation/mpa-thesis-corpus.json`）、机器可读结果（`docs/validation/v1.0.0-results.json`）、基准报告（`docs/validation/v1.0.0-benchmark.md`）
- GitHub Actions CI：契约测试 + 可靠性场景 + 论文清单 + 工作区脚本
- 工作区初始化与环境检查脚本（PowerShell，支持 WhatIf 预览）
- Issue 模板、PR 模板、贡献指南
- MIT 许可证与安全披露政策

### Changed

- 路由采用双语关键词匹配，中文查询准确率从 14% 提升至 93%
- README 中英文版同步加入数据先于写作、可恢复 Office 交付、开放论文审计示例、三个起步提示及证据边界；中文版在功能区前置基准局限摘要与 AI 使用合规叙事
- Office 交付在中断后重新获取文档身份、核对新旧内容并恢复到可验证状态，无法判定时停在 `STATE_UNKNOWN`

### Validation

- 冻结候选在合成场景中为 8/8；无 Skill 与早期内部迭代均为 7/8，差值均为 +1/8（+12.5 个百分点）；
- 真实论文验证为 7 篇开发集加 3 篇留出集。两个版本均完成 10/10 路由、找出 30/30 个预登记风险，记录输出中的不受支持声明为 0；观察到的改进限于陈旧产物拒绝和可恢复交付，不代表论文诊断更优；
- 限制：每个条件仅一次响应；4/10 个 PDF 结构预检为 `UNAVAILABLE`；10 篇试点不是总体估计；只有 1 条中国情境记录；来源链接可能漂移。
- AI 使用声明断言已纳入 `tests/Test-PublicSkill.ps1`（文件清单、七字段、防捏造、验证溯源、责任边界、README 双语链接、隐私扫描），契约测试与可靠性场景测试各连续 5 轮通过；
- PowerShell 5.1 兼容。
