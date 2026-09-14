#!/usr/bin/env python3
"""Fail-closed provenance/freshness guard for Gen142 reconcile snapshots.

This module owns no queue, scheduler, lease, actor state, credentials, or effects.
It validates that every control-relevant snapshot field is bound to a fresh,
non-self-attested evidence envelope before the pure reconcile kernel runs.
It does not fetch or authenticate external APIs; that remains the observer seam.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
from pathlib import Path

from tools import reconcile_kernel as rk

GUARD_SCHEMA = "hfo.reconcile_snapshot_guard.v0"
GUARD_VERSION = "gen142-snapshot-guard-r0"
CONTROL_FIELDS = ("actor", "demand", "dispatches", "worker_routes", "human_boundary")
ALLOWED_SOURCE_KINDS = {
    "github_api",
    "github_actions_api",
    "cloudflare_api",
    "vps_controller_api",
    "static_policy",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


def parse_utc(value: object) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = dt.datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(dt.timezone.utc)


def receipt(snapshot: object, decision: str, reason: str, **detail: object) -> dict:
    out = {
        "schema": GUARD_SCHEMA,
        "guard_version": GUARD_VERSION,
        "decision": decision,
        "reason": reason,
        "snapshot_sha256": rk.digest(snapshot),
        **detail,
    }
    out["receipt_sha256"] = rk.digest(out)
    return out


def validate(snapshot: object) -> dict:
    if not isinstance(snapshot, dict):
        return receipt(snapshot, "HOLD", "SNAPSHOT_TYPE")
    if snapshot.get("schema") != rk.SCHEMA:
        return receipt(snapshot, "HOLD", "SNAPSHOT_SCHEMA")
    if snapshot.get("policy_version") != rk.POLICY_VERSION:
        return receipt(snapshot, "HOLD", "POLICY_VERSION_MISMATCH")

    controller_at = parse_utc(snapshot.get("controller_observed_at"))
    if controller_at is None:
        return receipt(snapshot, "HOLD", "CONTROLLER_TIME_INVALID")

    observations = snapshot.get("observations")
    if not isinstance(observations, dict):
        return receipt(snapshot, "HOLD", "OBSERVATIONS_MISSING")

    for field in CONTROL_FIELDS:
        if field not in snapshot:
            return receipt(snapshot, "HOLD", "CONTROL_FIELD_MISSING", field=field)
        obs = observations.get(field)
        if not isinstance(obs, dict):
            return receipt(snapshot, "HOLD", "OBSERVATION_MISSING", field=field)
        if obs.get("self_attested") is not False:
            return receipt(snapshot, "HOLD", "SELF_ATTESTED_OBSERVATION", field=field)
        if obs.get("source_kind") not in ALLOWED_SOURCE_KINDS:
            return receipt(snapshot, "HOLD", "SOURCE_KIND_INVALID", field=field)
        if not isinstance(obs.get("source_ref"), str) or not obs["source_ref"].strip():
            return receipt(snapshot, "HOLD", "SOURCE_REF_MISSING", field=field)

        observed_at = parse_utc(obs.get("observed_at"))
        if observed_at is None:
            return receipt(snapshot, "HOLD", "OBSERVED_TIME_INVALID", field=field)
        max_age_s = obs.get("max_age_s")
        if not isinstance(max_age_s, int) or isinstance(max_age_s, bool) or max_age_s <= 0:
            return receipt(snapshot, "HOLD", "MAX_AGE_INVALID", field=field)
        age_s = (controller_at - observed_at).total_seconds()
        if age_s < 0:
            return receipt(snapshot, "HOLD", "OBSERVATION_FROM_FUTURE", field=field)
        if age_s > max_age_s:
            return receipt(snapshot, "HOLD", "OBSERVATION_STALE", field=field, age_s=age_s, max_age_s=max_age_s)

        source_sha = obs.get("source_sha256")
        if not isinstance(source_sha, str) or not SHA256_RE.fullmatch(source_sha):
            return receipt(snapshot, "HOLD", "SOURCE_HASH_INVALID", field=field)

        value_sha = obs.get("value_sha256")
        if not isinstance(value_sha, str) or not SHA256_RE.fullmatch(value_sha):
            return receipt(snapshot, "HOLD", "VALUE_HASH_INVALID", field=field)
        expected = rk.digest(snapshot[field])
        if value_sha != expected:
            return receipt(snapshot, "HOLD", "VALUE_HASH_MISMATCH", field=field, expected_sha256=expected)

    extras = sorted(set(observations) - set(CONTROL_FIELDS))
    if extras:
        return receipt(snapshot, "HOLD", "UNKNOWN_OBSERVATION_FIELDS", fields=extras)

    return receipt(snapshot, "PASS", "PROVENANCE_ENVELOPE_BOUND", checked_fields=list(CONTROL_FIELDS))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("snapshot")
    args = p.parse_args()
    try:
        snapshot = json.loads(Path(args.snapshot).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"decision": "HOLD", "reason": "SNAPSHOT_UNREADABLE", "error": type(exc).__name__}, sort_keys=True))
        return 2
    result = validate(snapshot)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["decision"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
