# Evidence Protocol: claims, observations and provenance

Applies to substantive case research and case-based fieldwork. Complements the existing MPA research contract and data-before-writing rule. Use a Markdown matrix by default; machine-readable JSON is optional only when persistence, automated checks or subsequent reuse are needed.

## Workflow

1. Register a *question* (Q01) and candidate explanation (H01/H02). A hypothesis is not a fact.
2. For each claim, specify an observable implication and a possible disconfirming observation before browsing, interviewing or coding.
3. Identify possible sources: policy text, administrative process records, meeting minutes, decisions, contracts, investment/participation logs, citizen testimony, organization interviews, quantitative outcomes.
4. Plan coverage across affected actor groups and event stages. Document important groups inaccessible to the researcher and missing negative cases.
5. Record obtained materials without inventing access, pages, timestamps or participant identities. Assign stable E001-style IDs only to actual evidence items; planned sources remain collection tasks, not evidence.
6. Validate source identity, provenance, timestamp, precision of locator, authorization and relevant context. Where possible corroborate independently; repeat claims from the same underlying record do not count as independent sources.
7. Link evidence IDs to claims and timeline events. Mark contradictions and unresolved alternative explanations; never silently pick one of conflicting accounts.
8. Before conclusions, audit every material claim for evidence status and inference strength; only use the supported degree of language.

## Evidence register (minimum)

| Evidence ID | Claim / hypothesis | Actor | Evidence type | Source identity | Locator | Date | Status | Supports / challenges | Access / sensitivity |
|---|---|---|---|---|---|---|---|---|---|
| E001 | H01 | organization A | meeting minutes | verified document identity | page/section | known or unknown | unverified | supports H01, preliminary | restricted |

The example is a schema illustration, **not a claim that E001 or the meeting minutes exist**. Never use this illustrative row as real case evidence.

Required status vocabulary:
- **verified**: source identity and claim-to-locator match checked; indicates verified provenance, *not proof that the interpretation is true*.
- **unverified**: material supplied but identity, context, translation, authenticity, or locator not yet checked.
- **disputed**: credible records or testimonies conflict; preserve both and describe divergence.
- **missing**: necessary evidence not obtained. This is a gap record, not an E-ID pretending to be a source.
- **inaccessible**: source exists or is reported, but legal/access restrictions prevent inspection. Never imply reading it.
- **not_applicable**: an item intentionally excluded with an explicit scope reason.

Keep facts, direct quotations, interpretations and recommendations distinct. Record if a source is an official perspective, stakeholder self-report, third-party assessment or independent observation. A source supports only what it contains. Quality of an interview depends on sampling, questioning, positionality and corroboration; do not mechanically score all evidence types on one universal numeric scale.

## Optional portable JSON representation

~~~json
{
  "question_id": "Q01",
  "hypothesis_id": "H01",
  "evidence_id": "E001",
  "actor": "organization A",
  "claim": "Illustrative claim only",
  "observable_implication": "What a real source must show",
  "source_id": "example-only",
  "locator": null,
  "observed_at": null,
  "status": "unverified",
  "supports": ["H01"],
  "challenges": [],
  "access": "restricted"
}
~~~

The JSON block is a schema illustration, not an actual research record. IDs are unique within each project; never overwrite a source silently. Preserve source versions and extraction decisions. Do not elevate a status to verified without re-reading the actual source. Null means unknown; do not create fictitious dates or line numbers.

## Privacy and research ethics

Do not commit interviews, raw transcripts, identifiable student or citizen records, consent forms, confidential administrative datasets or private contact details into a public repository. Keep sensitive originals outside public projects, with restricted access and pseudonymized study IDs. Do not re-identify or merge data beyond permission; check local ethics review and institutional rules before collecting. Zotero/Obsidian integration uses only existing, verified and authorized interfaces. Public output may include aggregate/de-identified findings only when disclosure risk is acceptably managed.

## Acceptance

A claim is publishable as fact only if the source and exact locator substantiate its descriptive scope; mechanism and causal conclusions require additional design and rival-explanation scrutiny. If proof is inadequate, explicitly say so. Deliver collection instructions and decision-relevant uncertainty rather than unsupported findings.