# AI-Use Disclosure Statement

Generate the statement only from tool use that actually happened in this session or that the student attests. The student remains the responsible party (谁使用、谁负责). Current programme, university, supervisor, ethics, formatting, and submission instructions override this file.

## When to generate

| Trigger | Rule |
|---|---|
| thesis, defence, or case-competition deliverable where AI tools were used | draft when the current institutional notice requires one; do not generate unrequested |
| AI tools were not used | state that no AI tool was used; do not generate an empty statement |
| institution provides its own template or portal | fill the institution's template instead of this structure |

## Statement fields

| Field | Source of truth | Empty-field rule |
|---|---|---|
| 工具名称 tool name | tools actually invoked this session | ask the student; never guess a substitute |
| 版本 version | version reported by the tool or session environment | `AUTHOR_INPUT_NEEDED` when no version observed |
| 官方网址 official URL | vendor's official site, fetched or attested by student | never invent or reconstruct a URL |
| 使用用途 purpose | the route and phase in which the tool ran | describe the actual route |
| 具体环节 phases | phases that actually executed | list only phases that ran |
| 参数设置 parameter settings | prompts, models, options the student actually set | attested by student; do not fabricate |
| 验证过程 verification process | checks that actually ran: source re-verification, numeric re-run, citation checks, page-anchored audits | never describe a verification that did not run |

## Verification-trace rule

Each verification-process entry must trace to an executed check. If the student cannot attest a check, record `AUTHOR_INPUT_NEEDED`. A statement with unresolved fields is a draft, not a final deliverable.

## Defence preparation

When the route includes defence, prepare one-line answers per tool use: what the tool did, what the student verified, where the verification evidence lives. Distinguish attested facts from recollection.

## Boundaries

- The statement describes AI assistance that occurred; it does not authorize prohibited uses.
- Core arguments, methods, and conclusions remain the student's own work.
- Do not sign, submit, or upload the statement on the student's behalf.
