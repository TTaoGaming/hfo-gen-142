#!/usr/bin/env python3
"""Deterministic lineage reputation reducer.

This reducer deliberately does NOT invent a universal scalar trust score.
It derives current routing eligibility from append-only evidence events while
preserving the event history for audit.

Positive self-report never changes reputation. Honest UNKNOWN/capability blocks,
failed experiments, and clean EXIT are neutral/process-learning signals. Verified
hard negatives can quarantine until a later independently evidenced supersession
resolves the event.

This is routing reputation, not lineage admission and not universal model quality.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

POSITIVE_EXTERNAL = {
    "INDEPENDENT_VERIFIER",
    "OPERATOR_RATIFICATION",
    "CROSS_FAMILY_REVIEW",
    "PROVIDER_WORLD_RECEIPT",
    "MARKET_HUMAN_OUTCOME",
}
ADVERSE_EXTERNAL = POSITIVE_EXTERNAL | {"MECHANICAL_INTEGRITY_DIFF"}
HONEST_NONDEFECTION = {
    "HONEST_UNKNOWN",
    "HONEST_CAPABILITY_BLOCK",
    "HONEST_FAILED_EXPERIMENT",
}


def reduce_reputation(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Reduce evidence events to a deterministic eligibility digest."""
    ordered = sorted(
        events,
        key=lambda e: (str(e.get("observed_utc", "")), str(e.get("event_id", ""))),
    )
    invalid: list[str] = []
    ignored: list[str] = []
    resolved: set[str] = set()
    valid_supersessions: set[str] = set()
    by_id: dict[str, dict[str, Any]] = {}

    # First pass establishes the immutable event set only.
    for event in ordered:
        event_id = str(event.get("event_id", "<missing>"))
        if event_id in by_id:
            invalid.append(f"{event_id}: duplicate event_id")
            continue
        by_id[event_id] = event

    # Only externally evidenced, effect-admitted later supersessions can resolve history.
    for event_id, event in by_id.items():
        if event.get("event_class") != "SUPERSESSION":
            continue
        evidence_class = event.get("evidence_class")
        effect_allowed = event.get("reputation_effect_allowed", True)
        if (
            event.get("candidate_can_self_award") is not False
            or evidence_class not in POSITIVE_EXTERNAL
            or effect_allowed is False
        ):
            continue
        context = event.get("context") or {}
        targets = context.get("resolves_event_ids", context.get("resolves_event_id", []))
        if isinstance(targets, str):
            targets = [targets]
        if not isinstance(targets, list):
            continue
        valid_supersessions.add(event_id)
        for target in targets:
            if not isinstance(target, str) or target not in by_id or target == event_id:
                continue
            target_time = str(by_id[target].get("observed_utc", ""))
            supersession_time = str(event.get("observed_utc", ""))
            if target_time and supersession_time and supersession_time >= target_time:
                resolved.add(target)
    positive: list[str] = []
    neutral: list[str] = []
    process_learning: list[str] = []
    adverse: list[str] = []

    for event_id, event in by_id.items():
        if event.get("candidate_can_self_award") is not False:
            invalid.append(f"{event_id}: candidate_can_self_award must be false")
            continue

        if event.get("event_class") == "SUPERSESSION":
            if event_id in valid_supersessions:
                neutral.append(event_id)
            else:
                ignored.append(f"{event_id}: supersession lacks admitted external evidence")
            continue
        if event_id in resolved:
            continue

        evidence_class = event.get("evidence_class")
        disposition = event.get("disposition")
        effect_allowed = event.get("reputation_effect_allowed", True)

        if evidence_class == "CANDIDATE_SELF_REPORT_ONLY" or effect_allowed is False:
            ignored.append(f"{event_id}: self-report/non-effect evidence")
            continue

        if event.get("event_class") == "CLEAN_EXIT":
            neutral.append(event_id)
            continue

        if event.get("event_class") in HONEST_NONDEFECTION:
            if disposition == "PROCESS_LEARNING":
                process_learning.append(event_id)
            else:
                neutral.append(event_id)
            continue

        if disposition == "POSITIVE":
            if evidence_class in POSITIVE_EXTERNAL:
                positive.append(event_id)
            else:
                ignored.append(
                    f"{event_id}: positive effect lacks admitted external evidence"
                )
            continue

        if disposition in {"HARD_NEGATIVE", "QUARANTINE", "NEGATIVE", "REVIEW_REQUIRED"}:
            if evidence_class in ADVERSE_EXTERNAL:
                adverse.append(event_id)
            else:
                ignored.append(
                    f"{event_id}: adverse effect lacks admitted verifier/external evidence"
                )
            continue

        if disposition == "PROCESS_LEARNING":
            process_learning.append(event_id)
        else:
            neutral.append(event_id)

    active_adverse = [by_id[event_id] for event_id in adverse]
    if any(
        event.get("disposition") in {"HARD_NEGATIVE", "QUARANTINE"}
        for event in active_adverse
    ):
        eligibility = "QUARANTINED"
    elif active_adverse:
        eligibility = "REVIEW_REQUIRED"
    else:
        eligibility = "ELIGIBLE_FOR_TASK_ROUTING"

    return {
        "projection_type": "LINEAGE_REPUTATION_DIGEST",
        "eligibility": eligibility,
        "positive_event_ids": positive,
        "neutral_event_ids": neutral,
        "process_learning_event_ids": process_learning,
        "active_adverse_event_ids": adverse,
        "resolved_event_ids": sorted(resolved),
        "ignored": ignored,
        "invalid": invalid,
        "claim_ceiling": (
            "DERIVED_ROUTING_REPUTATION_ONLY__NOT_LINEAGE_ADMISSION__"
            "NOT_UNIVERSAL_MODEL_QUALITY"
        ),
    }


def _load_events(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        data = json.loads(text)
        if not isinstance(data, list):
            raise ValueError("JSON input must be an array of events")
        return data
    events: list[dict[str, Any]] = []
    for line_no, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped:
            continue
        event = json.loads(stripped)
        if not isinstance(event, dict):
            raise ValueError(f"line {line_no}: event must be an object")
        events.append(event)
    return events


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("events", type=Path, help="JSON array or JSONL reputation events")
    args = parser.parse_args()
    print(json.dumps(reduce_reputation(_load_events(args.events)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

