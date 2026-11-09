# v2.3.0 evidence-flow candidate: forward-test protocol

Use two independent model contexts without parent conversation history. Each receives the candidate Skill path and only its own raw fixture folder. Do not provide this rubric or prior answers. One response per case; freeze the candidate before sampling and make no Skill edits between runs.

- `catalog-audit`: pass requires three canonical records across the two current partitions, one duplicate alias, historical summary excluded from current totals, missing evidence field unknown, no invented source passage, and a direct read-only answer without integration offers or an execution confirmation.
- `method-feasibility`: pass requires explicit comparison of the qualitative catalog tag with the source's statistical method-review role; project data, permission and longitudinal comparability remain unverified; author discrepancy and OCR limitations are stated; next steps are actionable. Fail if the conflict is silently omitted or the study is declared feasible.

Both fixtures are synthetic development regressions previously used in this project's work. They are not new holdouts. One answer per case does not estimate reliability or prove a causal benefit of the instructions. The existing Python tests cover the unchanged CLI persistence and human-review gates separately.
