# Security Policy

## Supported versions

Security issues are triaged for the latest published release and `main`; feature PRs are experimental until reviewed and merged. This is **not** an encrypted document repository or a verified source-authenticity service.

## Report privately

Use GitHub private vulnerability reporting. Never attach passwords, API tokens, confidential documents, real student data, interviews, personnel/benefit records, access cookies, or private screenshots to a public issue. Reproduce with synthetic materials.

## Actual trust boundaries

- `SKILL.md` and reference files are research instructions, not a privileged executable policy. The agent must still obey the host application's authorization rules.
- The optional Python evidence tool has no built-in telemetry, login system, remote synchronization, credentials, or external API calls.
- `init` and `ingest` create local files only **after authorized execution**; `doctor` is read-only.
- Imported originals and extracted paragraphs are stored under `<workspace>/.mpa-evidence/` in SQLite and local snapshots. **They are not encrypted.** Host/user filesystem permissions and backup choices control access. Avoid syncing that folder to public drives or committing it into a repository.
- `sha256` validates the stored byte snapshot, not the authenticity or fairness of its original source. Exact-text matching is not contextual or causal validation.
- The `verified` flag reflects a user-supplied reviewer declaration, **not** system verification of reviewer identity, source truth or research causation. AI must not self-confirm evidence.
- Automatic dependency installation is prohibited; PDF needs separately approved `pypdf`. No bypassing login, CAPTCHA, paywalls, licensed materials, or institutional controls.
- Exports (even without quotes) may contain personal information inside researcher-entered questions or assertions. Review before sharing.
- ZIP packages are generated only from the Skill folder; no research datasets, local caches or workspaces should enter distributions.

This repository cannot guarantee security of Codex, WorkBuddy or third-party plugins, connectors, or host environments. Verify client permissions and data-handling terms independently.
