#!/usr/bin/env python3
"""Thin deterministic reducer for one durable-actor mission transition.

This is not a scheduler or queue. Cloudflare Durable Objects keep semantic
ownership of identity/claim/fence/deadline/terminal state. This reducer only
admits evidence-backed heritage/skill promotion after a carrier episode.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ADMITTED_VERIFIERS = {
    "INDEPENDENT_VERIFIER",
    "FROZEN_MECHANICAL_VERIFIER",
    "PROVIDER_WORLD_RECEIPT",
    "MARKET_HUMAN_OUTCOME",
}
SUCCESS_TERMINALS = {"TERMINAL_SUCCESS", "VERIFIED_SUCCESS"}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _event_id(value: Any) -> str:
    return "sha256:" + hashlib.sha256(_canonical(value)).hexdigest()


def _hold(code: str, detail: str) -> dict[str, Any]:
    return {
        "state": "HOLD",
        "code": code,
        "detail": detail,
        "next_mission_ready": False,
        "promotion_allowed": False,
    }


def _require_obj(payload: dict[str, Any], key: str) -> dict[str, Any]:
    value = payload.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"{key} object required")
    return value


def _require_text(obj: dict[str, Any], field: str) -> str:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} non-empty string required")
    return value.strip()


def reduce_transition(payload: dict[str, Any]) -> dict[str, Any]:
    actor = _require_obj(payload, "actor")
    mission = _require_obj(payload, "mission")
    carrier = _require_obj(payload, "carrier")
    result = _require_obj(payload, "result")

    actor_id = _require_text(actor, "actor_id")
    mission_id = _require_text(mission, "mission_id")
    episode_id = _require_text(carrier, "carrier_episode_id")

    if mission.get("frontier_required") is True:
        if carrier.get("provider_tier") != "FRONTIER":
            return _hold(
                "BLOCK_FRONTIER_SUBSTITUTION",
                "frontier mission cannot use local/unknown carrier",
            )
    receipts = carrier.get("qualification_receipts")
    if not isinstance(receipts, list) or not receipts:
        return _hold("BLOCK_UNQUALIFIED_CARRIER", "qualification_receipts required")

    terminal = result.get("terminal_state")
    verifier_class = result.get("verifier_class")
    verifier_pass = result.get("verifier_pass") is True
    verifier_ref = result.get("verifier_receipt_ref")
    ack_ref = result.get("consumer_ack_ref")

    if terminal not in SUCCESS_TERMINALS:
        scar = {
            "event_class": "MISSION_SCAR",
            "actor_id": actor_id,
            "mission_id": mission_id,
            "carrier_episode_id": episode_id,
            "terminal_state": terminal,
            "observed_utc": result.get("observed_utc"),
            "failure_ref": result.get("failure_ref"),
        }
        scar["event_id"] = _event_id(scar)
        return {
            "state": "SCAR",
            "code": "TERMINAL_NOT_VERIFIED_SUCCESS",
            "next_mission_ready": bool(ack_ref),
            "promotion_allowed": False,
            "heritage_event": scar,
        }

    if verifier_class not in ADMITTED_VERIFIERS or not verifier_pass:
        return _hold(
            "BLOCK_UNVERIFIED_PROMOTION",
            "independent/frozen verifier pass required",
        )
    if not isinstance(verifier_ref, str) or not verifier_ref.strip():
        return _hold("BLOCK_MISSING_VERIFIER_RECEIPT", "verifier_receipt_ref required")
    if not isinstance(ack_ref, str) or not ack_ref.strip():
        return _hold("BLOCK_MISSING_CONSUMER_ACK", "consumer_ack_ref required")
    if result.get("candidate_self_awarded") is True:
        return _hold("BLOCK_SELF_AWARD", "carrier/candidate cannot award its own promotion")

    event = {
        "event_class": "VERIFIED_MISSION_EFFECT",
        "actor_id": actor_id,
        "mission_id": mission_id,
        "carrier_episode_id": episode_id,
        "provider": carrier.get("provider"),
        "model": carrier.get("model"),
        "provider_tier": carrier.get("provider_tier"),
        "output_ref": result.get("output_ref"),
        "output_sha256": result.get("output_sha256"),
        "verifier_class": verifier_class,
        "verifier_receipt_ref": verifier_ref,
        "consumer_ack_ref": ack_ref,
        "observed_utc": result.get("observed_utc"),
        "operator_touches": result.get("operator_touches", 0),
    }

    skill = payload.get("skill_candidate")
    if skill is not None and not isinstance(skill, dict):
        raise ValueError("skill_candidate must be object when present")

    promoted_skill = None
    if isinstance(skill, dict):
        skill_id = _require_text(skill, "skill_id")
        skill_version = _require_text(skill, "skill_version")
        promoted_skill = {
            "skill_id": skill_id,
            "skill_version": skill_version,
            "donor_actor_id": skill.get("donor_actor_id", actor_id),
            "mutation_of": skill.get("mutation_of"),
            "provenance_event": None,
        }
        event["skill_promotion"] = promoted_skill

    event["event_id"] = _event_id(event)
    if promoted_skill is not None:
        promoted_skill["provenance_event"] = event["event_id"]

    return {
        "state": "PROMOTE",
        "code": "VERIFIED_EFFECT_ADMITTED",
        "next_mission_ready": True,
        "promotion_allowed": promoted_skill is not None,
        "heritage_event": event,
        "promoted_skill": promoted_skill,
        "claim_ceiling": (
            "DETERMINISTIC_HERITAGE_PROMOTION_ONLY__"
            "NO_QUEUE_LEASE_PROVIDER_OR_EXTERNAL_SUBMIT_AUTHORITY"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    out = reduce_transition(payload)
    print(json.dumps(out, sort_keys=True, indent=2))
    return 0 if out["state"] in {"PROMOTE", "SCAR"} else 3


if __name__ == "__main__":
    raise SystemExit(main())
