# 十分钟快速开始：从一份材料到一条可复核的证据

本页只做一件事：让一份真实材料走完「预检 → 导入 → 定位 → 立论 → 引证 → 人工复核 → 门禁审计 → 导出」。
所有编号（`D-…`、`C0001`、`E0001`、`L3`）都必须来自命令的实际返回，**不要凭印象书写**。文中材料为合成示例。

## 0. 三条边界先说清

1. 工具只做机械校验：文件字节 SHA-256、逐字引文、定位是否一致。它**不判断**材料真伪、观点代表性、因果机制或政策效果。
2. 工作区 `.mpa-evidence/` 保存原文件副本、抽取全文和 SQLite 数据库，**均不加密**。涉及访谈、学生信息或单位内部资料时，先确认授权与目录权限，勿放入公开仓库。
3. `verified` 只能由研究者本人对照原文后声明。模型不得自查、自批或批量代签。

## 1. 预检（只读，不写任何文件）

```bash
SKILL_ROOT="$HOME/.agents/skills/mpa-skill"   # 换成你的实际安装路径
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" doctor
```

`doctor` 只读，输出 JSON。看四个字段：

| 字段 | 含义 | 不满足时怎么做 |
|---|---|---|
| `python_usable` | 当前解释器能否跑完所有内置命令 | `false`：停止，装 Python 3.10+ |
| `python_supported` / `python_minimum` | 是否达到受测下限（3.10） | `false` 但 `usable` 为 `true`：命令能跑，属**未测试**范围，正式交付前换 3.10+ |
| `warnings` | 上面这条的可读说明 | 照原话转述给使用者，不要自行忽略 |
| `pdf_text_available` | 是否有可选依赖 `pypdf` | `false` 且材料是 PDF：先征得同意再安装，或改用可提取的版本 |

## 2. 建库（一次性）

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" init "$HOME/MPA-Research"
```

工作区一旦建立即包含 `.mpa-evidence/`：`sources/`（原件副本）、`registry.sqlite3`（索引）。重复 `init` 不会破坏已有数据。

## 3. 导入材料

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" ingest "$HOME/MPA-Research" "$HOME/Downloads/policy.txt"
```

返回里有三样东西要抄下来：`doc_id`（形如 `D-95c0746e1ad4c218`）、`snapshot_sha256`、段落数。
**文档 ID 由内容哈希派生**：同一文件重复导入得到同一 ID（`duplicate: true`），改过内容则是新 ID，旧证据不会被静默改写。

## 4. 定位：唯一可信的原文窗口

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" segments "$HOME/MPA-Research" D-95c0746e1ad4c218 --search "政策"
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" segments "$HOME/MPA-Research" D-95c0746e1ad4c218 --locator L3
```

`--search` 只给预览（超长会截断并标注）；`--locator` 给该段**未截断**全文。引文只能从 `--locator` 的输出里复制。
定位类型：文本 `L1`、CSV `row.1`、DOCX 正文 `para.1`、脚注 `fn.1`、尾注 `en.1`、PDF 物理页 `p.1`；跨段用范围 `L3-L5`（同类型，最多 20 段）。

## 5. 立论

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" claim "$HOME/MPA-Research" \
  --question "政策执行是否存在差异？" --statement "两县采用不同的执行办法" --kind inference
```

`--kind` 取 `fact` / `inference` / `causal` / `recommendation`。因果论断请同时登记竞争性解释：

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" claim "$HOME/MPA-Research" \
  --question "差异从何而来？" --statement "财力差异导致执行差异" --kind causal --rival-of C0001
```

## 6. 引证（逐字匹配，不做近似替换）

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" cite "$HOME/MPA-Research" \
  --claim C0001 --document D-95c0746e1ad4c218 --locator L3 \
  --quote "政策目标为改善服务。" --relation supports
```

新登记的引证**一律 `unverified`**。相反证据用 `--relation challenges` 保留，不要删。

### 失败信息怎么读

`cite` 不会猜你的意思，它只告诉你差在哪：

