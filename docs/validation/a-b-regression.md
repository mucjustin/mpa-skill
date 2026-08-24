# A/B regression comparison method

## Purpose

Detect behavioral drift between skill versions before release. Two failure modes are checked:

1. **Safety-decision drift**: a version no longer makes the expected safety decision (for example, audit-before-writing or `AUTHOR_INPUT_NEEDED`).
2. **Template focus bias**: a version's answer, guided by its templates, omits a substantive dimension that a less constrained version produces.

## Method

1. Choose identical material and an identical prompt for each scenario: one safety-critical scenario from `tests/fixtures/reliability-scenarios.json`, and one substantive route task (for example, a China-context case analysis).
2. Run each version in an isolated context that loads only that version's `SKILL.md` and the references it directs to be loaded.
3. Single sampled response per condition per scenario.
4. Compare: expected safety decisions present; forbidden decisions absent; substantive answer coverage across supply-side tools, demand-side evaluation, and information-and-accountability mechanisms.

## Known limits

- Single sampled response per condition; sampling randomness can explain wording-level differences.
- The same underlying model executes both conditions; cross-model robustness is untested.
- Manual semantic scoring; conclusions support regression triage, not quality ranking.

## Run record

| Date | Versions compared | Scenarios | Result |
|---|---|---|---|
| 2026-08-24 | v1.0.0 vs v2.0.0 | `abstract-body-numerical-conflict` + China-context case analysis (community elderly canteen policy) | Safety decisions equivalent: both versions paused drafting, marked `AUTHOR_INPUT_NEEDED`, and chose neither conflicting value. v2.0.0's template-guided answer omitted the information-and-accountability dimension that v1.0.0's free-form answer produced; addressed in 2.1.0 by the alternatives coverage check in `templates.md`. |
