# 内置证据工作台操作指南（Skill Portable CLI）

This reference is part of the **installed Skill**. Call the bundled tool only when an actual local terminal, Python 3.10+ and user-authorized source/workspace filesystem access are available.

## 入口和预检（读取不修改）

The Skill root is the directory containing this Skill's SKILL.md. Never presume an installed path or depend on the original Git repository. The absolute entrypoint is:

- macOS/Linux: python3 "<skill-root>/scripts/mpa_evidence.py" doctor
- Windows: python "<skill-root>\scripts\mpa_evidence.py" doctor
- Optional existing project check: append --workspace "<workspace>".

Do not use a guessed globally installed `mpa-evidence` command. The TXT/MD/CSV/DOCX pipeline runs with Python's standard library without pip. PDF requires independently approved `pypdf` installation, reported by doctor as pdf_text_available. No automatic pip, network requests, OCR or bypassing encrypted files.

If doctor reports unsupported Python, required format dependency missing, inaccessible local files, or no terminal, STOP the local operation and deliver a bounded evidence collection plan instead. Never claim a file was processed, a document verified, or an output saved without reading the CLI response.

## Authorized source-to-evidence workflow

1. Explain that import saves a **second copy** of the supplied document and parsed full-text segments in the chosen local research workspace under `.mpa-evidence/`. Neither is encrypted. Do not import confidential, identifiable or restricted personal records without approval/appropriate safeguards. Confirm intended workspace and persistence permission before first `init`/`ingest`. Do not write inside the installed Skill directory or any public repository.
2. `python "<skill-root>/scripts/mpa_evidence.py" init "<workspace>"` (only with authorization).
3. `python "<skill-root>/scripts/mpa_evidence.py" ingest "<workspace>" "<source-file>"`. Check returned D-ID and SHA-256 snapshot; avoid inventing page/paragraph IDs. 
4. `python "<skill-root>/scripts/mpa_evidence.py" segments "<workspace>" "<D-ID>" --search "<term>"`, then use `--locator "L2"` / `"p.3"` / `"para.12"` / `"fn.1"` (DOCX footnote) / `"en.2"` (endnote) / `"row.5"` to inspect the exact untruncated segment before asserting a quotation exists.
5. `python "<skill-root>/scripts/mpa_evidence.py" claim "<workspace>" --question "<question>" --statement "<statement>" --kind inference` (other kinds: fact, causal, recommendation). Register a competing explanation with `--rival-of C0001`; audit warns `no_rival_explanation` for causal claims without a rival and `rival_untested` for a rival without evidence.
6. `python "<skill-root>/scripts/mpa_evidence.py" cite "<workspace>" --claim C0001 --document "<D-ID>" --locator "L2" --quote "<exact text>" --relation supports`. Use `--relation challenges` for conflicting accounts; preserve them as contradictions. Newly linked records are **always unverified**.
   - A quote spanning lines/pages uses a range such as `--locator "L2-L4"` (same locator type, at most 20 segments; segments are joined by newlines).
   - PDF extraction often inserts spaces or line breaks inside Chinese sentences. If cite reports that the quote matches only after ignoring whitespace/full-width differences, show the user the stored segment and, with their agreement, rerun with `--normalized`. The registry then stores the **verbatim source span**, records `match_mode: normalized`, and audit asks for a context check. Never use `--normalized` to paraphrase.
7. **Human-only verification gate**: show the user the original source identity, locator and quotation. Only after the researcher explicitly reports completing the check and instructs a specific review action may the agent run `review "<workspace>" E0001 --status verified --reviewer "<user-provided-label>"` (or `disputed`/`rejected` with a reason). The agent must not self-approve any evidence, infer user verification, invent reviewer names, or auto-run review in a batch.
8. `python "<skill-root>/scripts/mpa_evidence.py" audit "<workspace>" --json` then `export "<workspace>" --format md --output "<destination>"`. Default exports omit original quotations; `--include-quotes` may disclose confidential data and needs explicit authorization. Existing outputs are not overwritten without `--overwrite`.

## Research support commands

- `progress "<workspace>"` shows MPA Research Spine status, open tasks and `suggested_next`; update with `--set evidence=partial` (statuses: missing, partial, established, out_of_scope), `--todo "<task>"`, `--next T0001`, `--done T0001`. Start each short session by reading progress; end it by recording status and the next task.
- `check-draft "<workspace>" "<draft.md|.txt|.docx>"` maps `[C0001]` / `【C0001】` tags in the student's draft to claim and evidence status, and flags untagged causal wording and overclaiming. It exits 2 when a tag names an unknown claim. Explain results; do not rewrite the student's draft unless asked and allowed (see coaching-mode.md).
- `redact "<file.txt|.md|.csv>" --redact-terms "<terms.txt>" --output "<out>"` writes a de-identified copy; `export ... --redact-terms "<terms.txt>"` (or `--redact`) de-identifies registry exports. Automatic patterns (ID card, mobile, landline, email, 公文文号) are a safety net only; names, units and places must be listed by the student. The terms file is sensitive: never print it in chat or commit it.
- `workspace-init "<root>" [--config <path>] [--zotero <path>] [--dry-run]` creates Obsidian/ZoteroAttachments/ResearchData/ResearchProjects folders and a config file, refusing to overwrite an existing config. `env-check [--config <path>]` is read-only.

For exact options call `python "<skill-root>/scripts/mpa_evidence.py" --help`. This tool does not authenticate reviewers, make factual or causal determinations, perform OCR, or guarantee contextual validity. `verified` means the named person asserted an original-source comparison, **not** independently validated research truth. SQLite and source snapshots remain local and unencrypted. Programmatic file hashes and exact quotation matches are necessary but insufficient checks. Never infer a claim is true merely because one or more matching quotations exist.

## Task routing and graceful fallback

- Only need short class answer? Do not start local registry or prompt for elaborate dossier.
- Have no source files? Produce a question→actor→observable implication→collection method plan, with honest missing-evidence labels.
- Source has unsupported format or insufficient permissions? Do not write partial invented data; explain limitation and alternative evidence plan.
- Data present and access approved? Run doctor; import, inspect, cite, optionally request human review; audit before any substantive conclusion.
- Export only what is necessary, keeping [证据] / [推断] / [建议] distinct. Existing source statuses and manually verified decisions must never be silently promoted or rewritten.
