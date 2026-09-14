#!/usr/bin/env python3
"""Thin, fixed-authority observation adapter for the pure reconcile kernel.

This module does not own scheduling, leases, actor state, dispatch, or effects.
It performs read-only observations from a closed set of authorities, derives the
five reconcile fields, binds freshness/body hashes, and only then calls the
existing pure policy kernel. Missing, stale, redirected, or caller-selected
authority fails closed as HOLD.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any

from tools import reconcile_kernel as rk

SCHEMA = "hfo.trusted-reconcile-observation.v0"
MAX_RESPONSE_AGE_SECONDS = 300
CANONICAL_REPO = "TTaoGaming/hfo-gen-142"
TASK_DIR = Path("WORKCELLS/research-r0")
CF_BASE = "https://hfo-sigrun-va-r0.tommytai3.workers.dev"
AUTHORITY_URLS = {
    "cf_health": f"{CF_BASE}/health",
    "cf_status": f"{CF_BASE}/status",
    "gh_main": f"https://api.github.com/repos/{CANONICAL_REPO}/branches/main",
    "gh_runs": f"https://api.github.com/repos/{CANONICAL_REPO}/actions/workflows/research-cell-r0.yml/runs?per_page=20",
    "gh_comments": f"https://api.github.com/repos/{CANONICAL_REPO}/issues/13/comments?per_page=100&page=1",
    "cdev_pr": "https://api.github.com/repos/TTaoGaming/cdev-control/pulls/5",
    "cdev_runners": "https://api.github.com/repos/TTaoGaming/cdev-control/actions/runners?per_page=100",
}
GITHUB_PREFIX = "https://api.github.com/repos/"
_LINK_NEXT = re.compile(r'<([^>]+)>; rel="next"')


class AuthorityHold(RuntimeError):
    pass


@dataclass(frozen=True)
class Readback:
    name: str
    url: str
    observed_utc: str
    server_date_utc: str
    body_sha256: str
    payload: Any


def _utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _canon(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _parse_server_date(value: str) -> datetime:
    dt = parsedate_to_datetime(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class LiveReader:
    def __init__(self, gh_token: str, sva_token: str, timeout: int = 15):
        self.gh_token = gh_token.strip()
        self.sva_token = sva_token.strip()
        self.timeout = timeout

    def _token_for(self, name: str) -> str:
        if name == "cf_status":
            if not self.sva_token:
                raise AuthorityHold("SVA_TOKEN_MISSING")
            return self.sva_token
        if name.startswith("gh_") or name.startswith("cdev_"):
            if not self.gh_token:
                raise AuthorityHold("GITHUB_TOKEN_MISSING")
            return self.gh_token
        return ""

    def _fetch_url(self, name: str, url: str, token: str) -> tuple[Readback, dict[str, str]]:
        headers = {"accept": "application/vnd.github+json", "user-agent": "gen142-trusted-observer-r0"}
        if token:
            headers["authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as response:
                final_url = response.geturl()
                raw = response.read()
                response_headers = {k.lower(): v for k, v in response.headers.items()}
                status = response.status
        except urllib.error.HTTPError as exc:
            raise AuthorityHold(f"{name.upper()}_HTTP_{exc.code}") from exc
        except Exception as exc:
            raise AuthorityHold(f"{name.upper()}_READ_{type(exc).__name__}") from exc
        if status != 200:
            raise AuthorityHold(f"{name.upper()}_HTTP_{status}")
        if final_url != url:
            raise AuthorityHold(f"{name.upper()}_REDIRECT_REFUSED")
        server_date = response_headers.get("date", "")
        if not server_date:
            raise AuthorityHold(f"{name.upper()}_DATE_MISSING")
        try:
            payload = json.loads(raw)
        except Exception as exc:
            raise AuthorityHold(f"{name.upper()}_JSON_REFUSED") from exc
        now = datetime.now(timezone.utc)
        rb = Readback(
            name=name,
            url=url,
            observed_utc=_utc(now),
            server_date_utc=_utc(_parse_server_date(server_date)),
            body_sha256=_sha(raw),
            payload=payload,
        )
        return rb, response_headers

    def read(self, name: str) -> Readback:
        if name not in AUTHORITY_URLS or name == "gh_comments":
            raise AuthorityHold("AUTHORITY_NAME_REFUSED")
        return self._fetch_url(name, AUTHORITY_URLS[name], self._token_for(name))[0]

    def comments(self) -> list[Readback]:
        token = self._token_for("gh_comments")
        url = AUTHORITY_URLS["gh_comments"]
        out: list[Readback] = []
        seen: set[str] = set()
        while url:
            if url in seen or not url.startswith(f"https://api.github.com/repos/{CANONICAL_REPO}/issues/13/comments?"):
                raise AuthorityHold("GH_COMMENTS_PAGINATION_REFUSED")
            seen.add(url)
            rb, headers = self._fetch_url("gh_comments", url, token)
            out.append(rb)
            link = headers.get("link", "")
            m = _LINK_NEXT.search(link)
            url = m.group(1) if m else ""
        return out


def _fresh(rb: Readback, now: datetime) -> bool:
    try:
        server = datetime.fromisoformat(rb.server_date_utc.replace("Z", "+00:00"))
    except Exception:
        return False
    age = (now.astimezone(timezone.utc) - server.astimezone(timezone.utc)).total_seconds()
    return -30 <= age <= MAX_RESPONSE_AGE_SECONDS


def _hold(reason: str, sources: list[Readback] | None = None, **detail: Any) -> dict[str, Any]:
    src = sources or []
    out: dict[str, Any] = {
        "schema": SCHEMA,
        "status": "HOLD",
        "reason": reason,
        "sources": [
            {
                "name": r.name,
                "url": r.url,
                "observed_utc": r.observed_utc,
                "server_date_utc": r.server_date_utc,
                "body_sha256": r.body_sha256,
            }
            for r in src
        ],
        **detail,
    }
    out["observation_sha256"] = _sha(_canon(out))
    return out


def _derive_demand(task_dir: Path, comments: list[Readback]) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    ledger = "\n".join(str(c) for rb in comments for c in (rb.payload if isinstance(rb.payload, list) else []) if isinstance(c, dict) for c in [c.get("body", "")])
    demand: list[dict[str, Any]] = []
    task_evidence: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in sorted(task_dir.glob("*.json")):
        raw = path.read_bytes()
        task = json.loads(raw)
        if task.get("schema") != "hfo.research-workitem.v1":
            raise AuthorityHold(f"TASK_SCHEMA_REFUSED:{path.as_posix()}")
        wid = str(task.get("work_id", "")).strip()
        if not wid or wid in seen:
            raise AuthorityHold(f"TASK_ID_REFUSED:{wid}")
        seen.add(wid)
        priority = task.get("priority", 0)
        if not isinstance(priority, int):
            raise AuthorityHold(f"TASK_PRIORITY_REFUSED:{wid}")
        spec_sha = _sha(raw)
        marker = f"<!-- hfo-research-cell-r0:{wid}:{spec_sha} -->"
        admitted = task.get("admitted", True) is True
        blocked = task.get("blocked", False) is True
        retired = marker in ledger
        task_evidence.append({"path": path.as_posix(), "sha256": spec_sha, "work_id": wid})
        if admitted and not blocked and not retired:
            demand.append({"work_ref": f"github:{CANONICAL_REPO}:{path.as_posix()}", "priority": priority, "admitted": True, "blocked": False})
    demand.sort(key=lambda x: (-x["priority"], x["work_ref"]))
    return demand, task_evidence


def _actor(status: dict[str, Any]) -> dict[str, Any]:
    phase = status.get("phase")
    mission = status.get("mission") if isinstance(status.get("mission"), dict) else {}
    workitem_id = mission.get("workitem_id")
    ack = status.get("ack")
    return {
        "owner": rk.ACTOR_OWNER,
        "phase": phase,
        "workitem_id": workitem_id,
        "worker_job_available": status.get("worker_job") is not None,
        "terminal_consumed": bool(ack),
        "terminal_ref": f"sigrun-history:{workitem_id}" if phase == "TERMINAL" and workitem_id else None,
    }


def _dispatches(runs: dict[str, Any], current_run_id: str) -> list[dict[str, Any]]:
    out = []
    for run in runs.get("workflow_runs", []) if isinstance(runs, dict) else []:
        if not isinstance(run, dict) or str(run.get("id", "")) == current_run_id:
            continue
        if run.get("status") in {"queued", "in_progress", "waiting", "pending"}:
            out.append({"active": True, "dispatch_ref": f"github-actions:{run.get('id')}"})
    out.sort(key=lambda x: x["dispatch_ref"])
    return out


def _worker_routes(runners: dict[str, Any], cdev_pr: dict[str, Any]) -> list[dict[str, Any]]:
    admitted = bool(cdev_pr.get("merged_at"))
    out = []
    for runner in runners.get("runners", []) if isinstance(runners, dict) else []:
        if not isinstance(runner, dict):
            continue
        labels = {x.get("name") for x in runner.get("labels", []) if isinstance(x, dict)}
        if "self-hosted" not in labels:
            continue
        rid = runner.get("id")
        if rid is None:
            continue
        out.append({"route_id": f"cdev-control:runner:{rid}", "live": runner.get("status") == "online" and not runner.get("busy", False), "admitted": admitted})
    out.sort(key=lambda x: x["route_id"])
    return out


def observe(
    reader: Any,
    *,
    now: datetime,
    canonical_sha: str,
    current_run_id: str = "",
    task_dir: Path = TASK_DIR,
    caller_authority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if caller_authority:
        return _hold("CALLER_AUTHORITY_OVERRIDE_REFUSED")

    sources: list[Readback] = []
    payloads: dict[str, Any] = {}
    try:
        for name in ("cf_health", "cf_status", "gh_main", "gh_runs", "cdev_pr", "cdev_runners"):
            rb = reader.read(name)
            sources.append(rb)
            if rb.url != AUTHORITY_URLS[name]:
                return _hold("AUTHORITY_URL_MISMATCH", sources, source=name)
            if not _fresh(rb, now):
                return _hold("STALE_READBACK", sources, source=name)
            payloads[name] = rb.payload
        comment_pages = reader.comments()
        for rb in comment_pages:
            sources.append(rb)
            if not rb.url.startswith(f"https://api.github.com/repos/{CANONICAL_REPO}/issues/13/comments?"):
                return _hold("AUTHORITY_URL_MISMATCH", sources, source="gh_comments")
            if not _fresh(rb, now):
                return _hold("STALE_READBACK", sources, source="gh_comments")
    except AuthorityHold as exc:
        return _hold(str(exc), sources)

    health = payloads["cf_health"]
    if not isinstance(health, dict) or health.get("ok") is not True or health.get("actor") != "SIGRUN/C2":
        return _hold("CLOUDFLARE_HEALTH_REFUSED", sources)
    main = payloads["gh_main"]
    main_sha = ((main.get("commit") or {}).get("sha")) if isinstance(main, dict) else None
    if not canonical_sha or main_sha != canonical_sha:
        return _hold("CHECKOUT_NOT_CANONICAL_MAIN", sources, observed_main_sha=main_sha, checkout_sha=canonical_sha)

    try:
        demand, task_evidence = _derive_demand(task_dir, comment_pages)
    except (AuthorityHold, OSError, ValueError, json.JSONDecodeError) as exc:
        return _hold(f"DEMAND_DERIVATION_REFUSED:{type(exc).__name__}", sources)

    actor_status = payloads["cf_status"]
    if not isinstance(actor_status, dict):
        return _hold("ACTOR_STATUS_REFUSED", sources)
    cdev_pr = payloads["cdev_pr"] if isinstance(payloads["cdev_pr"], dict) else {}
    cdev_runners = payloads["cdev_runners"] if isinstance(payloads["cdev_runners"], dict) else {}
    snapshot = {
        "schema": rk.SCHEMA,
        "policy_version": rk.POLICY_VERSION,
        "actor": _actor(actor_status),
        "demand": demand,
        "dispatches": _dispatches(payloads["gh_runs"], current_run_id),
        "worker_routes": _worker_routes(cdev_runners, cdev_pr),
        "human_boundary": {"active": False} if cdev_pr.get("merged_at") else {
            "active": True,
            "type": "protected_merge",
            "minimal_action": "Satisfy the existing protected review/merge authority for TTaoGaming/cdev-control#5; do not weaken protection.",
            "resume_armed": False,
            "watch_ref": None,
        },
    }
    plan = rk.evaluate(snapshot)
    out = {
        "schema": SCHEMA,
        "status": "SNAPSHOT",
        "sources": [
            {"name": r.name, "url": r.url, "observed_utc": r.observed_utc, "server_date_utc": r.server_date_utc, "body_sha256": r.body_sha256}
            for r in sources
        ],
        "task_evidence": task_evidence,
        "snapshot": snapshot,
        "snapshot_sha256": rk.digest(snapshot),
        "plan": plan,
    }
    out["observation_sha256"] = _sha(_canon(out))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("output")
    args = ap.parse_args()
    reader = LiveReader(os.environ.get("GH_TOKEN", ""), os.environ.get("SVA_TOKEN", ""))
    result = observe(
        reader,
        now=datetime.now(timezone.utc),
        canonical_sha=os.environ.get("GITHUB_SHA", ""),
        current_run_id=os.environ.get("GITHUB_RUN_ID", ""),
    )
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps({"status": result["status"], "reason": result.get("reason"), "observation_sha256": result["observation_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
