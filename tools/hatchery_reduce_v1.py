#!/usr/bin/env python3
"""Pure deterministic hatchery fan-in reducer plus GitHub receipt writer."""
from __future__ import annotations
import argparse, hashlib, json, os, urllib.request
from pathlib import Path
from typing import Any

SCHEMA = "hfo.hatchery-event.v1"
OUT_SCHEMA = "hfo.hatchery-reduction.v1"
POLICY = "hatchery-reducer-v1"
MARKER = "hfo-hatchery-reduction-v1"
REPO = os.environ.get("GITHUB_REPOSITORY", "TTaoGaming/hfo-gen-142")
ISSUE = 13
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
LANE_ORDER = {"REDUCER": 0, "BENCHMARK": 1, "CROWN": 2, "DONOR": 3}


def canon(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256(value: Any) -> str:
    text = value if isinstance(value, str) else canon(value)
    return hashlib.sha256(text.encode()).hexdigest()


def validate_event(event: dict[str, Any]) -> list[dict[str, Any]]:
    if event.get("schema") != SCHEMA or event.get("policy") != "bounded-four-slot-hatchery-v1":
        raise ValueError("HATCHERY_EVENT_SCHEMA_REFUSED")
    entries = event.get("entries")
    if not isinstance(entries, list):
        raise ValueError("HATCHERY_EVENT_ENTRIES_REFUSED")
    if event.get("entries_sha256") != sha256(entries):
        raise ValueError("HATCHERY_EVENT_HASH_MISMATCH")
    return entries


def reduce_event(event: dict[str, Any]) -> dict[str, Any]:
    entries = validate_event(event)
    ready = [e for e in entries if isinstance(e, dict) and isinstance(e.get("result"), dict) and not e.get("error")]
    rate_limited = [e for e in entries if "3021" in str(e.get("error", "")) or "rate limiting" in str(e.get("error", "")).lower()]
    if ready:
        chosen = sorted(ready, key=lambda e: (LANE_ORDER.get(str(e.get("lane")), 99), str(e.get("slot", ""))))[0]
        result = chosen["result"]
        out = {
            "schema": OUT_SCHEMA, "policy_version": POLICY, "decision": "NEXT_RESEARCH_EDGE",
            "event_sha256": event["entries_sha256"], "source_slot": chosen.get("slot"),
            "source_lane": chosen.get("lane"), "result_sha256": chosen.get("result_sha256"),
            "survivors": result.get("survivors", []), "evidence_urls": result.get("evidence_urls", []),
            "finding": result.get("finding", ""), "blocker": result.get("blocker", ""),
            "next_executable_assay": result.get("next_executable_assay", ""),
            "operator_action_required": "NONE", "tao_relay_required": False,
        }
    elif rate_limited:
        out = {
            "schema": OUT_SCHEMA, "policy_version": POLICY, "decision": "BACKPRESSURE_PROVIDER_RATE_LIMIT",
            "event_sha256": event["entries_sha256"], "rate_limited_slots": sorted(str(e.get("slot", "")) for e in rate_limited),
            "next_transition": "WAIT_NEXT_SCHEDULED_HATCH", "operator_action_required": "NONE", "tao_relay_required": False,
        }
    else:
        out = {
            "schema": OUT_SCHEMA, "policy_version": POLICY, "decision": "HOLD_NO_ADMITTED_READY",
            "event_sha256": event["entries_sha256"], "material_entries": len(entries),
            "next_transition": "WAIT_NEXT_SCHEDULED_HATCH", "operator_action_required": "NONE", "tao_relay_required": False,
        }
    out["reduction_sha256"] = sha256(out)
    return out


def request_json(url: str, *, method: str = "GET", body: Any = None) -> Any:
    headers = {"accept": "application/vnd.github+json", "user-agent": POLICY}
    if TOKEN:
        headers.update({"authorization": f"Bearer {TOKEN}", "x-github-api-version": "2022-11-28"})
    data = None if body is None else json.dumps(body).encode()
    if data is not None:
        headers["content-type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode())


def latest_comments() -> list[dict[str, Any]]:
    issue = request_json(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}")
    page = max(1, (int(issue.get("comments", 0)) + 99) // 100)
    return request_json(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments?per_page=100&page={page}")


def post_reduction(reduction: dict[str, Any]) -> str | None:
    marker = f"<!-- {MARKER}:{reduction['reduction_sha256']} -->"
    if any(marker in str(row.get("body", "")) for row in latest_comments()):
        return None
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN_REQUIRED")
    body = "\n".join([
        "## HATCHERY REDUCTION v1 — MACHINE NEXT TRANSITION", "",
        f"- decision: `{reduction['decision']}`",
        f"- policy_version: `{POLICY}`",
        f"- event_sha256: `{reduction['event_sha256']}`",
        "- operator_action_required: `NONE`",
        "- tao_relay_required: `false`", "", "```json",
        json.dumps(reduction, sort_keys=True, ensure_ascii=False), "```", "", marker,
    ])
    result = request_json(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments", method="POST", body={"body": body})
    return str(result.get("html_url", ""))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("event")
    ap.add_argument("--output")
    args = ap.parse_args()
    path = Path(args.event)
    if not path.exists():
        print(json.dumps({"status": "NOOP_NO_HATCHERY_EVENT"}, sort_keys=True))
        return 0
    reduction = reduce_event(json.loads(path.read_text(encoding="utf-8")))
    if args.output:
        output = Path(args.output); output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(reduction, indent=2), encoding="utf-8")
    url = post_reduction(reduction)
    print(json.dumps({"status": "REDUCED" if url else "NOOP_ALREADY_REDUCED", "decision": reduction["decision"], "reduction_sha256": reduction["reduction_sha256"], "comment": url}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
