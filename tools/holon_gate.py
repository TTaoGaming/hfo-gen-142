#!/usr/bin/env python3
"""Fail-closed admission gate for Gen142 durable holon missions.

This is a forcing function, not a scheduler or state owner.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "hfo.holon-mission.v1"
SEMANTIC_OWNER = "hfo-sigrun-va-r0"
RECEIPT_SINK = "github:TTaoGaming/hfo-gen-142#13"
FRONTIER_CLASSES = {"frontier", "frontier_api", "frontier_subscription_bridge"}
BILLING_CLASSES = {"ZERO_MARGINAL", "PREPAID_OR_HARD_CAPPED", "METERED_PAID"}
AUTHORITY_ENVELOPE = Path(__file__).resolve().parents[1] / "AUTHORITY_ENVELOPE_V1.json"
HUMAN_BOUNDARIES = {
    "secret", "oauth", "2fa", "payment", "permission",
    "protected_merge", "irreversible_external_submit",
}
REQUIRED = {
    "schema", "mission_id", "actor_id", "parent_actor_id", "carrier_id",
    "domain", "domain_explicit", "intent", "fitness", "verifier",
    "deadline_utc", "max_attempts", "max_spend_usd", "effect_ceiling",
    "receipt_sink", "semantic_owner", "provider_policy", "human_boundaries",
    "control_plane", "promotion",
}

def verdict(code, mission=None, **detail):
    out = {"decision": "HOLD", "verdict": code, **detail}
    if mission:
        out["mission_id"] = mission.get("mission_id")
        out["actor_id"] = mission.get("actor_id")
    print(json.dumps(out, sort_keys=True))
    return 1

def parse_utc(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)

def evaluate(mission, raw=b""):
    if not isinstance(mission, dict):
        return verdict("MISSION_TYPE")
    missing = sorted(REQUIRED - set(mission))
    if missing:
        return verdict("MISSION_REQUIRED_FIELDS", mission, missing=missing)
    if mission.get("schema") != SCHEMA:
        return verdict("MISSION_SCHEMA", mission, declared=mission.get("schema"))
    if not mission.get("mission_id") or not mission.get("actor_id") or not mission.get("carrier_id"):
        return verdict("IDENTITY_REQUIRED", mission)
    if mission["actor_id"] == mission["carrier_id"]:
        return verdict("ACTOR_CARRIER_COLLAPSE", mission)

    domain = str(mission.get("domain", "")).strip()
    explicit = mission.get("domain_explicit") is True
    if not domain:
        return verdict("DOMAIN_REQUIRED", mission)
    if not explicit and domain.lower() != "domain_agnostic":
        return verdict("BLOCKED_DOMAIN_PROXY", mission, declared_domain=domain)

    fitness = mission.get("fitness")
    if not isinstance(fitness, dict) or not fitness.get("primary"):
        return verdict("FITNESS_REQUIRED", mission)
    if fitness.get("external_verification_required") is not True:
        return verdict("EXTERNAL_VERIFICATION_REQUIRED", mission)
    verifier = mission.get("verifier")
    if not isinstance(verifier, dict) or not verifier.get("id"):
        return verdict("VERIFIER_REQUIRED", mission)
    if verifier.get("frozen") is not True:
        return verdict("VERIFIER_NOT_FROZEN", mission)

    try:
        deadline = parse_utc(mission["deadline_utc"])
    except Exception:
        return verdict("DEADLINE_INVALID", mission)
    if deadline <= datetime.now(timezone.utc):
        return verdict("DEADLINE_EXPIRED", mission, deadline_utc=mission["deadline_utc"])
    attempts = mission.get("max_attempts")
    if not isinstance(attempts, int) or not 1 <= attempts <= 20:
        return verdict("ATTEMPT_BOUND_INVALID", mission, max_attempts=attempts)
    spend = mission.get("max_spend_usd")
    if not isinstance(spend, (int, float)) or isinstance(spend, bool) or spend < 0:
        return verdict("SPEND_BOUND_INVALID", mission, max_spend_usd=spend)
    try:
        authority_envelope = json.loads(AUTHORITY_ENVELOPE.read_text(encoding="utf-8"))
        spend_ceiling = authority_envelope["spend"]["incremental_usd_per_day"]
    except Exception as exc:
        return verdict("AUTHORITY_ENVELOPE_UNREADABLE", mission, error=type(exc).__name__)
    if not isinstance(spend_ceiling, (int, float)) or isinstance(spend_ceiling, bool) or spend_ceiling < 0:
        return verdict("AUTHORITY_SPEND_CEILING_INVALID", mission, declared=spend_ceiling)
    if spend > spend_ceiling:
        return verdict("BLOCKED_SPEND_AUTHORITY", mission, declared=spend, ceiling=spend_ceiling)
    if not mission.get("effect_ceiling"):
        return verdict("EFFECT_CEILING_REQUIRED", mission)

    if mission.get("receipt_sink") != RECEIPT_SINK:
        return verdict("RENDEZVOUS_MISMATCH", mission, required=RECEIPT_SINK)
    if mission.get("semantic_owner") != SEMANTIC_OWNER:
        return verdict("DUPLICATE_SEMANTIC_OWNER", mission, required=SEMANTIC_OWNER)

    cp = mission.get("control_plane")
    if not isinstance(cp, dict):
        return verdict("CONTROL_PLANE_POLICY_REQUIRED", mission)
    if cp.get("new_control_plane") is True:
        return verdict("BLOCKED_NEW_CONTROL_PLANE", mission)
    if cp.get("recover_probe_repair_completed") is not True:
        return verdict("RECOVER_PROBE_REPAIR_FIRST", mission)

    pp = mission.get("provider_policy")
    if not isinstance(pp, dict) or pp.get("role") != "leaf":
        return verdict("PROVIDER_NOT_LEAF", mission)
    billing_class = pp.get("billing_class")
    if billing_class not in BILLING_CLASSES:
        return verdict("BLOCKED_PROVIDER_BILLING_CLASS", mission, declared=billing_class)
    if pp.get("allow_paid_fallback") is not False:
        return verdict("BLOCKED_PAID_PROVIDER_FALLBACK", mission)
    if spend_ceiling == 0 and billing_class != "ZERO_MARGINAL":
        return verdict("BLOCKED_NONZERO_MARGINAL_ROUTE", mission, declared=billing_class)
    if billing_class == "ZERO_MARGINAL":
        if pp.get("zero_marginal_verified") is not True:
            return verdict("BLOCKED_ZERO_MARGINAL_UNVERIFIED", mission)
        if not pp.get("billing_evidence_ref"):
            return verdict("BILLING_EVIDENCE_REQUIRED", mission)
        if not pp.get("quota_source"):
            return verdict("QUOTA_SOURCE_REQUIRED", mission)
        if pp.get("quota_exhaustion") not in {"ROTATE_OR_HOLD", "HOLD"}:
            return verdict("QUOTA_EXHAUSTION_POLICY_REQUIRED", mission)
    if pp.get("frontier_required") is True:
        if pp.get("provider_live") is not True:
            return verdict("BLOCKED_PROVIDER_AUTH", mission)
        if pp.get("provider_class") not in FRONTIER_CLASSES:
            return verdict("BLOCKED_PROVIDER_CLASS", mission, declared=pp.get("provider_class"))
        if pp.get("allow_local_fallback") is not False:
            return verdict("BLOCKED_PROVIDER_FALLBACK", mission)

    boundaries = mission.get("human_boundaries")
    if not isinstance(boundaries, list) or any(x not in HUMAN_BOUNDARIES for x in boundaries):
        return verdict("HUMAN_BOUNDARY_INVALID", mission)
    if mission.get("tao_relay_required") is True and not boundaries:
        return verdict("TAO_RELAY_NOT_AUTHORITY_BOUND", mission)

    promotion = mission.get("promotion")
    if not isinstance(promotion, dict):
        return verdict("PROMOTION_POLICY_REQUIRED", mission)
    if promotion.get("requested") is True:
        if not promotion.get("verifier_receipt"):
            return verdict("PROMOTION_WITHOUT_VERIFIER", mission)
        if not promotion.get("consumer_ack"):
            return verdict("PROMOTION_WITHOUT_CONSUMER_ACK", mission)

    out = {
        "decision": "ADMIT",
        "verdict": "ADMIT",
        "schema": SCHEMA,
        "mission_id": mission["mission_id"],
        "actor_id": mission["actor_id"],
        "carrier_id": mission["carrier_id"],
        "semantic_owner": SEMANTIC_OWNER,
        "receipt_sink": RECEIPT_SINK,
        "mission_sha256": hashlib.sha256(raw or json.dumps(mission, sort_keys=True).encode()).hexdigest(),
    }
    print(json.dumps(out, sort_keys=True))
    return 0

def main():
    p = argparse.ArgumentParser()
    p.add_argument("mission")
    args = p.parse_args()
    raw = Path(args.mission).read_bytes()
    try:
        mission = json.loads(raw)
    except Exception as exc:
        return verdict("MISSION_UNREADABLE", error=type(exc).__name__)
    return evaluate(mission, raw)

if __name__ == "__main__":
    raise SystemExit(main())
