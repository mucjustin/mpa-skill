# Real-Data Workflow

Contract for rerunning analysis on a user-supplied dataset and writing results back into an MPA deliverable. Applies whenever a thesis, case, or memo carries quantitative claims that raw data can verify or refute.

## Order of operations

1. Audit data quality and preserve the raw file untouched; record inclusion and exclusion rules with counts.
2. Rerun the analysis before any prose change. Conclusions follow the data, never the reverse.
3. Mark any claim the data cannot support as `AUTHOR_INPUT_NEEDED`; never fabricate numbers, sample sizes, or fit statistics.
4. Rewrite the affected conclusions, then verify every numeric write-back in both directions: new values present, superseded values absent.

## Method discipline

- Know the standardization frame. Z-scores computed per exam session zero each session's mean, so group centroids encode relative position, not absolute progress. Improvement or value-added claims must name the frame that supports them.
- For longitudinal tracking, fit dimensionality reduction and clustering once on all observations (global PCA, global KMeans) and then assign labels. Per-session fitting lets group boundaries drift and breaks tracking.
- Report classifier accuracy together with the majority-class baseline and a confusion-matrix reading; high accuracy on an imbalanced target is not evidence of usable recall.
- State the validation design (split ratio, stratification, seed) next to every reported metric.

## Figure discipline

- Never invent data points. Figures render computed outputs only.
- Dense trajectories: mark the first and last points instead of every point, and add a direction cue.
- Check legend and axis-label overlap before delivery.
- CJK font contract: put a CJK-capable font first in `font.sans-serif` inside the plotting script; do not rely on a global matplotlibrc.

## Write-back discipline

- Keep a single source of truth for every number (analysis output JSON or equivalent) and derive prose and tables from it.
- Replace whole paragraphs or whole table cells; do not patch digits inside sentences.
- Save only after every replacement reports success; re-locate failed items and rerun them.
