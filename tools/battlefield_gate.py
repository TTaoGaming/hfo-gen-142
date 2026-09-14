#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = "battlefield.v1"

TOP_REQUIRED = {
    "schema_version", "battlefield_id", "observed_at_utc", "mission_class", "stage",
    "domain", "target", "prestige", "commercial", "evolution", "execution",
    "probability", "budget", "evidence"
}
TOP_ALLOWED = TOP_REQUIRED | {"claim", "notes"}

NESTED_ALLOWED = {
    "target": {
        "board", "track", "metric", "direction", "incumbent_name", "incumbent_score",
        "incumbent_checked_at_utc", "incumbent_url", "rules_url", "submission_url",
        "open_to_user", "public_proof_before_merge", "proof_latency_hours"
    },
    "prestige": {
        "tier", "institution_or_platform", "independent_verifier", "verifier_url",
        "public_attribution", "durable_public_evidence", "real_incumbent_competition",
        "competitor_count", "accepted_submission_protocol", "buyer_legibility"
    },
    "commercial": {
        "buyer_personas", "offer", "demand_evidence_urls", "p_paid_conversation_7d",
        "expected_cash_30d", "expected_cash_90d", "case_study_claim"
    },
    "evolution": {
        "donors", "mutable_axes", "weakness_hypothesis", "gap_evidence_urls",
        "canary", "full_run"
    },
    "execution": {
        "frontier_required", "provider_live", "provider_class", "provider_route",
        "no_weak_fallback", "evaluator_frozen", "local_reproduction_ready",
        "external_auth_ready", "carrier"
    },
    "probability": {
        "p_beat_incumbent", "p_public_proof_24h", "p_public_proof_7d",
        "confidence", "basis"
    },
    "budget": {"max_spend_usd", "max_operator_minutes", "max_wallclock_hours"},
    "claim": {
        "crown_won", "public_result_url", "accepted_protocol_result",
        "beats_incumbent", "attributable_identity"
    },
}

FRONTIER_CLASSES = {
    "frontier",
    "frontier_api",
    "frontier_subscription_bridge",
    "frontier_cloud_binding",
}

PRESTIGE_TRUE = (
    "independent_verifier",
    "public_attribution",
    "durable_public_evidence",
    "real_incumbent_competition",
    "accepted_submission_protocol",
)


def emit(decision, verdict, **detail):
    print(json.dumps({"decision": decision, "verdict": verdict, **detail}, sort_keys=True))
    return 0 if decision == "ADMIT" else 1


def fail(verdict, **detail):
    return emit("HOLD", verdict, **detail)


def parse_utc(value):
    if not isinstance(value, str):
        raise ValueError("not_string")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timezone_required")
    return dt.astimezone(timezone.utc)


def strict_shape(card):
    unknown = sorted(set(card) - TOP_ALLOWED)
    missing = sorted(TOP_REQUIRED - set(card))
    if unknown or missing:
        return fail("INVALID_SCHEMA", unknown=unknown, missing=missing)

    for section, allowed in NESTED_ALLOWED.items():
        if section not in card:
            continue
        value = card[section]
        if not isinstance(value, dict):
            return fail("INVALID_SCHEMA", section=section, problem="must_be_object")
        extra = sorted(set(value) - allowed)
        if extra:
            return fail("INVALID_SCHEMA", section=section, unknown=extra)
    return None


def require_keys(obj, keys, section):
    missing = [k for k in keys if k not in obj]
    if missing:
        return fail("INVALID_SCHEMA", section=section, missing=missing)
    return None


