# GEN142 PARTIAL WORLD STATE

Snapshot UTC: `2026-09-15T19:29:25Z`  
Reducer UUID: `d012a39b-a159-4fd6-b21e-0bdaed568872`  
Recovery order: **this file first**, then `#13` newest-first for deltas.  
Public GitHub is evidence/recovery and is Byzantine by default; it is **not** private execution authority. Cloudflare Sigrun remains semantic owner.  

This file is the stable reducer projection. Older status comments/files are historical evidence, not competing current state.

## Executive state

`OPERATOR_RELIEF=false`  
`CROWN_WON=false`  
`TAO_HOT_LOOP_ACTIONS_TARGET=0`  

The system has proven many individual lifecycle mechanisms. It has **not** proven a useful end-to-end mission that wakes naturally, admits useful demand, dispatches a real neural worker, independently verifies/consumes the result, and continues/quiesces for multiple cycles without Tao. That missing integrated loop is the bottleneck.

## PROVEN

### 1. Sigrun Durable Object can be reached through the trusted Actions path
- Cloudflare semantic owner: `hfo-sigrun-va-r0` at the existing authenticated worker endpoint.
- Oracle Actions can authenticate using the scoped `SVA_ACTIONS_TOKEN`; the token is masked and not exposed to worker carriers.
- Private ForcePackage checkpoint `SIGRUN-TRUNK-CP-20260915-1916` was admitted with `accepted_new=true`, `effect_ceiling=NONE`, and `TAO_HOT_LOOP_ACTIONS=0`.
- A later authenticated readback observed that exact workitem as `TERMINAL`, `terminal_consumed=true`; the private package was then disarmed with `pending_demand_count=0`.
- Evidence: `cdev-control` runs `35012818161` and `35013071185`; final disarm receipt SHA `a47c6065362a83bc6cb19864620954c12bcbeb8959b7d5369f24033c7a57e972`.

### 2. Deterministic reconcile machinery works in a bounded Actions cycle
- Current PR #5 head `b7f79d83c4582ce1c0beccd1ce3fdfa38e21cb39` passed the Oracle controller run `35005241885`.
- Exact source forcing gates passed `8 + 15 + 15`; controller suite passed `43/43`.
- Authenticated reconcile completed cleanly as `NO_ADMITTED_DEMAND / NO_EFFECT` with receipt SHA `ef7204162adb85d2096b9536f37ee617d085aac7d6f09cf0c5d55a614a0e9fbb`.
- This proves observe/reconcile/quiesce on a branch-triggered cycle. It does **not** prove production scheduled autonomy.

### 3. Existing WorkCell lifecycle can close without Tao for scoped workloads
- Public receipts show research WorkCell PASS -> ConsumerAck -> retirement with Tao hot-loop `0` (for example `#13` comments `5685731046` and `5685732455`).
- Terminal consume/replay protection, failure terminalization/quarantine, and deterministic reduction have executable tests/receipts.
- This proves the cell substrate; it does not prove arbitrary useful workload continuation.

### 4. Hatch/wake and public fan-in exist
- Scheduled Cloudflare hatchery births and GitHub fan-in/reduction have occurred without manual launch.
- PR #50 removed Tao from hatchery fan-in/retry pacing and merged the bounded one-slot/5m behavior.
- Public GitHub inputs are explicitly treated as untrusted observations; shared GitHub App identity, UUIDs, or familiar HFO prose do not confer authority.

### 5. Current crown portfolio has real external-fitness artifacts
- Packomania N120/N122/N124 packet is independently verified and send-ready, but still awaits external keeper acceptance.
- ECDSA.fail is the only currently justified new-compute crown lane in the reduced portfolio.
- Frontier Fast has a built/compiled Maple fallback candidate, but no trusted-runner performance receipt; DeepSeek is held on an upstream contract conflict.
- These are candidates/evidence, **not crowns**.

## PARTIAL

### 1. Production scheduled wake/reconcile
`cdev-control#5` contains the intended `7,37 * * * *` Oracle schedule, pinned public forcing-source commit, scoped secrets, private version-bound ForcePackage, authenticated observation/history, replay protection, worker adapter and durable artifacts. It is **open, not merged**. GitHub scheduled workflows only become the production/default-branch lane after promotion; a natural post-merge scheduled wake is still required.

