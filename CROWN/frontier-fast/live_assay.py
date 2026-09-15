#!/usr/bin/env python3
"""Fail-closed live target assay for the Gen142 Frontier Fast crown lane.

No token, account mutation, submission, or paid resource is required.  The
assay deliberately re-reads the external evaluator instead of trusting HFO
prose.  Exit 0 means the configured target is ACTIVE and still has no eligible
trusted-runner record on either the kernel or speculative board.
"""
from __future__ import annotations

import json
import sys
import urllib.parse
import urllib.request

BASE = "https://frontier.fast/api"
TARGET = "deepseek-v4-flash-gguf-gb10cuda-v1"
UA = "Mozilla/5.0 HFO-Gen142-Crown-Assay/1.0"


def get(path: str, query: dict[str, str] | None = None):
    url = BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def eligible_records(track: str, technique: str):
    rows = get("/leaderboard", {"contract": track, "technique": technique})
    if not isinstance(rows, list):
        raise RuntimeError("LEADERBOARD_NOT_LIST")
    return [r for r in rows if r.get("eligible") is True and r.get("harness") == "trusted-runner"]


def main() -> int:
    tracks = get("/tracks")
    if not isinstance(tracks, list):
        raise RuntimeError("TRACKS_NOT_LIST")
    track = next((t for t in tracks if t.get("id") == TARGET), None)
    if not track:
        raise RuntimeError("TARGET_MISSING")

    kernel = eligible_records(TARGET, "kernel")
    speculative = eligible_records(TARGET, "speculative")
    queue = get("/queue")
    draft = ((track.get("speculative") or {}).get("draftModel") or {})
    advertised = track.get("description") or ""

    reasons: list[str] = []
    if track.get("status") != "active":
        reasons.append("TARGET_NOT_ACTIVE")
    if kernel:
        reasons.append("KERNEL_FRONTIER_EXISTS")
    if speculative:
        reasons.append("SPECULATIVE_FRONTIER_EXISTS")
    if draft.get("pinnedOnRunner") is not True:
        reasons.append("DRAFT_NOT_PINNED")
    if draft.get("specType") != "draft-dspark":
        reasons.append("DRAFT_TYPE_NOT_DSPARK")
    if "25.51 tok/s" not in advertised or "17.51 stock" not in advertised:
        reasons.append("ADVERTISED_MEASUREMENT_MOVED")

    result = {
        "schema": "hfo.frontier-fast-live-assay.v1",
        "target": TARGET,
        "verdict": "PASS_CANDIDATE" if not reasons else "HOLD_TARGET_MOVED",
        "hold_reasons": reasons,
        "track": {
            "status": track.get("status"),
            "model": track.get("model"),
            "model_label": track.get("modelLabel"),
            "device": track.get("deviceLabel"),
            "engine": track.get("engine"),
            "recommended_vram_gib": track.get("recommendedVramGiB"),
        },
        "kernel_record_count": len(kernel),
        "speculative_record_count": len(speculative),
        "draft": {
            "id": draft.get("id"),
            "file": draft.get("file"),
            "pinned_on_runner": draft.get("pinnedOnRunner"),
            "provenance": draft.get("provenance"),
            "spec_type": draft.get("specType"),
        },
        "queue": {
            "depth": queue.get("depth"),
            "running": queue.get("running"),
            "estimated_minutes_per_run": queue.get("estimatedMinutesPerRun"),
        },
        "claim_ceiling": "CANDIDATE_ONLY_NOT_CROWN",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not reasons else 2


if __name__ == "__main__":
    raise SystemExit(main())
