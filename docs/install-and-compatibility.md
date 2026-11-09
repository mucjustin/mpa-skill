# 安装与兼容性 / Codex & WorkBuddy

**展示名称：MPA Research Agent（公共管理证据研究助手）**。技术 Skill ID、安装目录和 GitHub 仓库地址仍保留 `mpa-skill`、`mucjustin/mpa-skill`，不破坏已有命令。Skill 的 `metadata.version`（当前为 `"2.3.1"`）、CHANGELOG 与对应 GitHub Release 必须保持一致。正式附件请从 [Releases](https://github.com/mucjustin/mpa-skill/releases/latest) 下载。

`SKILL.md` 顶层使用标准 `name`、`description` 和 `metadata` 字段。版本、作者和双语展示信息均为 `metadata` 下的字符串；双语示例使用多行字符串保存。Codex 界面配置仍由 `agents/openai.yaml` 提供。项目发行工具读取 `metadata.version`，不再读取旧的顶层 `version`。安装包通过通用格式校验不代表已验证 WorkBuddy GUI 导入。

## 宿主支持与验证边界

| 功能 | Codex | WorkBuddy |
|---|---|---|
| 发现包含 `SKILL.md` 的 Skill | 官方支持 | 官方支持 |
| 加载 references 和执行脚本 | 具备对应文件/终端权限时支持 | 官方描述支持，实际客户端权限需核查 |
| 单目录自包含 Python 工具 | GitHub CI 隔离测试通过 | GitHub CI ZIP 解压隔离测试通过 |
| 安装 v2.3.1 | `main` / 正式 GitHub Release | ZIP 隔离执行已验证；**尚未实测 WorkBuddy GUI 导入** |
| PDF 文本处理 | 可选 `pypdf` | 需另行授权安装 `pypdf`，且宿主允许调用 |
| 操作系统 | macOS / Windows / Linux（CI 三平台测试） | 取决于宿主环境；只需 Python 3.10+，无需 PowerShell |

来源：
- [OpenAI Agent Skills 结构与运行要求](https://developers.openai.com/api/docs/guides/tools-skills)
- [WorkBuddy 技能结构、元数据和 scripts 说明](https://open.workbuddy.cn/docs/skill)
- [WorkBuddy 技能上传步骤](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Skills-Market)

## Codex：正式版本与测试版的区别

正式安装命令（默认取得 main 的现有版本）：

~~~bash
npx skills add mucjustin/mpa-skill -g -s mpa-skill -y --full-depth
~~~

PR #2 与 PR #3 均已合并到 `main`。默认安装命令将获取包含研究引擎和内置证据工具的新版；若需要固定复现某一次发行，请使用 [GitHub Releases](https://github.com/mucjustin/mpa-skill/releases/latest) 中对应的 ZIP 或标签源码。

参考本地工具预检（实际路径以你安装的位置为准）。macOS / Linux：

~~~bash
python3 "$HOME/.agents/skills/mpa-skill/scripts/mpa_evidence.py" doctor
~~~

Windows：

~~~powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') doctor
~~~

macOS 自带的 `python3` 若低于 3.10，可通过 [python.org](https://www.python.org/downloads/macos/) 安装包或 Homebrew（`brew install python`）安装新版本。

`doctor` 只读，不初始化数据库，不自动联网、不自动安装依赖。若 Python 版本不支持或没有终端权限，Skill 应只提供研究方案或证据收集计划。

## WorkBuddy：导入单目录 ZIP

从完整仓库根目录运行：

~~~bash
python3 tools/package_skill.py --output dist/mpa-skill.zip
~~~

正式版从 [GitHub Releases](https://github.com/mucjustin/mpa-skill/releases/latest) 下载 **`mpa-skill.zip`**，并核对附带的 `SHA256SUMS`。GitHub Actions 构建产物 `mpa-research-agent-skill` 是用于 CI 验证的临时双层 ZIP，不能与正式版附件混淆。

按照 WorkBuddy 界面依次进入「专家·技能·连接器 → 技能 → 添加技能 → 上传技能」，选择内部单 Skill ZIP。技能元数据应显示「公共管理证据研究助手」。

首次验收使用**自建的、不包含任何真实学生或访谈者信息的 TXT 文件**，提示 Skill：

> 先只检查本地证据工具的 Python、资料权限和工作区状态，不要创建项目或导入材料；请报告 doctor 的真实结果。

然后确认工作区及持久化授权，再执行导入和引用。WorkBuddy 如果把脚本运行放在沙盒、未开放本地文件夹或未安装 Python，应明确降级，不得假装完成。**目前通过的是文件结构与 Python 独立执行测试，不是 WorkBuddy 应用实际 UI 安装测试。**

## 证据、安全与学术边界

`ingest` 会复制原文件并把可提取文本存进工作区的 `.mpa-evidence/`；这些文件和 SQLite 数据库**不加密**，取决于宿主文件权限与备份策略。对学生、社保、访谈等敏感数据，只有机构授权且环境满足要求时才能使用，不能上传公开仓库。

对某主张的逐字引文定位、原始文件 SHA-256，均不证明主张真伪、数据代表性或因果性。`review --status verified` 只能依据研究者明确复核后的指令执行。

## 为什么不更换 GitHub 仓库名？

已有安装命令和 Skill ID 依赖 `mpa-skill`。这次只更新品牌与说明，保留现有仓库和包名；如要正式改名，需要独立迁移与兼容性评估。