### 2. ForcePackage / voice-to-mission path
- Private version-bound ForcePackage admission has worked for no-effect checkpoints.
- The current private package is deliberately `enabled=false` and emits no demand.
- Public generic ForcePackage compiler PR #55 is still open/unmerged.
- Therefore voice/HQ intent -> useful admitted runtime demand is not yet a production surface.

### 3. Neural worker dispatch
- A bounded Kimi no-tool/no-write worker adapter exists and has tests for credential stripping, exact profile admission, timeout/output ceilings and hash-bound completion.
- Latest authenticated CPR ledger says `worker_dispatch=NOT_DEMANDED` and `worker_execution=UNBOUND_LOCAL_CARRIER`; latest snapshots have `worker_routes=[]`.
- Code exists; live useful carrier execution through the reconciler is not proven.

### 4. Native Cloudflare scout/evolution lanes
- Typed submission/output guards, failure rotation, backpressure and QD/MOME contracts are merged.
- Recent hatchery receipts still contain failed lanes such as `PROPOSER_SUBMISSION_TOOL_COUNT_0` / `FALSIFIER_SUBMISSION_TOOL_COUNT_0`.
- The machinery wakes and fails closed; consistent useful output is not yet proven.

### 5. Recovery/continuity hardening
- Voice failover PR #56, public ForcePackage compiler PR #55, poison WorkItem quarantine PR #42, and structured native-scout reducer PR #48 remain candidates/open.
- Do not speak about them as deployed behavior merely because tests exist.

## BLOCKED

### 1. Operator relief
The acceptance test is not more architecture. It is **two consecutive natural useful cycles** satisfying all of:
1. default-branch scheduled wake occurs without Tao;
2. authenticated observation/reconcile selects admitted useful demand;
3. a real admitted worker executes without controller credentials;
4. independent verifier/result receipt closes;
5. ConsumerAck/retirement occurs;
6. next demand is selected or system quiesces deterministically;
7. `TAO_INTERVENTION_COUNT=0`, duplicate effects `=0`, invented authority `=0`.

Until that passes, `OPERATOR_RELIEF=false` even if individual receipts say `tao_runtime_relay_required=false` on idle/no-effect cycles.

### 2. Promotion boundary for the real scheduler
`cdev-control#5` still requires the repository's independent/last-push approval boundary before merge. **Do not push gratuitous changes to that head**; doing so only resets the approval problem. After merge, wait for and inspect a natural scheduled wake before declaring deployment.

### 3. Useful worker admission
A worker route must be explicitly enabled/admitted and then exercised on a useful bounded workitem. Static tests are insufficient. This is currently the clearest technical seam after scheduler promotion.

### 4. Human-only boundaries remain human
Credentials/account creation, OAuth/2FA/CAPTCHA, payment/new spend, protected permission/merge, changed terms, public identity, and irreversible external submission remain explicit human authority. Human unlock is not runtime CPR.

## UNKNOWN

- Whether the newest native scout revision produces clean useful READY results under live provider conditions after the most recent typed-output merges.
- Whether a useful crown/research ForcePackage can traverse HQ -> Sigrun -> worker -> verifier -> ConsumerAck -> successor without Tao once the default-branch scheduler is promoted.
- Whether any external crown is accepted by its third-party keeper. `CROWN_WON=false` until public independent readback exists.
- Current state newer than the last authenticated Sigrun readback (`2026-09-15T19:20:57Z`) must be re-observed rather than inferred.

## Reducer decision — shortest path

Do **not** build another scheduler, queue, actor store, registry, provider router or memory system.

1. Preserve exact `cdev-control#5` head and obtain its required independent approval/merge.
2. Observe the first natural default-branch `:07/:37` wake and archive its receipt.
3. Admit exactly one bounded useful worker route and one useful ForcePackage member; no broad swarm yet.
4. Run the two-cycle zero-Tao acceptance test above.
5. Only after PASS, increase force composition / crown compute.

The fastest way to relieve Tao is therefore **integration and promotion**, not more components.

## Public crown state

The separate tactical portfolio is summarized in `TRUNK/SIGRUN_TRUNK_TONIGHT_20260915_1916Z.md`. It does not override this systems truth table.

`RESULT=PARTIAL_WORLD_STATE__MECHANICAL_SUBSTRATE_PROVEN__USEFUL_AUTONOMY_NOT_PROVEN`  
`NEXT=MERGE_SCHEDULER__NATURAL_WAKE__ONE_USEFUL_WORKER__TWO_CYCLES_ZERO_TAO`
