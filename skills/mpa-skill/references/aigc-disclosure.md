# AI-Use Disclosure Statement

Generate the statement only from tool use that actually happened in this session or that the student attests. The statement discloses AI assistance; it never launders prohibited uses, and the student remains the responsible party. Current programme, university, supervisor, ethics, formatting, and submission instructions override this file; follow the current official notice (以当年通知为准).

## When to generate

| Trigger | Rule |
|---|---|
| thesis, defence, or case-competition deliverable where AI tools were used | draft the disclosure statement when the current institutional notice requires one; do not generate it unrequested |
| AI tools were not used | state that no AI tool was used; do not generate an empty statement |
| the institution provides its own template or portal | fill the institution's template instead of this structure; this file only supplies field discipline |

## Statement fields

| Field | Source of truth | Empty-field rule |
|---|---|---|
| 工具名称 tool name | tools actually invoked this session, named as installed | ask the student; never guess a substitute tool |
| 版本 version | version reported by the tool or the session environment | record `AUTHOR_INPUT_NEEDED` when no version was observed |
| 官方网址 official URL | the vendor's official site, fetched or attested by the student | never invent or reconstruct a URL from memory |
| 使用用途 purpose | the route and phase in which the tool ran | describe the actual route, not a generic purpose |
| 具体环节 phases | research design, literature, data, writing, formatting, or defence phases that actually executed | list only phases that ran |
| 参数设置 parameter settings | prompts, models, and options the student actually set | attested by the student; do not fabricate settings |
| 验证过程 verification process | checks that actually ran: source re-verification, numeric re-run, citation checks, page-anchored audits | never describe a verification that did not run |

## Verification-trace rule

Each verification-process entry must trace to an executed check: re-read source, rerun analysis, verified citation, or page-anchored audit. If the student cannot attest a check, record `AUTHOR_INPUT_NEEDED` instead of prose. A statement with unresolved fields is a draft, not a final deliverable.

## Defence questioning preparation

When the route includes defence, prepare one-line answers per tool use: what the tool did, what the student verified, and where the verification evidence lives. Answers must distinguish attested facts from recollection.

## Boundaries

- The statement describes AI assistance that occurred; it does not authorize uses the current rules prohibit.
- Core arguments, methods, and conclusions remain the student's own work; who uses the tool bears responsibility (谁使用、谁负责).
- Do not sign, submit, or upload the statement on the student's behalf.
