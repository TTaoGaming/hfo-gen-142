#!/usr/bin/env python3
"""Deterministic, stateless WorkCell runtime.

GitHub owns demand/receipts and native wakeups. This runtime owns no durable state,
queue, scheduler, lease, authority, or model policy. It executes at most one admitted
WorkItem per wake, records ConsumerAck, proves scheduled continuation when needed,
passes the terminal gate, publishes retirement, then exits.
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
ACK_PREFIX = "hfo-workcell-ack-v1"
RETIREMENT_MARKER_PREFIX = "hfo-workcell-v1"


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


def issue_comments(token: str, repo: str, issue: int) -> list[dict]:
    rows: list[dict] = []
    page = 1
    while True:
        _, batch = api(token, "GET", f"repos/{repo}/issues/{issue}/comments?per_page=100&page={page}")
        batch = batch or []
        rows.extend(batch)
        if len(batch) < 100:
            break
        page += 1
        if page > 100:
            raise RuntimeError("COMMENT_PAGINATION_REFUSED")
    return rows


def comment_ledger(rows: list[dict]) -> str:
    """All public prose for OBSERVE_ONLY/reporting uses, never retirement authority."""
    return "\n".join(str(row.get("body", "")) for row in rows)


def is_workcell_actions_comment(row: dict, required_heading: str | None = None) -> bool:
    user = (row.get("user") or {}).get("login")
    app = (row.get("performed_via_github_app") or {}).get("slug")
    body = str(row.get("body", ""))
    if user != "github-actions[bot]" or app != "github-actions":
        return False
    return required_heading is None or required_heading in body


def retirement_ledger(rows: list[dict]) -> str:
    """Return only machine-produced WorkCell retirement facts."""
    admitted = []
    for row in rows:
        body = str(row.get("body", ""))
        if not is_workcell_actions_comment(row, "## WORKCELL RETIREMENT v1"):
            continue
        if f"<!-- {RETIREMENT_MARKER_PREFIX}:" not in body:
            continue
        admitted.append(body)
    return "\n".join(admitted)


def find_comment(rows: list[dict], marker: str, required_heading: str | None = None) -> dict | None:
    for row in rows:
        if not is_workcell_actions_comment(row, required_heading):
            continue
        if marker in str(row.get("body", "")) and row.get("html_url"):
            return row
    return None


def worker_for(task: dict) -> Path:
    schema = task.get("schema")
    worker = WORKERS.get(schema)
    if worker is None:
        raise RuntimeError(f"WORKER_SCHEMA_UNSUPPORTED:{schema}")
    return worker


def post_comment(token: str, repo: str, issue: int, body: str) -> dict:
    status, response = api(token, "POST", f"repos/{repo}/issues/{issue}/comments", {"body": body})
    if status != 201 or not isinstance(response, dict) or not response.get("html_url"):
        raise RuntimeError("GITHUB_COMMENT_REFUSED")
    return response


def ack_marker(selected: dict) -> str:
    return f"<!-- {ACK_PREFIX}:{selected['work_id']}:{selected['spec_sha256']} -->"


def get_or_create_consumer_ack(token: str, repo: str, issue: int, rows: list[dict], selected: dict, report: str, selection_sha: str) -> dict:
    marker = ack_marker(selected)
    prior = find_comment(rows, marker, "## RESEARCH CELL R0")
    if prior is not None:
        return prior
    body = f"{report}\nSelection SHA256: {selection_sha}\n\n{marker}"
    return post_comment(token, repo, issue, body)


def observe_schedule(token: str, repo: str, workflow: str) -> dict:
    endpoint = f"repos/{repo}/actions/workflows/{workflow}"
    status, body = api(token, "GET", endpoint)
    if status != 200 or not isinstance(body, dict) or body.get("state") != "active":
        raise RuntimeError(f"WORKFLOW_WATCH_NOT_ACTIVE:{status}:{body}")
    base = {
        "receipt_type": "github_actions_watch",
        "owner": "github-actions",
        "receipt_id": f"workflow:{body.get('id', workflow)}",
        "status": "ARMED",
        "observed_utc": utc_now(),
        "provenance_ref": f"https://api.github.com/{endpoint}",
        "self_attested": False,
    }
    base["receipt_sha256"] = sha256(base)
    return base


def terminal_state_for(result: dict) -> str:
    for key in ("next_state", "verdict"):
        value = str(result.get(key, "")).upper()
        if value in {"PASS", "FAIL", "HOLD", "KILL"}:
            return value
    raise RuntimeError("WORKER_TERMINAL_STATE_UNDECLARED")


def validate_worker_result(result: dict, selected: dict) -> None:
    if result.get("schema") != "hfo.research-cell-result.v1":
        raise RuntimeError(f"WORKER_RESULT_SCHEMA_REFUSED:{result.get('schema')}")
    if result.get("work_id") != selected.get("work_id"):
        raise RuntimeError("WORKER_RESULT_WORK_ID_MISMATCH")
    if result.get("spec_sha256") != selected.get("spec_sha256"):
        raise RuntimeError("WORKER_RESULT_SPEC_HASH_MISMATCH")
    declared = str(result.get("result_sha256", ""))
    body = dict(result)
    body.pop("result_sha256", None)
    if len(declared) != 64 or declared != sha256(body):
        raise RuntimeError("WORKER_RESULT_HASH_MISMATCH")
    terminal_state_for(result)


def build_handoff(result: dict, ack_url: str, watch_receipt: dict | None) -> dict:
    handoff = {
        "schema": "hfo.terminal-handoff.v1",
        "mission_id": result["work_id"],
        "actor_id": "workcell-runtime-v1",
        "terminal_state": terminal_state_for(result),
        "tao_relay_required": False,
        "operator_action_required": "NONE",
        "verifier_receipt": {
            "result_sha256": result["result_sha256"],
            "source_count": len(result.get("sources", [])),
        },
        "consumer_ack": {"type": "github_issue_comment", "url": ack_url},
    }
    if watch_receipt:
        handoff["next"] = {
            "mode": "RECONCILE",
            "owner": "github-actions",
            "dispatch_receipt": watch_receipt,
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
    args = ap.parse_args()

    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or ""
    if not token or not args.repo:
        raise SystemExit("GITHUB_RUNTIME_CONTEXT_REQUIRED")
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    comments = issue_comments(token, args.repo, args.issue)
    selection = select_work(args.task_dir, retirement_ledger(comments))
    (outdir / "selection.json").write_text(json.dumps(selection, indent=2), encoding="utf-8")
    if not selection["selected"]:
        summary = {
            "schema": "hfo.workcell-runtime-receipt.v1",
            "status": "NOOP",
            "reason": "NO_ADMITTED_UNRETIRED_WORK",
            "selection_sha256": selection["selection_sha256"],
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
    worker_proc = subprocess.run([sys.executable, str(worker), str(task_path), str(worker_out)], check=False)
    result_path = worker_out / "result.json"
    report_path = worker_out / "report.md"
    if worker_proc.returncode != 0 and (not result_path.exists() or not report_path.exists()):
        raise RuntimeError(f"WORKER_NONZERO_WITHOUT_TERMINAL_RECEIPT:{worker_proc.returncode}")
    result = json.loads(result_path.read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    validate_worker_result(result, selected)

    ack = get_or_create_consumer_ack(
        token, args.repo, args.issue, comments, selected, report, selection["selection_sha256"]
    )
    (outdir / "consumer-ack.json").write_text(json.dumps(ack, indent=2), encoding="utf-8")

    comments_after_ack = issue_comments(token, args.repo, args.issue)
    planning_ledger = retirement_ledger(comments_after_ack) + "\n" + selected["marker"]
    next_selection = select_work(args.task_dir, planning_ledger)
    (outdir / "next-selection.json").write_text(json.dumps(next_selection, indent=2), encoding="utf-8")

    watch_receipt = observe_schedule(token, args.repo, args.workflow) if next_selection["selected"] else None
    if watch_receipt:
        (outdir / "watch-receipt.json").write_text(json.dumps(watch_receipt, indent=2), encoding="utf-8")

    handoff = build_handoff(result, ack["html_url"], watch_receipt)
    handoff_path = outdir / "handoff.json"
    handoff_path.write_text(json.dumps(handoff, indent=2), encoding="utf-8")
    run_terminal_gate(handoff_path)

    # Retirement is a separate durable fact and is published only after terminal admission.
    comments_before_retire = issue_comments(token, args.repo, args.issue)
    retirement = find_comment(comments_before_retire, selected["marker"], "## WORKCELL RETIREMENT v1")
    if retirement is None:
        next_id = next_selection["selected_work"]["work_id"] if next_selection["selected"] else "NONE"
        retirement_body = (
            f"## WORKCELL RETIREMENT v1\n\n"
            f"- WorkItem: `{result['work_id']}`\n"
            f"- Terminal state: `{terminal_state_for(result)}`\n"
            f"- ConsumerAck: {ack['html_url']}\n"
            f"- Result SHA256: `{result['result_sha256']}`\n"
            f"- Next WorkItem: `{next_id}`\n"
            f"- Continuation: `{'SCHEDULED_RECONCILE' if watch_receipt else 'MISSION_COMPLETE'}`\n\n"
            f"{selected['marker']}"
        )
        retirement = post_comment(token, args.repo, args.issue, retirement_body)
    (outdir / "retirement.json").write_text(json.dumps(retirement, indent=2), encoding="utf-8")

    summary = {
        "schema": "hfo.workcell-runtime-receipt.v1",
        "status": terminal_state_for(result),
        "worker_exit_code": worker_proc.returncode,
        "work_id": result["work_id"],
        "result_sha256": result["result_sha256"],
        "consumer_ack": ack["html_url"],
        "retirement": retirement["html_url"],
        "selection_sha256": selection["selection_sha256"],
        "next_work_id": next_selection["selected_work"]["work_id"] if next_selection["selected"] else None,
        "continuation_mode": "SCHEDULED_RECONCILE" if watch_receipt else "MISSION_COMPLETE",
        "tao_hot_loop_actions": 0,
    }
    summary["receipt_sha256"] = sha256(summary)
    (outdir / "runtime-receipt.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
