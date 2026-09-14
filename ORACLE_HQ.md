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
5. **ALLOCATE** — run the versioned deterministic reconciler policy over the canonical snapshot. Prefer Oracle for stable/lightweight work, Cloudflare for durable actor/workflow work, OVH for elastic/heavy/verifier work, laptop only for explicit UI/human-session work.
6. **EXECUTE** — launch exactly the bounded action selected by the reconciler through native/COTS owners; no custom HFO scheduler when GitHub Actions/Cloudflare Workflow suffice.
7. **VERIFY** — deterministic evaluator or independent verifier; model self-grading never promotes a result.
8. **CONSUMER_ACK** — durable downstream use/reject receipt for accepted knowledge/results.
9. **RELEASE** — carrier exits; durable work remains recoverable from Cloudflare/GitHub.
10. **LOOP** — a native wake reconstructs a fresh snapshot and runs the same versioned reconciliation policy. The next episode never depends on chat memory or Tao remembering to restart it.

## Zerg projection

- `LARVA` = uncommitted carrier capacity.
- `HATCHERY` = native launch/admission mechanism (GitHub Actions / Cloudflare Workflow / admitted VPS executor).
- `QUEEN` = **versioned deterministic reconciliation/allocation policy**. It is not a neural agent, personality, fallback brain, scheduler, queue, durable state owner, or authority owner. Current R0 contract: `DETERMINISTIC_RECONCILER_CONTRACT.md`; pure reference kernel: `tools/reconcile_kernel.py`.
- `OVERLORD` = current-state/liveness projection; no effect authority.
- `BURROW` = durable responsibility/state slot, normally Cloudflare-backed when admitted.
- `ROACH` = recoverable work lineage; carriers are disposable.
- `EVOLUTION_CHAMBER` = COTS search/evolution workload on Oracle/OVH/Cloudflare compute.
- `HIVE` = the composed control loop, not one giant agent.

`QUEEN_POLICY != SIGRUN_ACTOR != HATCHERY != WORKER != AUTHORITY`.

Queen evolution is policy evolution, not self-modifying authority:
`TRACE_CORPUS -> MUTATE_POLICY -> DETERMINISTIC_REPLAY -> FAILURE_INJECTION -> CANARY -> SOAK -> PROMOTE_VERSION`.
Every live transition receipt must bind the policy version + snapshot hash + plan hash. Candidate policies may change ranking/routing/retry/search strategy inside existing authority, but cannot create a second queue/state owner or widen effect ceilings.

## Looping-agent law

Every agent loop is a sequence of bounded episodes, not an immortal thread:

`work_id + carrier_uuid + skill + envelope_hash + target_binding + effect_ceiling -> result_id -> verifier -> ConsumerAck -> next work_id`

A carrier may die at any point without losing accepted state. Retryable or at-least-once work must use stable identities and idempotent accepted effects.

## No-fallback-human law

A missing deterministic transition is controller debt, not an invitation to escalate orchestration to Tao or to make Sigrun a universal fallback brain.

Tao may provide intent, policy, budget and true authority unlocks. A human unlock must already have an armed machine resume watcher. Routine observe/select/allocate/dispatch/poll/retry/fan-in/release/continue work belongs to the reconciler plus existing native owners.

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
6. daily canaries show continuity and correctly detect at least one controlled restart/reboot event;
7. one scheduled reconciliation wake assembles authoritative state, runs a pinned policy version, executes exactly one selected transition, persists controller/API-observed receipt, and the following wake continues without Tao;
8. at least two consecutive mission transitions complete with `tao_hot_loop_actions=0` and no neural agent choosing control flow.

Until then: `HQ_DESIGN_ADOPTED__RUNTIME_PARTIAL`.