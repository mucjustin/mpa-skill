# Execution Handbook

何时查阅：涉及数据重分析、本地文档写入、依赖工具选择或工作区配置时读取。Merges data workflow, Office editing, dependency management, and workspace configuration.

## 数据工作流 (Data Workflow)

有原始或项目数据时适用。结论跟数据走，不是数据跟结论走。Preserve raw data untouched; conclusions follow the data, never the reverse.

### 操作顺序

1. 审计数据质量，保留原始文件不动；记录纳入和排除规则及计数。
2. 重跑分析后再动正文。Mark 无法支持的数据声明为 `AUTHOR_INPUT_NEEDED`；不捏造数值、样本量或拟合统计量。
3. 改写受影响的结论，然后双向验证每个数值回写：新值存在、旧值消失 (new value present, old value absent)。

### 方法纪律

- 标准化分数 (standardized scores) 描述参考系内的相对位置 (relative position)。Z 分数按考试场次计算时，每场均值归零，组中心编码相对位置而非绝对进步。增值或改进声明必须指明支撑它的参考系。
- 纵向追踪或预测：先核对跨期变量、转换和类别含义的可比性。分别拟合时需对齐坐标与类别含义；评价集或未来波次参与拟合可能造成数据泄露。预测或留出评价时仅用训练数据拟合标准化、降维和聚类，再应用于评价数据；纯描述性全样本分析须说明用途与参考系，不能据此声称样本外预测有效。
- 分类器准确率须与多数类基线 (majority-class baseline) 和混淆矩阵一并报告；不平衡目标上的高准确率不等于可用召回率。
- 每个报告指标旁标注验证设计（划分比例、分层、随机种子）。

### 图表纪律

- 不发明数据点。图表只渲染计算输出。
- 密集轨迹：标记首末点而非每个点，加方向提示。
- 交付前检查图例和坐标轴标签是否重叠。
- CJK 字体合约：在绘图脚本的 `font.sans-serif` 中先放 CJK 字体；不依赖全局 matplotlibrc。

### 数值回写纪律

- 每个数字保持单一真值源（分析输出 JSON 或等价物），正文和表格从中派生。
- 替换整段或整表单元格；不在句子内部修补数字。
- 所有替换报告成功后才保存；重新定位失败项并重跑。

## 本地 Office 编辑

仅在内容已验收、路线需要本地 Office 变更且相应能力实际可用时加载。

### 能力预检

检查当前可用工具的 schema、实际返回结构与保存目标。记录文档身份和版本。表格、图片和样式操作按当前工具合约选择，不预设命令名、参数格式或返回字段。

### 变更事务

1. 捕获结构或版本快照。
2. 从文档中找到活动锚点并要求唯一匹配 (unique live anchor)。
3. 按绝对位置编辑时，按文档降序 (descending) 应用，避免前面的修改移动后续锚点；稳定标识符编辑遵守当前工具合约。
4. 每批后验证工具实际返回的字段并探测结果内容。

### 调用与中断恢复

使用当前 schema 指定的参数类型、文件定位方式和样式操作；以实际返回、保存文件及内容探测确认变更，不假设通用成功字段。

中断或身份漂移后重开保存目标，核对文档身份和版本，不复用缓存句柄：

1. 探测旧文本与新文本，判断此前写入是否落地。
2. 将状态分类为未应用、已应用、部分应用或 `STATE_UNKNOWN` (not applied, applied, partially applied, STATE_UNKNOWN)。
3. 仅对已知状态用幂等操作恢复。降序编辑本身不能保证重放幂等。
4. 遇 `STATE_UNKNOWN` 立即停止 (stop at STATE_UNKNOWN)，先查明状态，不盲目重放或宣称成功。

### 验收

验证新内容存在、旧内容消失、保存的产物可重开或渲染、目标与返回的版本/更新证据一致。报告计数。

## 内置本地证据工具（随 Skill 分发）

