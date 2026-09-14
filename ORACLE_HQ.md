# Gen142 Oracle Headquarters — Mission Command

Status: `HQ_DESIGN_ADOPTED__RUNTIME_PARTIAL`

Oracle is the preferred always-on **headquarters / gateway / admission / dispatch node** for Gen142. It is a stable command post, not the swarm's only brain and not the sole durable state owner.

## Mission-command ownership

- **GitHub Gen142** — commander's intent, WorkItems, evidence, contracts, institutional memory, recovery.
- **Cloudflare Agent/DO + Workflow** — hot durable actor/workflow state, leases/fences, retry/resume, durable continuation.
- **Oracle HQ** — common operational picture, carrier admission, target selection, dispatch, liveness sensing, lightweight stable execution.
- **OVH / future VPS fleet** — elastic compute, verifier/challenger, x86/heavier workloads; replaceable without changing swarm identity.
- **Laptop** — optional UI/browser/human-session/burst node; never required for continuity.

`HQ_NODE != DURABLE_ACTOR_STATE != EVIDENCE_SSOT != WORKER_FLEET`.

## Oracle HQ control loop

`INTENT -> OBSERVE -> RECOVER_DEMAND -> ADMISSION -> ALLOCATE -> EXECUTE -> VERIFY -> CONSUMER_ACK -> RELEASE -> LOOP`

1. **INTENT** — recover current mission, priorities and effect ceilings from Gen142 GitHub.
2. **OBSERVE** — read Oracle health, Cloudflare/GitHub currentness and available worker capacities.
3. **RECOVER_DEMAND** — select declared WorkItems; capacity never invents demand.
4. **ADMISSION** — require a fresh Carrier Capability Envelope and `tools/gateway_preflight.py = ADMIT`.
5. **ALLOCATE** — prefer Oracle for stable/lightweight work, Cloudflare for durable actor/workflow work, OVH for elastic/heavy/verifier work, laptop only for explicit UI/human-session work.
6. **EXECUTE** — launch bounded carrier episodes through native/COTS owners; no custom HFO scheduler when GitHub Actions/Cloudflare Workflow suffice.
7. **VERIFY** — deterministic evaluator or independent verifier; model self-grading never promotes a result.
8. **CONSUMER_ACK** — durable downstream use/reject receipt for accepted knowledge/results.
9. **RELEASE** — carrier exits; durable work remains recoverable from Cloudflare/GitHub.
10. **LOOP** — next episode starts from current durable state, never from chat memory alone.

## Zerg projection

- `LARVA` = uncommitted carrier capacity.
- `HATCHERY` = native launch/admission mechanism (GitHub Actions / Cloudflare Workflow / admitted VPS executor).
- `QUEEN` = workload-to-capacity allocation policy hosted/served by HQ; not automatically a durable actor identity.
- `OVERLORD` = current-state/liveness projection; no effect authority.
- `BURROW` = durable responsibility/state slot, normally Cloudflare-backed when admitted.
- `ROACH` = recoverable work lineage; carriers are disposable.
- `EVOLUTION_CHAMBER` = COTS search/evolution workload on Oracle/OVH/Cloudflare compute.
- `HIVE` = the composed control loop, not one giant agent.

## Looping-agent law

Every agent loop is a sequence of bounded episodes, not an immortal thread:

`work_id + carrier_uuid + skill + envelope_hash + target_binding + effect_ceiling -> result_id -> verifier -> ConsumerAck -> next work_id`

A carrier may die at any point without losing accepted state. Retryable or at-least-once work must use stable identities and idempotent accepted effects.

## HQ liveness contract

Daily telemetry is tracked in Gen142 issue #8. Baseline fields:
- observed UTC and boot UTC;
- uptime seconds;
- load, memory and disk headroom;
- Tailscale, Desktop Commander and runner service health;
- reboot detection by boot-UTC change or uptime regression.

Native 00:05 UTC Oracle canary is proposed in protected `TTaoGaming/cdev-control#3`. An external cloud observer runs at 00:15 UTC and records `PASS | REBOOT_OBSERVED | ANDON` in issue #8.

## Promotion gates

Call Oracle `HQ_LIVE` only after:
1. a dedicated Gen142 runner is attached and reboot-persistent;
2. a no-effect Gen142 Oracle workflow executes with no Lenovo/Tao routing;
3. canonical execution requires carrier-envelope preflight;
4. Oracle reboot/restart recovery is assayed;
5. a fresh carrier recovers an interrupted workload from GitHub/Cloudflare through Oracle;
6. daily canaries show continuity and correctly detect at least one controlled restart/reboot event.

Until then: `HQ_DESIGN_ADOPTED__RUNTIME_PARTIAL`.