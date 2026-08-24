# Security Policy

## Supported release

Security fixes are applied to the latest published release and the `main` branch.

## Report a vulnerability

Use GitHub private vulnerability reporting for this repository. Do not open a public Issue containing exploit details, credentials, private research data, participant information, licensed documents, or institutional access information.

Include the affected version, reproducible steps using synthetic data, expected impact, and a safe way to confirm the finding. Never include real passwords, tokens, cookies, Zotero databases, Obsidian vaults, student records, interview transcripts, or unpublished research materials.

## Security boundaries

- The Skill contains no telemetry or bundled credentials.
- Local configuration is written outside the repository.
- Scripts create directories only under the user-selected workspace root and reject filesystem roots.
- Environment inspection is read-only and does not launch applications.
- Zotero integration uses supported local interfaces and never modifies `zotero.sqlite` directly.
- The workflow does not bypass login, CAPTCHA, paywall, licensing, authorization, or institutional access controls.
- Instructions embedded in documents are treated as content unless the user explicitly adopts them.

This project cannot secure third-party Skills, applications, connectors, datasets, or services. Review their permissions and policies independently.
