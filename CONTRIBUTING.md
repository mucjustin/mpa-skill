# 🤝 贡献指南

感谢你考虑为 **MPA Skill** 贡献。本仓库面向所有 MPA、公共管理与公共政策方向的研究者，欢迎 Issue、Pull Request 与讨论。

---

## 📋 前置要求

- Windows 10 / 11（Skill 脚本为 Windows-first）；
- PowerShell 5.1+ 或 PowerShell 7+（`pwsh`）；
- Git。

---

## 🔄 开发流程

1. **Fork** 本仓库并克隆到本地；
2. 从 `main` 创建分支：`feat/xxx`、`fix/xxx`、`docs/xxx` 或 `test/xxx`；
3. 修改 `skills/mpa-skill/` 下的 Skill 内容或 `tests/` 下的测试；
4. 本地运行全部测试并确认通过（见下节）；
5. 按 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/) 规范提交，发起指向 `main` 的 Pull Request；
6. CI 在 `windows-latest` 上运行与本地相同的测试，通过后合并。

---

## 🧪 本地测试

```powershell
pwsh tests/Test-PublicSkill.ps1
pwsh tests/Test-WorkspaceScripts.ps1
```

| 测试脚本 | 作用 |
|---|---|
| `Test-PublicSkill.ps1` | 校验仓库结构、Skill 指令契约、README 与许可证的一致性，并拒绝个人路径、邮箱与令牌等隐私内容。 |
| `Test-WorkspaceScripts.ps1` | 在临时目录中验证初始化与环境检查脚本的行为，不会触碰真实工作区。 |

---

## ⚠️ 内容边界（重要）

- 公开版必须**零隐私信息**：不得引入个人盘符路径、账号、机构专属配置或任何可识别信息；
- 保持 Windows-first 声明真实：跨平台改造请先开 Issue 讨论；
- 不得放宽安全停止条件（登录、验证码、付费墙、破坏性写入）；
- Skill 行为契约变更必须同步更新 `tests/Test-PublicSkill.ps1`，保持测试与行为一致；
- 新增依赖必须在 `skills/mpa-skill/references/dependencies.md` 中声明，并说明缺失时的降级行为。

---

## ✍️ 提交规范

使用 [Conventional Commits](https://www.conventionalcommits.org/zh-hans/)：

| 前缀 | 用途 |
|---|---|
| `feat:` | 新功能 |
| `fix:` | 问题修复 |
| `docs:` | 文档改进 |
| `test:` | 测试相关 |
| `chore:` | 杂项维护 |
| `refactor:` | 重构（无行为变化） |

---

## 🏷️ 版本维护规范

- 版本号遵循语义化版本 `MAJOR.MINOR.PATCH`：
  - **MAJOR**：SKILL 行为契约、路由结构或安全边界的破坏性变更；
  - **MINOR**：向后兼容的新能力（新增 reference、脚本参数、交付物类型）；
  - **PATCH**：问题修正与文档改进；
- 发布流程：更新 `CHANGELOG.md` → 合并到 `main` → 打标签 `vX.Y.Z`；
- 未发布变更统一记录在 `CHANGELOG.md` 的 `[Unreleased]` 段；
- 请勿在 `main` 上保留未写入 CHANGELOG 的契约变更，`npx skills update` 会直接拉取 `main` 的最新版本。

---

## 📜 行为准则

请保持尊重、专业与建设性。本仓库聚焦于学术诚信、研究可核验性与 MPA 公共利益，任何鼓励造假、绕过授权或泄露隐私的贡献都不会被接受。
