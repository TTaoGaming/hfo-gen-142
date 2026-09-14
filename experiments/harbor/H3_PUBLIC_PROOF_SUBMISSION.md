# H3 — Harbor public-proof submission pack

**Actor UUID:** `099db845-7255-443d-8b72-ec22d743e826`  
**Lane:** H3 — packing public-proof submission  
**UTC:** 2026-09-14T14:00Z  
**Upstream pin:** `harbor-framework/harbor-index@5399ea1026fb2c7fc384cf8acd91a7d10fc943f3`  
**Law:** COTS only. This document does not introduce a scheduler, queue, wrapper harness, or alternate submission schema.

## PLAN

Convert the pinned upstream Harbor Index leaderboard protocol into a fail-closed handoff that a later carrier can execute after a finalist has completed the canonical run. Do **not** invent a submission JSON, custom uploader, or control plane. The official `leaderboard` CLI remains the submission mechanism.

Primary upstream evidence:

- `leaderboard/SUBMIT.md` at the pinned commit: <https://github.com/harbor-framework/harbor-index/blob/5399ea1026fb2c7fc384cf8acd91a7d10fc943f3/leaderboard/SUBMIT.md>
- `leaderboard/src/leaderboard/ci/static_analysis.py`: <https://github.com/harbor-framework/harbor-index/blob/5399ea1026fb2c7fc384cf8acd91a7d10fc943f3/leaderboard/src/leaderboard/ci/static_analysis.py>
- `leaderboard/src/leaderboard/core/hub.py`: <https://github.com/harbor-framework/harbor-index/blob/5399ea1026fb2c7fc384cf8acd91a7d10fc943f3/leaderboard/src/leaderboard/core/hub.py>
- canonical `job-config.yaml`: <https://github.com/harbor-framework/harbor-index/blob/5399ea1026fb2c7fc384cf8acd91a7d10fc943f3/job-config.yaml>

## DO — canonical public-proof path

### Gate A — final run must be leaderboard-valid before spending the full run

Fail closed unless all are true:

- Dataset: `harbor-index/harbor-index`
- Dataset ref expected by the pinned leaderboard code: `sha256:fdb3554453d29f96bfe87ddf36e6770f6ceadd375e8189c62718ef2f215bbbad`
- Coverage: exactly the leaderboard task set, currently `80` tasks
- Trial floor: `>=5` trials per task (`80 x >=5`)
- `timeout_multiplier: 1.0`
- No agent/verifier timeout overrides
- No CPU/GPU/memory/storage overrides
- Official judge config: `JUDGE_MODELS='["claude-opus-5"]'`, `JUDGE_REPEATS='3'`
- Public Harbor Hub visibility: final run uses `--upload --public`
- Agent/provider credentials are injected at runtime only; secrets never enter GitHub

The canonical config already pins the score-defining settings. Prefer layering only the finalist agent/model/provider-specific arguments and credentials onto `job-config.yaml`.

### Gate B — tournament jobs are NOT leaderboard submissions

G1/G2/G3 partial jobs are useful for successive halving but should not be sent through `lb submit`: upstream static analysis requires full task coverage and >=5 trials/task. This prevents wasting reviewer/CI cycles and avoids confusing a cheap assay with a public proof.

### Gate C — let upstream generate the submission

After a finalist produces one or more **public** Harbor Hub jobs that jointly satisfy Gate A, use the upstream CLI from the pinned checkout:

```sh
cd leaderboard
uv run lb submit \
  https://hub.harborframework.com/jobs/<FINAL_JOB_UUID> \
  [https://hub.harborframework.com/jobs/<OPTIONAL_ADDITIONAL_JOB_UUID> ...]
```

`lb submit` is the official COTS composition of:

1. `lb filter` — derives one submission per unique `(agent, agent_version, model, reasoning_effort)` from Hub job data.
2. `lb metadata` — fills required display metadata.
3. `lb open-prs` — creates one PR per submission file.

Do **not** hand-author trial lists or metrics. CI re-derives trials from `source_jobs`; maintainers/CI populate metrics and disqualifications.

### Gate D — non-interactive execution

The upstream guide states metadata can run without prompts when `leaderboard/src/leaderboard/display_names.json` already maps the finalist agent and model. If the finalist is unknown to that map, pre-fill the display-name mapping before invoking `lb submit`; do not leave a headless carrier hanging at an interactive prompt.

Required metadata checked by CI:

- `agent_display`
- `agent_org`
- `model_display`
- `model_org`
- `date`

### Gate E — public evidence chain

A submission is not externally verified merely because a job finished. Preserve the full public chain:

1. Public Harbor Hub final job URL(s).
2. Submitter PR containing exactly one `leaderboard/submissions/<name>.json` file.
3. Automatic **Static Analysis PASS** on that PR.
4. Promotion into the leaderboard-owned bot PR (the submitter PR being closed at promotion is normal).
5. Maintainer trajectory `/judge` report.
6. Maintainer `/apply` result for confirmed false positives, if any.
7. Merged bot PR.
8. Public Harbor Index leaderboard entry linked by CI after merge.

Only stages 7–8 constitute the durable third-party public proof target for GEN142 income translation.

## STUDY

### What this falsifies

- **A custom submission packer is unnecessary.** Upstream already provides `uv run lb submit` and owns the schema/PR flow.
- **Cheap tournament assays cannot directly become leaderboard rows.** The pinned checker requires `80` tasks x `>=5` trials/task.
- **A Hub upload alone is weaker than the requested external proof.** The durable proof is the merged leaderboard-owned submission plus public leaderboard entry.
- **Final-run validity must be decided before compute spend.** Timeout/resource/judge/dataset deviations are statically rejected even if the model score is high.

### Verified pinned invariants

From `static_analysis.py` at `5399ea1`:

- `EXPECTED_TASK_COUNT = 80`
- `MIN_TRIALS_PER_TASK = 5`
- `JUDGE_MODELS = {"claude-opus-5"}`
- `JUDGE_REPEATS = 3`

From `core/hub.py` at `5399ea1`:

- `DATASET = "harbor-index/harbor-index"`
- `DATASET_REF = "sha256:fdb3554453d29f96bfe87ddf36e6770f6ceadd375e8189c62718ef2f215bbbad"`

A known public submission at the same pin demonstrates the expected evidence shape (`source_jobs`, source filter, metadata, CI/maintainer-derived metrics):
<https://github.com/harbor-framework/harbor-index/blob/5399ea1026fb2c7fc384cf8acd91a7d10fc943f3/leaderboard/submissions/2026-07-14-gpt-5-6-terra-max-codex.json>

## ACT — handoff trigger

**Current H3 status: PACKED / EXECUTION BLOCKED UPSTREAM OF H3.**

H3 needs no further custom implementation. The next carrier should not touch this lane until H0/H2 produces a canonical public finalist run. When a qualifying Hub job exists, execute the exact upstream `lb submit` path above and record the resulting PR + static-analysis result + promoted bot PR/leaderboard URL.

**Release condition:** no Tao routing required. The only human-sensitive boundary remains credentials/auth if an existing authorized execution context cannot be recovered safely.
