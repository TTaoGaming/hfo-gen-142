"""Portable, no-effect bootstrap adapter. No queue, ledger, shell or provider calls."""
import argparse
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ABI = "gen142.hatchery/0"
MAX_INPUT = 16384
MAX_OUTPUT = 8192
PROFILE = "bootstrap.reduce.v1"

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)

def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()

def reduce_packet(packet):
    if not isinstance(packet, dict) or set(packet) != {"abi", "work_id", "profile", "effect_ceiling", "input", "input_sha256"}:
        raise ValueError("PACKET_SHAPE")
    if packet["abi"] != ABI or packet["profile"] != PROFILE:
        raise ValueError("UNSUPPORTED_PROFILE")
    if packet["effect_ceiling"] != "NONE":
        raise ValueError("UNSUPPORTED_EFFECT")
    work = packet["work_id"]
    if not isinstance(work, str) or not 1 <= len(work) <= 80 or not all(c.isascii() and (c.isalnum() or c in "-_") for c in work):
        raise ValueError("WORK_ID")
    data = packet["input"]
    if not isinstance(data, list) or not 1 <= len(data) <= 64:
        raise ValueError("INPUT_BOUND")
    if any(not isinstance(x, str) or not 1 <= len(x) <= 128 or not x.isascii() for x in data):
        raise ValueError("INPUT_ELEMENT")
    if packet["input_sha256"] != digest(data):
        raise ValueError("INPUT_HASH")
    counts = {}
    for item in data:
        counts[item] = counts.get(item, 0) + 1
    output = {"items": [{"text": k, "count": counts[k]} for k in sorted(counts)], "total": len(data)}
    return {"abi": ABI, "work_id": work, "status": "completed", "profile": PROFILE,
            "input_sha256": packet["input_sha256"], "output": output,
            "output_sha256": digest(output), "provider_calls": 0, "external_effects": 0,
            "claim_ceiling": "DETERMINISTIC_BOOTSTRAP_ONLY"}

def describe():
    return {"abi": ABI, "release_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "platform": {"os": platform.system().lower(), "arch": platform.machine().lower()},
            "profiles": [PROFILE], "provider_adapters": [],
            "admission_state": "UNADMITTED", "hot_state_owner": "GITHUB_SHADOW_ONLY",
            "observed_utc": datetime.now(timezone.utc).isoformat(),
            "limits": {"input_bytes": MAX_INPUT, "output_bytes": MAX_OUTPUT, "provider_calls": 0},
            "unsupported": ["arbitrary_code", "external_send", "provider_inference", "autonomous_loop"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--describe", action="store_true")
    parser.add_argument("--assay", action="store_true")
    args = parser.parse_args()
    if args.describe:
        result = describe()
    else:
        if args.assay:
            data = ["research", "evolution", "research", "applications"]
            packet = {"abi": ABI, "work_id": "bootstrap-common-three-hosts", "profile": PROFILE,
                      "effect_ceiling": "NONE", "input": data, "input_sha256": digest(data)}
        else:
            raw = sys.stdin.buffer.read(MAX_INPUT + 1)
            if len(raw) > MAX_INPUT:
                raise ValueError("INPUT_BYTES")
            packet = json.loads(raw)
        result = reduce_packet(packet)
    encoded = canonical(result).encode()
    if len(encoded) > MAX_OUTPUT:
        raise ValueError("OUTPUT_BYTES")
    sys.stdout.buffer.write(encoded + b"\n")

if __name__ == "__main__":
    try:
        main()
    except (ValueError, TypeError, KeyError) as error:
        print(canonical({"status": "rejected", "reason": str(error)[:160], "provider_calls": 0}))
        raise SystemExit(2)
