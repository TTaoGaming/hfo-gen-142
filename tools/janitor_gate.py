#!/usr/bin/env python3
"""Fail-closed admission gate for bounded Gen142 cleanup effects."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "hfo.cleanup-request.v1"
OWNER_SCHEMA = "hfo.cleanup-owner.v1"
SEMANTIC_OWNER = "hfo-sigrun-va-r0"
HEX64 = set("0123456789abcdef")
TERMINAL_STATES = {"PASS", "FAIL", "KILL", "CANCELLED"}
ACTION_BY_KIND = {
    "TEMP_DIR": "DELETE_TEMP_DIR",
    "CACHE_DIR": "DELETE_CACHE_DIR",
    "WORKTREE": "REMOVE_WORKTREE",
}


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_utc(value: Any) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp must be string")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp timezone required")
    return parsed.astimezone(timezone.utc)


def sha256_json(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def is_hex64(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in HEX64 for c in value.lower())


def decision(state: str, code: str, doc: Any, **detail: Any) -> dict[str, Any]:
    out = {
        "schema": "hfo.cleanup-gate-receipt.v1",
        "decision": state,
        "code": code,
        "request_sha256": sha256_json(doc),
        **detail,
    }
    out["receipt_sha256"] = sha256_json(out)
    return out


def hold(code: str, doc: Any, **detail: Any) -> dict[str, Any]:
    return decision("HOLD", code, doc, **detail)


def _under(target: Path, root: Path) -> bool:
    try:
        return os.path.commonpath([str(target), str(root)]) == str(root) and target != root
    except (ValueError, OSError):
        return False


def _safe_roots(values: list[str]) -> list[Path]:
    roots: list[Path] = []
    home = Path.home().resolve()
    for raw in values:
        p = Path(raw).expanduser()
        if not p.is_absolute():
            continue
        p = p.resolve()
        if p == Path(p.anchor) or p == home:
            continue
        roots.append(p)
    return roots


def _worktree_observation(resource: dict[str, Any], target: Path) -> tuple[bool, str]:
    repo_raw = resource.get("repo_root")
    if not isinstance(repo_raw, str) or not repo_raw.strip():
        return False, "WORKTREE_REPO_ROOT_MISSING"
    repo = Path(repo_raw).expanduser().resolve()
    if not repo.is_dir():
        return False, "WORKTREE_REPO_ROOT_MISSING"
    listing = subprocess.run(
        ["git", "-C", str(repo), "worktree", "list", "--porcelain"],
        text=True, capture_output=True, check=False,
    )
    if listing.returncode != 0:
        return False, "WORKTREE_REGISTRY_UNREADABLE"
    registered = []
    for line in listing.stdout.splitlines():
        if line.startswith("worktree "):
            registered.append(Path(line[9:]).resolve())
    if target not in registered:
        return False, "WORKTREE_NOT_REGISTERED"
    status = subprocess.run(
        ["git", "-C", str(target), "status", "--porcelain"],
        text=True, capture_output=True, check=False,
    )
    if status.returncode != 0:
        return False, "WORKTREE_STATUS_UNREADABLE"
    if status.stdout.strip():
        return False, "WORKTREE_DIRTY"
    return True, "WORKTREE_CLEAN_REGISTERED"


def _owner_marker(resource: dict[str, Any], target: Path) -> tuple[bool, str]:
    marker = target / ".hfo-cleanup-owner.json"
    try:
        value = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError):
        return False, "OWNER_MARKER_MISSING_OR_INVALID"
    expected = {
        "schema": OWNER_SCHEMA,
        "resource_id": resource.get("resource_id"),
        "owner_work_ref": resource.get("owner_work_ref"),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            return False, "OWNER_MARKER_MISMATCH"
    return True, "OWNER_MARKER_MATCH"


def evaluate(doc: Any, allowed_roots: list[str], *, now: datetime | None = None, inspect_local: bool = True) -> dict[str, Any]:
    if not isinstance(doc, dict):
        return hold("CLEANUP_TYPE", doc)
    required = {"schema", "cleanup_id", "actor_owner", "work_ref", "requested_action", "resource", "observed"}
    missing = sorted(required - set(doc))
    if missing:
        return hold("CLEANUP_REQUIRED_FIELDS", doc, missing=missing)
    if doc.get("schema") != SCHEMA:
        return hold("CLEANUP_SCHEMA", doc)
    if doc.get("actor_owner") != SEMANTIC_OWNER:
        return hold("CLEANUP_OWNER_INVALID", doc)
    if not isinstance(doc.get("cleanup_id"), str) or not doc["cleanup_id"].strip():
        return hold("CLEANUP_ID_INVALID", doc)
    if not isinstance(doc.get("work_ref"), str) or not doc["work_ref"].strip():
        return hold("CLEANUP_WORK_REF_INVALID", doc)

    resource = doc.get("resource")
    observed = doc.get("observed")
    if not isinstance(resource, dict) or not isinstance(observed, dict):
        return hold("CLEANUP_NESTED_OBJECT_REQUIRED", doc)
    for key in ("resource_id", "kind", "target", "owner_work_ref", "expires_utc", "disposable", "protected", "external_effect"):
        if key not in resource:
            return hold("CLEANUP_RESOURCE_FIELDS", doc, missing=key)
    for key in ("observed_utc", "exists", "identity_match", "active_lease", "pending_consumers", "terminal_state", "durable_evidence_ref", "evidence_sha256", "self_attested"):
        if key not in observed:
            return hold("CLEANUP_OBSERVED_FIELDS", doc, missing=key)

    kind = resource.get("kind")
    expected_action = ACTION_BY_KIND.get(kind)
    if expected_action is None or doc.get("requested_action") != expected_action:
        return hold("CLEANUP_ACTION_KIND_MISMATCH", doc, kind=kind)
    if resource.get("owner_work_ref") != doc.get("work_ref"):
        return hold("CLEANUP_WORK_OWNERSHIP_MISMATCH", doc)
    if resource.get("disposable") is not True or resource.get("protected") is not False:
        return hold("CLEANUP_RESOURCE_NOT_DISPOSABLE", doc)
    if resource.get("external_effect") is not False:
        return hold("CLEANUP_EXTERNAL_EFFECT_REFUSED", doc)
    if observed.get("active_lease") is not False:
        return hold("CLEANUP_ACTIVE_LEASE", doc)
    if observed.get("pending_consumers") != 0:
        return hold("CLEANUP_PENDING_CONSUMER", doc)
    if observed.get("terminal_state") not in TERMINAL_STATES:
        return hold("CLEANUP_TERMINAL_EVIDENCE_REQUIRED", doc)
    if observed.get("self_attested") is not False:
        return hold("CLEANUP_SELF_ATTESTED_EVIDENCE", doc)
    if observed.get("identity_match") is not True:
        return hold("CLEANUP_IDENTITY_MISMATCH", doc)
    if not isinstance(observed.get("durable_evidence_ref"), str) or not observed["durable_evidence_ref"].strip():
        return hold("CLEANUP_DURABLE_EVIDENCE_REQUIRED", doc)
    if not is_hex64(observed.get("evidence_sha256")):
        return hold("CLEANUP_EVIDENCE_SHA_INVALID", doc)

    current = now or utc_now()
    try:
        expires = parse_utc(resource.get("expires_utc"))
        observed_at = parse_utc(observed.get("observed_utc"))
    except ValueError as exc:
        return hold("CLEANUP_TIMESTAMP_INVALID", doc, detail=str(exc))
    if observed_at > current:
        return hold("CLEANUP_OBSERVATION_FROM_FUTURE", doc)
    if current < expires:
        return hold("CLEANUP_TTL_LIVE", doc)

    roots = _safe_roots(allowed_roots)
    if not roots:
        return hold("CLEANUP_ALLOW_ROOT_REQUIRED", doc)
    raw_target = resource.get("target")
    if not isinstance(raw_target, str) or not Path(raw_target).expanduser().is_absolute():
        return hold("CLEANUP_TARGET_ABSOLUTE_REQUIRED", doc)
    target = Path(raw_target).expanduser().resolve(strict=False)
    if not any(_under(target, root) for root in roots):
        return hold("CLEANUP_TARGET_OUTSIDE_ALLOW_ROOT", doc)

    if inspect_local:
        exists = target.exists()
        if observed.get("exists") is not exists:
            return hold("CLEANUP_EXISTENCE_OBSERVATION_STALE", doc, actual_exists=exists)
        if not exists:
            return decision("NOOP_CLEAN", "CLEANUP_ALREADY_ABSENT", doc, resource_id=resource["resource_id"])
        if not target.is_dir():
            return hold("CLEANUP_TARGET_NOT_DIRECTORY", doc)
        if kind in {"TEMP_DIR", "CACHE_DIR"}:
            matched, code = _owner_marker(resource, target)
        else:
            matched, code = _worktree_observation(resource, target)
        if not matched:
            return hold(code, doc)

    return decision(
        "ADMIT_CLEANUP", "CLEANUP_ADMITTED", doc,
        resource_id=resource["resource_id"], kind=kind, action=expected_action,
        target_sha256=hashlib.sha256(str(target).encode()).hexdigest(),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("request")
    parser.add_argument("--allowed-root", action="append", default=[])
    args = parser.parse_args()
    try:
        doc = json.loads(Path(args.request).read_text(encoding="utf-8"))
    except Exception as exc:
        print(json.dumps({"decision":"HOLD","code":"CLEANUP_UNREADABLE","error":type(exc).__name__}, sort_keys=True))
        return 2
    result = evaluate(doc, args.allowed_root)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["decision"] in {"ADMIT_CLEANUP", "NOOP_CLEAN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
