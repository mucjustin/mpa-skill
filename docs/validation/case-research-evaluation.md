# Case Research Engine: evaluation plan (not benchmark results)

This protocol is a proposed evaluation for the new evidence-led case route. It does **not** demonstrate model improvement or claim that any semantic scenarios have been executed.

## Evaluation conditions

Compare (A) no Skill, (B) tagged baseline v2.1.0, (C) candidate branch. Keep model, instructions, data access, input source bundle, prompt, format and scoring rubric constant. Run isolated fresh contexts with at least three replicates per scenario and report sampling variability. Do not expose scenario expected/forbidden decisions to evaluated agents. Include Chinese public-management cases and a holdout set not used to tune the rules.

## What to test

The machine-readable cases at tests/fixtures/case-research-scenarios.json specify expected and forbidden decisions. These are scenarios for a *future semantic model evaluation*; the CI script only checks fixture integrity, routing links, and contract statements.

Assess:
- Research question and lens fit: plausible alternative frames, reasons for selection, no gratuitous conflict.
- Evidence planning: actor/time/source coverage, missing materials made explicit, no fabricated records.
- Claim traceability: material assertions correctly linked to real source and locator.
- Mechanism tests: intermediate sequence supported, credible rival explanations considered, counterevidence surfaced.
- Causal restraint: no pre/post-only causal claim or automatic IV/DID/grounded-theory fit.
- Reusability and task cost: short answers remain short; an expanded research dossier is not forced.

Use human expert double-scoring with a documented adjudication process; include precision (false alarms), not merely recall. Report qualitative misses and safety regressions with examples. Never report structural contract-test passes as proof of actual agent research quality.

## Release criteria

All existing CI tests pass; new structural tests pass; semantic benchmark shows no high-severity fabricated evidence, silent contradiction resolution, or unjustified causal inference on holdout scenarios. Gate any claims of improvement on actual results, rather than an invented percentage.