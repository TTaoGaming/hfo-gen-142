#!/usr/bin/env python3
"""Fail-closed assembler for authoritative Gen142 reconciler observations.

This module owns no scheduler, queue, lease, actor state, credentials, or effects.
It only validates bounded controller/API observations and emits one canonical
hfo.reconcile_snapshot.v0 document for tools/reconcile_kernel.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

INPUT_SCHEMA = "hfo.reconcile_observations.v0"
SNAPSHOT_SCHEMA = "hfo.reconcile_snapshot.v0"
POLICY_VERSION = "gen142-reconciler-r0"
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED_KINDS = {
    "actor": dict,
    "demand": list,
    "dispatches": list,
    "worker_routes": list,
    "human_boundary": dict,
}
ALLOWED_SOURCE_OWNERS = {
    "actor": {"hfo-sigrun-va-r0"},
    "demand": {"github"},
    "dispatches": {"github-actions", "cloudflare-workflow"},
    "worker_routes": {"github", "github-actions", "cloudflare-workflow"},
    "human_boundary": {"github", "github-actions", "hfo-sigrun-va-r0", "cloudflare-workflow"},
}


def canon(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canon(value).encode()).hexdigest()


def hold(code, **detail):
    return {"decision": "HOLD", "reason": code, **detail}


def parse_utc(value):
    text = str(value or "")
    if not text.endswith("Z"):
        raise ValueError("utc_z_required")
    dt = datetime.fromisoformat(text[:-1] + "+00:00")
    return dt.astimezone(timezone.utc)


def assemble(doc):
    if not isinstance(doc, dict):
        return hold("OBSERVATIONS_TYPE")
    if doc.get("schema") != INPUT_SCHEMA:
        return hold("OBSERVATIONS_SCHEMA", declared=doc.get("schema"))
    if doc.get("policy_version") != POLICY_VERSION:
        return hold("POLICY_VERSION_MISMATCH", declared=doc.get("policy_version"))

    try:
        snapshot_time = parse_utc(doc.get("snapshot_observed_utc"))
    except Exception:
        return hold("SNAPSHOT_OBSERVED_UTC_INVALID")

    max_age = doc.get("max_age_seconds")
    if not isinstance(max_age, int) or not (1 <= max_age <= 3600):
        return hold("MAX_AGE_INVALID", declared=max_age)

    observations = doc.get("observations")
    if not isinstance(observations, list):
        return hold("OBSERVATIONS_LIST_INVALID")

    seen = {}
    evidence = {}
    for obs in observations:
        if not isinstance(obs, dict):
            return hold("OBSERVATION_TYPE")
        kind = obs.get("kind")
        if kind not in REQUIRED_KINDS:
            return hold("OBSERVATION_KIND_INVALID", declared=kind)
        if kind in seen:
            return hold("DUPLICATE_OBSERVATION_KIND", kind=kind)

        source_owner = obs.get("source_owner")
        if source_owner not in ALLOWED_SOURCE_OWNERS[kind]:
            return hold(
                "SOURCE_OWNER_INVALID",
                kind=kind,
                declared=source_owner,
                allowed=sorted(ALLOWED_SOURCE_OWNERS[kind]),
            )
        if obs.get("self_attested") is not False:
            return hold("SELF_ATTESTED_OBSERVATION_FORBIDDEN", kind=kind)

        provenance_ref = str(obs.get("provenance_ref") or "").strip()
        if not provenance_ref:
            return hold("PROVENANCE_REF_REQUIRED", kind=kind)

        source_receipt_sha256 = str(obs.get("source_receipt_sha256") or "")
        if not HEX64.fullmatch(source_receipt_sha256):
            return hold("SOURCE_RECEIPT_SHA256_INVALID", kind=kind)

        try:
            observed_time = parse_utc(obs.get("observed_utc"))
        except Exception:
            return hold("OBSERVATION_UTC_INVALID", kind=kind)
        age = (snapshot_time - observed_time).total_seconds()
        if age < 0:
            return hold("OBSERVATION_FROM_FUTURE", kind=kind)
        if age > max_age:
            return hold(
                "STALE_OBSERVATION",
                kind=kind,
                age_seconds=int(age),
                max_age_seconds=max_age,
            )

        data = obs.get("data")
        expected_type = REQUIRED_KINDS[kind]
        if not isinstance(data, expected_type):
            return hold(
                "OBSERVATION_DATA_TYPE",
                kind=kind,
                expected=expected_type.__name__,
            )

        seen[kind] = data
        evidence[kind] = {
            "source_owner": source_owner,
            "observed_utc": obs["observed_utc"],
            "provenance_ref": provenance_ref,
            "source_receipt_sha256": source_receipt_sha256,
            "data_sha256": digest(data),
            "self_attested": False,
        }

    missing = sorted(set(REQUIRED_KINDS) - set(seen))
    if missing:
        return hold("REQUIRED_OBSERVATION_MISSING", missing=missing)

    snapshot = {
        "schema": SNAPSHOT_SCHEMA,
        "policy_version": POLICY_VERSION,
        "actor": seen["actor"],
        "demand": seen["demand"],
        "dispatches": seen["dispatches"],
        "worker_routes": seen["worker_routes"],
        "human_boundary": seen["human_boundary"],
        "observation": {
            "snapshot_observed_utc": doc["snapshot_observed_utc"],
            "max_age_seconds": max_age,
            "evidence": evidence,
        },
    }
    return {"decision": "PASS", "snapshot": snapshot, "snapshot_sha256": digest(snapshot)}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("observations")
    args = p.parse_args()
    try:
        doc = json.loads(Path(args.observations).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps(hold("OBSERVATIONS_UNREADABLE", error=type(exc).__name__), sort_keys=True))
        return 2

    result = assemble(doc)
    if result["decision"] != "PASS":
        print(json.dumps(result, sort_keys=True))
        return 2
    print(json.dumps(result["snapshot"], sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
