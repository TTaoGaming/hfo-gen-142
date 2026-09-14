# Gen142 Mobile Oracle HQ Bridge

Status: `MOBILE_DIRECT_DC_LIVE__GITHUB_COCKPIT_PENDING_REVIEW__TAILSCALE_WEB_HOLD`.

## Goal
Pilot the swarm from mobile without requiring Lenovo or physical VPS access.

## Primary live path
`ChatGPT mobile -> Remote Desktop Commander -> Oracle HQ -> Gen142 gateway preflight -> bounded work -> GitHub/Cloudflare receipt`

This path is already live: Oracle is a separately registered Desktop Commander device and the carrier-admission gate has been installed/tested there. Lenovo is not in the runtime chain.

## Secondary audited cockpit
Private repo `TTaoGaming/cdev-control` issue #4 is the mobile cockpit. Protected PR #3 stages two workflows on the existing Oracle self-hosted runner:
- daily 00:05 UTC Oracle HQ canary;
- issue-comment bridge for allowlisted `hq status` and `hq canary` requests.

Branch protection currently requires an independent reviewer; self-approval is correctly rejected. Do not weaken protection. Once merged, mobile GitHub or a mobile ChatGPT carrier with GitHub access can use issue #4 and receive bounded receipts without Desktop Commander.

## Oracle-local HQ bridge
A rootless local service is running at `127.0.0.1:18790` under the Desktop Commander account:
- `GET /api/status` — fixed host/service telemetry;
- `POST /api/canary` — same bounded health assay;
- `POST /api/intent` — queues text as `QUEUED_NOT_ADMITTED`; it does not execute it.

An hourly cloud keeper verifies/restarts this local process through direct Oracle Desktop Commander. The local bridge is not public and Tailscale Serve exposure is not enabled.

## Safety / forcing law
`MOBILE_INTENT != WORKITEM != ADMISSION != EXECUTION`.

No mobile surface accepts arbitrary execution. Future launch verbs must resolve to a durable Gen142 WorkItem + named Agent Skill + carrier envelope + deterministic target binding + effect ceiling, then pass `tools/gateway_preflight.py` before execution.

## Desired end state
1. Mobile ChatGPT is the normal human command surface.
2. Oracle HQ is the stable gateway/admission node.
3. Cloudflare owns hot durable actor/workflow state.
4. GitHub owns institutional demand/evidence/recovery.
5. OVH/future VPSes and laptop remain replaceable carriers/workers.
6. Private GitHub cockpit is the audited fallback when a cloud carrier lacks Desktop Commander.
7. No physical access to Oracle/OVH is part of the operating model.
