#!/usr/bin/env python3
"""Detect contradictions in the live Frontier Fast target contract.

A leaderboard can be empty while its published execution instructions are
internally inconsistent.  That is a HOLD, not permission to guess a submission.
"""
from __future__ import annotations

import json
import re
import urllib.request

URL = "https://frontier.fast/api/tracks"
TARGET = "deepseek-v4-flash-gguf-gb10cuda-v1"
UA = "Mozilla/5.0 HFO-Gen142-Crown-Assay/1.0"

req = urllib.request.Request(URL, headers={"User-Agent": UA, "Accept": "application/json"})
with urllib.request.urlopen(req, timeout=20) as response:
    tracks = json.load(response)

track = next(x for x in tracks if x.get("id") == TARGET)
speculative = track.get("speculative") or {}
draft = speculative.get("draftModel") or {}
canonical = draft.get("specType")
how_to_run = "\n".join(str(x) for x in (speculative.get("howToRun") or []))
mentioned = sorted(set(re.findall(r"draft-(?:simple|eagle3|mtp|dflash|dspark)", how_to_run)))
consistent = bool(canonical) and canonical in mentioned and all(x == canonical for x in mentioned)

result = {
    "schema": "hfo.frontier-fast-contract-assay.v0",
    "target": TARGET,
    "draft_model_spec_type": canonical,
    "how_to_run_spec_types": mentioned,
    "consistent": consistent,
    "verdict": "PASS" if consistent else "HOLD_PUBLISHED_CONTRACT_CONFLICT",
}
print(json.dumps(result, indent=2, sort_keys=True))
raise SystemExit(0 if consistent else 2)
