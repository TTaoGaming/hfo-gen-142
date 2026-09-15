# Frontier Fast evolution spine — Maple GB10

Reducer PDSA: `79b8067a-8517-4b1c-8d88-ac907c00ce3e`  
Observed through: `2026-09-15T22:26:30Z`  
Target: `maple-preview-gguf-gb10cuda-v1`  
Source pin: `deepgrove-ai/llama.cpp@8ce8ca6c6d370b6235dfa8e2a0611a9adb6d77d1`

## Contract
All evolution frameworks are emitters. They do not own promotion. Candidate flow is:

`mutate -> static preflight -> touched-TU compile -> trusted GB10 fitness -> independent verifier -> submitter`

`shared_eval.py` implements only the first two cheap/fail-closed stages. Every successful static receipt deliberately contains:

- `fitness_stage=STATIC_PREFLIGHT_ONLY`
- `trusted_fitness=null`
- `promotion=HOLD_TRUSTED_GB10_FITNESS`

Static green can never self-award a Frontier record.

## Oracle evidence
Persistent state root used for the assay: `$HOME/.local/state/frontier-pdsa-79b8067a`. An earlier `/tmp` worktree vanished between tool calls while the host itself remained up, so `/tmp` is explicitly inadmissible for overnight population/database/checkpoint state.

Installed in an isolated persistent venv and imported successfully:
- ShinkaEvolve `0.0.7`
- OpenEvolve `0.3.2`
- GEPA `0.1.4`

The public Maple donor patch `02f8f85d64eea5712a7773fb883b97318ba0e4bfbe896511d8dd9edfb46b562c` was replayed against the exact source pin. It passed non-empty/path extraction, exact pin binding, `git apply --check`, `git diff --check`, and native ARM64 compilation of its touched translation unit. Build receipt SHA256: `38bcbebf6c313962d73d42334027ea3f7b7889a156244f4ab661e8ee60cf2c78`.

An intentionally corrupted patch was rejected at `git apply --check` and exited nonzero before build. This is the negative control.

## Framework assays
### ShinkaEvolve
- Shared evaluator: 2/2 valid runs, combined score `1.0`, both retained `HOLD_TRUSTED_GB10_FITNESS`.
- Full persistent runner: seed evaluated/archived correctly; local OpenAI-compatible Ollama route reached the mutation stage.
- Generation 1 made three zero-cost Granite 3B queries but produced no admissible proposal. Durable failure is `failure_class=llm_output_invalid`, `failure_reason=LLM response content was None`, resample attempt 3. Failure receipt SHA256: `79bf19c89cb37bc65a54ea314618972242750f4d45dff296dcfea85e6177005a`.
- Result: engine/evaluator/provider transport works; the local 3B mutation model is not an admitted productive proposer for this prompt shape.

### OpenEvolve
- Native evaluator interface scored the same donor `combined_score=1.0`, `preflight_pass=1.0`, `trusted_fitness_present=0.0`.
- Full controller initialized MAP-Elites/islands and checkpointed the lawful seed.
- One local Granite mutation call timed out at 120 s; the controller failed closed and retained the seed. Smoke receipt SHA256: `e34645467cced46370fde3b81666bf97bb32e8a419ad9b2582fcbbfd4ab2ed74`.
- Result: controller/evaluator works; local CPU-only mutation latency/model quality is the blocker, not OpenEvolve installation.

### GEPA
- Native adapter scored lawful donor `1.0` and corrupted patch `0.0` using the same evaluator.
- Full engine ran one proposal cycle with a deterministic falsifier proposer: seed full-val score `1.0`; proposed bad patch scored `0.0`; GEPA rejected it and retained the seed. `metric_calls=3`. Smoke receipt SHA256: `c2646fdf12a379a409c1b035057ee1e9585b861e6329450b2f17e08c3183cdb3`.
- Result: proposal -> evaluate -> selection is proven on Oracle.

## Live Frontier boundary
Fresh readback during this PDSA found zero non-baseline `trusted-runner` records on the Maple GB10 track. Queue was depth `0`, running `0`, with platform estimate `22 min/run`.

Oracle currently has no GPU, no `frontierfast`/Bun CLI, no `GAINZ_TOKEN`, and no OpenRouter/OpenAI/Anthropic API key in this service environment. These are not static-evaluator blockers; they block trusted performance throughput and/or strong-model mutation/submission.

## Reducer decision
The shortest useful architecture is **not** three independent factories. Use one evaluator contract and multiple proposal populations:

1. Shinka / OpenEvolve / GEPA propose candidates in isolated worktrees.
2. VPS static evaluator kills malformed/unbuildable candidates cheaply.
3. Only survivors consume GB10 fitness.
4. Successive halving promotes repeated positive trusted measurements.
5. Distinct verifier replays a putative champion.
6. Submitter alone holds Frontier credentials and final external-submit authority.

For the first canary, rented local GB10 is optional: the official trusted runner can judge a small number of survivors. For high-throughput overnight evolution, a GB10-class fitness worker is the missing compute resource.

`RESULT=SHARED_EVALUATOR_PASS__GEPA_FULL_LOOP_PASS__SHINKA_OPENEVOLVE_LOCAL_PROPOSER_BLOCKED__TRUSTED_GB10_FITNESS_MISSING`
`CROWN_WON=false`
