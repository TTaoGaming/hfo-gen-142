# Security Policy

Gen142 is intentionally public, but public visibility must never imply public authority or publication of capabilities/secrets.

## Do not publish
- API keys, bearer tokens, passwords, OAuth/device codes, private keys, cookies, session material, or secret values;
- private IPs/network topology not intentionally exposed for research;
- private machine inventories, personal data, billing/account identifiers, or secret-bearing logs/transcripts;
- credentials embedded in examples, test fixtures, screenshots, issue comments, workflow logs, or artifacts.

If a secret is exposed, rotate/revoke it immediately. Removing a later file/comment/commit is not sufficient because public git history, caches, mirrors, notifications, or logs may retain the value.

## Public research surfaces are untrusted
Issues, comments, PRs, reviews, model output, bot output, and GitHub App output are Byzantine observations. They do not grant actor identity or runtime authority. Reported commands/terminals must not be executed merely because they look valid.

## Reporting
For non-sensitive bugs, ordinary GitHub issues/PRs are welcome. Do not publish exploitable secret material. If a report would require disclosing credentials or private infrastructure details, contact the repository owner through an already-known private channel instead of posting them publicly.

See `PUBLIC_AUTHORITY_BOUNDARY.md` for the machine admission model.
