#!/usr/bin/env python3
"""Pure deterministic Gen142 reconciliation policy.

This module owns no queue, scheduler, lease, actor state, credentials, or effects.
It maps an authoritative snapshot to exactly one bounded next plan.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "hfo.reconcile_snapshot.v0"
POLICY_VERSION = "gen142-reconciler-r0"
ACTOR_OWNER = "hfo-sigrun-va-r0"
ACTIVE_OWNER_PHASES = {"READY", "CLAIMED", "RESULT", "VERIFIED", "ACKED"}
VALID_PHASES = ACTIVE_OWNER_PHASES | {"IDLE", "WAITING_WORKER", "TERMINAL"}
HUMAN_BOUNDARIES = {
    "secret", "oauth", "2fa", "payment", "permission",
    "protected_merge", "irreversible_external_submit",
}


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


def hold(snapshot, code, **detail):
    base = {
        "schema": "hfo.reconcile_plan.v0",
        "policy_version": POLICY_VERSION,
        "decision": "HOLD",
        "reason": code,
        "tao_relay_required": False,
        "action": {"kind": "NONE"},
        **detail,
    }
    base["snapshot_sha256"] = digest(snapshot)
    base["plan_sha256"] = digest(base)
    return base


def admitted_demand(snapshot):
    out = []
    for item in snapshot.get("demand", []):
        if not isinstance(item, dict):
            continue
        if item.get("admitted") is not True or item.get("blocked") is True:
            continue
        ref = str(item.get("work_ref", "")).strip()
        priority = item.get("priority")
        if not ref or not isinstance(priority, int):
            continue
        out.append((priority, ref, item))
    out.sort(key=lambda x: (-x[0], x[1]))
    return [x[2] for x in out]


def live_worker_routes(snapshot):
    routes = []
    for route in snapshot.get("worker_routes", []):
        if not isinstance(route, dict):
            continue
        if route.get("live") is True and route.get("admitted") is True:
            rid = str(route.get("route_id", "")).strip()
            if rid:
                routes.append((rid, route))
    routes.sort(key=lambda x: x[0])
    return [x[1] for x in routes]


def plan(snapshot, decision, reason, action, tao=False, **detail):
    out = {
        "schema": "hfo.reconcile_plan.v0",
        "policy_version": POLICY_VERSION,
        "decision": decision,
        "reason": reason,
        "tao_relay_required": tao,
        "action": action,
        **detail,
    }
    out["snapshot_sha256"] = digest(snapshot)
    out["plan_sha256"] = digest(out)
    return out


def evaluate(snapshot):
    if not isinstance(snapshot, dict):
        return hold(snapshot, "SNAPSHOT_TYPE")
    if snapshot.get("schema") != SCHEMA:
        return hold(snapshot, "SNAPSHOT_SCHEMA")
    if snapshot.get("policy_version") != POLICY_VERSION:
        return hold(snapshot, "POLICY_VERSION_MISMATCH")

    actor = snapshot.get("actor")
    if not isinstance(actor, dict) or actor.get("owner") != ACTOR_OWNER:
        return hold(snapshot, "ACTOR_OWNER_INVALID")
    phase = actor.get("phase")
    if phase not in VALID_PHASES:
        return hold(snapshot, "ACTOR_PHASE_INVALID", phase=phase)

    boundary = snapshot.get("human_boundary") or {"active": False}
    if not isinstance(boundary, dict):
        return hold(snapshot, "HUMAN_BOUNDARY_INVALID")
    if boundary.get("active") is True:
        if boundary.get("type") not in HUMAN_BOUNDARIES:
            return hold(snapshot, "HUMAN_BOUNDARY_TYPE_INVALID")
        if boundary.get("resume_armed") is not True or not boundary.get("watch_ref"):
            return hold(snapshot, "HUMAN_BOUNDARY_RESUME_NOT_ARMED")
        action = str(boundary.get("minimal_action", "")).strip()
        if not action:
            return hold(snapshot, "HUMAN_BOUNDARY_ACTION_MISSING")
        return plan(
            snapshot, "WAIT", "WAIT_HUMAN_UNLOCK",
            {"kind": "WAIT_HUMAN_UNLOCK", "boundary": boundary["type"], "watch_ref": boundary["watch_ref"]},
            tao=True, operator_action_required=action,
        )

    dispatches = snapshot.get("dispatches", [])
    if not isinstance(dispatches, list):
        return hold(snapshot, "DISPATCH_LIST_INVALID")
    active = [d for d in dispatches if isinstance(d, dict) and d.get("active") is True]
    if len(active) > 1:
        return hold(snapshot, "DUPLICATE_ACTIVE_DISPATCH", count=len(active))
    if len(active) == 1:
        return plan(snapshot, "WAIT", "DISPATCH_ALREADY_ACTIVE", {"kind": "WAIT_DISPATCH", "dispatch_ref": active[0].get("dispatch_ref")})

    if phase in ACTIVE_OWNER_PHASES:
        return plan(snapshot, "WAIT", "SEMANTIC_OWNER_ADVANCING", {"kind": "WAIT_ACTOR", "phase": phase})

    if phase == "WAITING_WORKER":
        if actor.get("worker_job_available") is True:
            routes = live_worker_routes(snapshot)
            if routes:
                route = routes[0]
                return plan(snapshot, "ACT", "WORKER_JOB_READY", {
                    "kind": "DISPATCH_WORKER",
                    "route_id": route["route_id"],
                    "workitem_id": actor.get("workitem_id"),
                })
        return plan(snapshot, "WAIT", "WORKER_OWNER_DEADLINE", {"kind": "WAIT_WORKER_DEADLINE"})

    if phase == "TERMINAL" and actor.get("terminal_consumed") is not True:
        return plan(snapshot, "ACT", "TERMINAL_NEEDS_CONSUMER", {
            "kind": "CONSUME_TERMINAL",
            "workitem_id": actor.get("workitem_id"),
            "terminal_ref": actor.get("terminal_ref"),
        })

    ready = admitted_demand(snapshot)
    if ready and phase in {"IDLE", "TERMINAL"}:
        item = ready[0]
        return plan(snapshot, "ACT", "ADMITTED_DEMAND_READY", {
            "kind": "SUBMIT_NEXT",
            "owner": ACTOR_OWNER,
            "work_ref": item["work_ref"],
            "priority": item["priority"],
        })

    return plan(snapshot, "IDLE", "NO_ADMITTED_DEMAND", {"kind": "NONE"})


def main():
    p = argparse.ArgumentParser()
    p.add_argument("snapshot")
    args = p.parse_args()
    try:
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"decision": "HOLD", "reason": "SNAPSHOT_UNREADABLE", "error": type(exc).__name__}, sort_keys=True))
        return 2
    result = evaluate(snapshot)
    print(json.dumps(result, sort_keys=True))
    return 2 if result["decision"] == "HOLD" else 0


if __name__ == "__main__":
    raise SystemExit(main())
