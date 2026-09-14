#!/usr/bin/env python3
"""Thin pointer-to-plan adapter for Gen142 carriers.

Generates disposable carrier identity and projects the existing deterministic
reconciler plan into a morph role. Owns no durable state or authority.
"""
from __future__ import annotations

import argparse
import json
import uuid
from pathlib import Path

import reconcile_kernel

HATCH_VERSION = "gen142-larva-hatch-r0"

ROLE_BY_ACTION = {
    "SUBMIT_NEXT": "mission_carrier",
    "DISPATCH_WORKER": "worker",
    "CONSUME_TERMINAL": "reducer",
    "CLEAN_RESOURCE": "janitor",
    "WAIT_HUMAN_UNLOCK": "resume_watcher",
    "WAIT_DISPATCH": "observer",
    "WAIT_ACTOR": "observer",
    "WAIT_WORKER_DEADLINE": "observer",
    "NONE": "idle",
}


def selected_demand_role(snapshot: dict, plan: dict) -> str | None:
    action = plan.get("action") or {}
    if action.get("kind") != "SUBMIT_NEXT":
        return None
    ref = action.get("work_ref")
    for item in snapshot.get("demand", []):
        if isinstance(item, dict) and item.get("work_ref") == ref:
            role = str(item.get("role", "")).strip()
            return role or None
    return None


def hatch(snapshot: dict, carrier_uuid: str | None = None) -> dict:
    plan = reconcile_kernel.evaluate(snapshot)
    action = plan.get("action") or {"kind": "NONE"}
    role = selected_demand_role(snapshot, plan) or ROLE_BY_ACTION.get(
        action.get("kind"), "bounded_carrier"
    )
    return {
        "schema": "hfo.larva_hatch.v0",
        "hatch_version": HATCH_VERSION,
        "carrier_uuid": carrier_uuid or str(uuid.uuid4()),
        "policy_version": plan.get("policy_version"),
        "decision": plan.get("decision"),
        "reason": plan.get("reason"),
        "morph_role": role,
        "action": action,
        "tao_relay_required": plan.get("tao_relay_required", False),
        "snapshot_sha256": plan.get("snapshot_sha256"),
        "plan_sha256": plan.get("plan_sha256"),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("snapshot")
    parser.add_argument("--uuid", dest="carrier_uuid")
    args = parser.parse_args()
    try:
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"decision": "HOLD", "reason": "SNAPSHOT_UNREADABLE", "error": type(exc).__name__}, sort_keys=True))
        return 2
    receipt = hatch(snapshot, args.carrier_uuid)
    print(json.dumps(receipt, sort_keys=True))
    return 2 if receipt["decision"] == "HOLD" else 0


if __name__ == "__main__":
    raise SystemExit(main())
