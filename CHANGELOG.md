# Changelog

本项目所有显著变更均记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

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
