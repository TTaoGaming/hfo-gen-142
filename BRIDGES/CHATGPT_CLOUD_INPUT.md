# ChatGPT Cloud Input Bridge — Gen142

Status: `LAPTOP_LIVE / VPS_AUTH_HOLD`.

Purpose: bounded input-only ChatGPT normal-chat capacity bridge. This is an actuator, not lifecycle truth, not authority, and not a model-output scraper.

## Current verified path
- dedicated Account-B persistent browser profile remains authenticated through the existing Playwright donor;
- fresh structural probe returns `READY`;
- current UI route `Latest + XHIGH` verifies as `Extra High`;
- true headless Chrome is challenged by the provider and remains HOLD; no bypass is attempted;
- headful Chrome moved off-screen is the current laptop actuator to avoid foreground focus theft;
- prompt bytes are read back exactly before Enter;
- any stale/non-empty composer fails closed before send;
- launch nonces are checked against the existing receipt ledger before reuse;
- possible-send ambiguity remains `HOLD_NO_RESUBMIT`.

## Recovery assay 2026-09-14 UTC
A single novel Gen142 canary used nonce `FB076AB722C3` with `Latest + XHIGH`, submitted once, and produced a confirmed conversation URL. The browser collected zero assistant-output bytes. The spawned carrier then wrote a bound START ACK to Gen142 issue #2 as comment `5657967166`, echoing the same nonce, a fresh carrier UUID, UTC, and self-attested `GPT-5.6 Sol / ChatGPT` harness.

This is evidence that the laptop bridge is currently usable end-to-end. The explicit legacy UI route named `GPT-5.6 Sol` did not verify in the current selector surface; therefore Gen142 should bind to the observed UI contract `Latest + XHIGH`, while the child may self-report the resolved model separately.

## Regressions now guarded
- background actuator must remain headful but off-screen by default; visible UI is opt-in;
- stale composer text is a pre-send HOLD;
- prompt readback mismatch is a pre-send HOLD;
- any nonce already present in durable local receipt history is non-replayable;
- provider/auth/challenge/throttle/ambiguous-send states stop rather than retry.

Current local bridge regression suite: 13/13 PASS after these guards.

## Historical scar retained
A prior Account-B send with nonce `7338EAEB06A3` ended `HOLD_UNKNOWN_EFFECT_AFTER_SEND`; later profile sessions repeatedly rehydrated that exact draft. Durable receipt history contains that nonce once and current recovery did not replay it. Do not infer that clearing DOM text alone clears provider/profile draft state.

## VPS cutover
Do not copy raw browser cookies or the laptop profile to Linux. A VPS bridge earns `VPS_LIVE` only after:
1. native Playwright/Chromium runtime works on the VPS;
2. a dedicated VPS browser profile is authenticated by normal provider login without credential export/bypass;
3. no-send composer/model/effort probes pass;
4. one unique-nonce input-only canary yields a bound GitHub child ACK;
5. restart/recovery does not require Lenovo.

Preferred VPS is x86_64 OVH. Playwright runtime bootstrap has begun there. `TAO_RELAY_REQUIRED=false` once the one-time profile authentication gate is crossed.
