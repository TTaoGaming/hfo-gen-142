#!/usr/bin/env python3
"""Trusted observation adapter for the Gen142 deterministic reconciler.

This module is intentionally an I/O boundary. It owns no durable state and
accepts no caller-selected authority URLs. It fetches a fixed set of admitted
controllers, derives one immutable hfo.reconcile_snapshot.v0, and then hands
that snapshot to the pure reconcile_kernel policy.

Unknown, stale, contradictory, or unauthenticated observations fail closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

from tools import reconcile_kernel as rk

SCHEMA = "hfo.trusted-observer-result.v0"
OBSERVER_VERSION = "gen142-trusted-observer-r0"

# Authority identities are code-owned, not WorkItem/caller supplied.
CF_STATUS_URL = "https://hfo-sigrun-va-r0.tommytai3.workers.dev/status"
GH_REPO = "TTaoGaming/hfo-gen-142"
GH_ISSUE = 13
GH_DEMAND_DIR = "WORKCELLS/research-r0"
ROUTE_REPO = "TTaoGaming/cdev-control"
ROUTE_PR = 5
ROUTE_WORKFLOW = "gen142-autocell-r0.yml"
ROUTE_ID = "oracle-actions-arm64"
MAX_OBSERVATION_AGE_SECONDS = 120

DISPATCH_MARKER = re.compile(
    r"<!--\s*hfo-reconcile-dispatch:"
    r"(?P<ref>[A-Za-z0-9._:@/-]{1,200}):"
    r"(?P<state>ACTIVE|TERMINAL)\s*-->"
)


class ObservationError(RuntimeError):
    pass


def canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception as exc:
        raise ObservationError("OBSERVED_AT_INVALID") from exc
    if dt.tzinfo is None:
        raise ObservationError("OBSERVED_AT_NAIVE")
    return dt.astimezone(timezone.utc)


def source_receipt(source_ref: str, raw: bytes, observed_at: datetime) -> dict[str, Any]:
    return {
        "source_ref": source_ref,
        "body_sha256": sha256_bytes(raw),
        "observed_at": iso_utc(observed_at),
        "self_attested": False,
    }


def require_fresh(receipts: Iterable[dict[str, Any]], now: datetime) -> None:
    for receipt in receipts:
        observed = parse_utc(str(receipt.get("observed_at", "")))
        age = (now - observed).total_seconds()
        if age < -5:
            raise ObservationError("OBSERVATION_FROM_FUTURE")
        if age > MAX_OBSERVATION_AGE_SECONDS:
            raise ObservationError("OBSERVATION_STALE")
        if receipt.get("self_attested") is not False:
            raise ObservationError("OBSERVATION_SELF_ATTESTED")
        if not re.fullmatch(r"[a-f0-9]{64}", str(receipt.get("body_sha256", ""))):
            raise ObservationError("OBSERVATION_HASH_INVALID")


def _headers(token: str | None = None) -> dict[str, str]:
    out = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GEN142-trusted-observer-r0/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        out["Authorization"] = f"Bearer {token}"
    return out


def http_get(
    url: str,
    *,
    headers: dict[str, str],
    timeout: int = 20,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> tuple[bytes, dict[str, str]]:
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with opener(req, timeout=timeout) as response:
            raw = response.read()
            response_headers = {str(k).lower(): str(v) for k, v in response.headers.items()}
            return raw, response_headers
    except urllib.error.HTTPError as exc:
        raise ObservationError(f"HTTP_{exc.code}:{url}") from exc
    except Exception as exc:
        raise ObservationError(f"FETCH_FAILED:{url}") from exc


def decode_json(raw: bytes, code: str) -> Any:
    try:
        return json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ObservationError(code) from exc


def github_get_json(
    path: str,
    token: str,
    observed_at: datetime,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> tuple[Any, dict[str, Any]]:
    url = f"https://api.github.com{path}"
    raw, _ = http_get(url, headers=_headers(token), opener=opener)
    return decode_json(raw, "GITHUB_JSON_INVALID"), source_receipt(url, raw, observed_at)


def github_all_issue_comments(
    token: str,
    observed_at: datetime,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    comments: list[dict[str, Any]] = []
    receipts: list[dict[str, Any]] = []
    page = 1
    while True:
        path = f"/repos/{GH_REPO}/issues/{GH_ISSUE}/comments?per_page=100&page={page}"
        payload, receipt = github_get_json(path, token, observed_at, opener=opener)
        if not isinstance(payload, list):
            raise ObservationError("ISSUE_COMMENTS_INVALID")
        comments.extend(x for x in payload if isinstance(x, dict))
        receipts.append(receipt)
        if len(payload) < 100:
            break
        page += 1
        if page > 20:
            raise ObservationError("ISSUE_COMMENTS_PAGINATION_REFUSED")
    return comments, receipts


def github_demand(
    token: str,
    observed_at: datetime,
    *,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    path = f"/repos/{GH_REPO}/contents/{GH_DEMAND_DIR}?ref=main"
    listing, listing_receipt = github_get_json(path, token, observed_at, opener=opener)
    if not isinstance(listing, list):
        raise ObservationError("DEMAND_LISTING_INVALID")
    rows: list[dict[str, Any]] = []
    receipts = [listing_receipt]
    for entry in listing:
        if not isinstance(entry, dict):
            continue
        name = str(entry.get("name", ""))
        if not name.endswith(".json"):
            continue
        api_url = entry.get("url")
        if not isinstance(api_url, str) or not api_url.startswith(
            f"https://api.github.com/repos/{GH_REPO}/contents/{GH_DEMAND_DIR}/"
        ):
            raise ObservationError("DEMAND_ENTRY_AUTHORITY_INVALID")
        raw, _ = http_get(api_url, headers=_headers(token), opener=opener)
        envelope = decode_json(raw, "DEMAND_CONTENT_ENVELOPE_INVALID")
        if not isinstance(envelope, dict) or envelope.get("encoding") != "base64":
            raise ObservationError("DEMAND_CONTENT_ENCODING_INVALID")
        import base64
        try:
            body = base64.b64decode(str(envelope["content"]).encode(), validate=False)
            task = json.loads(body.decode("utf-8"))
        except Exception as exc:
            raise ObservationError("DEMAND_TASK_INVALID") from exc
        if task.get("schema") != "hfo.research-workitem.v1":
            raise ObservationError("DEMAND_TASK_SCHEMA_INVALID")
        work_id = str(task.get("work_id", "")).strip()
        priority = task.get("priority", 0)
        if not work_id or not isinstance(priority, int):
            raise ObservationError("DEMAND_TASK_FIELDS_INVALID")
        rows.append(
            {
                "work_id": work_id,
                "path": str(entry.get("path", "")),
                "priority": priority,
                "admitted": task.get("admitted", True) is True,
                "blocked": task.get("blocked", False) is True,
                "spec_sha256": sha256_bytes(body),
            }
        )
        receipts.append(source_receipt(api_url, raw, observed_at))
    rows.sort(key=lambda x: x["work_id"])
    return rows, receipts


def retired_ids(comments: list[dict[str, Any]], demand: list[dict[str, Any]]) -> set[str]:
    bodies = "\n".join(str(c.get("body", "")) for c in comments)
    retired: set[str] = set()
    for row in demand:
        marker = f"<!-- hfo-research-cell-r0:{row['work_id']}:{row['spec_sha256']} -->"
        if marker in bodies:
            retired.add(row["work_id"])
    return retired


def derive_dispatches(comments: list[dict[str, Any]]) -> list[dict[str, Any]]:
    # GitHub #13 is the evidence rendezvous. Only fixed-format controller receipts
    # count; arbitrary prose or caller metadata never creates an active dispatch.
    latest: dict[str, str] = {}
    for comment in comments:
        body = str(comment.get("body", ""))
        for match in DISPATCH_MARKER.finditer(body):
            latest[match.group("ref")] = match.group("state")
    return [
        {"active": True, "dispatch_ref": ref}
        for ref, state in sorted(latest.items())
        if state == "ACTIVE"
    ]


def derive_actor(cf_state: dict[str, Any]) -> dict[str, Any]:
    if cf_state.get("actor") != "SIGRUN/C2":
        raise ObservationError("CLOUDFLARE_ACTOR_IDENTITY_INVALID")
    phase = cf_state.get("phase")
    if phase not in rk.VALID_PHASES:
        raise ObservationError("CLOUDFLARE_PHASE_INVALID")
    mission = cf_state.get("mission")
    workitem_id = mission.get("workitem_id") if isinstance(mission, dict) else None
    worker_job = cf_state.get("worker_job")
    terminal_ref = (
        f"{CF_STATUS_URL.rsplit('/status', 1)[0]}/history/{workitem_id}"
        if phase == "TERMINAL" and workitem_id
        else None
    )
    return {
        "owner": rk.ACTOR_OWNER,
        "phase": phase,
        "workitem_id": workitem_id,
        "worker_job_available": bool(phase == "WAITING_WORKER" and isinstance(worker_job, dict)),
        # External terminal consumption is not inferred from Sigrun's internal P7 ACK.
        "terminal_consumed": False if phase == "TERMINAL" else True,
        "terminal_ref": terminal_ref,
    }


def derive_routes(
    route_pr: dict[str, Any],
    latest_route_run: dict[str, Any] | None,
    now: datetime,
) -> list[dict[str, Any]]:
    # Route admission is fixed to cdev-control#5. Until merged to main, it is not
    # an admitted worker route even if branch assays succeed.
    if route_pr.get("merged") is not True:
        return []
    if not isinstance(latest_route_run, dict):
        return []
    if latest_route_run.get("conclusion") != "success" or latest_route_run.get("head_branch") != "main":
        return []
    updated = parse_utc(str(latest_route_run.get("updated_at", "")))
    if (now - updated).total_seconds() > 3600:
        return []
    return [{"route_id": ROUTE_ID, "live": True, "admitted": True}]


def build_snapshot(
    *,
    cf_state: dict[str, Any],
    demand_rows: list[dict[str, Any]],
    comments: list[dict[str, Any]],
    route_pr: dict[str, Any],
    latest_route_run: dict[str, Any] | None,
    receipts: list[dict[str, Any]],
    now: datetime,
) -> dict[str, Any]:
    require_fresh(receipts, now)
    retired = retired_ids(comments, demand_rows)
    demand = [
        {
            "work_ref": f"github:{GH_REPO}:{row['path']}",
            "priority": row["priority"],
            "admitted": bool(row["admitted"]),
            "blocked": bool(row["blocked"] or row["work_id"] in retired),
        }
        for row in demand_rows
    ]
    snapshot = {
        "schema": rk.SCHEMA,
        "policy_version": rk.POLICY_VERSION,
        "actor": derive_actor(cf_state),
        "demand": demand,
        "dispatches": derive_dispatches(comments),
        "worker_routes": derive_routes(route_pr, latest_route_run, now),
        "human_boundary": {"active": False},
        "observation": {
            "observer_version": OBSERVER_VERSION,
            "observed_at": iso_utc(now),
            "sources": sorted(receipts, key=lambda x: x["source_ref"]),
        },
    }
    return snapshot


def collect(
    *,
    env: dict[str, str] | None = None,
    opener: Callable[..., Any] = urllib.request.urlopen,
    now_fn: Callable[[], datetime] = utc_now,
) -> dict[str, Any]:
    env = os.environ if env is None else env
    token = env.get("SVA_TOKEN", "")
    gh_token = env.get("GH_TOKEN", "")
    if not token:
        raise ObservationError("SVA_TOKEN_MISSING")
    if not gh_token:
        raise ObservationError("GH_TOKEN_MISSING")

    observed_at = now_fn()

    # Cloudflare source identity is fixed in code. SVA_BASE_URL or any caller URL
    # is deliberately ignored.
    cf_raw, _ = http_get(
        CF_STATUS_URL,
        headers={"Authorization": f"Bearer {token}", "User-Agent": _headers()["User-Agent"]},
        opener=opener,
    )
    cf_state = decode_json(cf_raw, "CLOUDFLARE_STATUS_INVALID")
    if not isinstance(cf_state, dict):
        raise ObservationError("CLOUDFLARE_STATUS_INVALID")
    receipts: list[dict[str, Any]] = [source_receipt(CF_STATUS_URL, cf_raw, observed_at)]

    comments, comment_receipts = github_all_issue_comments(gh_token, observed_at, opener=opener)
    demand, demand_receipts = github_demand(gh_token, observed_at, opener=opener)
    receipts.extend(comment_receipts)
    receipts.extend(demand_receipts)

    route_pr_path = f"/repos/{ROUTE_REPO}/pulls/{ROUTE_PR}"
    route_pr, route_pr_receipt = github_get_json(route_pr_path, gh_token, observed_at, opener=opener)
    if not isinstance(route_pr, dict):
        raise ObservationError("ROUTE_PR_INVALID")
    receipts.append(route_pr_receipt)

    latest_route_run: dict[str, Any] | None = None
    if route_pr.get("merged") is True:
        runs_path = (
            f"/repos/{ROUTE_REPO}/actions/workflows/{ROUTE_WORKFLOW}/runs"
            "?branch=main&status=success&per_page=1"
        )
        runs, runs_receipt = github_get_json(runs_path, gh_token, observed_at, opener=opener)
        receipts.append(runs_receipt)
        if not isinstance(runs, dict) or not isinstance(runs.get("workflow_runs"), list):
            raise ObservationError("ROUTE_RUNS_INVALID")
        if runs["workflow_runs"]:
            latest_route_run = runs["workflow_runs"][0]

    return build_snapshot(
        cf_state=cf_state,
        demand_rows=demand,
        comments=comments,
        route_pr=route_pr,
        latest_route_run=latest_route_run,
        receipts=receipts,
        now=observed_at,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    args = parser.parse_args(argv)
    out = Path(args.output)
    try:
        snapshot = collect()
        plan = rk.evaluate(snapshot)
        result = {
            "schema": SCHEMA,
            "observer_version": OBSERVER_VERSION,
            "status": "PASS" if plan["decision"] != "HOLD" else "HOLD",
            "snapshot": snapshot,
            "plan": plan,
        }
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps({"status": result["status"], "plan_sha256": plan["plan_sha256"]}, sort_keys=True))
        return 0 if result["status"] == "PASS" else 2
    except ObservationError as exc:
        result = {
            "schema": SCHEMA,
            "observer_version": OBSERVER_VERSION,
            "status": "HOLD",
            "reason": str(exc),
        }
        out.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps(result, sort_keys=True))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
