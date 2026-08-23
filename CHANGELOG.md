# Changelog

本项目所有显著变更均记录在本文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循[语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

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
