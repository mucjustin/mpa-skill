# Contributing / 贡献指南

欢迎为 **MPA Research Agent** 贡献。GitHub 仓库仍为 `mucjustin/mpa-skill`，Skill 安装标识仍为 `mpa-skill`；不要为了品牌调整无意中破坏已有安装链路。

## 工程边界

- **仅一个可发现的 Skill：** `skills/mpa-skill/SKILL.md`。新增功能尽量以按需 references 或脚本提供。
- **确定性代码优先：** 源文件解析、逐字引文定位、哈希、状态管理放在 `skills/mpa-skill/scripts/evidence_workbench/`；研究判断仍需可核验来源和人的复核。
- **默认安全：** 导入资料会在工作区复制源文件并建立未加密的本地 SQLite 库。涉及个人、学生、社会保障或机构敏感记录应先确保合法授权；不得上传真实资料到公开仓库或测试夹具。
- **学术边界：** 引文匹配不是事实核查，人工复核状态不等于结论成立；不能把观察相关性说成因果效果。
- **多客户端：** Codex 和 WorkBuddy 使用同一个 Skill 文件夹，不维护平行的重复源代码；外部客户端真实安装情况应单独报告。

## 开发环境

- Python 3.10+（标准库支持文本、CSV、DOCX 核心流程）。
- PDF 文字提取可选：`python -m pip install 'pypdf>=5,<8'`。
- PowerShell 7+ 用于 Windows 下的现有兼容性/工作区测试。无 PowerShell 的平台可运行 Python 测试，但不代表原有 PowerShell 脚本均能运行。
- Git + 可执行 Python 的本地 shell；不在 CI 或 Skill 中静默下载其他软件。

## PR 流程

1. 基于最新目标分支建 feature/fix/docs 分支，提交 PR；避免直接修改 `main`。
2. 修改 `SKILL.md` / references 后检查触发范围是否被无意扩大。
3. 修改 Python 工具后添加端到端测试；新引文必须保持 `unverified`，不能由模型直接标记 `verified`。
4. 对 WorkBuddy 元数据及 ZIP 分发结构运行打包与隔离执行测试。
5. 运行全部可用测试后提交，失败时修复并附上复现说明。

## 验证命令

~~~powershell
python -m pip install -e '.[pdf]'
python -m unittest discover -s tests -p 'test_evidence_*.py' -v
python -m unittest discover -s tests -p 'test_skill_portability.py' -v
python -m unittest discover -s tests -p 'test_skill_package.py' -v
python tools/package_skill.py --output dist/mpa-skill.zip
pwsh -NoProfile -File tests/Test-PublicSkill.ps1
pwsh -NoProfile -File tests/Test-CaseResearch.ps1
pwsh -NoProfile -File tests/Test-ReliabilityScenarios.ps1
pwsh -NoProfile -File tests/Test-BenchmarkManifest.ps1
pwsh -NoProfile -File tests/Test-WorkspaceScripts.ps1
~~~

机器测试验证确定性行为，不是独立的学术质量 A/B 基准。评测报告要区分开发集、留出集、人工评价与尚未实际完成的实验。

## 版本与维护

使用 Conventional Commits：`feat:`、`fix:`、`docs:`、`test:`、`refactor:`、`chore:`。发布前同步 `SKILL.md` 的 `version`、`CHANGELOG.md` 和用户文档。历史评测数据保留原始口径，不能为宣传改写既有实验结论。

## 安全报告

公开 Issue 不接受漏洞利用细节、私有数据、密钥、真实访谈/学生记录等。参见 [SECURITY.md](SECURITY.md)，使用 GitHub 私密漏洞报告。
