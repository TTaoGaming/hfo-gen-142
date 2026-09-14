#!/usr/bin/env python3
"""Fail-closed capability-market gate for Gen142.

Modes:
  job       validate a job envelope and require market allocation when eligible
  bid       validate a capability bid against the job envelope
  selection validate trusted winner selection
  scale     block population growth when operator pain is not improving

This tool never selects a model by itself, grants a lease, sends/spends/publishes,
or creates provider effects. It emits deterministic admission decisions for the
current durable-owner/reference-monitor path after upstream authority admission.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REQUIRED_JOB_FIELDS = (
    "job_id",
    "objective_id",
    "acceptance_tests",
    "effect_ceiling",
    "deadline_or_recheck",
    "privacy_class",
    "mutable_workpiece_key",
    "verification_class",
)
REQUIRED_BID_FIELDS = (
    "bidder_actor_or_phenotype_id",
    "exact_capability_id_and_version",
    "qualification_receipts",
    "proposed_carrier_class",
    "predicted_cost",
    "predicted_latency",
    "confidence",
    "confidence_evidence_basis",
    "required_tools",
    "required_effect_authority",
    "known_failure_scars",
    "proposed_acceptance_route",
)


def _load(path: str | None) -> dict[str, Any]:
    raw = Path(path).read_text(encoding="utf-8") if path else sys.stdin.read()
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("payload must be an object")
    return data


def deny(code: str, detail: str, strife_id: str | None = None) -> dict[str, Any]:
    out: dict[str, Any] = {
        "state": "DENY",
        "code": code,
        "detail": detail,
        "downstream_effect_budget": 0,
        "claim_ceiling": "CAPABILITY_MARKET_ADMISSION_ONLY__NO_LEASE_EFFECT_OR_PROVIDER_AUTHORITY",
    }
    if strife_id:
        out["strife_id"] = strife_id
    return out


def allow(code: str, **extra: Any) -> dict[str, Any]:
    return {
        "state": "ALLOW",
        "code": code,
        "claim_ceiling": "CAPABILITY_MARKET_ADMISSION_ONLY__NO_LEASE_EFFECT_OR_PROVIDER_AUTHORITY",
        **extra,
    }


def _present(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nonnegative_number(value: Any, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError(f"{label} must be a nonnegative number")
    return float(value)


def _nonempty_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a non-empty list")
    return value


def evaluate_job(payload: dict[str, Any]) -> dict[str, Any]:
    job = payload.get("job")
    if not isinstance(job, dict):
        raise ValueError("job object required")
    for field in REQUIRED_JOB_FIELDS:
        value = job.get(field)
        if field == "acceptance_tests":
            _nonempty_list(value, field)
        elif not _present(value):
            return deny("BLOCK_INCOMPLETE_JOB_ENVELOPE", f"missing {field}")
    if not isinstance(job.get("exact_input_refs", []), list):
        raise ValueError("exact_input_refs must be a list")
    market_eligible = job.get("market_eligible") is True
    operator_selects_worker = job.get("operator_selects_worker_manually") is True
    if market_eligible and operator_selects_worker:
        return deny(
            "BLOCK_OPERATOR_MANUAL_WORKER_SELECTION",
            "eligible job must use capability discovery/bidding; operator is not the worker router",
            "gen142.strife.operator-message-bus.v1",
        )
    if market_eligible and job.get("allocation_mode") != "CONTRACT_NET_TOP_K":
        return deny("BLOCK_CAPABILITY_MARKET_BYPASS", "eligible job requires CONTRACT_NET_TOP_K allocation")
    if job.get("broadcast_to_all_neural_actors") is True:
        return deny("BLOCK_NEURAL_BROADCAST_ALLOCATION", "candidate discovery must be deterministic/top-K first")
    return allow("JOB_ENVELOPE_ADMITTED", market_eligible=market_eligible)


def evaluate_bid(payload: dict[str, Any]) -> dict[str, Any]:
    job = payload.get("job")
    bid = payload.get("bid")
    if not isinstance(job, dict) or not isinstance(bid, dict):
        raise ValueError("job and bid objects required")
    for field in REQUIRED_BID_FIELDS:
        if field in {"qualification_receipts", "required_tools", "known_failure_scars"}:
            if not isinstance(bid.get(field), list):
                raise ValueError(f"{field} must be a list")
            if field == "qualification_receipts" and not bid[field]:
                return deny("BLOCK_UNQUALIFIED_CAPABILITY_CLAIM", "qualification_receipts empty")
        elif field in {"predicted_cost", "predicted_latency", "confidence"}:
            continue
        elif not _present(bid.get(field)):
            return deny("BLOCK_INCOMPLETE_CAPABILITY_BID", f"missing {field}")
    predicted_cost = _nonnegative_number(bid.get("predicted_cost"), "predicted_cost")
    predicted_latency = _nonnegative_number(bid.get("predicted_latency"), "predicted_latency")
    confidence = _nonnegative_number(bid.get("confidence"), "confidence")
    if confidence > 1.0:
        return deny("BLOCK_INVALID_BID_CONFIDENCE", "confidence must be <=1")
    max_cost = job.get("max_cost")
    if max_cost is not None and predicted_cost > _nonnegative_number(max_cost, "max_cost"):
        return deny("BLOCK_BID_OVER_JOB_BUDGET", "predicted cost exceeds job max")
    if bid.get("capability_qualification_state") not in {"QUALIFIED", "CONSTRAINED_QUALIFIED"}:
        return deny("BLOCK_UNQUALIFIED_CAPABILITY_CLAIM", "capability is not currently qualified")
    if bid.get("self_accepts_bid") is True or bid.get("self_grants_lease") is True:
        return deny("BLOCK_BIDDER_SELF_AWARD", "bidder may propose but cannot accept itself or grant its own lease")
    return allow(
        "BID_ADMITTED",
        bidder=bid.get("bidder_actor_or_phenotype_id"),
        predicted_cost=predicted_cost,
        predicted_latency=predicted_latency,
    )


def evaluate_selection(payload: dict[str, Any]) -> dict[str, Any]:
    selection = payload.get("selection")
    if not isinstance(selection, dict):
        raise ValueError("selection object required")
    selector = selection.get("selector_actor_id")
    if not _present(selector):
        return deny("BLOCK_MISSING_CAPABILITY_SELECTOR", "selector_actor_id required")
    authority_receipts = selection.get("selector_authority_receipts")
    if (
        selection.get("selector_authority_admitted") is not True
        or not isinstance(authority_receipts, list)
        or not authority_receipts
    ):
        return deny(
            "BLOCK_UNADMITTED_CAPABILITY_SELECTOR",
            "selector authority must be admitted upstream by the current durable state owner",
        )
    winners = selection.get("winner_bid_ids")
    if not isinstance(winners, list):
        raise ValueError("winner_bid_ids must be a list")
    if len(winners) > 1 and selection.get("same_mutable_workpiece") is True:
        return deny("BLOCK_MULTIPLE_WINNERS_SAME_WORKPIECE", "at most one winner for a mutable workpiece")
    if selection.get("selected_bid_is_qualified") is not True and winners:
        return deny("BLOCK_SELECTED_UNQUALIFIED_BID", "winner lacks current qualification")
    if selection.get("bidder_selected_itself") is True:
        return deny("BLOCK_BIDDER_SELF_AWARD", "bidder cannot be its own admitted selector")
    return allow(
        "SELECTION_ADMITTED",
        winner_count=len(winners),
        selector_actor_id=selector,
        selector_authority_receipts=authority_receipts,
    )

def evaluate_scale(payload: dict[str, Any]) -> dict[str, Any]:
    scale = payload.get("scale")
    if not isinstance(scale, dict):
        raise ValueError("scale object required")
    current_population = scale.get("current_population")
    proposed_population = scale.get("proposed_population")
    if not isinstance(current_population, int) or not isinstance(proposed_population, int):
        raise ValueError("population values must be integers")
    if proposed_population <= current_population:
        return allow("NO_POPULATION_GROWTH")
    baseline = _nonnegative_number(scale.get("baseline_operator_touches_per_verified_world_effect"), "baseline_operator_touches_per_verified_world_effect")
    current = _nonnegative_number(scale.get("current_operator_touches_per_verified_world_effect"), "current_operator_touches_per_verified_world_effect")
    admitted_ceiling = _nonnegative_number(scale.get("admitted_operator_touch_ceiling"), "admitted_operator_touch_ceiling")
    sample = scale.get("verified_world_effect_sample_size")
    if not isinstance(sample, int) or sample < 1:
        return deny("BLOCK_SCALE_WITHOUT_WORLD_EFFECT_SAMPLE", "population growth requires verified world-effect sample")
    if current > admitted_ceiling or current > baseline:
        return deny(
            "BLOCK_SCALE_OPERATOR_PAIN_NOT_IMPROVING",
            f"operator touches/world-effect current={current} baseline={baseline} ceiling={admitted_ceiling}",
            "gen142.strife.duplicate-activation-heritage.v1",
        )
    return allow("SCALE_CANDIDATE_ADMITTED", current_population=current_population, proposed_population=proposed_population)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("job", "bid", "selection", "scale"), required=True)
    parser.add_argument("--input")
    args = parser.parse_args(argv)
    try:
        payload = _load(args.input)
        fn = {
            "job": evaluate_job,
            "bid": evaluate_bid,
            "selection": evaluate_selection,
            "scale": evaluate_scale,
        }[args.mode]
        result = fn(payload)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        result = {"state": "ERROR", "code": "INVALID_CAPABILITY_MARKET_INPUT", "detail": str(exc)}
        print(json.dumps(result, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "ALLOW" else 3


if __name__ == "__main__":
    raise SystemExit(main())
