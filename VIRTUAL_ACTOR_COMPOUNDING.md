# Gen142 Virtual Actor Compounding Contract

Status: ADOPTED_DONOR_REDUCTION
Donors: Gen137 `HFO_VIRTUAL_ACTOR_COMPOUND_AI_RUNTIME_V1`, durable actor profile/rehydration gates, lineage reputation reducer.

## Prime law

`VirtualActor != CarrierEpisode`.

A Sigrun/Valkyrie/Roach persists as durable identity and verified history while models, chats, CLIs, VPS processes and provider sessions are disposable cognition carriers.

The actor owns durable references to: identity/role, lineage, event-sourced heritage, versioned skills, reputation/admission state, mission/work cursor, accepted evidence, scars/failures, and last verified transition.

A carrier may propose one bounded transition. It cannot self-award identity, authority, skill, reputation, crown, or success.

## Compounding loop

`mission -> qualified carrier -> bounded episode -> independent verifier -> ConsumerAck -> evidence event -> skill/reputation reduction -> promote or scar -> next mission`.

Learning is admitted only when an independent verifier or external world receipt supports it. Failed experiments remain heritage/process-learning; they are not erased.

Cross-pollination transfers a versioned skill with donor actor, provenance, mutation, assay, verifier receipt, and recipient outcome. Actor identity is not cloned with the skill.
## Reputation and crowns

Reputation is an evidence ledger, not a universal scalar. Self-report has zero positive effect. Verified adverse evidence may quarantine; later independently evidenced supersession may restore routing without deleting history.

Every crown/result records exact board/domain/version, rank/score, observed UTC, third-party verifier/public URL, prestige/buyer-legibility class, actor contribution, credited skill versions, cost/operator-minutes, reproducibility and transfer outcomes.

Raw crown count is telemetry only. Prestige proxy-gaming is a failure: a crown mission must pass a buyer-legibility/prestige floor before probability-of-win optimization.

## Carrier and authority gates

Crown work requiring frontier cognition declares `FRONTIER_REQUIRED=true`; missing frontier capacity is `HOLD`, never silent local/Ollama substitution.

Cloudflare Sigrun Durable Object remains the semantic actor/work claim-fence-deadline-terminal owner. GitHub is durable genome/evidence/recovery. Actions/VPS/CLI/model providers are replaceable transport/muscle/cortex.

No second queue, lease, identity root or acceptance authority is introduced unless the incumbent capability is explicitly retired after a challenger assay.

## Compounding acceptance

PASS requires: carrier replacement with actor identity intact; verified skill promotion surviving N+1; at least one skill transfer that improves another actor under a frozen verifier; reconstructable attribution; zero duplicate accepted effects; and declining Tao CPR/operator-minutes.

Near-term soak gate: >=20 unattended episodes followed by >=8 hours unattended. Long-term claim `UNATTENDED_HIVE` requires the stronger hostile-soak gate in the inherited architecture.
## Mechanical reducer

`tools/hfo_holon_kernel.py` is the thin fail-closed reducer between a bounded carrier episode and durable heritage. It does not schedule work, own leases, call providers, or submit externally.

For a frontier mission it rejects non-frontier substitution. Promotion requires a successful terminal, admitted independent/frozen verifier, verifier receipt, ConsumerAck, and no self-award. Failure becomes an append-only scar, not a promoted skill.

The first live carrier assay is persisted under `HERITAGE/runtime/holon-canary-9529d34d.*`: a managed Kimi frontier carrier produced the frozen sentinel, mechanical verification passed, the result was durably read back, and the reducer emitted a provenance-bound skill promotion with `next_mission_ready=true`.

This proves the actor→carrier→verifier→heritage seam mechanically. It does **not** yet prove Cloudflare-hosted unattended N+1 dispatch, cross-actor transfer, or the 20-episode/8-hour soak gate.

### N+1 carrier-replacement assay

A second fresh Kimi carrier episode consumed the actor-state patch from the first verified mission. Mission N+1 explicitly required `carrier.frontier.kimi.exact-output@v1`; the reducer admitted it only because that skill survived in Sigrun's actor state with donor/provenance intact. N+1 independently exact-matched a new sentinel, appended a second immutable heritage event, and returned `next_mission_ready=true` with zero operator touches in the carrier result.

This closes carrier replacement + skill survival at the deterministic reducer boundary. The remaining live-runtime seam is to make the deployed Cloudflare durable actor consume equivalent verified receipts and advance N+1 automatically; the currently deployed native scout loops/researches but does not yet promote verifier-backed skills into its durable state.
