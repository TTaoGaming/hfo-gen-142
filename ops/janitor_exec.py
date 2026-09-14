#!/usr/bin/env python3
"""Bounded cleanup leaf. It never schedules/retries/claims; it executes one admitted janitor effect."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools import janitor_gate  # noqa: E402


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def digest(value) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def write_receipt(path: Path, receipt: dict) -> None:
    receipt = dict(receipt)
    receipt["receipt_sha256"] = digest(receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, sort_keys=True))


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--request", required=True)
    p.add_argument("--receipt", required=True)
    p.add_argument("--allowed-root", action="append", default=[])
    args = p.parse_args()
    request_path = Path(args.request)
    receipt_path = Path(args.receipt)
    try:
        doc = json.loads(request_path.read_text(encoding="utf-8"))
    except Exception as exc:
        write_receipt(receipt_path, {
            "schema":"hfo.janitor-receipt.v1", "observed_utc":now_utc(),
            "status":"HOLD_REQUEST_UNREADABLE", "error":type(exc).__name__, "external_effect":False,
        })
        return 20

    gate = janitor_gate.evaluate(doc, args.allowed_root)
    base = {
        "schema":"hfo.janitor-receipt.v1",
        "observed_utc":now_utc(),
        "cleanup_id":doc.get("cleanup_id"),
        "work_ref":doc.get("work_ref"),
        "resource_id":(doc.get("resource") or {}).get("resource_id"),
        "request_sha256":janitor_gate.sha256_json(doc),
        "gate_receipt_sha256":gate.get("receipt_sha256"),
        "target_sha256":gate.get("target_sha256"),
        "external_effect":False,
    }
    if gate["decision"] == "NOOP_CLEAN":
        write_receipt(receipt_path, {**base, "status":"ALREADY_CLEAN", "action":None})
        return 0
    if gate["decision"] != "ADMIT_CLEANUP":
        write_receipt(receipt_path, {**base, "status":"HOLD_GATE", "gate":gate.get("code"), "action":None})
        return 21

    # Re-evaluate immediately before effect to narrow the observation/effect race.
    gate2 = janitor_gate.evaluate(doc, args.allowed_root)
    if gate2["decision"] != "ADMIT_CLEANUP" or gate2.get("receipt_sha256") != gate.get("receipt_sha256"):
        write_receipt(receipt_path, {**base, "status":"HOLD_RECHECK_CHANGED", "gate":gate2.get("code"), "action":None})
        return 22

    resource = doc["resource"]
    target = Path(resource["target"]).expanduser().resolve()
    action = doc["requested_action"]
    try:
        if action in {"DELETE_TEMP_DIR", "DELETE_CACHE_DIR"}:
            shutil.rmtree(target)
        elif action == "REMOVE_WORKTREE":
            repo = Path(resource["repo_root"]).expanduser().resolve()
            proc = subprocess.run(
                ["git", "-C", str(repo), "worktree", "remove", str(target)],
                text=True, capture_output=True, check=False,
            )
            if proc.returncode != 0:
                raise RuntimeError("GIT_WORKTREE_REMOVE_REFUSED")
        else:
            raise RuntimeError("JANITOR_ACTION_UNIMPLEMENTED")
    except Exception as exc:
        write_receipt(receipt_path, {**base, "status":"FAILED", "action":action, "error":type(exc).__name__})
        return 23

    if target.exists():
        write_receipt(receipt_path, {**base, "status":"FAILED_TARGET_REMAINS", "action":action})
        return 24
    write_receipt(receipt_path, {**base, "status":"CLEANED", "action":action})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
