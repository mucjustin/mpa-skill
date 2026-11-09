# Execution handbook repair — 2026-11-09

Candidate `b532af8` was frozen with the [protocol](execution-repair-protocol.md) before model sampling. Two fresh independent model-agent contexts received the Skill path and only their own synthetic request. No rubric, previous answer or parent conversation history was provided; no Skill edits occurred between samples.

| Case | Result | Observed behavior |
|---|---|---|
| [temporal-prediction](temporal-prediction-answer.md) | PASS | Rejected all-five-year preprocessing for held-out prediction, froze transformations and clustering from training years, preserved cross-time comparability checks, and reported no invented performance or causal results. |
| [current-office-contract](current-office-answer.md) | PASS | Stopped at STATE_UNKNOWN, avoided replay while inspection was unavailable, used current revision and returned fields, and did not invent the unspecified edits payload or historical commands. |

**2/2 synthetic development cases passed**, one response per case. This does not estimate reliability or establish actual statistical or Office-tool performance. The child-agent interface exposes final answers rather than an independently auditable file-open trace or machine-readable child model identifier. Complete answers are linked above; no no-Skill control was run.

The handbook now makes preprocessing depend on the evaluation design, uses current tool contracts, and distinguishes descending positional editing from safe replay. The knowledge map also explicitly requires original or current official sources before using its theory/context summaries as evidence.

Local Python 3.12: 55 project tests, generic Skill source/ZIP validation, release metadata and diff checks passed. The prior macOS/Python 3.13 queue resolved successfully without configuration changes; all six jobs of run `42664312889` passed before this follow-up. The final follow-up commit requires its own CI run.
