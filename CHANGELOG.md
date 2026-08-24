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

## [1.0.0] - 2026-08-24

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
- 公开基准资产：论文清单、机器可读结果、基准报告
- GitHub Actions CI：契约测试 + 可靠性场景 + 论文清单 + 工作区脚本
- 工作区初始化与环境检查脚本（PowerShell，支持 WhatIf 预览）
- Issue 模板、PR 模板、贡献指南
- MIT 许可证与安全披露政策

### Validation

- 合成场景 8/8 通过
- 论文验证 10/10 路由正确、30/30 风险召回、0 编造
- PowerShell 5.1 兼容
