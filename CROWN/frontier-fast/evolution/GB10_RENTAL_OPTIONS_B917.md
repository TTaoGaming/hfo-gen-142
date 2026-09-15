# EXACT GB10 RENTAL OPTIONS — B917 NO-SPEND CHECKPOINT

Parent PDSA: `b91706cc-6b96-4b63-aaff-a8a548b83080`  
Checked: `2026-09-15`  
State: `PURCHASE_DECISION_READY / NO_SPEND_PERFORMED`

This is a human purchase boundary packet, not authorization to rent. Prices/availability can move; re-read the checkout page before payment.

## Shortlist

| Provider | Published exact hardware/access | Current list price / commitment | Fit for first assay |
|---|---|---:|---|
| Enverge DGX Spark Cloud | Dedicated NVIDIA DGX Spark / GB10, 128 GB unified memory, bare-metal SSH, root, Docker, NVMe, CUDA 13 | `$0.75/hour`, pay-as-you-go; site says per-minute usage / no commitment | Strong exact-hardware fit if capacity is immediately available. |
| AxForge | Dedicated NVIDIA DGX Spark GB10, 128 GB unified memory, full SSH; EU regions | `€0.69/hour` on-demand on pricing page; longer bookings cheaper | Strong exact-hardware fit; EU geography may add latency but does not alter local benchmark validity. |
| GPUwerk | 1x DGX Spark, 128 GB unified memory, 1 TB NVMe | `$0.79/hour`, per-minute, no commitment; pricing page describes prepaid credit/top-up behavior | Strong exact-hardware fit; explicitly verify current credit minimum and workspace deletion semantics before use. |

A private NVIDIA Developer Forum rental advertises a physical DGX Spark / GB10 at `$0.60/hour`, 1-hour blocks, remote SSH. It is lower price but single-person continuity/support is a different trust profile; not the default choice for an evidence-critical first assay.

## Sources

- Enverge: `https://spark.enverge.ai/` and `https://enverge.ai/terms`
- AxForge: `https://axforge.ai/pricing/`
- GPUwerk: `https://gpuwerk.com/pricing/`
- NVIDIA forum listing: `https://forums.developer.nvidia.com/t/dgx-spark-available-for-rent-0-60-hour-remote-ssh-access-st-louis-mo/370854`

## Bounded first-rental envelope

If Tao authorizes a new-spend experiment, start with **one exact node** only. A 6-hour compute budget at the published rates is roughly `$4.50` on Enverge, `€4.14` on AxForge, or `$4.74` on GPUwerk, excluding taxes/top-up mechanics. Do not infer those totals as checkout quotes.

Before machine admission, record:
1. provider + exact checkout rate;
2. hard wall-clock duration and maximum total charge;
3. shutdown/delete semantics (billing must stop on teardown);
4. SSH/root availability and persistent-workspace behavior;
5. generated host access via approved private channel only;
6. `gb10_probe.py` output = `PASS_EXACT_GB10`;
7. immediate stock A/A calibration before any candidate test.

If `gb10_probe.py` returns anything else, classify the host `DIRECTIONAL_FITNESS_ONLY` or terminate it; do not consume crown-compute budget on the wrong machine.

## Stop conditions

Terminate and stop spend when any of these hold:
- exact GB10 admission fails;
- source/model/harness cannot reproduce the track baseline within the calibrated envelope;
- first two bounded generations produce no reproducible positive survivor;
- provider billing becomes ambiguous;
- persistent workspace cannot be exported/checkpointed safely.

No auto-renew, silent scale-out, second node, or paid API fallback is authorized by this document.

`RESULT=GB10_RENTAL_SHORTLIST_READY__NEW_SPEND_REQUIRES_TAO`
