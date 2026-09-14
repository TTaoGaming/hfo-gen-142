#!/usr/bin/env python3
"""Fail-closed terminal handoff gate: Tao may not be the hot-loop router."""
import argparse
import json
import re
from pathlib import Path

SCHEMA = "hfo.terminal-handoff.v1"
HUMAN_BOUNDARIES = {
    "secret", "oauth", "2fa", "payment", "permission",
    "protected_merge", "irreversible_external_submit",
}
AUTO_OWNERS = {"hfo-sigrun-va-r0", "github-actions", "cloudflare-workflow"}
TERMINAL_STATES = {"PASS", "FAIL", "HOLD", "KILL"}
AUTO_MODES = {"AUTO_DISPATCH", "RECONCILE", "MISSION_COMPLETE"}
RECEIPT_STATUSES = {"ACCEPTED", "SCHEDULED", "RUNNING", "COMPLETED", "ARMED"}
HEX64 = re.compile(r"^[0-9a-f]{64}$")
FORBIDDEN_OPERATOR_PHRASES = (
    "launch next", "launch agent", "run next", "restart worker", "restart agent",
    "retry", "route", "gather thread", "gather result", "monitor", "check status", "check back",
)
REQUIRED = {
    "schema", "mission_id", "actor_id", "terminal_state",
    "tao_relay_required", "operator_action_required", "next",
}
RECEIPT_REQUIRED = {
    "receipt_type", "owner", "receipt_id", "status", "observed_utc",
    "provenance_ref", "receipt_sha256", "self_attested",
}


def verdict(code, **detail):
    print(json.dumps({"decision": "HOLD", "verdict": code, **detail}, sort_keys=True))
    return 1


def receipt_error(owner, receipt, expected_work_ref=None, allow_armed=False):
    if not isinstance(receipt, dict):
        return "STRUCTURED_DISPATCH_RECEIPT_REQUIRED", {}
    missing = sorted(RECEIPT_REQUIRED - set(receipt))
    if missing:
        return "DISPATCH_RECEIPT_FIELDS", {"missing": missing}
    if receipt.get("owner") != owner:
        return "DISPATCH_RECEIPT_OWNER_MISMATCH", {"declared": receipt.get("owner"), "expected": owner}
    if receipt.get("self_attested") is not False:
        return "SELF_ATTESTED_TRANSITION_FORBIDDEN", {}
    status = receipt.get("status")
    if status not in RECEIPT_STATUSES:
        return "DISPATCH_RECEIPT_STATUS_INVALID", {"declared": status}
    if status == "ARMED" and not allow_armed:
        return "DISPATCH_NOT_YET_MATERIALIZED", {}
    if not HEX64.fullmatch(str(receipt.get("receipt_sha256", ""))):
        return "DISPATCH_RECEIPT_SHA256_INVALID", {}
    observed = str(receipt.get("observed_utc", ""))
    if "T" not in observed or not observed.endswith("Z"):
        return "DISPATCH_RECEIPT_UTC_INVALID", {"declared": observed}
    provenance = str(receipt.get("provenance_ref", ""))
    rtype = receipt.get("receipt_type")
    if owner == "github-actions":
        allowed = (
            rtype == "github_actions_run" and "/actions/runs/" in provenance,
            rtype == "github_workflow_dispatch" and "/actions/workflows/" in provenance and provenance.endswith("/dispatches"),
            allow_armed and rtype == "github_actions_watch" and "/actions/workflows/" in provenance,
        )
        if not any(allowed):
            return "GITHUB_ACTIONS_RECEIPT_UNBOUND", {"receipt_type": rtype, "provenance_ref": provenance}
    elif owner == "hfo-sigrun-va-r0":
        allowed = (
            rtype == "sigrun_transition" and provenance.startswith("sigrun-history:"),
            allow_armed and rtype == "sigrun_watch" and provenance.startswith("sigrun-watch:"),
        )
        if not any(allowed):
            return "SIGRUN_RECEIPT_UNBOUND", {"receipt_type": rtype, "provenance_ref": provenance}
    elif owner == "cloudflare-workflow":
        allowed = (
            rtype == "cloudflare_workflow" and provenance.startswith("cloudflare-workflow:"),
            allow_armed and rtype == "cloudflare_workflow_watch" and provenance.startswith("cloudflare-workflow-watch:"),
        )
        if not any(allowed):
            return "CLOUDFLARE_RECEIPT_UNBOUND", {"receipt_type": rtype, "provenance_ref": provenance}
    if expected_work_ref is not None and receipt.get("work_ref") != expected_work_ref:
        return "DISPATCH_RECEIPT_WORK_MISMATCH", {
            "declared": receipt.get("work_ref"), "expected": expected_work_ref,
        }
    return None


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
        lowered = action.lower()
        if any(phrase in lowered for phrase in FORBIDDEN_OPERATOR_PHRASES):
            return verdict("HUMAN_BOUNDARY_CONTAINS_OPERATOR_WORK", action=action)
        evidence = doc.get("human_boundary_evidence")
        required_evidence = {"target", "machine_attempt_ref", "why_human_only", "minimal_action"}
        if not isinstance(evidence, dict) or required_evidence - set(evidence):
            return verdict("HUMAN_BOUNDARY_EVIDENCE_REQUIRED")
        if str(evidence.get("minimal_action", "")).strip() != action:
            return verdict("HUMAN_ACTION_NOT_MINIMAL_BOUNDARY_ACTION")
        resume = nxt.get("resume")
        if not isinstance(resume, dict):
            return verdict("AUTOMATIC_RESUME_REQUIRED")
        owner = resume.get("owner")
        if owner not in AUTO_OWNERS:
            return verdict("AUTO_RESUME_OWNER_INVALID", declared=owner)
        if not resume.get("resume_condition") or not resume.get("watch_ref"):
            return verdict("AUTO_RESUME_WATCH_REQUIRED")
        err = receipt_error(owner, resume.get("resume_receipt"), allow_armed=True)
        if err:
            return verdict(err[0], **err[1])
    else:
        if doc.get("human_boundary") not in (None, "", "NONE"):
            return verdict("SPURIOUS_HUMAN_BOUNDARY")
        if str(doc.get("operator_action_required", "NONE")).upper() != "NONE":
            return verdict("BLOCKED_TAO_HOT_LOOP")
        mode = nxt.get("mode")
        if mode not in AUTO_MODES:
            return verdict("AUTO_HANDOFF_MODE_REQUIRED", declared=mode)
        if mode in {"AUTO_DISPATCH", "RECONCILE"}:
            owner = nxt.get("owner")
            if owner not in AUTO_OWNERS:
                return verdict("AUTO_HANDOFF_OWNER_INVALID", declared=owner)
            work_ref = nxt.get("work_ref") if mode == "AUTO_DISPATCH" else None
            if mode == "AUTO_DISPATCH" and not work_ref:
                return verdict("NEXT_WORK_REF_REQUIRED")
            err = receipt_error(
                owner,
                nxt.get("dispatch_receipt"),
                expected_work_ref=work_ref,
                allow_armed=(mode == "RECONCILE"),
            )
            if err:
                return verdict(err[0], **err[1])
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
