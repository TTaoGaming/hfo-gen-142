# Gen142 World State — latest

Observed: 2026-09-14T13:22Z. Partial current projection; claims are scope-bounded.

## Recovery surfaces
- Public repo: `TTaoGaming/hfo-gen-142`
- Recovery/evidence coordination: issue #1
- Durable Roach/Burrow fan-in and G1/G2 evidence: issue #2
- Hive integration/reduction: issue #3 and `HIVE_R0.md`
- Oracle HQ uptime/canary telemetry: issue #8
- Slow identity: `GENE_SEED.md`
- Headquarters doctrine: `ORACLE_HQ.md`
- Preferred gateway profile: `ORACLE_GATEWAY.md`

## Infrastructure
- GitHub: LIVE for repository evidence, workflows, issues and current carrier mutations.
- Cloudflare G1 durability/idempotency: SCOPED_PASS. One deterministic no-effect work survived caller replacement and Worker redeploy; duplicate effect replay admitted exactly one effect. This is not 24/7 Evo proof.
- Oracle VPS: LIVE and now the **preferred Gen142 headquarters/gateway/ingress host**. Host `thrud-a1-free-20260830`, ARM64. Baseline canary at `2026-09-14T12:13:45Z`: boot `2026-08-30T20:19:20.840949Z`, uptime `1266864.27s` (~14.66d), Desktop Commander active, Tailscale active, both existing GitHub runner services active, ~11.48 GB RAM available, ~33.09 GB disk free. Rootless Gen142 carrier-envelope preflight/gated-exec on Oracle is proven fail-closed.
- Oracle HQ telemetry: LIVE. Baseline is durable in issue #8. External daily observer is scheduled at `00:15 UTC` and records `PASS | REBOOT_OBSERVED | ANDON`. Native `00:05 UTC` runner canary is proposed in protected `TTaoGaming/cdev-control#3` and becomes active only after protected checks/merge.
- GEN142 Oracle Actions dispatch: HOLD_REGISTRATION_BOUNDARY. `.github/workflows/oracle-cell-r0.yml` exists, but GEN142 runs remain queued because no eligible self-hosted runner is attached to this repository.
- OVH VPS: DEGRADED / ELASTIC_ONLY. Oracle Tailscale reports peer `thrud-vps` online, but direct Desktop Commander process execution is currently disconnected. Treat OVH as replaceable burst/verifier/challenger capacity, not headquarters identity.
- Lenovo: OPTIONAL_EDGE_ONLY. It may be on continuously but travel/crash/reset are expected failure modes. Never require it for hot state, routing, recovery or quorum.
- Legacy Sigrun/Kimi actor path: QUARANTINED pending replacement; prior work remained `WAITING_WORKER` with repeated recovery/alarm cycling and no terminal result.
- WorldWeaver custom domain: agent access remains BROKEN_OR_ENVIRONMENTALLY_UNREACHABLE; raw GitHub mirror is the recovery fallback.

## Operator survivability / mobile control
- Current AI control plane: Desktop Commander reaches Lenovo, Oracle and OVH for terminal/files/processes, but exposes no general GUI/screen-control surface.
- Existing human GUI bridge on Lenovo: TeamViewer 15.81.5 service is installed, running and automatic, but current unattended/mobile configuration is not trusted as production-ready.
- Lenovo and Oracle are both on Tailscale. Taildrop Lenovo -> Oracle is proven. Direct Lenovo -> Oracle SSH is not admitted. Enabling Tailscale SSH currently requires privileged host configuration (`sudo tailscale set --ssh` / operator delegation).
- GitHub CLI on Lenovo is authenticated as `TTaoGaming` with `repo`, `workflow`, `read:org`, `gist` scopes. This is useful for local human-authorized credential gates but must not become a hot-state dependency.
- Recommended COTS human control plane for next PDSA: **MeshCentral + Tailscale**. MeshCentral should provide browser-based Lenovo desktop plus terminal/files/device state for Linux nodes; do not install Linux desktop environments on VPSes unless a real GUI workload requires them.
- Keep Tailscale as recovery/private-network substrate and Desktop Commander as ChatGPT machine-execution plane. TeamViewer/RustDesk may remain optional secondary desktop paths, not primary architecture.
- New acceptance criterion: **operator survivability gate** — with only an arbitrary/mobile device and Lenovo unavailable as a routing dependency, Tao can authenticate, inspect critical nodes, reach VPS terminal/files, GUI-control the workstation when required, inspect GitHub/Cloudflare, and recover a failed cell.

