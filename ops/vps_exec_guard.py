#!/usr/bin/env python3
"""Bounded leaf-worker wrapper for VPS execution.

This does NOT claim work, retry, schedule, promote, or own semantic state.
It only enforces the admitted holon mission before launching one bounded carrier.
"""
import argparse
import hashlib
import json
import os
import platform
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "tools" / "holon_gate.py"
FRONTIER_CLASSES = {"frontier", "frontier_api", "frontier_subscription_bridge"}

def utc_now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def write_receipt(path, receipt):
    raw = json.dumps(receipt, sort_keys=True, separators=(",", ":")).encode()
    receipt["receipt_sha256"] = hashlib.sha256(raw).hexdigest()
    text = json.dumps(receipt, sort_keys=True) + "\n"
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(text, encoding="utf-8")
    print(text, end="")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mission", required=True)
    p.add_argument("--receipt", required=True)
    p.add_argument("--timeout-seconds", type=int, default=900)
    p.add_argument("command", nargs=argparse.REMAINDER)
    a = p.parse_args()
    command = a.command[1:] if a.command and a.command[0] == "--" else a.command
    if not command:
        raise SystemExit("command required after --")

    mission_raw = Path(a.mission).read_bytes()
    mission = json.loads(mission_raw)
    gate = subprocess.run(
        [sys.executable, str(GATE), a.mission],
        text=True, capture_output=True, check=False,
    )
    if gate.returncode != 0:
        receipt = {
            "schema": "hfo.vps-exec-receipt.v1", "observed_utc": utc_now(),
            "mission_id": mission.get("mission_id"), "actor_id": mission.get("actor_id"),
            "carrier_id": mission.get("carrier_id"), "status": "HOLD_GATE",
            "gate": gate.stdout.strip() or gate.stderr.strip(), "external_effect": False,
        }
        write_receipt(a.receipt, receipt)
        return 20

    pp = mission.get("provider_policy", {})
    runtime_provider = os.environ.get("HFO_PROVIDER_ID", "")
    runtime_class = os.environ.get("HFO_PROVIDER_CLASS", "")
    local_fallback = os.environ.get("HFO_ALLOW_LOCAL_FALLBACK", "").lower() in {"1", "true", "yes"}
    if pp.get("frontier_required") is True:
        if not runtime_provider or runtime_class not in FRONTIER_CLASSES or local_fallback:
            receipt = {
                "schema": "hfo.vps-exec-receipt.v1", "observed_utc": utc_now(),
                "mission_id": mission.get("mission_id"), "actor_id": mission.get("actor_id"),
                "carrier_id": mission.get("carrier_id"), "status": "HOLD_RUNTIME_PROVIDER",
                "provider_present": bool(runtime_provider), "provider_class": runtime_class or None,
                "local_fallback": local_fallback, "external_effect": False,
            }
            write_receipt(a.receipt, receipt)
            return 21

    deadline = datetime.fromisoformat(mission["deadline_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)
    remaining = int((deadline - datetime.now(timezone.utc)).total_seconds())
    wall = max(1, min(a.timeout_seconds, remaining))
    argv_sha = hashlib.sha256(json.dumps(command, separators=(",", ":")).encode()).hexdigest()
    started = time.monotonic()
    started_utc = utc_now()
    timed_out = False
    proc = None
    try:
        proc = subprocess.Popen(command, start_new_session=True)
        rc = proc.wait(timeout=wall)
    except subprocess.TimeoutExpired:
        timed_out = True
        rc = 124
        if proc is not None:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                proc.wait(timeout=5)
            except Exception:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except Exception:
                    pass
    duration = round(time.monotonic() - started, 3)
    receipt = {
        "schema": "hfo.vps-exec-receipt.v1",
        "mission_id": mission["mission_id"],
        "actor_id": mission["actor_id"],
        "carrier_id": mission["carrier_id"],
        "started_utc": started_utc,
        "observed_utc": utc_now(),
        "status": "TIMEOUT" if timed_out else ("EXIT_0" if rc == 0 else "EXIT_NONZERO"),
        "returncode": rc,
        "duration_seconds": duration,
        "wall_clock_ceiling_seconds": wall,
        "provider_id": runtime_provider or None,
        "provider_class": runtime_class or None,
        "platform": {"system": platform.system(), "machine": platform.machine()},
        "argv_sha256": argv_sha,
        "mission_sha256": hashlib.sha256(mission_raw).hexdigest(),
        "semantic_owner": mission["semantic_owner"],
        "external_effect": mission["effect_ceiling"] != "NO_EXTERNAL_EFFECT",
        "note": "execution receipt only; semantic Result/Verifier/ConsumerAck remains owned by admitted control plane",
    }
    write_receipt(a.receipt, receipt)
    return rc

if __name__ == "__main__":
    raise SystemExit(main())
