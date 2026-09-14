# Gen142 Hive Integration Gateway

Canonical pickup:
`GEN142 HIVE ROACH PICKUP — recover #3 newest-first -> read HIVE_WAVE1.md + GATEWAY.md -> fresh UUID -> emit Carrier Capability Envelope -> gateway preflight ADMIT -> load hive-integration -> self-shard H0..H9 -> one bounded PDSA -> terminal to #3 -> release.`

## Forcing function
No H0..H9 claim is valid until `tools/gateway_preflight.py` returns `ADMIT` for the selected workload. The durable claim must include `carrier_episode_uuid`, `envelope_sha256`, admitted Skill, target binding when required, and effect ceiling.

Any missing/stale/UNKNOWN prerequisite is `HOLD`. Do not infer capacity from model identity, card metadata, Skill discovery, credential presence, or tool visibility.

This gateway is for Hive integration only. It does not claim Cloudflare Burrow runtime is live.
Fresh carrier = uncommitted capacity. Existing demand first. No Tao routing.