def between_0_1(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 1


def evaluate(card):
    shape = strict_shape(card)
    if shape is not None:
        return shape

    if card["schema_version"] != SCHEMA_VERSION:
        return fail("INVALID_SCHEMA_VERSION", expected=SCHEMA_VERSION)

    if card["mission_class"] not in {"prestige_crown", "case_study", "income_contract"}:
        return fail("INVALID_MISSION_CLASS")
    if card["stage"] not in {"scout", "canary", "attack", "claim"}:
        return fail("INVALID_STAGE")

    for section, keys in {
        "target": (
            "board", "track", "metric", "direction", "incumbent_name", "incumbent_score",
            "incumbent_checked_at_utc", "incumbent_url", "rules_url", "open_to_user",
            "public_proof_before_merge", "proof_latency_hours"
        ),
        "prestige": (
            "tier", "institution_or_platform", "independent_verifier", "verifier_url",
            "public_attribution", "durable_public_evidence", "real_incumbent_competition",
            "competitor_count", "accepted_submission_protocol", "buyer_legibility"
        ),
        "commercial": (
            "buyer_personas", "offer", "demand_evidence_urls", "p_paid_conversation_7d",
            "expected_cash_30d", "expected_cash_90d", "case_study_claim"
        ),
        "evolution": (
            "donors", "mutable_axes", "weakness_hypothesis", "gap_evidence_urls",
            "canary", "full_run"
        ),
        "execution": (
            "frontier_required", "provider_live", "provider_class", "provider_route",
            "no_weak_fallback", "evaluator_frozen", "local_reproduction_ready",
            "external_auth_ready", "carrier"
        ),
        "probability": (
            "p_beat_incumbent", "p_public_proof_24h", "p_public_proof_7d",
            "confidence", "basis"
        ),
        "budget": ("max_spend_usd", "max_operator_minutes", "max_wallclock_hours"),
    }.items():
        result = require_keys(card[section], keys, section)
        if result is not None:
            return result

    t = card["target"]
    p = card["prestige"]
    c = card["commercial"]
    e = card["evolution"]
    x = card["execution"]
    prob = card["probability"]
    budget = card["budget"]

    try:
        age_h = (datetime.now(timezone.utc) - parse_utc(t["incumbent_checked_at_utc"])).total_seconds() / 3600
    except Exception as exc:
        return fail("INVALID_INCUMBENT_TIMESTAMP", error=str(exc))
    if card["stage"] in {"canary", "attack", "claim"} and (age_h < -1 or age_h > 24):
        return fail("STALE_BATTLEFIELD", incumbent_age_hours=round(age_h, 2))

    if t["direction"] not in {"maximize", "minimize"} or t["open_to_user"] is not True:
        return fail("KILL_INELIGIBLE_BATTLEFIELD")

    if card["mission_class"] in {"prestige_crown", "case_study"}:
        if p["independent_verifier"] is not True or p["durable_public_evidence"] is not True:
            return fail("KILL_DEMO", reason="external_verifier_or_public_evidence_missing")

    if card["mission_class"] == "prestige_crown":
        if p["tier"] not in {"A", "B"}:
            return fail("KILL_PROXY", reason="prestige_tier_below_floor")
        missing_prestige = [k for k in PRESTIGE_TRUE if p.get(k) is not True]
        if missing_prestige:
            return fail("KILL_PROXY", missing=missing_prestige)
        if not isinstance(p["competitor_count"], int) or p["competitor_count"] < 3:
            return fail("KILL_PROXY", reason="insufficient_real_competition")
        if not between_0_1(p["buyer_legibility"]) or p["buyer_legibility"] < 0.60:
            return fail("KILL_PROXY", reason="buyer_legibility_below_floor")
        if t["public_proof_before_merge"] is not True and t["proof_latency_hours"] > 168:
            return fail("KILL_PUBLICATION_TRAP")

    if not isinstance(c["buyer_personas"], list) or len(c["buyer_personas"]) < 1:
        return fail("KILL_NO_BUYER")
    if not isinstance(c["demand_evidence_urls"], list) or len(c["demand_evidence_urls"]) < 1:
        return fail("KILL_NO_INCOME_PATH", reason="no_declared_demand_evidence")
    if not isinstance(c["offer"], str) or len(c["offer"].strip()) < 12:
        return fail("KILL_NO_INCOME_PATH", reason="offer_not_specific")
    if not between_0_1(c["p_paid_conversation_7d"]):
        return fail("INVALID_PROBABILITY", field="commercial.p_paid_conversation_7d")
    if not isinstance(c["expected_cash_30d"], (int, float)) or c["expected_cash_30d"] <= 0:
        return fail("KILL_NO_INCOME_PATH", reason="expected_cash_30d_not_positive")

    donors = e["donors"]
    if not isinstance(donors, list) or len(donors) < 2:
        return fail("KILL_NO_DONOR_DENSITY")
    if any(not isinstance(d, dict) or d.get("allowed") is not True or not d.get("url") for d in donors):
        return fail("KILL_DONOR_POLICY", reason="donor_missing_url_or_permission")
    if not isinstance(e["mutable_axes"], list) or len(e["mutable_axes"]) < 2:
        return fail("KILL_NOT_EVOLVABLE", reason="fewer_than_two_mutable_axes")
    if not isinstance(e["weakness_hypothesis"], str) or len(e["weakness_hypothesis"].strip()) < 20:
        return fail("KILL_RANDOM_FIGHT", reason="no_specific_weakness_hypothesis")
    if not isinstance(e["gap_evidence_urls"], list) or len(e["gap_evidence_urls"]) < 1:
        return fail("KILL_RANDOM_FIGHT", reason="no_gap_evidence")

    canary = e["canary"]
    full_run = e["full_run"]
    if not isinstance(canary, dict) or not isinstance(full_run, dict):
        return fail("INVALID_SCHEMA", section="evolution", problem="canary/full_run_must_be_objects")
    for field in ("runtime_minutes", "cost_usd", "status", "promotion_rule"):
        if field not in canary:
            return fail("INVALID_SCHEMA", section="evolution.canary", missing=[field])
    for field in ("runtime_minutes", "cost_usd"):
        if field not in full_run:
            return fail("INVALID_SCHEMA", section="evolution.full_run", missing=[field])

    if canary["runtime_minutes"] > budget["max_wallclock_hours"] * 60:
        return fail("KILL_CANARY_TOO_SLOW")
    if canary["cost_usd"] > budget["max_spend_usd"]:
        return fail("KILL_CANARY_TOO_EXPENSIVE")

    if x["frontier_required"] is True:
        if x["no_weak_fallback"] is not True:
            return fail("KILL_SUBSTITUTION", reason="weak_fallback_allowed")
        if x["provider_live"] is not True:
            return fail("BLOCKED_PROVIDER_AUTH")
        if x["provider_class"] not in FRONTIER_CLASSES:
            return fail("BLOCKED_PROVIDER_CLASS", provider_class=x["provider_class"])

    if card["stage"] in {"canary", "attack", "claim"} and x["evaluator_frozen"] is not True:
        return fail("BLOCKED_EVALUATOR_NOT_FROZEN")
    if card["stage"] in {"attack", "claim"} and canary["status"] != "PASS":
        return fail("HOLD_CANARY_FIRST", status=canary["status"])
    if card["stage"] == "attack" and x["external_auth_ready"] is not True:
        return fail("BLOCKED_EXTERNAL_AUTH")

    for field in ("p_beat_incumbent", "p_public_proof_24h", "p_public_proof_7d", "confidence"):
        if not between_0_1(prob[field]):
            return fail("INVALID_PROBABILITY", field=f"probability.{field}")
    if not isinstance(prob["basis"], str) or len(prob["basis"].strip()) < 30:
        return fail("INVALID_PROBABILITY", field="probability.basis", reason="basis_too_thin")

    if not isinstance(card["evidence"], list) or len(card["evidence"]) < 3:
        return fail("INSUFFICIENT_EVIDENCE", minimum=3)

    if card["stage"] == "claim":
        claim = card.get("claim")
        if not isinstance(claim, dict):
            return fail("REJECT_UNPROVEN_CROWN", reason="missing_claim_object")
        result = require_keys(
            claim,
            ("crown_won", "public_result_url", "accepted_protocol_result",
             "beats_incumbent", "attributable_identity"),
            "claim",
        )
        if result is not None:
            return result
        if claim["crown_won"] is not True:
            return fail("REJECT_UNPROVEN_CROWN", reason="crown_won_not_true")
        if claim["accepted_protocol_result"] is not True or claim["beats_incumbent"] is not True:
            return fail("REJECT_UNPROVEN_CROWN")
        if not claim["public_result_url"] or not claim["attributable_identity"]:
            return fail("REJECT_UNPROVEN_CROWN", reason="missing_public_attribution")

    prestige_weight = {"A": 1.0, "B": 0.75, "C": 0.4}.get(p["tier"], 0.0)
    donor_factor = min(1.0, len(donors) / 5.0)
    publication_factor = min(1.0, 24.0 / max(float(t["proof_latency_hours"]), 1.0))
    burden = 1.0 + budget["max_operator_minutes"] / 60.0 + max(canary["cost_usd"], 0) / 100.0
    routing_score = (
        prestige_weight
        * p["buyer_legibility"]
        * prob["p_beat_incumbent"]
        * prob["p_public_proof_7d"]
        * donor_factor
        * publication_factor
        / burden
    )
    return emit(
        "ADMIT",
        f"ADMIT_{card['stage'].upper()}",
        routing_score=round(routing_score, 6),
        battlefield_id=card["battlefield_id"],
    )


def main():
    parser = argparse.ArgumentParser(description="Fail-closed battlefield admission gate")
    parser.add_argument("card")
    args = parser.parse_args()
    try:
        card = json.loads(Path(args.card).read_text(encoding="utf-8"))
    except Exception as exc:
        return fail("INVALID_JSON", error=str(exc))
    return evaluate(card)


if __name__ == "__main__":
    raise SystemExit(main())