## Current runtime contract
`WORKLOAD != CAPACITY != CARRIER != ACTOR != PHENOTYPE != SKILL != TOOL != AUTHORITY != EVIDENCE`.

Placement:
`Cloudflare durable state/workflows + GitHub institutional evidence + Oracle stable HQ/gateway/executor + OVH/laptop disposable capacity`.

`HQ_NODE != GATEWAY_HOST != ACTOR_STATE_OWNER != EVIDENCE_SSOT != DISPOSABLE_WORKER`.

Minimal intended hot path: `GitHub intent/demand/evidence -> Oracle HQ common operating picture + gateway preflight/admission -> Cloudflare Agent/DO + Workflow durable ownership -> admitted Oracle/OVH work cell -> reducer/ConsumerAck -> GitHub receipt`.

## Gate status
- G1 Cloudflare durability/idempotency: SCOPED_PASS.
- Carrier Capability Envelope + executable gateway preflight: PASS on Oracle rootless execution path. Missing/stale/unbound envelopes fail closed before command execution.
- Oracle HQ daily external canary: ARMED at 00:15 UTC with baseline PASS.
- Native Oracle runner canary: PR_READY_HOLD_MERGE at `TTaoGaming/cdev-control#3`.
- G2 admitted/default-path VPS execution with Lenovo unavailable: HOLD. Oracle substrate itself is PASS; missing dedicated GEN142 runner attachment/reboot-persistent dispatch is the exact blocking boundary.
- G3 two-generation COTS evolution cell with frozen evaluator, runtime/dependency fingerprint, bounded disk, durable lineage, restart/resume, zero duplicate accepted effects, zero Tao routing: HOLD until G2 drains.
- Operator survivability / arbitrary-device recovery: HOLD. Terminal automation is strong; unified mobile/browser GUI + fleet recovery path is not yet proven end-to-end.

## Mission-command / Zerg loop
`INTENT -> OBSERVE -> RECOVER_DEMAND -> ADMISSION -> ALLOCATE -> EXECUTE -> VERIFY -> CONSUMER_ACK -> RELEASE -> LOOP`.

Oracle hosts the headquarters/common-operating-picture and allocation surface. Cloudflare owns hot durable actor/workflow state. GitHub owns durable intent/evidence. Carriers are disposable bounded episodes; looping means repeated recoverable episodes, not immortal chats.

## Placement policy
1. Oracle is preferred for headquarters, gateway, ingress, admission, stable low-cost execution and provider/CLI bridges when workload capability fits.
2. Cloudflare owns hot durable actor/workflow state and recovery semantics; Oracle local disk must not become unique irreplaceable state.
3. OVH is elastic capacity: scale up/down/replace without changing actor identity or coordination contracts.
4. Laptop is opportunistic edge/UI/burst capacity only.
5. Workload-specific placement overrides require evidence in the Carrier Capability Envelope, not provider/model preference or convenience.
6. Human GUI/control must not be coupled to one physical laptop. Prefer browser-based COTS fleet management plus Tailscale recovery over bespoke HFO bridges.

## Next PDSA / next edges
1. **Operator-control PDSA:** deploy/assay a minimal MeshCentral control plane using COTS only. Target: mobile/browser -> authenticated control surface -> Lenovo desktop + Oracle terminal/files. Keep it reversible and do not expose public unauthenticated ports.
2. Falsify the MeshCentral choice against RustDesk/Guacamole only on measured criteria: arbitrary-device access, unattended Windows GUI, Linux terminal/files, recovery complexity, MFA/auth, hidden dependencies, and operator minutes.
3. Register/attach one dedicated reboot-persistent Oracle self-hosted runner to `TTaoGaming/hfo-gen-142`; then let existing queued `GEN142 Oracle Cell R0` drain and independently read back Oracle/aarch64 receipt.
4. Merge/activate protected `cdev-control#3` after required checks to get native 00:05 UTC Oracle canaries.
5. Make `tools/gateway_preflight.py` mandatory on the canonical Oracle executor path; rootless gated-exec is proven, root-owned `hfo-evolution.service` still permits privileged bypass.
6. Assay Oracle HQ recovery across process/service restart or host reboot without Lenovo/Tao routing.
7. If G2 PASS, immediately run one bounded G3 evolution cell on Oracle.
8. Stabilize/re-assay OVH, then use it as verifier/challenger/overflow rather than duplicating the Oracle phenotype.
9. Scale Burrows/cells only after measured evaluator/information gain; do not revive the old multi-lane Kimi colony by default.

Operator/admin action currently required for full G2: authorize/provide one GEN142 self-hosted runner registration path on Oracle. No Tao routing should be required after that runner is attached.
