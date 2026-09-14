# Gen142 Oracle Gateway — stable placement profile

**DESIGN/PLACEMENT PROFILE, NOT CURRENT RUNTIME TRUTH.** Current recovery/runtime truth is issue #13 newest-first; Oracle operational telemetry belongs on issue #8.

Oracle is a preferred candidate for stable low-cost gateway/execution work only when the current Carrier Capability Envelope proves the workload fits and the target is reachable/admitted.

## Ownership
- Cloudflare durable actor/workflow plane owns hot semantic state and recovery semantics where admitted.
- GitHub Gen142 owns institutional intent/evidence/recovery.
- Oracle may provide ingress, preflight, provider/CLI bridges and bounded execution.
- OVH/other VPSes are replaceable overflow/verifier/challenger capacity.
- Laptop is optional UI/human-session/burst capacity.

`GATEWAY_HOST != ACTOR_STATE_OWNER != EVIDENCE_SSOT != DISPOSABLE_WORKER`.

## Placement/failover law
Host preference is advisory. `PREFERRED_TARGET != REACHABLE != ADMITTED != AUTHORIZED`.

Durable work identity/checkpoint/evidence must survive Oracle loss in Cloudflare/GitHub. Oracle local disk must never be the unique irreplaceable state copy. A replacement admitted target may continue without Tao context ferry.

## Currentness gate
Before using Oracle, reacquire current host reachability, runtime/service state, resource headroom, auth/credential boundary and workload-specific target binding from live evidence. Stale or missing evidence -> UNKNOWN/HOLD.

Any promotion such as `GEN142_GATEWAY_LIVE` requires fresh runtime receipts; this file cannot grant it.