需要在本地处理已获授权的原始案例材料时，读取 [证据工作台操作指南](evidence-workbench-usage.md)。该程序的唯一实现位于 `../scripts/evidence_workbench/`，入口为 `../scripts/mpa_evidence.py`，无需从仓库根目录安装。先运行只读 doctor 检查 Python 和可选 PDF 依赖，不静默安装第三方组件。没有终端或本地文件读写能力时仅输出证据规划，不虚构执行结果。用户须明确授权持久化资料；模型不得代替人工核实或标记 verified。工具只核验快照与原文匹配，不能证明来源真实性、因果机制与研究结论。


## 依赖管理

所有集成为可选项 (all integrations are optional)。编排路线前先检查已安装的 Skills、插件、应用和工具；不从名称推断集成存在。

| 需求 | 已安装时的首选能力 | 优雅降级 |
|---|---|---|
| 文档和 PDF | 已安装的文档/PDF 阅读器和转换器 | 直接读取支持的文件；报告不支持的格式 |
| 文献工作流 | 端到端文献控制器 | 分别使用验证过的检索、合法获取和源卡片能力 |
| 单篇论文阅读 | 论文卡片或全文阅读器 | 提取基于源的结构化阅读笔记 |
| 研究设计 | 学术研究或提案工作流 | 直接应用 MPA 研究契约 |
| 定量或定性数据 | 已安装的分析、表格、笔记本或统计工具 | 审计数据并报告缺失的执行能力 |
| 引用 | 引用和参考文献验证工具 | 使用可用的权威来源验证标识符和字段 |
| Zotero | 支持的本地 API、连接器或链接附件助手 | 准备验证过的用户运行交接；绝不直接编辑数据库 |
| Obsidian | 本地 Markdown 文件系统访问或 Obsidian 集成 | 授权时将可移植 Markdown 写入配置的 Vault |
| Word 或幻灯片 | 已安装的文档或演示文稿工作流 | 交付已验收的 Markdown 和交接规范 |

当首选依赖不可用时，选择保持所需证据和安全边界的最接近已验证能力 (unavailable, use closest verified capability)。若无适当能力，执行前报告缺失依赖 (missing, report before execution)，将已完成的只读分析与被阻塞的集成分开。

## 工作区配置

首次持久写入前解析本地路径。绝不推断示例路径存在。

### 解析顺序

1. 设置了 `MPA_WORKSPACE_CONFIG` 环境变量时读取其命名的 JSON 文件。
2. 否则读取平台默认位置：macOS `~/Library/Application Support/mpa-skill/config.json`；Windows `%APPDATA%\mpa-skill\config.json`；Linux `$XDG_CONFIG_HOME/mpa-skill/config.json`（默认 `~/.config`）。
3. 无有效配置时，经用户确认后运行 `python "<skill-root>/scripts/mpa_evidence.py" workspace-init "<workspace-root>"`（可先加 `--dry-run` 预览），或请用户选择工作区根目录。`env-check` 只读检查配置与 Zotero 连接器。不需要 PowerShell。

必需 JSON 属性：`workspace_root`、`obsidian_vault`、`zotero_executable`、`zotero_attachments`、`research_data`、`research_projects`。配置是本地机器状态，不提交到 Skill 仓库。

### Zotero

绝不直接修改 `zotero.sqlite`。使用支持的本地接口，验证重复和父项决策，优先使用合法的已有附件，验证最终附件路径。仅在用户请求或授权 Zotero 集成后，若受支持的本地接口不可达，自动启动配置的 Zotero 可执行文件 (start Zotero automatically)，等待就绪后继续。仅在自动启动失败 (if launch fails) 时请用户手动启动。

### Obsidian 和文件

每个源保持一个规范源笔记，将派生的课程、案例、提案或论文笔记链接到它。记录源身份、页面证据、访问日期、集成状态、决策、待办和风险。保留原始数据并与清洗数据、代码、表格、图表和报告分离。
