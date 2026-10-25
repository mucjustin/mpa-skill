# 本地证据工作台：可运行的最小实现

本工具不是论文代写工具，也不是自动事实核查服务。它是一个离线的、来源可追溯的研究材料索引，服务公共管理案例研究与人工复核。**程序能检查文件字节与引文定位是否一致，不等于证明访谈真实性、观点代表性、因果机制或政策效果。**

## 能力与限制

- Python 3.10+。TXT/Markdown、UTF-8 CSV、DOCX（正文段落）通过标准库解析；PDF 使用可选 pypdf 提取文本。
- 导入时复制原始文件到本地 .mpa-evidence/sources/，记录 SHA-256 和文件版本 ID。文本定位 L1，CSV 为 row.1，DOCX 为 para.1，PDF 为 p.1。
- 重复导入同内容不会生成新记录，修订后重新导入则生成新文档 ID，旧证据不会被静默重写。
- 引用必须逐字存在于定位段落；默认 unverified。研究者运行 review 才能标为 verified、disputed、rejected。人工复核不是证明学术结论正确。
- audit 识别源文件损坏、引文不符、缺少证据、未复核或争议证据，并提示因果结论需要额外方法审查。
- **暂不支持** OCR、加密 PDF、DOCX 真实页码、Excel 工作簿、音视频、来源真实性鉴定、自动因果推断、用户权限验证、云同步和文件加密。
- PDF 定位指物理页序号，可能不同于印刷页码；复杂表格、图片、布局会影响提取。DOCX 仅定位正文段落，文档修订后应使用新的版本 ID。

## 安装与分发

本证据程序内置于 MPA Research Agent，且与 WorkBuddy 交付使用同一份实现。Codex/WorkBuddy 安装步骤请参见 [安装与兼容性指南](install-and-compatibility.md)。未获得持久化资料授权或缺少本地终端时，退化为证据规划。

**本功能已打包进 `skills/mpa-skill/scripts/`**：用户安装单个 `mpa-skill` 后，在具备 Python 3.10+ 与文件/终端权限的环境下，无需额外安装项目即可运行 TXT/MD/CSV/DOCX 证据工作流。请优先阅读安装后 Skill 内置的 `references/evidence-workbench-usage.md`，并从 Skill 实际所在路径运行：

~~~powershell
$skillRoot = Join-Path $HOME '.agents\skills\mpa-skill'
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') doctor
~~~

安装路径仅为示例，应以当前环境中实际安装的 Skill 目录为准。PDF 文本提取是**可选依赖** `pypdf`，仅在用户授权时安装，例如 `python -m pip install 'pypdf>=5,<8'`；无依赖时可处理上述四类文本文件。也可在完整源码仓库执行 `python -m pip install -e '.[pdf]'` 使用兼容的 `python -m evidence_workbench` 命令。Skill 不会自动联网安装依赖。

## 使用示例（占位符，不代表真实资料）

~~~powershell
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') init "C:\MPA-Research"
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') ingest "C:\MPA-Research" "C:\samples\policy.txt"
# 记录返回的 D- 文档编号
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') segments "C:\MPA-Research" "D-实际返回ID" --search "政策"
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') segments "C:\MPA-Research" "D-实际返回ID" --locator L3
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') claim "C:\MPA-Research" --question "政策执行是否存在差异？" --statement "部分组织采用不同执行办法" --kind inference
# 记录返回 C0001，再使用真实定位与原文
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') cite "C:\MPA-Research" --claim C0001 --document "D-实际返回ID" --locator L3 --quote "源文件确实存在的逐字文本" --relation supports
# 仅在人工对照原文后复核
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') review "C:\MPA-Research" E0001 --status verified --reviewer "researcher1" --note "已对照原始材料"
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') audit "C:\MPA-Research" --json
python (Join-Path $skillRoot 'scripts\mpa_evidence.py') export "C:\MPA-Research" --format md --output "C:\MPA-Research\matrix.md"
~~~

上面的编号、定位和引语都是占位符，必须替换为 ingest 和 segments 实际返回的内容。长引语可通过 --quote-file PATH 传入 UTF-8 文件。相反证据用 --relation challenges 留存。导出目标若已存在，需显式 --overwrite；如需连引文导出，额外指定 --include-quotes。

## 研究边界

- 文件 SHA 匹配只证明归档字节未改变，并不说明原始材料真实可信。
- 逐字引用匹配不代表语境完整，也不证明观点正确。
- verified 由研究者手动声明，目前不做身份验证，不能当作第三方学术核证。
- 不同记录可能来自同一来源，不一定构成独立三角互证。
- 事件先后关系与前后对比不能直接证明因果，需要独立研究设计。

## 隐私与测试

本地 .mpa-evidence/ 保存源文件副本、SQLite 数据库和提取的原文。**未加密，也不保证跨用户访问控制**。涉及学生、访谈者、单位内部资料时，必须确认授权并放置于受保护的目录；请勿将该目录提交至公开仓库或公开分享。Git 忽略规则不是数据保密手段，导出前仍需检查主张和其他元数据可能包含的个人信息。

~~~powershell
python -m pip install -e '.[pdf]'
python -m unittest discover -s tests -p 'test_evidence_*.py' -v
~~~

CI 测试只证明软件在合成场景下的行为表现，尚未完成对真实研究质量或使用效率的独立评估。
