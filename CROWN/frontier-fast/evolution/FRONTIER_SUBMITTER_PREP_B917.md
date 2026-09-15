# FRONTIER FAST SUBMITTER LEAF — B917 NO-SECRET PREP

Parent PDSA: `b91706cc-6b96-4b63-aaff-a8a548b83080`  
State: `READY_NO_SECRET / NO_EXTERNAL_SUBMIT / CROWN_WON=false`

This is a narrow **leaf**, not a scheduler, semantic owner, evaluator, or mutation worker. It is designed so proposal/evaluation workers never receive `GAINZ_TOKEN`.

## Upstream contract readback

Current `metaspartan/frontier-fast/AGENTS.md` says:
- sign in on frontier.fast with GitHub and mint a durable agent token;
- token is submit-only scope and must never be committed;
- clone/setup can be done without exposing the token;
- llama.cpp candidate patches live under `Sources/patches/<track-id>/`;
- `displayName` must describe the change;
- max 3 submissions in flight per account;
- official ranked verification is separate from local iteration;
- status can be read from the authenticated submissions endpoint.

The upstream CLI loop is:

```bash
curl -fsSL https://frontier.fast/install.sh | sh
frontierfast login <token>                         # HUMAN/SECRET BOUNDARY
frontierfast clone --track <track-id>
cd frontier-fast
frontierfast setup
frontierfast run --local-iterate
frontierfast submit --name "<change summary>" --agent "<agent>" --notes-file notes.md --pr <public-pr-url>
frontierfast status
```

Equivalent submission from a clone is documented upstream as `GAINZ_TOKEN=<token> bun run Sources/cli.ts submit ...`.

## Isolation contract

1. Candidate/mutation/evaluator hosts receive **zero** Frontier submit credentials.
2. Submitter receives only a verifier-approved immutable candidate reference:
   - track ID;
   - public fork + exact commit SHA;
   - PR URL;
   - patch SHA256 / candidate artifact hashes;
   - independent verifier receipt;
   - display name and notes artifact hashes.
3. Submitter re-fetches the exact public commit and verifies all supplied hashes.
4. Submitter re-reads live track contract, leaderboard and queue immediately before any submit.
5. If live contract/allowlist/gates changed, return `HOLD_CONTRACT_DRIFT` rather than rewriting candidate bytes.
6. If queue/in-flight account cap blocks admission, return typed backpressure rather than retry spam.
7. The first irreversible external submit remains a Tao authority boundary until explicitly widened.
8. Token never appears in stdout, GitHub issue/comment, artifact, candidate prompt or evaluator environment.

## Dry-run acceptance — no token required

A shard may complete these now:
- fetch upstream repo + exact candidate commit;
- verify candidate path lies within track allowlist;
- verify patch applies/build/static gate;
- verify `notes.md` exists and contains measured evidence, not a narrative-only speed claim;
- verify display name describes the lever;
- fetch unauthenticated `/api/tracks`, `/api/leaderboard`, `/api/findings`, `/api/queue` with an explicit benign User-Agent;
- emit `SUBMIT_PACKET_READY_NO_SECRET` plus hashes.

It must **not** simulate success for the authenticated submit/status endpoints.

## Human/Tao batch

Only after independent candidate verification:
1. GitHub sign-in / account action if not already complete.
2. Current terms acceptance if presented.
3. Fork under the intended public identity if not already present.
4. Mint submit-only token and install it in the isolated private submitter secret store.
5. Approve the first irreversible submit.

After submission, the machine resumes automatically: status polling -> trusted-runner verdict -> public leaderboard readback -> ConsumerAck. `CROWN_WON=true` is forbidden before that final public readback.

`RESULT=SUBMITTER_CONTRACT_READY__SECRET_NOT_ADMITTED__NO_SUBMIT`
`CROWN_WON=false`
