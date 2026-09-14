# Gen142 World State — latest

Observed: 2026-09-14T11:32Z. Partial current projection; claims are scope-bounded.

## Recovery surfaces
- Public repo: `TTaoGaming/hfo-gen-142`
- Recovery/evidence coordination: issue #1
- Durable Roach/Burrow fan-in and G1/G2 evidence: issue #2
- Hive integration/reduction: issue #3 and `HIVE_R0.md`
- Slow identity: `GENE_SEED.md`

## Infrastructure
- GitHub: LIVE for repository evidence, workflows, issues and current carrier mutations.
- Cloudflare G1 durability/idempotency: SCOPED_PASS. One deterministic no-effect work survived caller replacement and Worker redeploy; duplicate effect replay admitted exactly one effect. This is not 24/7 Evo proof.
- Oracle VPS: LIVE. Desktop Commander ping/process path is live; host `thrud-a1-free-20260830`, ARM64. Existing self-hosted Actions runner `hfo-gen140-oracle-r1` executed a bounded no-effect GEN142 contract-read assay successfully via GEN140 donor workflow run `34838622253`.
- GEN142 Oracle Actions dispatch: HOLD_REGISTRATION_BOUNDARY. `.github/workflows/oracle-cell-r0.yml` exists, but GEN142 runs `34838663934` and `34838690159` remain queued because no eligible self-hosted runner is attached to this repository.
- OVH VPS: DEGRADED. Registered and pingable, but process execution has intermittently returned `Not connected`; do not use as primary cell until stabilized/re-assayed.
- Lenovo: NOT_REQUIRED for the positive Oracle substrate assay; do not treat it as a trusted hot-state dependency.
- Legacy Sigrun/Kimi actor path: QUARANTINED pending replacement; prior work remained `WAITING_WORKER` with repeated recovery/alarm cycling and no terminal result.
- WorldWeaver custom domain: agent access remains BROKEN_OR_ENVIRONMENTALLY_UNREACHABLE; raw GitHub mirror is the recovery fallback.

## Current runtime contract
`WORKLOAD != CAPACITY != CARRIER != ACTOR != PHENOTYPE != SKILL != TOOL != AUTHORITY != EVIDENCE`.

Minimal intended hot path: `Cloudflare Agent/DO -> AgentWorkflow -> admitted VPS work cell -> reducer/ConsumerAck`; GitHub is institutional evidence/recovery, not concurrent hot state after Cloudflare promotion.

## Gate status
- G1 Cloudflare durability/idempotency: SCOPED_PASS.
- G2 admitted/default-path VPS execution with Lenovo unavailable: HOLD. Oracle work-cell substrate itself is PASS; missing GEN142 runner attachment/registration is now the exact blocking boundary.
- G3 two-generation COTS evolution cell with frozen evaluator, runtime/dependency fingerprint, bounded disk, durable lineage, restart/resume, zero duplicate accepted effects, zero Tao routing: HOLD until G2 drains.

## Next edges
1. Register/attach one dedicated Oracle self-hosted runner to `TTaoGaming/hfo-gen-142` (default `self-hosted,Linux,ARM64` labels are enough for first drain).
2. Let existing queued `GEN142 Oracle Cell R0` drain and independently read back the Oracle/aarch64 receipt.
3. If PASS, promote G2 only within that scope and immediately run one bounded G3 evolution cell on Oracle.
4. Stabilize/re-assay OVH, then use it as verifier/challenger rather than duplicating the Oracle phenotype.
5. Scale Burrows/cells only after measured evaluator/information gain; do not revive the old multi-lane Kimi colony by default.

Operator/admin action currently required: authorize/provide one GEN142 self-hosted runner registration path. No Tao routing is required after that runner is attached.