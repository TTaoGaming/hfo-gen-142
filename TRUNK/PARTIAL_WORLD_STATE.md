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

## Frontier Fast evolution blocker trace — 2026-09-15T20:38Z

Goal: run ShinkaEvolve / OpenEvolve / GEPA as COTS evolutionary search on VPS capacity, with Cloudflare/Sigrun owning mission state, and Frontier Fast trusted runners owning final external fitness.

### PROVEN / easy
- Oracle VPS is viable as the evolution-controller host: ARM64, Python 3.12, `uv`, ~11 GiB RAM / ~10 GiB available, ~24 GiB free disk, Node 22/npm present.
- Isolated Oracle smoke environment successfully installed and imported `shinka-evolve`, `openevolve`, and `gepa` together under Python 3.11; install footprint ~545 MiB. Framework installation itself is **not a blocker**.
- OVH is available as secondary x86_64 host (~7.6 GiB RAM, ~48 GiB free disk, Docker present), but currently lacks Python pip/uv bootstrap.
- Both VPS hosts are CPU-only; no NVIDIA GPU is present.
- Live Frontier Fast queue observed `depth=0`, `running=0`, `estimatedMinutesPerRun=22`; the platform allows max 3 submissions in flight/account and uses trusted paired runs plus independent confirmation for ranking.

### CURRENT BEST CROWN TARGETS
- Live API currently shows **no trusted-runner kernel record** on `maple-preview-gguf-gb10cuda-v1` and **no trusted-runner kernel record** on `deepseek-v4-flash-gguf-gb10cuda-v1`.
- Maple GB10 is the clean first target: open, recommended VRAM ~8 GiB, exact pinned engine contract available, and an existing HFO Maple candidate patch already applies/builds at translation-unit level but lacks performance proof.
- DeepSeek V4 Flash is open but requires ~110 GiB VRAM locally and its live speculative metadata is internally contradictory: pinned draft says `draft-dspark`, while generated `howToRun` examples use `draft-dflash`. Keep kernel-only work possible, but HOLD speculative automation until upstream contract resolves.

### REAL BLOCKERS
1. **No shared Frontier evaluator adapter.** None of Shinka/OpenEvolve/GEPA is currently wired to a frozen Frontier Fast evaluator. Need one thin semantic owner that: creates isolated worktree -> applies candidate only inside allowlisted paths -> builds pinned engine -> correctness gate -> local performance when GPU exists -> returns structured metric + diagnostics. Framework-specific wrappers should call this same evaluator; do not create three evaluator truths.
2. **No dense local fitness signal.** VPS hosts have no GPU. Frontier's trusted runner is suitable as promotion/final verifier, not as the inner evolutionary loop: a rejected candidate burns ~20+ minutes and only 3 can be in flight. Serious multi-generation search therefore needs an admitted GPU fitness worker, ideally exact GB10 for Maple, or at least an NVIDIA GPU for directional local filtering. Without GPU, evolution is mostly mutation + compile/static filtering followed by sparse remote evaluations.
3. **Mutation-model auth is not wired on Oracle service path.** Current shell has Kimi CLI, but no Codex/Claude CLI and no `OPENROUTER_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY`. Shinka can use Headless subscription-backed Codex/Claude, but those agent CLIs/auth are not present. OpenEvolve/GEPA can use API/OpenAI-compatible providers, but provider credentials are not currently admitted to the evolution worker environment.
4. **Frontier submit identity not wired.** Oracle currently has no `frontierfast` CLI, no Bun, and no `GAINZ_TOKEN`. Frontier writes require a bearer token scoped to the user's GitHub account. Account/login/token/fork are legitimate human authority boundaries; token must stay private and scoped to the submitter leaf, not Cloudflare prompts/public GitHub.
5. **Cloudflare/VPS automatic mission path is not promoted.** `cdev-control#5` remains open/unmerged; therefore the default-branch `:07/:37` scheduler that should wake/reconcile this workload is not production. Branch canaries prove mechanics, not unattended useful work.
6. **Useful worker route remains unproven.** Latest authenticated CPR ledger has `worker_routes=[]`; current private ForcePackage is disarmed. Need one bounded evolution-worker route before broad population fan-out.
7. **Do not run three evolutionary controllers against one mutable tree.** Shinka, OpenEvolve, and GEPA each own selection/population semantics. Running all three as coequal controllers would recreate branch/state pollution. Use isolated experiment pools sharing one frozen evaluator; reducer promotes only hash-bound champions. Start with Shinka as primary because it has async evolution plus documented Headless subscription-backed mutation; use GEPA/OpenEvolve as independent emitter/challenger pools after the same evaluator passes.

### SHORTEST PATH
A. Human: create/auth Frontier Fast identity/token + fork; optionally authenticate one Headless-supported coding CLI on Oracle or admit one API provider secret.
B. Machine: install Frontier CLI/Bun on Oracle; freeze Maple GB10 live contract/recipe/findings into an experiment capsule.
C. Build one shared `frontier_eval` adapter and Shinka wrapper first; smoke 2 generations using compile/correctness-only fitness on CPU.
D. Add an exact/near GB10 GPU worker for local score; successive-halving only then becomes meaningful.
E. Submit only promoted champions to Frontier Fast; record every dead/promising/won finding.
F. Separately promote `cdev-control#5`; once natural wake is proven, bind this experiment capsule as one useful ForcePackage and require two consecutive zero-Tao cycles.

`FRONTIER_EVOLUTION_BLOCKER=EVALUATOR_PLUS_GPU_FITNESS_PLUS_AUTH_WIRING__NOT_FRAMEWORK_INSTALL`
`BEST_FIRST_TARGET=maple-preview-gguf-gb10cuda-v1`
`DEEPSEEK_SPECULATION=HOLD_CONTRACT_CONFLICT`

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
