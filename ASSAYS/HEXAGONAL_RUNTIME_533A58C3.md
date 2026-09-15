# Hexagonal runtime falsification — 533a58c3

UTC start: `2026-09-15T21:20:06Z`  
Claim: `#13` comment `5688249910`  
Question: can one ForcePackage/worker contract substitute provider + harness leaves without changing semantic ownership, verifier, or ConsumerAck semantics?

## Frozen acceptance

`SAME JOB -> ADAPTER A / PROVIDER A -> TERMINAL + INDEPENDENT VERIFIER + CONSUMERACK`

then the same bound job/capability/verifier through a distinct adapter/provider. Optional stronger assay also replaces host. `TAO_HOT_LOOP_ACTIONS=0`; every route must be `ZERO_MARGINAL` under the current no-debt provider contract.

The gate in `tools/hexagonal_runtime_gate.py` refuses claims based only on similar model text. It requires matching job/task/capability/output/verifier bindings, controller observation, independent verifier receipt, ConsumerAck, terminal state, distinct providers/adapters/harnesses, and optional distinct hosts.

## What passed

### Architecture / kernel
- `ACTOR != CARRIER` and provider-as-leaf are already explicit in `HOLON_MISSION_COMMAND_CONTRACT.md`.
- WorkCell lifecycle is adapter-shaped and keeps scheduling/claim/verification outside worker leaves.
- `ops/vps_exec_guard.py` is provider-class aware without owning semantic state.
- Provider specificity in `cdev-control#5` is concentrated in the worker leaf import/route check; claim/fence/reconcile/history logic remains outside the leaf.

### Real two-provider leaf execution
Frozen task:

`Return exactly this one line and nothing else: HEXAGONAL_CANARY_V1_533a58c3`

Task SHA256: `fa22772e43eeb597ee67762fc691c41aa35ca164e1b95cc1adf10798abeebf1a`  
Expected semantic output SHA256: `98b19ebf8d16c29327b3d4ba23aac74110b34eaf1b7c218b86e17eb1da81cfa8`

A private child candidate (`TTaoGaming/cdev-control#10`, based on #5 and not modifying #5) implements one candidate `hfo.sigrun.worker_job.v2` bounded-text capability with two leaf profiles:
- Kimi subscription/no-tools;
- Codex ChatGPT subscription/empty-workspace + read-only + browser/MCP/plugin/shell-feature disables.

On LenovoSlim7 the actual adapter code executed the same immutable job through both installed subscription-backed CLIs. Both returned existing schema `hfo.sigrun.worker_completion.v1`, exact expected stdout, identical stdout SHA above, same job/workitem/mission/fence, and `timed_out=false`, `truncated=false`.

Private candidate verification: profile tests `6/6 PASS`; complete `test_gen142*.py` suite `49/49 PASS`.

Harness scars found and repaired inside the candidate leaf: Windows npm `.cmd` wrapping, Kimi version drift around `--work-dir`, minimal benign `SYSTEMROOT` process dependency, and UTF-8 diagnostic decoding. No controller/provider secret expansion was needed.

`MULTI_VENDOR_LEAF_PORT=PASS_SCOPED`

## What did not pass

### Sigrun multi-adapter routing
Current deployed-lineage Sigrun remains Kimi-R1 specific:
- operation is `KIMI_TEXT`;
- `carrier_profile_id` is typed/refused against `h07-kimi-subscription-tools-empty-v1`;
- worker completion validation requires that Kimi profile;
- the inner verifier-bound bytes use provider-specific schema `hfo.sigrun.kimi_text_result.v1`.

The outer `hfo.sigrun.text_result.v1`, Result -> HRIST -> P7 flow, claim/fence/deadline machinery are structurally reusable. But no controller-observed second provider has traversed them. This needs a versioned generic text-worker profile/result schema and a reviewed thin adapter registry; do not mutate the existing R1 contract in place.

`SIGRUN_MULTI_ADAPTER_ROUTING=NOT_PROVEN`

### ForcePackage production path
Private no-effect ForcePackages have been admitted/terminal-consumed, but `cdev-control#5` is still unmerged and its included package is disabled/HASH_ECHO-only. Generic public ForcePackage compiler #55 explicitly does not dispatch or bind providers.

`GENERIC_USEFUL_FORCEPACKAGE_DISPATCH=NOT_PROVEN`

### Host substitution
- Lenovo: Kimi and Codex live.
- Oracle: Kimi binary exists but Desktop Commander service context reports `LLM not set`; Codex/Claude/Gemini binaries absent.
- OVH: no Kimi/Codex/Claude/Gemini CLI in the probed service context.

`HOST_SUBSTITUTION=NOT_PROVEN`

### Third provider
Claude local auth metadata reported logged-in, but a real noninteractive canary returned `401 OAuth access token has expired`. Treat as `HOLD_AUTH_STALE`, not live capacity. Historical OpenRouter-free route returned HTTP 401 and its leaked legacy credential remains compromised; it is not an admitted fallback.

`THIRD_PROVIDER=HOLD_AUTH_STALE_OR_UNADMITTED`

## Machine gate result on current evidence

The real Kimi + Codex direct leaf receipts deliberately lack controller-observed Sigrun terminal, independent verifier receipt, and ConsumerAck. Feeding those facts into `hexagonal_runtime_gate.py` returns `HOLD / RECEIPT_BINDING_REQUIRED` rather than self-awarding PASS.

Gate regressions on Oracle ARM64: `9/9 PASS`, `py_compile PASS`, `git diff --check PASS`.

## Reducer verdict

`HEXAGONAL_DESIGN=PASS`  
`MULTI_VENDOR_LEAF_EXECUTION=PASS_SCOPED`  
`SIGRUN_MULTI_ADAPTER_ROUTING=NOT_PROVEN`  
`HOST_SUBSTITUTION=NOT_PROVEN`  
`GENERIC_FORCEPACKAGE_EXECUTION=PARTIAL`  
`HEXAGONAL_RUNTIME=PARTIAL__HOLD`

## Smallest next forcing function

1. Promote a **versioned** generic bounded-text worker contract alongside Kimi R1; do not mutate R1 history.
2. Generalize only the provider-specific Sigrun text mission/job/inner-result profile surface while preserving the existing claim/fence/HRIST/P7 state machine.
3. Bind the existing cdev leaf port as a thin adapter registry; no provider becomes a control plane.
4. Submit the same immutable no-effect job twice through Sigrun: Kimi and Codex, each controller-observed through Result -> HRIST -> P7 -> TERMINAL.
5. Feed both immutable receipts into `hexagonal_runtime_gate.py`. Only an `ADMIT / HEXAGONAL_RUNTIME_PASS` permits the runtime claim.
6. Separately repeat one profile on Oracle/OVH after provider admission to prove host substitution.

Do not merge #5 merely to satisfy this assay. Scheduler promotion and operational hexagonality are separate acceptance gates.
