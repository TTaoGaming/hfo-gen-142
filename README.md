# HFO Gen 142 — BYZANTINE-AWARE SWARM

**Primary design law:** assume any agent, tool, carrier, memory, receipt, or coordinator may be stale, wrong, duplicated, incomplete, self-interested, or compromised by accident. Trust must be earned by independent evidence and bounded authority.

Gen142 exists to stop operator harm from unreliable swarm behavior. The system must reduce Tao's workload rather than create more routing, cleanup, reconciliation, context-ferry, or repeated explanation.

## Non-negotiable invariants

1. **No agent is trusted by default.** Claims are proposals until independently verified.
2. **No self-verification.** Producer, evaluator, admission authority, and promotion authority must not collapse into one principal for material claims.
3. **No unbounded authority.** Every worker gets the minimum capability, time, spend, filesystem, and effect ceiling required.
4. **No unbounded writes.** Disk, cache, artifact, log, branch, issue, process, and retry growth must have quotas and deterministic cleanup.
5. **No operator CPR.** Tao is not the scheduler, context courier, collision resolver, retry loop, janitor, or memory bus.
6. **No chat-memory dependency.** Durable state belongs in explicit recoverable artifacts with provenance; a fresh carrier must be able to resume without Tao retelling history.
7. **No recommendation before falsification.** Important plans and claimed wins require an adversarial pass.
8. **No silent UNKNOWN→TRUE promotion.** Missing evidence stays UNKNOWN.
9. **No custom infrastructure when COTS already owns the job.** Thin adapters only unless a concrete native-gap receipt exists.
10. **No scale before one closed loop works.** One bounded cell must survive restart and close repeated generations before fan-out.

## Immediate Gen142 acceptance test

A single autonomous competition/evolution cell must run **two consecutive generations** with:

- laptop not required for hot state;
- frozen evaluator and explicit fitness;
- bounded disk growth;
- duplicate material effects = 0;
- independent verification/falsification;
- durable lineage and recovery receipt;
- Tao routing/context-ferry/cleanup actions = 0 after mission admission.

Until that passes, the correct swarm size is **one**.

Scoped evidence, 2026-09-14: the [work-cell projection](WORK_CELL.md) completed
two admitted numerical recipes through Shinka, recovered one killed caller using
systemd, and obtained separate Cloudflare geometry checks plus native Workflow
acceptance in 29.01 seconds. [Exact receipt](hatchery/shinka-cell/WORK_CELL_R1.json).
This used zero model calls and found no champion. The live Kimi attempt timed
out and remains a retained uncertain reservation. Overnight neural evolution,
general workloads and multi-host concurrency are not established by this assay.

## Recovery posture

Gen140/141 are donor/evidence archives, not templates to copy wholesale. Import only proven components by immutable reference. Secrets, personal data, local machine state, and private operational details do not belong in this public repository.

**North star:** `MISSION -> BOUNDED WORK -> INDEPENDENT EVIDENCE -> REDUCE -> LEARN -> REPEAT`, while making the human operator's burden trend toward zero.
