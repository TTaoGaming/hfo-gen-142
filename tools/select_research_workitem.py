#!/usr/bin/env python3
"""Pure deterministic selector for cloneable WorkCell demand."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path

SCHEMA = "hfo.research-workitem.v1"
OUT_SCHEMA = "hfo.workcell-selection.v1"
MARKER_PREFIX = "hfo-workcell-v1"
LEGACY_PREFIX = "hfo-research-cell-r0"
QUARANTINE_PREFIX = "hfo-workcell-quarantine-v1"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canon(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def select_work(task_dir: str | Path, retired_text: str) -> dict:
    root = Path(task_dir)
    seen: set[str] = set()
    rows = []
    for path in sorted(root.glob("*.json")):
        raw = path.read_bytes()
        task = json.loads(raw)
        if task.get("schema") != SCHEMA:
            raise ValueError(f"TASK_SCHEMA_REFUSED:{path}")
        wid = str(task.get("work_id", "")).strip()
        if not wid or wid in seen:
            raise ValueError(f"WORK_ID_REFUSED:{wid}")
        seen.add(wid)
        priority = task.get("priority", 0)
        if not isinstance(priority, int):
            raise ValueError(f"PRIORITY_REFUSED:{wid}")
        spec_sha = sha256(raw)
        marker = f"<!-- {MARKER_PREFIX}:{wid}:{spec_sha} -->"
        legacy = f"<!-- {LEGACY_PREFIX}:{wid}:{spec_sha} -->"
        quarantine_marker = f"<!-- {QUARANTINE_PREFIX}:{wid}:{spec_sha} -->"
        retired = marker in retired_text or legacy in retired_text
        quarantined = quarantine_marker in retired_text
        admitted = task.get("admitted", True) is True and task.get("blocked", False) is not True
        rows.append({
            "work_id": wid, "task_path": path.as_posix(), "priority": priority,
            "spec_sha256": spec_sha, "marker": marker, "retired": retired,
            "quarantine_marker": quarantine_marker, "quarantined": quarantined,
            "admitted": admitted,
        })
    candidates = [r for r in rows if r["admitted"] and not r["retired"] and not r["quarantined"]]
    candidates.sort(key=lambda r: (-r["priority"], r["work_id"], r["task_path"]))
    selected = candidates[0] if candidates else None
    out = {
        "schema": OUT_SCHEMA, "selected": selected is not None,
        "selected_work": selected, "scanned": len(rows),
        "retired": sum(1 for r in rows if r["retired"]),
        "quarantined": sum(1 for r in rows if r["quarantined"]),
        "candidates": len(candidates),
    }
    out["selection_sha256"] = sha256(canon(out))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("task_dir")
    ap.add_argument("retirement_ledger")
    ap.add_argument("output")
    args = ap.parse_args()
    try:
        ledger = Path(args.retirement_ledger).read_text(encoding="utf-8", errors="replace")
        out = select_work(args.task_dir, ledger)
    except (ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc))
    Path(args.output).write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
