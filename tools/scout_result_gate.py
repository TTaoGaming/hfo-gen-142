#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

REQUIRED_RESULT_KEYS = {
    "observed_utc", "lane", "finding", "strongest_falsifier",
    "blocker", "next_executable_assay",
}
ALLOWED_LANES = {"CROWN", "DONOR", "BENCHMARK", "REDUCER"}


def verdict(state: object) -> dict[str, object]:
    if not isinstance(state, dict):
        return {"decision": "HOLD", "code": "STATE_OBJECT_REQUIRED"}
    if state.get("phase") != "READY":
        return {"decision": "HOLD", "code": "SCOUT_NOT_READY"}
    if state.get("lastError") not in (None, ""):
        return {"decision": "HOLD", "code": "SCOUT_ERROR_PRESENT"}
    raw = state.get("lastResult")
    digest = state.get("lastResultSha256")
    if not isinstance(raw, str) or not raw.strip():
        return {"decision": "HOLD", "code": "RESULT_BYTES_REQUIRED"}
    if not isinstance(digest, str) or len(digest) != 64:
        return {"decision": "HOLD", "code": "RESULT_HASH_REQUIRED"}
    actual = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    if actual != digest:
        return {"decision": "HOLD", "code": "RESULT_HASH_MISMATCH"}
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        return {"decision": "HOLD", "code": "RESULT_JSON_REFUSED"}
    if not isinstance(result, dict):
        return {"decision": "HOLD", "code": "RESULT_OBJECT_REQUIRED"}
    if not REQUIRED_RESULT_KEYS.issubset(result):
        return {"decision": "HOLD", "code": "RESULT_SHAPE_REFUSED"}
    lane = result.get("lane")
    if lane not in ALLOWED_LANES or state.get("lastLane") != lane:
        return {"decision": "HOLD", "code": "RESULT_LANE_MISMATCH"}
    epoch = state.get("epoch")
    if not isinstance(epoch, int) or epoch < 1:
        return {"decision": "HOLD", "code": "SCOUT_EPOCH_REFUSED"}
    return {
        "decision": "ADMIT_RESEARCH_RESULT",
        "code": "READY_RESULT_VERIFIED",
        "actor_id": state.get("actorId"),
        "epoch": epoch,
        "lane": lane,
        "result_sha256": actual,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("state")
    args = ap.parse_args()
    out = verdict(json.loads(Path(args.state).read_text(encoding="utf-8")))
    print(json.dumps(out, sort_keys=True))
    return 0 if out["decision"] == "ADMIT_RESEARCH_RESULT" else 2


if __name__ == "__main__":
    raise SystemExit(main())
