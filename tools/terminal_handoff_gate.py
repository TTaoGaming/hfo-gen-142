#!/usr/bin/env python3
"""Fail-closed terminal handoff gate: Tao may not be the hot-loop router."""
import argparse
import json
from pathlib import Path

SCHEMA = "hfo.terminal-handoff.v1"
HUMAN_BOUNDARIES = {
    "secret", "oauth", "2fa", "payment", "permission",
    "protected_merge", "irreversible_external_submit",
}
AUTO_OWNERS = {"hfo-sigrun-va-r0", "github-actions", "cloudflare-workflow"}
TERMINAL_STATES = {"PASS", "FAIL", "HOLD", "KILL"}
AUTO_MODES = {"AUTO_DISPATCH", "RECONCILE", "MISSION_COMPLETE"}
REQUIRED = {
    "schema", "mission_id", "actor_id", "terminal_state",
    "tao_relay_required", "operator_action_required", "next",
}


def verdict(code, **detail):
    print(json.dumps({"decision": "HOLD", "verdict": code, **detail}, sort_keys=True))
    return 1


def evaluate(doc):
    if not isinstance(doc, dict):
        return verdict("HANDOFF_TYPE")
    missing = sorted(REQUIRED - set(doc))
    if missing:
        return verdict("HANDOFF_REQUIRED_FIELDS", missing=missing)
    if doc.get("schema") != SCHEMA:
        return verdict("HANDOFF_SCHEMA", declared=doc.get("schema"))
    if not doc.get("mission_id") or not doc.get("actor_id"):
        return verdict("IDENTITY_REQUIRED")
    if doc.get("terminal_state") not in TERMINAL_STATES:
        return verdict("TERMINAL_STATE_INVALID", declared=doc.get("terminal_state"))

    nxt = doc.get("next")
    if not isinstance(nxt, dict) or not nxt.get("mode"):
        return verdict("NEXT_HANDOFF_REQUIRED")

    relay = doc.get("tao_relay_required")
    if not isinstance(relay, bool):
        return verdict("TAO_RELAY_BOOLEAN_REQUIRED")

    if relay:
        boundary = doc.get("human_boundary")
        if boundary not in HUMAN_BOUNDARIES:
            return verdict("TAO_RELAY_NOT_AUTHORITY_BOUND", boundary=boundary)
        if nxt.get("mode") != "HUMAN_BOUNDARY":
            return verdict("HUMAN_BOUNDARY_MODE_REQUIRED")
        action = str(doc.get("operator_action_required", "")).strip()
        if not action or action.upper() == "NONE":
            return verdict("HUMAN_ACTION_MUST_BE_NAMED")
    else:
        if doc.get("human_boundary") not in (None, "", "NONE"):
            return verdict("SPURIOUS_HUMAN_BOUNDARY")
        if str(doc.get("operator_action_required", "NONE")).upper() != "NONE":
            return verdict("BLOCKED_TAO_HOT_LOOP")
        mode = nxt.get("mode")
        if mode not in AUTO_MODES:
            return verdict("AUTO_HANDOFF_MODE_REQUIRED", declared=mode)
        if mode in {"AUTO_DISPATCH", "RECONCILE"}:
            if nxt.get("owner") not in AUTO_OWNERS:
                return verdict("AUTO_HANDOFF_OWNER_INVALID", declared=nxt.get("owner"))
            if not nxt.get("dispatch_receipt"):
                return verdict("DISPATCH_RECEIPT_REQUIRED")
        if mode == "AUTO_DISPATCH" and not nxt.get("work_ref"):
            return verdict("NEXT_WORK_REF_REQUIRED")
        if mode == "MISSION_COMPLETE":
            if doc.get("mission_complete") is not True:
                return verdict("MISSION_COMPLETE_NOT_PROVEN")
            if not doc.get("verifier_receipt") or not doc.get("consumer_ack"):
                return verdict("MISSION_COMPLETE_EVIDENCE_REQUIRED")

    print(json.dumps({
        "decision": "ADMIT_TERMINAL",
        "verdict": "ADMIT_TERMINAL",
        "mission_id": doc["mission_id"],
        "actor_id": doc["actor_id"],
        "next_mode": nxt["mode"],
        "tao_relay_required": relay,
    }, sort_keys=True))
    return 0


def main():
    p = argparse.ArgumentParser()
    p.add_argument("handoff")
    args = p.parse_args()
    try:
        doc = json.loads(Path(args.handoff).read_text(encoding="utf-8"))
    except Exception as exc:
        return verdict("HANDOFF_UNREADABLE", error=type(exc).__name__)
    return evaluate(doc)


if __name__ == "__main__":
    raise SystemExit(main())