| 返回 | 含义 | 处理 |
|---|---|---|
| `The quoted text is verbatim at L1, not at L3.` | 引文存在，但不在你给的定位 | 换 `--locator L1` 重跑 |
| `Longest verbatim span is 10 characters (…); 1 extra character(s) after it: '。'` | 多/少了标点、空格或错字 | 按提示删改后重跑；匹配不会放松 |
| `No usable verbatim span … inspect the exact segment first: segments "…" D-… --locator L3` | 该段没有相近文本 | 先 `segments --locator` 看原文，再决定引用哪段 |
| `… matches only after ignoring whitespace/full-width differences; rerun with --normalized` | PDF 抽取插入了空格/换行 | 确认语境后用 `--normalized`；库里保存的仍是原文逐字片段 |
| `Unknown document ID 'D-…'. … Registered documents: …` | 文档 ID 写错（无法靠猜修正） | 用提示里列出的真实 ID，或重新 `ingest` |
| `Evidence link already exists; refusing duplicate.` | 同一论断+定位+引文+关系已登记 | 换关系或改论断，不要重复登记 |

## 7. 人工复核（唯一能改状态的动作）

把原始材料、定位和引文一起给研究者看；研究者确认后，**由他给出口头/书面指令**，再由 agent 执行：

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" review "$HOME/MPA-Research" E0001 \
  --status verified --reviewer "研究者本人标注" --note "已对照原始材料第 3 段"
```

`disputed` / `rejected` 必须写 `--note` 说明理由。`reviewer` 是声明，不是身份验证。

## 8. 门禁审计（两种严格度）

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" audit "$HOME/MPA-Research"          # 只拦完整性错误
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" audit "$HOME/MPA-Research" --strict # 未决警告也拦
```

| 场景 | 默认 audit | `--strict` |
|---|---|---|
| 源文件被改动 → `source_hash_mismatch` | `ok:false`，退出码 2 | 同左 |
| 引文与定位不再一致 → `quote_locator_mismatch` | `ok:false`，退出码 2 | 同左 |
| 引证仍未复核 → `pending_manual_review` | `ok:true`，退出码 0，`counts.warning` 计数 | `ok:false`，退出码 2 |
| 论断无证据 / 因果无竞争解释 | 同上（warning） | 同上 |

写脚本或要求「干净交付」时用 `--strict`；平时用它读 `counts` 和 `issues` 决定下一步，而不是看一个布尔值。

## 9. 导出

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" export "$HOME/MPA-Research" \
  --format md --output "$HOME/MPA-Research/evidence-matrix.md"
```

默认不含原文引文（`--include-quotes` 才会带出，涉密材料需单独授权）；目标已存在需显式 `--overwrite`。
`[证据]` / `[推断]` / `[建议]` 三类在导出中保持分开，脚本不会替你升级任何状态。

## 10. 每次研究的节奏

```bash
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" progress "$HOME/MPA-Research"            # 开始：读主线与下一步
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" progress "$HOME/MPA-Research" --set evidence=partial --todo "补 2023 年执行记录"
python3 "$SKILL_ROOT/scripts/mpa_evidence.py" progress "$HOME/MPA-Research" --done T0001 --next T0002
```

研究主线八环：问题、利益相关方、制度、理论、证据、方法、分析、建议。状态取 `missing` / `partial` / `established` / `out_of_scope`。

## 附：命令一览

| 命令 | 作用 | 是否写入 |
|---|---|---|
| `doctor` | 环境与工作区预检 | 否 |
| `init` | 建立私有工作区 | 是（仅首次） |
| `ingest` | 快照并索引来源 | 是 |
| `segments` | 查原文定位 | 否 |
| `claim` | 登记论断/假设/竞争解释 | 是 |
| `cite` | 逐字引文绑定论断 | 是 |
| `review` | 记录人工复核决定 | 是（人工授权后） |
| `audit` | 完整性与未决问题检查（`--strict` 可做门禁） | 否 |
| `export` | 导出证据矩阵（md/json） | 是（写到指定路径） |
| `check-draft` | 检查初稿 `[C0001]` 标注覆盖 | 否 |
| `progress` | 研究主线状态与待办 | 是 |
| `redact` | 生成脱敏副本 | 是（写到指定路径） |
| `workspace-init` / `env-check` | 建目录与配置 / 只读检查 | 是 / 否 |

完整参数：`python3 "$SKILL_ROOT/scripts/mpa_evidence.py" --help`。设计说明见 [本地证据工作台](evidence-workbench.md)，安装与兼容性见 [安装指南](install-and-compatibility.md)。
