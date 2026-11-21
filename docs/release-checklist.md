# 发布前检查清单

本页是「把 `main` 推成一次正式发行」的操作备忘。它记录的是仓库里**实际生效**的机械校验，不是流程倡议：每一条都能用命令复现，任何一条没过，CI 会在测试阶段直接变红。

## 0. 发布由什么触发

| 触发 | 发生什么 |
|---|---|
| push 到 `main` | 先跑 `test` 六矩阵（ubuntu / macos / windows × Python 3.10 / 3.13），全绿后跑 `publish-release` |
| PR 到 `main` | 只跑 `test`，不发布 |
| `workflow_dispatch` | 只跑 `test`，不发布（`publish-release` 有 `github.event_name == 'push'` 条件） |
| 手动 `gh release create` | 绕过全部门禁，**不要这样发** |

`publish-release` 的版本号唯一来源是 `python tools/check_release.py --print-version`，也就是 `SKILL.md` 的 `metadata.version`。它只有三条路径：

1. 该 tag 的 release 已存在 → 打印 `Release vX.Y.Z already exists; do not overwrite published artifacts.`，`exit 0`（所以纯文档提交推上 main 是安全的，不会重发）。
2. tag 已存在但指向别的 commit → `exit 1`，发布失败。
3. 都不存在 → `gh release create --target "$GITHUB_SHA" --notes-file docs/releases/vX.Y.Z.md --latest`，上传 `mpa-skill.zip` 与 `SHA256SUMS`。

## 1. 六处版本轴，必须在同一次提交里对齐

| 位置 | 要求的形式 |
|---|---|
| `skills/mpa-skill/SKILL.md` | `metadata.version: "X.Y.Z"`，**必须带双引号**，且 `metadata:` 下恰好一处 `version:` |
| `pyproject.toml` | `[project]` 段内 `version = "X.Y.Z"`，恰好一处 |
| `CHANGELOG.md` | 恰好一个 `## [Unreleased]`；恰好一个 `## [X.Y.Z] - YYYY-MM-DD`，且必须排在 `## [2.1.0]` **之前** |
| `docs/releases/vX.Y.Z.md` | 新建文件，正文必须出现字面量 `vX.Y.Z` |
| `README.md`、`README.en.md` | 正文必须出现字面量 `vX.Y.Z`（当前是 `**当前版本：vX.Y.Z。**` 那一行） |
| `docs/install-and-compatibility.md` | 正文必须出现字面量 `vX.Y.Z`（首段版本号 + 安装表行） |

漏一处就会得到 `Version drift in <path>` 或 `CHANGELOG must contain exactly one dated [X.Y.Z] section`。这六处是同一件事的六种投影，不存在「只改其中一处」的合法情形。

## 2. 本地三道预检

```bash
python3 -m unittest discover -s tests      # 期望：Ran N tests ... OK
python3 tools/check_release.py             # 期望：RELEASE METADATA PASS: vX.Y.Z
python3 tools/package_skill.py --output /tmp/dist/mpa-skill.zip
                                           # 期望：SKILL PACKAGE PASS: ... (N files)
```

| 命令 | 失败时的第一动作 |
|---|---|
| `unittest` | 看第一个 `FAIL`/`ERROR` 的文件行号；`test_skill_contract` 类失败通常意味着改了 `SKILL.md` 的红线措辞或断了 references 双向链接 |
| `check_release.py` | 见第 8 节报错对照表 |
| `package_skill.py` | 检查是否有 `.sqlite`、`.pem`、`__pycache__`、`.mpa-evidence/` 混进 `skills/mpa-skill/`，或单包超 50 MiB |

## 3. 打包内容自检

```bash
rm -rf /tmp/relcheck && mkdir -p /tmp/relcheck && cd /tmp/relcheck
unzip -q /tmp/dist/mpa-skill.zip
head -12 mpa-skill/SKILL.md | grep 'version:'
find . -type f | wc -l
```

- 顶层目录必须是 `mpa-skill/`，`SKILL.md` 直接位于其下。
- 包内 `version:` 必须与新版本号一致（读的是同一份 `SKILL.md`）。
- 文件数与 `SKILL PACKAGE PASS` 括号里的数字一致。
- 打包器硬性排除：`__pycache__`、`.mpa-evidence`、`.git`、`.pytest_cache`、任何以 `.` 开头的路径段、`.pyc/.pyo/.sqlite/.sqlite3/.db/.key/.pem`、`.DS_Store`、`Thumbs.db`。

## 4. 提交与推送

```bash
git add -A
git commit -m "release: vX.Y.Z <一句话主题>"
git push origin main
```

