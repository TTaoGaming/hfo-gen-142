#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import urllib.request
from pathlib import Path

PIN = "7b3f6fb1384309bd4abca866fe3bef2993139b91"
ROOT = f"https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop"


def fetch(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def status_is_infeasible(status: str) -> bool:
    return "INFEASIBLE" in status.upper()


def main() -> None:
    ap = argparse.ArgumentParser(description="Independent PyJobShop formulation for FJSPLib bound falsification")
    ap.add_argument("--instance", required=True)
    ap.add_argument("--target", type=int, required=True, help="Prove/refute existence of any schedule with makespan <= target")
    ap.add_argument("--seconds", type=float, default=600)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    import ortools
    import pyjobshop
    from pyjobshop import Model

    inst, inst_sha = fetch(f"{ROOT}/instances/json/{a.instance}.json")
    bks, bks_sha = fetch(f"{ROOT}/solutions/bks.json")
    row = next(x for x in bks if x["instance"] == a.instance)

    machine_ids = sorted({int(x["machine"]) for x in inst["operations"]})
    op_ids = sorted({int(x["operation"]) for x in inst["operations"]})
    model = Model()
    machines = {mid: model.add_machine(name=str(mid)) for mid in machine_ids}
    # latest_end makes this a pure feasibility decision for makespan <= target.
    tasks = {op: model.add_task(latest_end=a.target, name=str(op)) for op in op_ids}
    mode_count = 0
    for x in inst["operations"]:
        op, mid, duration = int(x["operation"]), int(x["machine"]), int(x["duration"])
        model.add_mode(tasks[op], machines[mid], duration=duration)
        mode_count += 1
    for edge in inst["precedences"]:
        model.add_end_before_start(tasks[int(edge["before"])], tasks[int(edge["after"])])

    result = model.solve(time_limit=a.seconds, display=True, num_workers=a.workers)
    status = str(result.status)
    payload = {
        "schema": "hfo.fjsplib-pyjobshop-bound-proof.v1",
        "instance": a.instance,
        "target": a.target,
        "source_commit": PIN,
        "instance_sha256": inst_sha,
        "bks_sha256": bks_sha,
        "published_lb": int(row["lower_bound"]),
        "published_ub": int(row["upper_bound"]),
        "tasks": len(op_ids),
        "machines": len(machine_ids),
        "modes": mode_count,
        "precedences": len(inst["precedences"]),
        "status": status,
        "objective": None if result.objective == float("inf") else float(result.objective),
        "lower_bound": float(result.lower_bound),
        "runtime": float(result.runtime),
        "time_limit": a.seconds,
        "workers": a.workers,
        "pyjobshop_version": getattr(pyjobshop, "__version__", "unknown"),
        "ortools_version": getattr(ortools, "__version__", "unknown"),
        "python": platform.python_version(),
    }
    payload["proves_no_schedule_at_or_below_target"] = status_is_infeasible(status)
    Path(a.out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, sort_keys=True))


if __name__ == "__main__":
    main()
