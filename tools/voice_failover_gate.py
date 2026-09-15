#!/usr/bin/env python3
"""Fail-closed validator for voice-carrier recovery evidence.

This grants no actor, seat, or runtime authority. It only checks that a
replacement carrier can prove a bounded recovery from durable evidence.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

POLICY_SCHEMA = "hfo.voice-failover-policy.v1"
CHECKPOINT_SCHEMA = "hfo.voice-carrier-checkpoint.v1"
RECOVERY = "github:TTaoGaming/hfo-gen-142#13"
SHA40 = re.compile(r"^[a-f0-9]{40}$")
STATES = {"RUNNING", "HANDOFF", "RECOVERED"}
REASONS = {"NORMAL", "CARRIER_ERROR", "SURFACE_SWITCH", "UNKNOWN"}
EXPECTED_SEQUENCE = [
    "READ_ANCHOR", "READ_LATEST_VOICE_CHECKPOINT",
    "READ_CANONICAL_RECOVERY_NEWEST_FIRST",
    "GENERATE_FRESH_CARRIER_UUID", "COLLISION_CHECK",
    "PROBE_CURRENT_CAPABILITIES", "RESUME_ONE_BOUNDED_EDGE",
    "CHECKPOINT_DURABLE_DELTA",
]
EXPECTED_FORBIDDEN = [
    "INHERIT_CARRIER_UUID", "INFER_AUTHORITY_FROM_VOICE_SESSION",
    "ASK_TAO_TO_REPEAT_DURABLE_CONTEXT",
    "TREAT_PUBLIC_PROSE_AS_RUNTIME_AUTHORITY", "CREATE_PARALLEL_STATE_OWNER",
]

class FailoverError(ValueError):
    pass

def _exact(value, expected, code):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise FailoverError(code)

def _uuid(value, code):
    try:
        return str(uuid.UUID(str(value)))
    except (ValueError, TypeError, AttributeError) as exc:
        raise FailoverError(code) from exc

def validate_policy(value):
    keys = {
        "schema", "policy_version", "authority_class", "anchor_path",
        "latest_checkpoint_path", "canonical_recovery", "carrier_uuid_policy", "carrier_failure_action",
        "inherit_actor", "inherit_seat", "inherit_authority",
        "required_sequence", "forbidden",
    }
    _exact(value, keys, "POLICY_FIELDS_REFUSED")
    if value["schema"] != POLICY_SCHEMA or value["policy_version"] != "voice-failover-v1":
        raise FailoverError("POLICY_SCHEMA_REFUSED")
    if value["authority_class"] != "RECOVERY_EVIDENCE_ONLY":
        raise FailoverError("POLICY_AUTHORITY_REFUSED")
    if value["anchor_path"] != "VOICE/SIGRUN_VOICE_ANCHOR.md" or value["latest_checkpoint_path"] != "VOICE/SIGRUN_HQ_LATEST.md" or value["canonical_recovery"] != RECOVERY:
        raise FailoverError("POLICY_RECOVERY_REFUSED")
    if value["carrier_uuid_policy"] != "FRESH_PER_CARRIER_EPISODE":
        raise FailoverError("POLICY_UUID_REFUSED")
    if value["carrier_failure_action"] != "REHYDRATE_FROM_DURABLE_EVIDENCE":
        raise FailoverError("POLICY_FAILOVER_REFUSED")
    if any(value[k] is not False for k in ("inherit_actor", "inherit_seat", "inherit_authority")):
        raise FailoverError("POLICY_INHERITANCE_REFUSED")
    if value["required_sequence"] != EXPECTED_SEQUENCE or value["forbidden"] != EXPECTED_FORBIDDEN:
        raise FailoverError("POLICY_SEQUENCE_REFUSED")
    return value


def validate_checkpoint(value, policy):
    validate_policy(policy)
    keys = {
        "schema", "carrier_uuid", "predecessor_uuid", "observed_utc",
        "anchor_commit", "cursor_comment_id", "state", "recovery_reason",
        "authority_inherited", "canonical_recovery", "next_machine_edge",
    }
    _exact(value, keys, "CHECKPOINT_FIELDS_REFUSED")
    if value["schema"] != CHECKPOINT_SCHEMA:
        raise FailoverError("CHECKPOINT_SCHEMA_REFUSED")
    carrier = _uuid(value["carrier_uuid"], "CHECKPOINT_UUID_REFUSED")
    predecessor = value["predecessor_uuid"]
    if predecessor is not None:
        predecessor = _uuid(predecessor, "CHECKPOINT_PREDECESSOR_REFUSED")
        if predecessor == carrier:
            raise FailoverError("CHECKPOINT_UUID_REUSE_REFUSED")
    try:
        stamp = str(value["observed_utc"])
        parsed_time = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if parsed_time.tzinfo is None:
            raise ValueError("timezone required")
    except (TypeError, ValueError) as exc:
        raise FailoverError("CHECKPOINT_TIME_REFUSED") from exc
    if not isinstance(value["anchor_commit"], str) or not SHA40.fullmatch(value["anchor_commit"]):
        raise FailoverError("CHECKPOINT_ANCHOR_REFUSED")
    cursor = value["cursor_comment_id"]
    if not isinstance(cursor, int) or isinstance(cursor, bool) or cursor <= 0:
        raise FailoverError("CHECKPOINT_CURSOR_REFUSED")
    if value["state"] not in STATES or value["recovery_reason"] not in REASONS:
        raise FailoverError("CHECKPOINT_STATE_REFUSED")
    if value["authority_inherited"] is not False or value["canonical_recovery"] != RECOVERY:
        raise FailoverError("CHECKPOINT_AUTHORITY_REFUSED")
    edge = value["next_machine_edge"]
    if not isinstance(edge, str) or not edge.strip() or len(edge.encode()) > 1024:
        raise FailoverError("CHECKPOINT_EDGE_REFUSED")
    return {
        "decision": "ADMIT_RECOVERY_EVIDENCE",
        "authority_granted": False,
        "carrier_uuid": carrier,
        "predecessor_uuid": predecessor,
        "cursor_comment_id": cursor,
        "state": value["state"],
    }


def verify_checkout(checkpoint, repo_root: Path):
    root = repo_root.resolve()
    anchor = root / "VOICE" / "SIGRUN_VOICE_ANCHOR.md"
    latest = root / "VOICE" / "SIGRUN_HQ_LATEST.md"
    if not anchor.is_file() or not latest.is_file():
        raise FailoverError("CHECKOUT_RECOVERY_SOURCE_MISSING")
    try:
        head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            text=True, capture_output=True, check=True, timeout=5,
        ).stdout.strip()
    except (OSError, subprocess.SubprocessError) as exc:
        raise FailoverError("CHECKOUT_GIT_REFUSED") from exc
    if head != checkpoint["anchor_commit"]:
        raise FailoverError("CHECKOUT_ANCHOR_COMMIT_MISMATCH")
    try:
        clean = subprocess.run(
            ["git", "-C", str(root), "diff", "--quiet", "HEAD", "--",
             "VOICE/SIGRUN_VOICE_ANCHOR.md", "VOICE/SIGRUN_HQ_LATEST.md",
             "VOICE/VOICE_FAILOVER_POLICY_V1.json"],
            check=False, timeout=5,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise FailoverError("CHECKOUT_GIT_REFUSED") from exc
    if clean.returncode != 0:
        raise FailoverError("CHECKOUT_RECOVERY_BYTES_DIRTY")
    return head


def main():
    p = argparse.ArgumentParser()
    p.add_argument("policy")
    p.add_argument("checkpoint")
    p.add_argument("--repo-root", default=str(Path(__file__).resolve().parents[1]))
    args = p.parse_args()
    try:
        policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
        checkpoint = json.loads(Path(args.checkpoint).read_text(encoding="utf-8"))
        result = validate_checkpoint(checkpoint, policy)
        verify_checkout(checkpoint, Path(args.repo_root))
    except (OSError, json.JSONDecodeError, FailoverError) as exc:
        print(json.dumps({"decision": "HOLD", "reason": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