**不要本地 `git tag`。** tag 由 CI 创建，指向 CI 实际测过并打包的那个 commit。若本地先打了 tag 再推，`publish-release` 会跳到第 2 条路径——tag 指向的不是它自己的 `$GITHUB_SHA`，直接 `exit 1`。

## 5. 盯 CI

```bash
gh api "/repos/OWNER/REPO/actions/runs?per_page=3" \
  --jq '.workflow_runs[] | "\(.id) \(.head_sha[0:7]) \(.status)/\(.conclusion) \(.name)"'
gh api "/repos/OWNER/REPO/actions/runs/<RUN_ID>/jobs" \
  --jq '.jobs[] | "\(.name): \(.status)/\(.conclusion)"'
```

一次完整发行的 job 数是 **7**：六个 `Tests (...)` 加一个 `Publish versioned release after green CI`。

> `gh run list` 在本机实测会长时间不返回（TUI/GraphQL 路径问题），用上面的 `gh api` REST 接口替代。

## 6. 发布后核验（必做，不要只看 CI 绿灯）

```bash
cd /tmp && rm -rf postcheck && mkdir postcheck && cd postcheck
gh release download vX.Y.Z -R OWNER/REPO
shasum -a 256 -c SHA256SUMS                    # 期望：mpa-skill.zip: OK
unzip -p mpa-skill.zip mpa-skill/SKILL.md | grep 'metadata\|version:'
gh api /repos/OWNER/REPO/releases/tags/vX.Y.Z --jq '.body' | head -20
```

四项各自证明一件事：附件齐全、下载到的字节与声明一致、包内版本号确实是要发的版本、release notes 来自 `docs/releases/vX.Y.Z.md` 而不是空白或旧稿。

## 7. 版本发错了怎么办

| 情形 | 处理 |
|---|---|
| 版本号发错 / 内容有致命缺陷 | **不要重发同号**。`gh release delete vX.Y.Z --yes --cleanup-tag`，然后升到 `X.Y.Z+1` 重新走全流程。已被下载的 zip 与 `SHA256SUMS` 一旦被原地重写就无法追溯 |
| 只是想改文档、不想发版 | 直接推 `main`。`publish-release` 命中「release 已存在」分支，`exit 0`，不会产生新发行 |
| 发布 job 因网络/调度失败，但代码没问题 | 在 Actions 页面 `Re-run failed jobs`。代码未变时 `$GITHUB_SHA` 不变，不会撞 tag 冲突 |

## 8. `check_release.py` 报错对照表

| 报错 | 原因与修法 |
|---|---|
| `SKILL.md YAML frontmatter is missing` | `SKILL.md` 首行必须是 `---`，第二段闭合 `---` 前不能有注释垃圾 |
| `SKILL.md metadata.version requires one quoted semantic version` | `version:` 必须是 `"X.Y.Z"` 三段式且带引号；写成 `2.3` 或去引号都会失败 |
| `SKILL.md requires one metadata mapping` | `metadata:` 出现两次，或缩进被打断 |
| `CHANGELOG must contain exactly one dated [X.Y.Z] section` | 标题格式必须是 `## [X.Y.Z] - YYYY-MM-DD`；漏日期、写成 `## X.Y.Z`、或同一版本两段都算失败 |
| `CHANGELOG must contain exactly one [Unreleased] section` | 升版时把旧 `[Unreleased]` 改名成新版本号，再在顶部补一个空的 `[Unreleased]` |
| `Current release must precede the archived v2.1.0 section` | 新版本段被插到了 `## [2.1.0]` 后面；`CHANGELOG` 必须倒序 |
| `Versioned GitHub release notes are missing` | `docs/releases/vX.Y.Z.md` 不存在，或文件里连 `vX.Y.Z` 都没出现 |
| `Version drift in <path>` | 该文档里没有字面量 `vX.Y.Z`；注意是 `v` 开头的完整写法 |
| `pyproject.toml version X does not match Skill version Y` | 两条版本轴漂移，改 `pyproject.toml` 对齐 `SKILL.md` |
| `pyproject.toml [project] requires exactly one version` | `[project]` 段里出现了第二个 `version =` |

## 9. 不要做的事

- 不要在已发布的 commit 上 `commit --amend` 后强推 `main`：tag 仍指向旧 commit，下一次发版会在 tag 冲突检查处 `exit 1`。
- 不要为了让 CI 变绿去放宽 `tools/check_release.py` 的校验。它是本地预检与 CI 共用的唯一真相，放宽等于把漂移变成静默。
- 不要提交 `.mpa-evidence/`、`.sqlite`、`.pem`、`__pycache__`：打包器会挡，但工作区一旦被污染，本地预检结果也不可信。
- 不要在 `publish-release` 成功后再手动 `gh release upload` 覆盖同名资产：`SHA256SUMS` 会与 zip 失配。
