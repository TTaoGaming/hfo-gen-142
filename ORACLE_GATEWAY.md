# Gen142 Oracle Gateway Profile

Status: PREFERRED_GATEWAY__RUNTIME_PARTIAL
Observed UTC: 2026-09-14T12:02:38Z

## Placement decision
Oracle VPS `thrud-a1-free-20260830` is the preferred 24/7 Gen142 gateway/ingress node.

Why:
- free/stable capacity intended to remain provisioned;
- live uptime at observation: `1266197.89` seconds = 14d 15h 43m since boot `2026-08-30 20:19`;
- `hfo-desktop-commander.service`: active + enabled;
- Tailscale: active;
- two existing GitHub runner services: active;
- ~11 GiB RAM, ~10 GiB available at observation;
- 31 GiB root disk free at observation;
- direct Gen142 carrier-envelope gateway preflight has passed on Oracle.

## Ownership
Oracle is the preferred **gateway / ingress / admission / stable executor host**. It is not the sole durable source of truth.

- Cloudflare Agent/DO + Workflow: hot durable actor/workflow state, retries, leases/fences.
- GitHub Gen142: institutional coordination, evidence, recovery, canonical contracts.
- Oracle: always-on ingress, gateway preflight, provider/CLI bridges, deterministic executor selection, stable low-cost compute.
- OVH: elastic/disposable compute or verifier/challenger; size/provider may change without changing actor identity.
- Laptop: opportunistic edge/UI/burst carrier only; never required for hot state, routing, recovery, or quorum.

`GATEWAY_HOST != ACTOR_STATE_OWNER != EVIDENCE_SSOT != DISPOSABLE_WORKER`.

## Placement priority
For workloads compatible with Oracle capacity:
1. Oracle gateway/executor.
2. Cloudflare-native execution when the workload belongs inside the durable actor/workflow plane.
3. OVH for burst, x86-specific, heavier, verifier/challenger, or overflow work.
4. Laptop only for UI/human-session work or explicit opportunistic burst.

A workload may override this only with a measured capability/fitness reason in its Carrier Capability Envelope.

## Failover law
Oracle unavailability must not strand durable work. Durable `work_id`, checkpoint, lineage, admission evidence and next edge must already exist in Cloudflare/GitHub. A replacement carrier may resume through another admitted gateway without Tao context ferry.

Do not store unique irreplaceable state only on Oracle local disk.

## Current exact blockers
- Dedicated Gen142 self-hosted GitHub runner is not yet attached to this repository; queued Gen142 Oracle workflow remains the G2 registration boundary.
- Root-owned `hfo-evolution.service` is not yet systemd-gated by `tools/gateway_preflight.py`; rootless Oracle gated execution is proven, privileged bypass remains possible.
- OVH direct Desktop Commander endpoint is currently degraded/offline from this carrier, though Oracle Tailscale reports peer `thrud-vps` online.

## Promotion gate
Call Oracle `GEN142_GATEWAY_LIVE` only when:
1. dedicated Gen142 runner is attached and reboot-persistent;
2. one queued no-effect Oracle workflow drains without Lenovo/Tao routing;
3. gateway preflight is mandatory on the canonical execution path;
4. reboot/restart recovery of gateway service is assayed;
5. a fresh carrier recovers current work from GitHub/Cloudflare and resumes through Oracle with no local-only context.

Until then use `PREFERRED_GATEWAY__RUNTIME_PARTIAL`, not 24/7-autonomy PASS.
