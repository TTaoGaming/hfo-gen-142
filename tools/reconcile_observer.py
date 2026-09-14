#!/usr/bin/env python3
"""Trusted read-only observer for the Gen142 deterministic reconciler.

Authority is established by this adapter fetching fixed controller/API surfaces.
Payload-supplied provenance fields are data only and are never trusted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tools import reconcile_kernel as rk

OBSERVER_VERSION = "gen142-trusted-observer-r0"
ACTOR_ID = "SIGRUN/C2"
ACTOR_STATUS_URL = "https://hfo-sigrun-va-r0.tommytai3.workers.dev/status"
ISSUE_COMMENTS_URL = "https://api.github.com/repos/TTaoGaming/hfo-gen-142/issues/13/comments"
WORKFLOW_RUNS_URL = "https://api.github.com/repos/TTaoGaming/cdev-control/actions/workflows/gen142-autocell-r0.yml/runs"
DEFAULT_TASK_DIR = "WORKCELLS/research-r0"
ACTIVE_RUN_STATES = {"queued", "in_progress", "waiting", "requested", "pending"}


class ObservationHold(RuntimeError):
    pass


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _http_json(url: str, token: str | None = None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": OBSERVER_VERSION}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    with urlopen(req, timeout=20) as response:
        raw = response.read()
        server_date = response.headers.get("Date")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ObservationHold("SOURCE_JSON_INVALID") from exc
    observed = parsedate_to_datetime(server_date).astimezone(timezone.utc).isoformat().replace("+00:00", "Z") if server_date else utc_now()
    return payload, raw, observed


def _github_pages(base_url: str, token: str):
    rows = []
    raw_parts = []
    observed = None
    page = 1
    while True:
        url = base_url + "?" + urlencode({"per_page": 100, "page": page})
        payload, raw, when = _http_json(url, token)
        if not isinstance(payload, list):
            raise ObservationHold("GITHUB_PAGE_NOT_LIST")
        rows.extend(payload)
        raw_parts.append(raw)
        observed = when
        if len(payload) < 100:
            break
        page += 1
        if page > 20:
            raise ObservationHold("GITHUB_PAGINATION_CEILING")
    return rows, b"\n".join(raw_parts), observed or utc_now()


def _load_tasks(task_dir: Path, comment_text: str):
    demand = []
    provenance = []
    for path in sorted(task_dir.glob("*.json")):
        raw = path.read_bytes()
        task = json.loads(raw)
        if task.get("schema") != "hfo.research-workitem.v1":
            raise ObservationHold(f"TASK_SCHEMA_REFUSED:{path.as_posix()}")
        wid = str(task.get("work_id", "")).strip()
        priority = task.get("priority", 0)
        if not wid or not isinstance(priority, int):
            raise ObservationHold(f"TASK_ID_OR_PRIORITY_REFUSED:{path.as_posix()}")
        spec_sha = sha256_bytes(raw)
        marker = f"<!-- hfo-research-cell-r0:{wid}:{spec_sha} -->"
        retired = marker in comment_text
        admitted = task.get("admitted", True) is True and task.get("blocked", False) is not True
        if admitted and not retired:
            demand.append({
                "work_ref": f"github:TTaoGaming/hfo-gen-142:{path.as_posix()}",
                "priority": priority,
                "admitted": True,
                "blocked": False,
            })
        provenance.append({"path": path.as_posix(), "sha256": spec_sha, "retired": retired})
    return demand, provenance


def derive_snapshot(*, actor_status, comments, workflow_runs, task_dir: Path, fetched_utc: str, source_hashes: dict, repo_commit: str):
    """Derive only control fields from raw source payloads.

    The caller cannot supply source references or trust flags. Fixed refs below are
    compiled into the adapter, and all payload metadata with similar names is ignored.
    """
    if not isinstance(actor_status, dict) or actor_status.get("actor") != ACTOR_ID:
        raise ObservationHold("ACTOR_IDENTITY_REFUSED")
    phase = actor_status.get("phase")
    if phase not in rk.VALID_PHASES:
        raise ObservationHold("ACTOR_PHASE_REFUSED")
    mission = actor_status.get("mission") if isinstance(actor_status.get("mission"), dict) else {}
    workitem_id = mission.get("workitem_id")
    if workitem_id is not None and not isinstance(workitem_id, str):
        raise ObservationHold("ACTOR_WORKITEM_REFUSED")

    bodies = [c.get("body", "") for c in comments if isinstance(c, dict) and isinstance(c.get("body", ""), str)]
    comment_text = "\n".join(bodies)
    demand, task_provenance = _load_tasks(task_dir, comment_text)

    if isinstance(workflow_runs, dict):
        runs = workflow_runs.get("workflow_runs", [])
    else:
        runs = workflow_runs
    if not isinstance(runs, list):
        raise ObservationHold("WORKFLOW_RUNS_REFUSED")
    dispatches = []
    for run in runs:
        if not isinstance(run, dict) or run.get("status") not in ACTIVE_RUN_STATES:
            continue
        rid = run.get("id")
        if not isinstance(rid, int):
            raise ObservationHold("WORKFLOW_RUN_ID_REFUSED")
        dispatches.append({"active": True, "dispatch_ref": f"github-actions:TTaoGaming/cdev-control:{rid}"})

    terminal = phase == "TERMINAL"
    terminal_ref = None
    if terminal and workitem_id:
        terminal_ref = f"{ACTOR_STATUS_URL.rsplit('/', 1)[0]}/history/{workitem_id}"

    snapshot = {
        "schema": rk.SCHEMA,
        "policy_version": rk.POLICY_VERSION,
        "actor": {
            "owner": rk.ACTOR_OWNER,
            "phase": phase,
            "workitem_id": workitem_id,
            "worker_job_available": phase == "WAITING_WORKER" and isinstance(actor_status.get("worker_job"), dict),
            "terminal_consumed": not terminal,
            "terminal_ref": terminal_ref,
        },
        "demand": demand,
        "dispatches": dispatches,
        # No route is asserted until an authoritative route reader exists.
        "worker_routes": [],
        "human_boundary": {"active": False},
        "observation": {
            "observer_version": OBSERVER_VERSION,
            "fetched_utc": fetched_utc,
            "repo_commit": repo_commit,
            "sources": {
                "actor": {"ref": ACTOR_STATUS_URL, "sha256": source_hashes["actor"]},
                "demand_ledger": {"ref": ISSUE_COMMENTS_URL, "sha256": source_hashes["comments"]},
                "dispatches": {"ref": WORKFLOW_RUNS_URL, "sha256": source_hashes["runs"]},
                "tasks": task_provenance,
            },
        },
    }
    return snapshot


def observe_live(task_dir: Path):
    sva_token = os.environ.get("SVA_TOKEN", "")
    gh_token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")
    repo_commit = os.environ.get("GITHUB_SHA", "")
    if not sva_token:
        raise ObservationHold("SVA_TOKEN_MISSING")
    if not gh_token:
        raise ObservationHold("GITHUB_TOKEN_MISSING")
    if not repo_commit:
        raise ObservationHold("GITHUB_SHA_MISSING")

    actor, actor_raw, actor_when = _http_json(ACTOR_STATUS_URL, sva_token)
    comments, comments_raw, comments_when = _github_pages(ISSUE_COMMENTS_URL, gh_token)
    runs_url = WORKFLOW_RUNS_URL + "?" + urlencode({"per_page": 30})
    runs, runs_raw, runs_when = _http_json(runs_url, gh_token)
    fetched_utc = max(actor_when, comments_when, runs_when)
    hashes = {
        "actor": sha256_bytes(actor_raw),
        "comments": sha256_bytes(comments_raw),
        "runs": sha256_bytes(runs_raw),
    }
    return derive_snapshot(
        actor_status=actor,
        comments=comments,
        workflow_runs=runs,
        task_dir=task_dir,
        fetched_utc=fetched_utc,
        source_hashes=hashes,
        repo_commit=repo_commit,
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", default=DEFAULT_TASK_DIR)
    ap.add_argument("--output")
    args = ap.parse_args()
    try:
        snapshot = observe_live(Path(args.task_dir))
        plan = rk.evaluate(snapshot)
        out = {"status": "OBSERVED", "snapshot": snapshot, "plan": plan}
        code = 2 if plan["decision"] == "HOLD" else 0
    except ObservationHold as exc:
        out = {
            "status": "HOLD",
            "reason": str(exc),
            "observer_version": OBSERVER_VERSION,
            "tao_relay_required": str(exc) == "SVA_TOKEN_MISSING",
        }
        code = 2
    text = json.dumps(out, sort_keys=True)
    if args.output:
        Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(text)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
