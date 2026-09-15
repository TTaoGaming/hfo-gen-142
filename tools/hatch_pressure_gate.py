#!/usr/bin/env python3
"""Fail-closed pre-hatch flow-control gate for Gen142.

Pure policy only: no scheduler, queue, lease, provider call, or mutation.
It prevents new semantic work from outrunning fan-in/reconciliation capacity.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "hfo.hatch-pressure-snapshot.v1"
POLICY = "gen142-hatch-pressure-r0"
MAX_ACTIVE = 3
MAX_UNCONSUMED_TERMINALS = 2
MAX_PENDING_FANIN = 3
MAX_RECENT_LAUNCHES = 4
RECENT_WINDOW_MINUTES = 30
DUPLICATE_COOLDOWN_MINUTES = 60
PROVIDER_STATES = {"READY", "THROTTLED", "BLOCKED", "UNKNOWN", "NOT_REQUIRED"}
FORMATIONS = {"SINGLE": 1, "TWINLING": 2}


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(value) -> str:
    data = value if isinstance(value, bytes) else canon(value)
    return hashlib.sha256(data).hexdigest()


def emit(snapshot, decision, reason, **detail):
    out = {
        "schema": "hfo.hatch-pressure-decision.v1",
        "policy_version": POLICY,
        "decision": decision,
        "reason": reason,
        "snapshot_sha256": sha256(snapshot),
        **detail,
    }
    out["decision_sha256"] = sha256(out)
    return out


def hold(snapshot, reason, **detail):
    return emit(snapshot, "HOLD", reason, **detail)


def _items(value):
    return value if isinstance(value, list) else None


def _nonneg_int(value):
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def evaluate(snapshot):
    if not isinstance(snapshot, dict):
        return hold(snapshot, "SNAPSHOT_TYPE")
    if snapshot.get("schema") != SCHEMA:
        return hold(snapshot, "SNAPSHOT_SCHEMA")
    if snapshot.get("policy_version") != POLICY:
        return hold(snapshot, "POLICY_VERSION_MISMATCH")

    requested = snapshot.get("requested")
    flow = snapshot.get("flow")
    if not isinstance(requested, dict) or not isinstance(flow, dict):
        return hold(snapshot, "SNAPSHOT_FIELDS_INVALID")

    semantic_key = str(requested.get("semantic_key", "")).strip()
    formation = requested.get("formation")
    count = requested.get("count")
    if not semantic_key or formation not in FORMATIONS or count != FORMATIONS[formation]:
        return hold(snapshot, "HATCH_REQUEST_INVALID")

    if requested.get("tao_hot_loop_required") is True:
        return hold(snapshot, "HOLD_OPERATOR_RUNTIME")
    if requested.get("verifier_bound") is not True:
        return hold(snapshot, "HOLD_VERIFIER_UNBOUND")
    if requested.get("consumer_bound") is not True:
        return hold(snapshot, "HOLD_CONSUMER_UNBOUND")

    provider = requested.get("provider")
    provider_state = flow.get("provider_state")
    if not isinstance(provider_state, dict) or provider_state.get("provider") != provider:
        return hold(snapshot, "PROVIDER_OBSERVATION_MISSING")
    state = provider_state.get("state")
    if state not in PROVIDER_STATES:
        return hold(snapshot, "PROVIDER_STATE_INVALID")
    if state == "THROTTLED":
        return hold(snapshot, "HOLD_PROVIDER_THROTTLED", retry_after_seconds=provider_state.get("retry_after_seconds"))
    if state == "BLOCKED":
        return hold(snapshot, "HOLD_PROVIDER_BLOCKED")
    if state == "UNKNOWN":
        return hold(snapshot, "HOLD_PROVIDER_UNKNOWN")

    active = _items(flow.get("active_claims"))
    recent = _items(flow.get("recent_launches"))
    failures = _items(flow.get("repeated_failures"))
    if active is None or recent is None or failures is None:
        return hold(snapshot, "FLOW_LIST_INVALID")

    if any(isinstance(x, dict) and x.get("semantic_key") == semantic_key for x in active):
        return hold(snapshot, "HOLD_DUPLICATE_ACTIVE_SEMANTIC_WORK")
    if len(active) >= MAX_ACTIVE:
        return hold(snapshot, "HOLD_WIP_LIMIT", active_claims=len(active), limit=MAX_ACTIVE)

    unconsumed = flow.get("unconsumed_terminals")
    pending_verifiers = flow.get("pending_verifiers")
    pending_acks = flow.get("pending_consumer_acks")
    if not all(_nonneg_int(x) for x in (unconsumed, pending_verifiers, pending_acks)):
        return hold(snapshot, "FLOW_COUNT_INVALID")
    if unconsumed >= MAX_UNCONSUMED_TERMINALS:
        return hold(snapshot, "HOLD_UNCONSUMED_TERMINAL_BACKLOG", count=unconsumed)
    if pending_verifiers + pending_acks >= MAX_PENDING_FANIN:
        return hold(snapshot, "HOLD_FANIN_BACKLOG", pending_verifiers=pending_verifiers, pending_consumer_acks=pending_acks)

    duplicate_recent = [x for x in recent if isinstance(x, dict) and x.get("semantic_key") == semantic_key and x.get("age_minutes", 10**9) < DUPLICATE_COOLDOWN_MINUTES]
    if duplicate_recent:
        return hold(snapshot, "HOLD_RECENT_DUPLICATE_SEMANTIC_WORK", duplicate_count=len(duplicate_recent))

    burst = [x for x in recent if isinstance(x, dict) and isinstance(x.get("age_minutes"), (int, float)) and 0 <= x["age_minutes"] <= RECENT_WINDOW_MINUTES]
    if len(burst) >= MAX_RECENT_LAUNCHES:
        return hold(snapshot, "HOLD_HATCH_BURST", recent_launches=len(burst), window_minutes=RECENT_WINDOW_MINUTES)

    for item in failures:
        if not isinstance(item, dict):
            continue
        if item.get("semantic_key") != semantic_key:
            continue
        if item.get("count", 0) >= 2 and item.get("strategy_changed") is not True:
            return hold(snapshot, "HOLD_REPEATED_FAILURE_WITHOUT_MUTATION", fingerprint=item.get("fingerprint"))

    return emit(
        snapshot,
        "ADMIT",
        "ADMIT_HATCH",
        semantic_key=semantic_key,
        formation=formation,
        count=count,
        pressure={
            "active_claims": len(active),
            "unconsumed_terminals": unconsumed,
            "pending_fanin": pending_verifiers + pending_acks,
            "recent_launches_30m": len(burst),
        },
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Fail-closed Gen142 pre-hatch pressure gate")
    ap.add_argument("snapshot")
    args = ap.parse_args()
    try:
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"decision": "HOLD", "reason": "SNAPSHOT_UNREADABLE", "error": type(exc).__name__}, sort_keys=True))
        return 2
    out = evaluate(snapshot)
    print(json.dumps(out, sort_keys=True))
    return 0 if out["decision"] == "ADMIT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
