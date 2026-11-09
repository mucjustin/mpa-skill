# v2.3.0 evidence-flow candidate — 2026-11-09

Candidate `4a1b296` is based on public `main` at `9bb5869`. The [protocol](v230-evidence-flow-protocol.md) and synthetic fixtures were frozen before sampling. Two fresh model-agent contexts, without parent conversation history, were instructed to load the candidate Skill and only their own fixture materials. They received no rubric or previous answers. No Skill edits occurred between runs.

## Results

| Case | Result | Evidence in the actual answer |
|---|---|---|
| catalog-audit | PASS | Answered directly: “4 条记录、3 篇唯一文献”; identified the duplicate alias and historical snapshot; treated the blank field as unknown and required original passages before factual citation. No execution confirmation or integration offer. |
| method-feasibility | PASS | Explicitly said “标签与正文冲突” and “应识别为定量方法述评”; withheld feasibility because permissions, IDs, measurement comparability, sample and attrition were unknown; identified the author discrepancy and OCR/reading limits, then gave concrete data checks. |

**2/2 development regression cases passed** under the preregistered all-conditions rubric. Complete answers: [catalog](v230-catalog-answer.md), [method](v230-method-answer.md). Only the method answer's absolute local file links were normalized to repository-relative links for publication. These are previously used synthetic cases, one response per case, not a new holdout or a reliability estimate. The child-agent interface exposes final answers but no independent file-open trace or machine-readable child model identifier. The setup required reading the Skill; saved answers do not independently prove which references were loaded. No no-Skill control was run.

## Software checks and remaining compatibility issue

- Mac local environment: Python 3.12.14; `python -m unittest discover -s tests -v`: 54 tests passed, including installed-package portability and the CLI persistence/manual-review gates.
- `tools/check_release.py`: PASS for the retained 2.3.0 release metadata. Changes remain under Unreleased; no new release was published.
- `git diff --check`: PASS.
- The system Skill Creator `quick_validate.py` rejects the existing custom frontmatter keys (`version`, `author`, translated display/description/example fields). Running the validator against both upstream `9bb5869` and this candidate produces the same failure. This pre-existing format compatibility issue remains unresolved; the project test suite is not a substitute for the generic validator.

These runs do not validate real CAJ/OCR extraction, research truth, causal inference, sensitive data handling, or actual Zotero/Obsidian mutations. The CLI and its database format were not modified.
