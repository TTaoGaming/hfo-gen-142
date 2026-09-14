#!/usr/bin/env python3
"""Deterministic, stateless WorkCell runtime.

GitHub owns demand/receipts and native wakeups. This runtime owns no durable state,
queue, scheduler, lease, authority, or model policy. It executes at most one admitted
WorkItem per wake, records ConsumerAck, optionally dispatches one next wake, then exits.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from select_research_workitem import select_work

ROOT = Path(__file__).resolve().parents[1]
WORKERS = {"hfo.research-workitem.v1": ROOT / "tools" / "research_cell_r0.py"}


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def sha256(value) -> str:
    data = value if isinstance(value, bytes) else canon(value)
    return hashlib.sha256(data).hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def api(token: str, method: str, path: str, payload=None):
    url = f"https://api.github.com/{path.lstrip('/')}"
    data = None if payload is None else json.dumps(payload).encode()
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GEN142-workcell-runtime-v1",
    }
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read()
            body = json.loads(raw.decode()) if raw else None
            return r.status, body
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"GITHUB_API_{method}_{exc.code}:{path}:{detail[:500]}") from exc


def issue_ledger(token: str, repo: str, issue: int) -> str:
    bodies = []
    page = 1
    while True:
        _, rows = api(token, "GET", f"repos/{repo}/issues/{issue}/comments?per_page=100&page={page}")
        rows = rows or []
        bodies.extend(str(row.get("body", "")) for row in rows)
        if len(rows) < 100:
            break
        page += 1
        if page > 100:
            raise RuntimeError("COMMENT_PAGINATION_REFUSED")
    return "\n".join(bodies)


def worker_for(task: dict) -> Path:
    schema = task.get("schema")
    worker = WORKERS.get(schema)
    if worker is None:
        raise RuntimeError(f"WORKER_SCHEMA_UNSUPPORTED:{schema}")
    return worker


def post_consumer_ack(token: str, repo: str, issue: int, body: str) -> dict:
    status, response = api(token, "POST", f"repos/{repo}/issues/{issue}/comments", {"body": body})
    if status != 201 or not isinstance(response, dict) or not response.get("html_url"):
        raise RuntimeError("CONSUMER_ACK_REFUSED")
    return response


def dispatch_next(token: str, repo: str, workflow: str, ref: str, next_work: dict) -> dict:
    endpoint = f"repos/{repo}/actions/workflows/{workflow}/dispatches"
    status, _ = api(token, "POST", endpoint, {"ref": ref})
    if status != 204:
        raise RuntimeError(f"WORKFLOW_DISPATCH_REFUSED:{status}")
    work_ref = f"github:{repo}:{next_work['task_path']}"
    base = {
        "receipt_type": "github_workflow_dispatch",
        "owner": "github-actions",
        "receipt_id": f"{os.getenv('GITHUB_RUN_ID','local')}:{os.getenv('GITHUB_RUN_ATTEMPT','0')}:{next_work['work_id']}",
        "status": "ACCEPTED",
        "observed_utc": utc_now(),
        "provenance_ref": f"https://api.github.com/{endpoint}",
        "self_attested": False,
        "work_ref": work_ref,
    }
    base["receipt_sha256"] = sha256(base)
    return base


def build_handoff(result: dict, ack_url: str, dispatch_receipt: dict | None) -> dict:
    handoff = {
        "schema": "hfo.terminal-handoff.v1",
        "mission_id": result["work_id"],
        "actor_id": "workcell-runtime-v1",
        "terminal_state": "PASS",
        "tao_relay_required": False,
        "operator_action_required": "NONE",
        "verifier_receipt": {
            "result_sha256": result["result_sha256"],
            "source_count": len(result.get("sources", [])),
        },
        "consumer_ack": {"type": "github_issue_comment", "url": ack_url},
    }
    if dispatch_receipt:
        handoff["next"] = {
            "mode": "AUTO_DISPATCH", "owner": "github-actions",
            "work_ref": dispatch_receipt["work_ref"],
            "dispatch_receipt": dispatch_receipt,
        }
    else:
        handoff["next"] = {"mode": "MISSION_COMPLETE"}
        handoff["mission_complete"] = True
    return handoff


def run_terminal_gate(handoff_path: Path) -> None:
    gate = ROOT / "tools" / "terminal_handoff_gate.py"
    p = subprocess.run([sys.executable, str(gate), str(handoff_path)], text=True, capture_output=True)
    if p.stdout:
        print(p.stdout.strip())
    if p.returncode != 0:
        raise RuntimeError(f"TERMINAL_GATE_REFUSED:{p.stderr or p.stdout}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--task-dir", required=True)
    ap.add_argument("--issue", type=int, required=True)
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY", ""))
    ap.add_argument("--ref", default="main")
    args = ap.parse_args()

    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or ""
    if not token or not args.repo:
        raise SystemExit("GITHUB_RUNTIME_CONTEXT_REQUIRED")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    ledger = issue_ledger(token, args.repo, args.issue)
    selection = select_work(args.task_dir, ledger)
    (outdir / "selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
    if not selection["selected"]:
        summary = {
            "schema": "hfo.workcell-runtime-receipt.v1", "status": "NOOP",
            "reason": "NO_ADMITTED_UNRETIRED_WORK", "selection_sha256": selection["selection_sha256"],
            "tao_hot_loop_actions": 0,
        }
        summary["receipt_sha256"] = sha256(summary)
        (outdir / "runtime-receipt.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(json.dumps(summary, sort_keys=True))
        return 0

    selected = selection["selected_work"]
    task_path = Path(selected["task_path"])
    task = json.loads(task_path.read_text(encoding="utf-8"))
    worker = worker_for(task)
    worker_out = outdir / "worker"
    worker_out.mkdir(exist_ok=True)
    subprocess.run([sys.executable, str(worker), str(task_path), str(worker_out)], check=True)
    result = json.loads((worker_out / "result.json").read_text(encoding="utf-8"))
    report = (worker_out / "report.md").read_text(encoding="utf-8")
    ack_body = f"{report}\nSelection SHA256: {selection['selection_sha256']}\n\n{selected['marker']}"
    ack = post_consumer_ack(token, args.repo, args.issue, ack_body)
    (outdir / "consumer-ack.json").write_text(json.dumps(ack, indent=2), encoding="utf-8")

    post_ledger = issue_ledger(token, args.repo, args.issue)
    next_selection = select_work(args.task_dir, post_ledger)
    (outdir / "next-selection.json").write_text(json.dumps(next_selection, indent=2), encoding="utf-8")
    dispatch_receipt = None
    if next_selection["selected"]:
        dispatch_receipt = dispatch_next(token, args.repo, args.workflow, args.ref, next_selection["selected_work"])
        (outdir / "dispatch-receipt.json").write_text(json.dumps(dispatch_receipt, indent=2), encoding="utf-8")

    handoff = build_handoff(result, ack["html_url"], dispatch_receipt)
    handoff_path = outdir / "handoff.json"
    handoff_path.write_text(json.dumps(handoff, indent=2), encoding="utf-8")
    run_terminal_gate(handoff_path)

    summary = {
        "schema": "hfo.workcell-runtime-receipt.v1", "status": "PASS",
        "work_id": result["work_id"], "result_sha256": result["result_sha256"],
        "consumer_ack": ack["html_url"], "selection_sha256": selection["selection_sha256"],
        "next_work_id": next_selection["selected_work"]["work_id"] if next_selection["selected"] else None,
        "next_dispatched": dispatch_receipt is not None, "tao_hot_loop_actions": 0,
    }
    summary["receipt_sha256"] = sha256(summary)
    (outdir / "runtime-receipt.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
