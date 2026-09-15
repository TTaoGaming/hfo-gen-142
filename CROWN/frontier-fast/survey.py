#!/usr/bin/env python3
"""Survey Frontier Fast without inventing a target ranking.

The output separates external facts (active/frozen, baseline, verified
non-baseline records) from the human/business judgment of buyer legibility.
This is deliberately boring: it prevents an LLM from changing battlefields
because another name sounds more prestigious on the next turn.
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request

BASE = "https://frontier.fast/api"
UA = "Mozilla/5.0 HFO-Gen142-Crown-Survey/1.0"


def get(path: str, query: dict[str, str] | None = None):
    url = BASE + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.load(response)


def main() -> int:
    tracks = get("/tracks")
    rows = []
    for track in tracks:
        if track.get("status") != "active":
            continue
        tid = track["id"]
        board = get("/leaderboard", {"contract": tid, "technique": "all"})
        eligible = [r for r in board if r.get("eligible") is True]
        nonbaseline = [r for r in eligible if r.get("source") != "pinned-baseline"]
        best = max((float(r.get("score") or 0) for r in nonbaseline), default=None)
        rows.append({
            "track_id": tid,
            "model_label": track.get("modelLabel"),
            "device": track.get("deviceLabel"),
            "engine": track.get("engine"),
            "vendor": track.get("vendor"),
            "eligible_nonbaseline_records": len(nonbaseline),
            "best_nonbaseline_score": best,
            "empty_of_verified_nonbaseline_records": len(nonbaseline) == 0,
        })
    rows.sort(key=lambda r: (r["eligible_nonbaseline_records"], r["track_id"]))
    out = {
        "schema": "hfo.frontier-fast-survey.v0",
        "active_track_count": len(rows),
        "active_zero_nonbaseline_tracks": [r["track_id"] for r in rows if r["empty_of_verified_nonbaseline_records"]],
        "tracks": rows,
        "selection_rule": "external facts only; buyer-legibility is a separately versioned decision",
    }
    print(json.dumps(out, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
