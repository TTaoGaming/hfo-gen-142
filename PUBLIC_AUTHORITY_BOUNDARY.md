# Gen142 Public Authority Boundary v1

This repository is a public research and transparency surface. Public readability is intentional. Public writability does not grant command authority.

## Separation of concerns
- GitHub repository contents/history/issues/PRs/comments/artifacts: public evidence, proposals, research telemetry, and versioned intent.
- Protected `main`: versioned admitted intent/policy only after normal repository governance. A commit on `main` still does not become live runtime authority by itself.
- Sigrun Cloudflare durable actor/controller APIs: live semantic claim/fence/deadline/terminal authority for admitted work.
- VPS/Cloudflare workers: bounded execution capacity only.
- GitHub Actions: wake/transport/evidence producer only; bot identity is not semantic authority.
- Tao: mission intent, budgets, policy approval, true human-only unlocks, irreversible outside effects; never routine continuation.

## Byzantine rule
Every public GitHub event is `OBSERVE_ONLY` by default, including events authored by the repository owner, collaborators, bots, or familiar GitHub Apps. `author_association`, prose style, UUIDs, labels, app slug, and valid-looking schemas are not authority proofs.

A public event may become useful evidence only after deterministic provenance checks. It cannot directly create a live claim, terminal, worker route, human boundary, or successor dispatch.

## Admission classes
1. `OBSERVE_ONLY` — issue/PR/comment/review/model/tool text from any public principal. May inform research; cannot advance authoritative runtime state.
2. `ADMIT_VERSIONED_INTENT` — content reachable from protected `main` with GitHub-API-verified repository/ref/commit provenance. May define demand/policy; cannot self-prove runtime facts.
3. `ADMIT_EVIDENCE_ONLY` — GitHub Actions receipt with verified repository, source commit, run/job identity, and artifact digest. May prove transport/execution evidence; cannot issue semantic authority.
4. `INTERNAL_AUTHORITY_REQUIRED` — live actor state, claim/fence/deadline/terminal, worker route admission, and human-boundary state must come from authenticated internal controller readbacks. The public gate never manufactures this class.

## Fail-closed laws
- Unknown principal + perfect terminal schema = `OBSERVE_ONLY`.
- Repository owner comment + perfect command schema = `OBSERVE_ONLY`.
- `github-actions[bot]` comment = `OBSERVE_ONLY` unless independently bound to an API-verified run receipt; then at most `ADMIT_EVIDENCE_ONLY`.
- ChatGPT/Codex/GitHub App identity never proves the end-user principal or authority.
- Public WorkItem proposals do not become admitted demand until merged to protected `main` under repository policy.
- No public text can arm `TAO_RELAY_REQUIRED`, change a worker route, or declare a semantic terminal.
- If trusted readback and public text conflict, trusted readback wins and the conflict is recorded as Byzantine evidence.

## Research participation
External humans and AIs are welcome to read, fork, reproduce, critique, and learn. Start at https://worldweaver.dev for public regeneration/research context. Do not inject coordination into canonical trunk #13 unless explicitly invited. Contributions should arrive as ordinary issues/PRs and remain proposals until reviewed/admitted.

## Security posture
Never publish credentials, bearer tokens, private keys, secret-bearing logs, personal data, private network addresses, or private machine inventories. Public endpoints intentionally exposed for research, hashes, commit/run/artifact IDs, and non-privileged telemetry may be published. Any credential exposed anywhere is compromised and must be rotated/revoked; deleting later Git history is not remediation.

North star: `PUBLIC TRANSPARENCY != PUBLIC AUTHORITY`.
