# GEN142 Baton Pass

Updated: 2026-09-14T13:22Z

## Recover newest-first
1. Read `WORLD_STATE/latest.md`.
2. Read issue #2 newest-first.
3. Read `HIVE_R0.md`, `ORACLE_HQ.md`, `ORACLE_GATEWAY.md` only as needed.
4. Do not ask Tao to ferry context. GitHub is the recovery surface.

## Current facts
- G1 Cloudflare durability/idempotency: `SCOPED_PASS`.
- Oracle VPS execution substrate: `PASS`.
- GEN142 native Oracle dispatch: `HOLD_REGISTRATION_BOUNDARY`; workflow exists and queued jobs are waiting for a GEN142-attached self-hosted runner.
- Staged GEN142 GitHub Actions ARM64 runner package exists on Oracle under `/var/lib/hfo-desktop-commander/hfo-runners/gen142`; do not clone GEN140 credentials.
- Lenovo `gh` is authenticated as `TTaoGaming`; use only for human-authorized credential gates, not hot state.
- Desktop Commander reaches Lenovo/Oracle/OVH for terminal/files/processes but has no GUI/screen-control surface.
- TeamViewer is installed/running on Lenovo but unattended/mobile correctness is unproven.
- Lenovo and Oracle share Tailscale; Taildrop Lenovo -> Oracle works; direct Lenovo -> Oracle SSH is not admitted.
- OVH remains `DEGRADED / ELASTIC_ONLY`.
- Legacy Sigrun/Kimi actor path remains quarantined.

## PDSA result from prior carrier
PLAN: remove Tao/Lenovo as hidden operator dependency and identify the missing arbitrary-device control layer while continuing G2 preparation.
DO: probed Desktop Commander capabilities, Lenovo remote-control services, Tailscale topology/transport, GitHub auth, TeamViewer state, runner staging and current gate evidence; researched COTS control-plane options.
STUDY: terminal automation is strong but GUI/operator survivability is not. TeamViewer exists but is not a trusted fleet-wide control plane. MeshCentral + Tailscale is the current best COTS hypothesis; VPSes should expose terminal/files, not gratuitous Linux desktops.
ACT: add an explicit operator-survivability gate and run one bounded MeshCentral assay before expanding custom bridges. Keep G2 runner-registration as the exact execution blocker.

## Next bounded PDSA
Target: prove or falsify a COTS operator control plane with minimal dependencies.

Acceptance assay:
1. From a phone/arbitrary browser, authenticate to the control plane.
2. Reach Lenovo GUI unattended.
3. Reach Oracle terminal + files without Lenovo routing.
4. No public unauthenticated management port.
5. Recovery path remains available through Tailscale.
6. Record setup/operator minutes and hidden dependencies.
7. If MeshCentral fails materially, compare RustDesk/Guacamole on the same assay; do not recommendation-hop without falsification.

Parallel exact G2 edge:
- Register/attach one dedicated GEN142 self-hosted runner to Oracle using an authorized GitHub registration path.
- Let queued `oracle-cell-r0` drain.
- Verify `Oracle/aarch64` receipt and Lenovo-independent execution.
- Then run one bounded G3 evolution cell with frozen evaluator + restart/resume + duplicate-effect suppression.

## Thread terminal seal
- This chat/thread is terminal and will not be resumed.
- Tao is manually gathering threads and will regenerate a fresh carrier.
- No state in this conversation should be treated as authoritative unless reproduced on GitHub.
- Recovery authority is `BATON_PASS.md` + `WORLD_STATE/latest.md` + issue #2 newest-first.
- Current carrier is released. No pending background work exists.

## Pickup prompt
`GEN142 BATON PICKUP — recover TTaoGaming/hfo-gen-142 BATON_PASS.md + WORLD_STATE/latest.md + issue #2 newest-first -> fresh carrier UUID -> run one bounded PDSA on the highest-value unresolved edge: (A) operator-survivability COTS control-plane assay, or (B) G2 GEN142 Oracle runner registration/dispatch if authorized path is available -> checkpoint terminal evidence to #2 and update WORLD_STATE -> release. COTS first, no new scheduler/state store, no Tao context ferrying.`
