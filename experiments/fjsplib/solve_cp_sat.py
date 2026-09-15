#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

from ortools.sat.python import cp_model

PIN = "7b3f6fb1384309bd4abca866fe3bef2993139b91"
ROOT = f"https://raw.githubusercontent.com/ScheduleOpt/benchmarks/{PIN}/flexible-jobshop"


def fetch_json(url: str):
    with urllib.request.urlopen(url, timeout=30) as r:
        raw = r.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--instance", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--seconds", type=float, default=420)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--outdir", default="out")
    a = ap.parse_args()

    inst_url = f"{ROOT}/instances/json/{a.instance}.json"
    bks_url = f"{ROOT}/solutions/bks.json"
    inst, inst_sha = fetch_json(inst_url)
    bks, bks_sha = fetch_json(bks_url)
    row = next(x for x in bks if x["instance"] == a.instance)
    published_ub = int(row["upper_bound"])
    published_lb = int(row["lower_bound"])
    target = published_ub - 1

    by_op = defaultdict(list)
    machines = defaultdict(list)
    for x in inst["operations"]:
        by_op[int(x["operation"])].append(x)

    model = cp_model.CpModel()
    starts, ends, presences = {}, {}, {}
    for op in sorted(by_op):
        opts = by_op[op]
        durations = {int(x["duration"]) for x in opts}
        if len(durations) != 1:
            raise RuntimeError(f"machine-dependent durations not supported in this canary: op={op}")
        dur = next(iter(durations))
        starts[op] = model.new_int_var(0, target, f"s_{op}")
        ends[op] = model.new_int_var(0, target, f"e_{op}")
        model.add(ends[op] == starts[op] + dur)
        ps = []
        for x in opts:
            m = int(x["machine"])
            p = model.new_bool_var(f"op_{op}_m_{m}")
            iv = model.new_optional_interval_var(starts[op], dur, ends[op], p, f"iv_{op}_m_{m}")
            machines[m].append(iv)
            presences[(op, m)] = p
            ps.append(p)
        model.add_exactly_one(ps)

    for e in inst["precedences"]:
        model.add(ends[int(e["before"])] <= starts[int(e["after"])])
    for m in sorted(machines):
        model.add_no_overlap(machines[m])

    makespan = model.new_int_var(0, target, "makespan")
    model.add_max_equality(makespan, [ends[o] for o in sorted(ends)])
    model.add(makespan <= target)
    model.minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = a.seconds
    solver.parameters.num_search_workers = a.workers
    solver.parameters.random_seed = a.seed
    solver.parameters.randomize_search = True
    solver.parameters.log_search_progress = True
    status = solver.solve(model)
    status_name = solver.status_name(status)

    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    result = {
        "schema": "hfo.fjsplib-bks-hunt.v1",
        "instance": a.instance,
        "source_commit": PIN,
        "instance_sha256": inst_sha,
        "bks_sha256": bks_sha,
        "published_lb": published_lb,
        "published_ub": published_ub,
        "target": target,
        "seed": a.seed,
        "status": status_name,
        "wall_time_s": solver.wall_time,
        "best_objective_bound": solver.best_objective_bound if status in (cp_model.OPTIMAL, cp_model.FEASIBLE, cp_model.UNKNOWN) else None,
        "objective": solver.objective_value if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
    }

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        schedule = []
        for op in sorted(by_op):
            chosen = [m for (o, m), p in presences.items() if o == op and solver.boolean_value(p)]
            if len(chosen) != 1:
                raise RuntimeError(f"bad choice cardinality op={op}: {chosen}")
            m = chosen[0]
            duration = int(by_op[op][0]["duration"])
            schedule.append({
                "operation": op,
                "machine": m,
                "start": solver.value(starts[op]),
                "end": solver.value(ends[op]),
                "duration": duration,
            })
        result["certificate"] = schedule
        result["makespan"] = solver.value(makespan)
        result["improves_public_ub"] = result["makespan"] < published_ub
        result["closes_public_gap"] = result["makespan"] <= published_lb

    p = out / f"{a.instance}-seed{a.seed}.json"
    p.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result.get(k) for k in ("instance", "seed", "status", "published_lb", "published_ub", "target", "objective", "best_objective_bound", "wall_time_s", "improves_public_ub", "closes_public_gap")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
