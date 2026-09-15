#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import json
import os
import sys
import urllib.request
from typing import Any
try:
    from tools.scout_result_gate import verdict as scout_result_verdict
except ModuleNotFoundError:
    from scout_result_gate import verdict as scout_result_verdict

STATE_URL = "https://hfo-gen142-native-scout-r0.tommytai3.workers.dev/state"
REPO = os.environ.get("GITHUB_REPOSITORY", "TTaoGaming/hfo-gen-142")
ISSUE = 13
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or ""
ACTOR = "SIGRUN-GEN142-SCOUT-R0"
READY_MARK = "hfo-scout-fanin-v1"
ANDON_MARK = "hfo-scout-andon-v1"


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def request_json(url: str, *, method: str = "GET", body: Any = None) -> Any:
    headers = {"accept": "application/vnd.github+json", "user-agent": "gen142-scout-fanin-v1"}
    if TOKEN:
        headers["authorization"] = f"Bearer {TOKEN}"
        headers["x-github-api-version"] = "2022-11-28"
    data = None if body is None else json.dumps(body).encode("utf-8")
    if data is not None:
        headers["content-type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def latest_comments() -> list[dict[str, Any]]:
    issue = request_json(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}")
    count = int(issue.get("comments", 0))
    page = max(1, (count + 99) // 100)
    return request_json(f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments?per_page=100&page={page}")


def has_marker(marker: str) -> bool:
    return any(marker in (comment.get("body") or "") for comment in latest_comments())


def post_comment(body: str) -> None:
    if not TOKEN:
        raise RuntimeError("GITHUB_TOKEN_REQUIRED")
    request_json(
        f"https://api.github.com/repos/{REPO}/issues/{ISSUE}/comments",
        method="POST",
        body={"body": body},
    )


def validate_ready(state: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if state.get("actorId") != ACTOR:
        raise ValueError("SCOUT_ACTOR_REFUSED")
    admission = scout_result_verdict(state)
    if admission.get("decision") != "ADMIT_RESEARCH_RESULT":
        raise ValueError(str(admission.get("code", "SCOUT_RESULT_HOLD")))
    lane = state.get("lastLane")
    attempt_lane = state.get("lastAttemptLane")
    if attempt_lane is not None and lane != attempt_lane:
        raise ValueError("READY_OUTER_LANE_MISMATCH")
    text = state["lastResult"]
    digest = state["lastResultSha256"]
    value = json.loads(text)
    survivors = value.get("survivors", [])
    if not isinstance(survivors, list) or len(survivors) > 3 or not all(isinstance(x, str) for x in survivors):
        raise ValueError("READY_SURVIVORS_REFUSED")
    return digest, value


def fanin_ready(state: dict[str, Any]) -> int:
    digest, value = validate_ready(state)
    marker = f"<!-- {READY_MARK}:{digest} -->"
    if has_marker(marker):
        print(json.dumps({"status": "NOOP_ALREADY_FANNED_IN", "digest": digest}))
        return 0
    body = "\n".join([
        "## SCOUT FAN-IN v1 — READY / PROPOSAL ADMITTED TO BLACKBOARD",
        "",
        f"- actor: `{state.get('actorId')}`",
        f"- epoch: `{state.get('epoch')}`",
        f"- lane: `{state.get('lastLane')}`",
        f"- result_sha256: `{digest}`",
        f"- debate_sha256: `{state.get('lastDebateSha256')}`",
        f"- debate_version: `{state.get('debateVersion')}`",
        "- authority: `PROPOSAL_ONLY`; producer != verifier; no crown claim",
        "",
        "```json",
        json.dumps(value, sort_keys=True, ensure_ascii=False),
        "```",
        "",
        marker,
    ])
    post_comment(body)
    print(json.dumps({"status": "FANNED_IN", "digest": digest, "lane": state.get("lastLane")}))
    return 0


def fanin_andon(state: dict[str, Any]) -> int:
    phase = str(state.get("phase", "UNKNOWN"))
    fingerprint = str(state.get("lastFailureFingerprint") or sha256(f"{phase}|{state.get('lastError')}"))
    marker = f"<!-- {ANDON_MARK}:{state.get('epoch')}:{phase}:{fingerprint} -->"
    if has_marker(marker):
        print(json.dumps({"status": "NOOP_ANDON_ALREADY_FANNED_IN", "fingerprint": fingerprint}))
        return 0
    body = "\n".join([
        "## SCOUT ANDON v1 — NO RESULT ADMITTED",
        "",
        f"- actor: `{state.get('actorId')}`",
        f"- phase: `{phase}`",
        f"- epoch: `{state.get('epoch')}`",
        f"- attempted_lane: `{state.get('lastAttemptLane')}`",
        f"- failure_fingerprint: `{fingerprint}`",
        f"- same_failure_count: `{state.get('sameFailureCount')}`",
        f"- error: `{str(state.get('lastError') or '')[:700]}`",
        "- forcing: FAILED/RECOVERY state is not consumable research output",
        "",
        marker,
    ])
    post_comment(body)
    print(json.dumps({"status": "ANDON_FANNED_IN", "fingerprint": fingerprint}))
    return 0


def main() -> int:
    state = request_json(STATE_URL)
    phase = state.get("phase")
    if phase == "READY":
        try:
            return fanin_ready(state)
        except (ValueError, json.JSONDecodeError) as error:
            state["phase"] = "INVALID_READY"
            state["lastError"] = f"SCOUT_ADMISSION_REFUSED:{error}"
            state["lastFailureFingerprint"] = sha256(str(state["lastError"]))
            return fanin_andon(state)
    if phase in {"FAILED", "RECOVERY_REQUIRED"}:
        return fanin_andon(state)
    print(json.dumps({"status": "NOOP_PHASE", "phase": phase, "epoch": state.get("epoch")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
