# Gen142 World State — latest

Observed: 2026-09-14T12:02Z. Partial current projection; claims are scope-bounded.

## Recovery surfaces
- Public repo: `TTaoGaming/hfo-gen-142`
- Recovery/evidence coordination: issue #1
- Durable Roach/Burrow fan-in and G1/G2 evidence: issue #2
- Hive integration/reduction: issue #3 and `HIVE_R0.md`
- Slow identity: `GENE_SEED.md`
- Preferred gateway profile: `ORACLE_GATEWAY.md`

## Infrastructure
- GitHub: LIVE for repository evidence, workflows, issues and current carrier mutations.
- Cloudflare G1 durability/idempotency: SCOPED_PASS. One deterministic no-effect work survived caller replacement and Worker redeploy; duplicate effect replay admitted exactly one effect. This is not 24/7 Evo proof.
- Oracle VPS: LIVE and now the **preferred Gen142 gateway/ingress host**. Host `thrud-a1-free-20260830`, ARM64. Live observation at `2026-09-14T12:02:38Z`: uptime `1266197.89s` = 14d 15h 43m; boot `2026-08-30 20:19`; Desktop Commander active+enabled; Tailscale active; both existing GitHub runner services active; ~10 GiB RAM available; 31 GiB root disk free. Rootless Gen142 carrier-envelope preflight/gated-exec on Oracle is proven fail-closed.
- GEN142 Oracle Actions dispatch: HOLD_REGISTRATION_BOUNDARY. `.github/workflows/oracle-cell-r0.yml` exists, but GEN142 runs remain queued because no eligible self-hosted runner is attached to this repository.
- OVH VPS: DEGRADED / ELASTIC_ONLY. Oracle Tailscale reports peer `thrud-vps` online, but direct Desktop Commander process execution is currently disconnected. Treat OVH as replaceable burst/verifier/challenger capacity, not gateway identity.
- Lenovo: OPTIONAL_EDGE_ONLY. It may be on continuously but travel/crash/reset are expected failure modes. Never require it for hot state, routing, recovery or quorum.
- Legacy Sigrun/Kimi actor path: QUARANTINED pending replacement; prior work remained `WAITING_WORKER` with repeated recovery/alarm cycling and no terminal result.
- WorldWeaver custom domain: agent access remains BROKEN_OR_ENVIRONMENTALLY_UNREACHABLE; raw GitHub mirror is the recovery fallback.

## Current runtime contract
`WORKLOAD != CAPACITY != CARRIER != ACTOR != PHENOTYPE != SKILL != TOOL != AUTHORITY != EVIDENCE`.

Placement:
`Cloudflare durable state/workflows + GitHub institutional evidence + Oracle stable gateway/executor + OVH/laptop disposable capacity`.

`GATEWAY_HOST != ACTOR_STATE_OWNER != EVIDENCE_SSOT != DISPOSABLE_WORKER`.

Minimal intended hot path: `GitHub demand/evidence -> Oracle gateway preflight/admission -> Cloudflare Agent/DO + Workflow durable ownership -> admitted Oracle/OVH work cell -> reducer/ConsumerAck -> GitHub receipt`.

## Gate status
- G1 Cloudflare durability/idempotency: SCOPED_PASS.
- Carrier Capability Envelope + executable gateway preflight: PASS on Oracle rootless execution path. Missing/stale/unbound envelopes fail closed before command execution.
- G2 admitted/default-path VPS execution with Lenovo unavailable: HOLD. Oracle substrate itself is PASS; missing dedicated GEN142 runner attachment/reboot-persistent dispatch is the exact blocking boundary.
- G3 two-generation COTS evolution cell with frozen evaluator, runtime/dependency fingerprint, bounded disk, durable lineage, restart/resume, zero duplicate accepted effects, zero Tao routing: HOLD until G2 drains.

## Placement policy
1. Oracle is preferred for gateway, ingress, admission, stable low-cost execution and provider/CLI bridges when workload capability fits.
2. Cloudflare owns hot durable actor/workflow state and recovery semantics; Oracle local disk must not become unique irreplaceable state.
3. OVH is elastic capacity: scale up/down/replace without changing actor identity or coordination contracts.
4. Laptop is opportunistic edge/UI/burst capacity only.
5. Workload-specific placement overrides require evidence in the Carrier Capability Envelope, not provider/model preference or convenience.

## Next edges
1. Register/attach one dedicated reboot-persistent Oracle self-hosted runner to `TTaoGaming/hfo-gen-142`.
2. Let existing queued `GEN142 Oracle Cell R0` drain and independently read back the Oracle/aarch64 receipt.
3. Make `tools/gateway_preflight.py` mandatory on the canonical Oracle executor path; rootless gated-exec is proven, root-owned `hfo-evolution.service` still permits privileged bypass.
4. Assay Oracle gateway recovery across process/service restart or host reboot without Lenovo/Tao.
5. If G2 PASS, immediately run one bounded G3 evolution cell on Oracle.
6. Stabilize/re-assay OVH, then use it as verifier/challenger/overflow rather than duplicating the Oracle phenotype.
7. Scale Burrows/cells only after measured evaluator/information gain; do not revive the old multi-lane Kimi colony by default.

Operator/admin action currently required for full G2: authorize/provide one GEN142 self-hosted runner registration path on Oracle. No Tao routing should be required after that runner is attached.
